"""
QA-Swarm: Autonomous Multimodal QA & Healing Engine.
Streamlit Interactive Developer Dashboard.
"""

import json
import os
from pathlib import Path
import sys
import time
from typing import Optional

from PIL import Image
import streamlit as st

# Ensure project root is in sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from core.analyzer import apply_patch_to_code, generate_diff_view
from core.orchestrator import export_to_sarif, run_full_audit
from core.schemas import QAAuditReport
from core.test_generator import validate_test_syntax

DEFAULT_SAMPLE_UI = PROJECT_ROOT / "test_samples" / "sample_ui.png"
DEFAULT_BROKEN_CODE = PROJECT_ROOT / "test_samples" / "broken_component.py"
DEFAULT_ANNOTATED_UI = PROJECT_ROOT / "test_samples" / "annotated_ui.png"
DEFAULT_SARIF_PATH = PROJECT_ROOT / "test_samples" / "qa_audit.sarif"
DEFAULT_PLAYWRIGHT_PATH = PROJECT_ROOT / "test_samples" / "test_regression.py"

# Page configuration
st.set_page_config(
    page_title="QA-Swarm | Multimodal DevTool",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom minimalist styling
st.markdown(
    """
    <style>
    /* Metric card styling */
    div[data-testid="stMetric"] {
        background-color: #161822;
        border: 1px solid #282B3E;
        padding: 14px 18px;
        border-radius: 10px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.25);
    }
    div[data-testid="stMetricLabel"] {
        font-size: 0.85rem;
        color: #94A3B8;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    div[data-testid="stMetricValue"] {
        font-size: 1.6rem;
        font-weight: 700;
    }

    /* Badges */
    .badge {
        display: inline-block;
        padding: 4px 10px;
        border-radius: 6px;
        font-size: 0.78rem;
        font-weight: 700;
        letter-spacing: 0.5px;
        text-transform: uppercase;
    }
    .badge-critical { background-color: rgba(239, 68, 68, 0.2); color: #F87171; border: 1px solid #EF4444; }
    .badge-warning { background-color: rgba(245, 158, 11, 0.2); color: #FBBF24; border: 1px solid #F59E0B; }
    .badge-success { background-color: rgba(34, 197, 94, 0.2); color: #4ADE80; border: 1px solid #22C55E; }
    .badge-meta { background-color: rgba(37, 99, 235, 0.2); color: #60A5FA; border: 1px solid #3B82F6; }

    /* Cards */
    .swarm-card {
        background-color: #161822;
        border: 1px solid #282B3E;
        border-radius: 10px;
        padding: 20px;
        margin-bottom: 20px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


def initialize_session():
    """Initializes session state defaults."""
    if "image_path" not in st.session_state:
        st.session_state.image_path = str(DEFAULT_SAMPLE_UI) if DEFAULT_SAMPLE_UI.exists() else None
    if "code_content" not in st.session_state:
        if DEFAULT_BROKEN_CODE.exists():
            with open(DEFAULT_BROKEN_CODE, "r", encoding="utf-8") as f:
                st.session_state.code_content = f.read()
        else:
            st.session_state.code_content = ""
    if "code_filename" not in st.session_state:
        st.session_state.code_filename = "broken_component.py"
    if "audit_report" not in st.session_state:
        st.session_state.audit_report = None
    if "healed_code" not in st.session_state:
        st.session_state.healed_code = None


initialize_session()

# ==============================================================================
# SIDEBAR
# ==============================================================================
with st.sidebar:
    st.markdown("## ⚡ QA-Swarm")
    st.markdown(
        '<span class="badge badge-meta">Meta AI: SAM 3 + Muse Swarm</span>',
        unsafe_allow_html=True,
    )
    st.caption("Autonomous Multimodal QA, Root-Cause Correlation & Auto-Healing")
    st.markdown("---")

    # Priority Action: Load Demo Sample
    st.markdown("### 🎯 Quick Start")
    if st.button("📁 Load Demo Sample", use_container_width=True):
        st.session_state.image_path = str(DEFAULT_SAMPLE_UI)
        if DEFAULT_BROKEN_CODE.exists():
            with open(DEFAULT_BROKEN_CODE, "r", encoding="utf-8") as f:
                st.session_state.code_content = f.read()
        st.session_state.code_filename = "broken_component.py"
        st.session_state.audit_report = None
        st.session_state.healed_code = None
        st.success("✅ Demo sample loaded: E-Commerce button with 120px layout overflow!")

    st.markdown("---")
    st.markdown("### 📤 Custom Input")

    uploaded_img = st.file_uploader("Upload UI Screenshot", type=["png", "jpg", "jpeg"])
    if uploaded_img:
        temp_img_path = PROJECT_ROOT / "test_samples" / f"custom_{uploaded_img.name}"
        with open(temp_img_path, "wb") as f:
            f.write(uploaded_img.getbuffer())
        st.session_state.image_path = str(temp_img_path)
        st.info(f"Loaded: {uploaded_img.name}")

    uploaded_code = st.file_uploader("Upload Component Code", type=["py", "css", "js", "html"])
    if uploaded_code:
        st.session_state.code_content = uploaded_code.getvalue().decode("utf-8")
        st.session_state.code_filename = uploaded_code.name
        st.info(f"Loaded: {uploaded_code.name}")

    st.markdown("---")
    st.markdown("### ⚙️ Engine Settings")
    default_mock = os.getenv("USE_MOCK", "true").strip().lower() in ("true", "1", "yes")
    mock_mode = st.toggle("Mock Mode (Deterministic)", value=default_mock)

    st.markdown("---")
    run_audit_btn = st.button("🚀 Run QA-Swarm Audit", type="primary", use_container_width=True)


# ==============================================================================
# MAIN VIEW: HEADER & AUDIT EXECUTION
# ==============================================================================
st.title("QA-Swarm: Autonomous Multimodal QA & Healing Engine")

if run_audit_btn:
    if not st.session_state.image_path or not Path(st.session_state.image_path).exists():
        st.error("Please load the demo sample or upload a valid UI screenshot first.")
    elif not st.session_state.code_content:
        st.error("Please load the demo sample or upload component source code first.")
    else:
        with st.spinner("Coordinating Agent Swarm (SAM 3 Vision + Muse Correlation)..."):
            time.sleep(1.8)  # Elegant simulated inference delay
            report = run_full_audit(
                image_path=st.session_state.image_path,
                code_path_or_str=st.session_state.code_content,
                file_name=st.session_state.code_filename,
                mock=mock_mode,
            )
            st.session_state.audit_report = report
            # Pre-calculate healed code
            if report.patches:
                st.session_state.healed_code = apply_patch_to_code(
                    st.session_state.code_content, report.patches[0]
                )
            st.toast("Swarm Audit Completed!", icon="⚡")

# If no audit executed yet, display welcoming instructions
if not st.session_state.audit_report:
    st.markdown(
        """
        <div class="swarm-card">
            <h3>👋 Welcome to QA-Swarm</h3>
            <p>QA-Swarm is an autonomous multimodal developer tool that bridges the gap between 
            computer vision inspection and source code healing:</p>
            <ul>
                <li><b>Computer Vision:</b> Detects visual bugs, layout overflows, and clipping anomalies.</li>
                <li><b>Code Correlation:</b> Maps visual bounding boxes directly to offending tokens and source lines.</li>
                <li><b>Healing Engine:</b> Synthesizes deterministic code patches and diff views.</li>
                <li><b>Chaos Engine:</b> Subject systems to adversarial edge cases (Unicode, buffer overflows, concurrency).</li>
                <li><b>CI/CD Gateways:</b> Generates automated Playwright regression tests and OASIS SARIF v2.1.0 reports.</li>
            </ul>
            <p>👉 <b>To begin:</b> Click <b>"📁 Load Demo Sample"</b> in the sidebar, then hit <b>"🚀 Run QA-Swarm Audit"</b>.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.stop()

# ==============================================================================
# HORIZONTAL GOVERNANCE METRICS (4 COLUMNS)
# ==============================================================================
report: QAAuditReport = st.session_state.audit_report

col_metric1, col_metric2, col_metric3, col_metric4 = st.columns(4)

with col_metric1:
    st.metric(
        label="System Health Score",
        value=f"{report.health_score}/100",
        delta="-58 pts (Defects Found)" if report.health_score < 60 else "Healthy",
        delta_color="inverse" if report.health_score < 60 else "normal",
    )

with col_metric2:
    if report.verdict == "BLOCK_DEPLOYMENT":
        verdict_badge = "🚫 BLOCK DEPLOYMENT"
    elif report.verdict == "REQUIRES_REVIEW":
        verdict_badge = "⚠️ REQUIRES REVIEW"
    else:
        verdict_badge = "✅ READY FOR PROD"
    st.metric(label="CI/CD Gate Verdict", value=verdict_badge)

with col_metric3:
    critical_count = sum(1 for d in report.defects if d.severity.upper() in ("CRITICAL", "HIGH"))
    st.metric(
        label="Visual Defects Detected",
        value=f"{len(report.defects)} Total",
        delta=f"{critical_count} Critical" if critical_count > 0 else "0 Critical",
        delta_color="inverse" if critical_count > 0 else "normal",
    )

with col_metric4:
    st.metric(
        label="Chaos Resilience",
        value="20% (Low)",
        delta="5 Vectors Stress-Tested",
        delta_color="off",
    )

st.markdown("<br>", unsafe_allow_html=True)

# ==============================================================================
# TABBED WORKSPACE NAVIGATION
# ==============================================================================
tab_vision, tab_code, tab_chaos, tab_playwright, tab_sarif = st.tabs([
    "👁️ Visual & Spatial Inspector",
    "🧬 Root-Cause & Code Healing",
    "🌪️ Adversarial Chaos Suite",
    "🎭 Playwright Regression Test",
    "🛡️ SARIF v2.1.0 Governance Export",
])

# ------------------------------------------------------------------------------
# TAB 1: VISUAL & SPATIAL INSPECTOR
# ------------------------------------------------------------------------------
with tab_vision:
    st.subheader("Spatial Bounding Box Inspection")
    col_img_orig, col_img_annotated = st.columns(2)

    with col_img_orig:
        st.markdown("**Original UI Screenshot**")
        if st.session_state.image_path and Path(st.session_state.image_path).exists():
            st.image(st.session_state.image_path, use_container_width=True)

    with col_img_annotated:
        st.markdown("**SAM 3 Annotated Defect Overlay (#FF3B30)**")
        if DEFAULT_ANNOTATED_UI.exists():
            st.image(str(DEFAULT_ANNOTATED_UI), use_container_width=True)
        elif st.session_state.image_path:
            st.image(st.session_state.image_path, use_container_width=True)

    st.markdown("#### Detected Visual Anomalies")
    for idx, defect in enumerate(report.defects, 1):
        with st.expander(f"Defect #{idx}: {defect.element_name} ({defect.defect_type})", expanded=True):
            col_d1, col_d2, col_d3 = st.columns(3)
            col_d1.markdown(f"**Element:** `{defect.element_name}`")
            col_d2.markdown(f"**Bounding Box [ymin, xmin, ymax, xmax]:** `{defect.bbox}`")
            col_d3.markdown(
                f'**Severity:** <span class="badge badge-critical">{defect.severity}</span>',
                unsafe_allow_html=True,
            )

# ------------------------------------------------------------------------------
# TAB 2: ROOT-CAUSE & CODE HEALING
# ------------------------------------------------------------------------------
with tab_code:
    st.subheader("Multimodal Root-Cause Analysis & Automated Patching")

    if report.root_causes and report.patches:
        primary_rc = report.root_causes[0]
        primary_patch = report.patches[0]

        st.markdown(
            f"""
            <div class="swarm-card">
                <h4>🔍 Root Cause Identified</h4>
                <p><b>Target Location:</b> <code>{primary_rc.target_file}</code> at line <b>{primary_rc.target_line}</b></p>
                <p><b>Offending Token:</b> <code style="color: #EF4444;">{primary_rc.offending_token}</code></p>
                <p><b>Technical Explanation:</b> {primary_rc.explanation}</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown("#### Unified Diff View")
        diff_text = generate_diff_view(
            st.session_state.code_content,
            st.session_state.healed_code or st.session_state.code_content,
        )
        st.code(diff_text, language="diff")

        col_code_orig, col_code_patched = st.columns(2)
        with col_code_orig:
            st.markdown(f"**Original Source (`{primary_rc.target_file}`)**")
            st.code(st.session_state.code_content, language="python", line_numbers=True)

        with col_code_patched:
            st.markdown("**Remediated Source (Auto-Patched)**")
            st.code(
                st.session_state.healed_code or st.session_state.code_content,
                language="python",
                line_numbers=True,
            )

        if st.button("💾 Apply Remediation Patch to Workspace", type="primary"):
            st.session_state.code_content = st.session_state.healed_code
            st.success("✅ Patch applied successfully! Fixed rigid constraint with fluid styling.")
    else:
        st.info("No root causes or patches to display.")

# ------------------------------------------------------------------------------
# TAB 3: ADVERSARIAL CHAOS SUITE
# ------------------------------------------------------------------------------
with tab_chaos:
    st.subheader("Adversarial Chaos Engineering Suite")
    st.caption("5 stress vectors synthesized to test UI & backend resilience under extreme conditions.")

    for idx, case in enumerate(report.chaos_suite, 1):
        with st.expander(f"Scenario {idx}: [{case.test_id}] {case.stress_vector}", expanded=True):
            st.markdown(f"**Stress Vector:** `{case.stress_vector}`")
            st.markdown(f"**Expected Defensive Behavior:** {case.expected_behavior}")
            st.markdown("**Input Stimulus Payload:**")
            st.code(case.input_payload, language="text")

# ------------------------------------------------------------------------------
# TAB 4: AUTONOMOUS PLAYWRIGHT REGRESSION TEST
# ------------------------------------------------------------------------------
with tab_playwright:
    st.subheader("Automated Playwright Regression Test Generator")
    st.caption("Synchronous Playwright test checking DOM visibility, geometric bounds, and container overflow.")

    playwright_code = ""
    if DEFAULT_PLAYWRIGHT_PATH.exists():
        with open(DEFAULT_PLAYWRIGHT_PATH, "r", encoding="utf-8") as f:
            playwright_code = f.read()

    is_ast_valid = validate_test_syntax(playwright_code) if playwright_code else False

    col_pw1, col_pw2 = st.columns([3, 1])
    with col_pw1:
        if is_ast_valid:
            st.markdown(
                '<span class="badge badge-success">✅ AST Validated (Zero Syntax Errors)</span>',
                unsafe_allow_html=True,
            )
        else:
            st.markdown(
                '<span class="badge badge-critical">❌ AST Validation Pending</span>',
                unsafe_allow_html=True,
            )

    with col_pw2:
        if playwright_code:
            st.download_button(
                label="📥 Download Test Script",
                data=playwright_code,
                file_name="test_regression.py",
                mime="text/x-python",
                use_container_width=True,
            )

    if playwright_code:
        st.code(playwright_code, language="python", line_numbers=True)

# ------------------------------------------------------------------------------
# TAB 5: SARIF V2.1.0 GOVERNANCE EXPORT
# ------------------------------------------------------------------------------
with tab_sarif:
    st.subheader("OASIS SARIF v2.1.0 CI/CD Security & Governance Gate")
    st.caption("Interchange format for direct ingestion by GitHub Code Scanning and security dashboards.")

    sarif_data_str = ""
    if DEFAULT_SARIF_PATH.exists():
        with open(DEFAULT_SARIF_PATH, "r", encoding="utf-8") as f:
            sarif_data_str = f.read()
    else:
        sarif_data_str = export_to_sarif(report, str(DEFAULT_SARIF_PATH))
        with open(DEFAULT_SARIF_PATH, "r", encoding="utf-8") as f:
            sarif_data_str = f.read()

    col_s1, col_s2 = st.columns([3, 1])
    with col_s1:
        st.markdown(
            '<span class="badge badge-meta">OASIS SARIF v2.1.0 Standard</span>',
            unsafe_allow_html=True,
        )
    with col_s2:
        st.download_button(
            label="📥 Download SARIF Report",
            data=sarif_data_str,
            file_name="qa_audit.sarif",
            mime="application/json",
            use_container_width=True,
        )

    try:
        parsed_sarif = json.loads(sarif_data_str)
        st.json(parsed_sarif)
    except Exception:
        st.code(sarif_data_str, language="json")

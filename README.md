# ⚡ QA-Swarm: Autonomous Multimodal QA & Healing Engine

[![Python 3.12](https://img.shields.io/badge/Python-3.12+-blue.svg?logo=python&logoColor=white)](https://www.python.org/)
[![Meta AI Hackathon](https://img.shields.io/badge/Meta%20AI-Hackathon%20Project-0466c8.svg?logo=meta&logoColor=white)](https://github.com/meta-hackathon/qa-swarm)
[![Pydantic v2](https://img.shields.io/badge/Pydantic-v2.14-E92063.svg?logo=pydantic&logoColor=white)](https://docs.pydantic.dev/)
[![SARIF v2.1.0](https://img.shields.io/badge/SARIF-v2.1.0-4361ee.svg?logo=github)](https://sarifweb.azurewebsites.net/)
[![Playwright Tested](https://img.shields.io/badge/Playwright-Automated%20Tests-2EAD33.svg?logo=playwright&logoColor=white)](https://playwright.dev/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

---

## 📌 Executive Summary

**QA-Swarm** is an enterprise-grade, closed-loop autonomous quality engineering system that bridges the gap between **computer vision inspection** and **automated source code remediation**. 

Traditional visual regression tools merely capture pixel differences without understanding code semantics, while static analyzers inspect code without knowing how UI renders in the real world. **QA-Swarm** unifies both paradigms into a cohesive, multimodal agent swarm powered by:

- **SAM 3 (Spatial Visual Cortex):** Detects visual defects, layout clipping, margin breaks, and overflows, outputting normalized spatial bounding boxes `[ymin, xmin, ymax, xmax]` with automated clamping.
- **Muse Spark (Causal Correlator):** Performs multimodal correlation linking observed pixel anomalies directly to offending source code tokens, files, and exact line numbers (1-indexed).
- **Muse Code (Healing Engine):** Synthesizes surgical, deterministic code patches and unified diffs (`difflib`) that resolve layout constraints without duplicating lines or altering indentation.
- **Adversarial Chaos Engine:** Subject components to 5 aggressive stress vectors (Buffer overflow, Bi-directional Unicode/RTL, Type mutation, CSS/HTML syntax breakout, and Concurrency event storms).
- **Autonomous Playwright Generator:** Generates mathematical AST-validated synchronous Playwright regression tests verifying DOM bounds, visibility, and `scrollWidth <= clientWidth`.
- **CI/CD Governance & SARIF v2.1.0:** Computes a weighted Health Score ($0-100$) and exports standardized OASIS SARIF reports for native **GitHub Code Scanning** integration.

---

## 🏛️ System Architecture

The following directed acyclic graph (DAG) illustrates how data flows through QA-Swarm from raw developer inputs to CI/CD gates and the interactive dashboard:

```mermaid
flowchart TD
    subgraph Inputs["1. System Inputs"]
        UI_IMG["UI Screenshot (PNG/JPG)"]
        SRC_CODE["Component Code (Python/CSS/JS)"]
    end

    subgraph Perception["2. Multimodal Perception"]
        SAM3["SAM 3 Vision Cortex<br/>core/vision.py"]
        DEFECTS["VisualDefect Entities<br/>(BBoxes #FF3B30, Severity)"]
    end

    subgraph Correlation["3. Multimodal Reasoning"]
        MUSE_SPARK["Muse Spark Correlator<br/>core/correlator.py"]
        ROOT_CAUSE["RootCauseLink<br/>(Target Line & Offending Token)"]
    end

    subgraph Healing["4. Healing & Remediation"]
        MUSE_CODE["Muse Code Analyzer<br/>core/analyzer.py"]
        PATCH["CodePatch & Unified Diff<br/>(width: 120px -> width: 100%)"]
    end

    subgraph Adversarial["5. Adversarial Verification"]
        CHAOS["Chaos Engine Suite<br/>core/chaos.py (5 Vectors)"]
        PLAYWRIGHT["Playwright Generator<br/>core/test_generator.py (AST Verified)"]
    end

    subgraph Governance["6. Orchestration & Output"]
        ORCH["Swarm Orchestrator<br/>core/orchestrator.py"]
        SCORE["Health Score & Verdict<br/>(0-100 / BLOCK_DEPLOYMENT)"]
        SARIF["OASIS SARIF v2.1.0<br/>GitHub Code Scanning"]
        DASH["Streamlit Dashboard<br/>app/main.py"]
    end

    UI_IMG --> SAM3
    SAM3 --> DEFECTS
    SRC_CODE --> MUSE_SPARK
    DEFECTS --> MUSE_SPARK
    MUSE_SPARK --> ROOT_CAUSE
    ROOT_CAUSE --> MUSE_CODE
    SRC_CODE --> MUSE_CODE
    MUSE_CODE --> PATCH
    SRC_CODE --> CHAOS
    DEFECTS --> PLAYWRIGHT
    PATCH --> PLAYWRIGHT
    DEFECTS --> ORCH
    ROOT_CAUSE --> ORCH
    CHAOS --> ORCH
    PATCH --> ORCH
    ORCH --> SCORE
    ORCH --> SARIF
    ORCH --> DASH
```

---

## 🔬 Competitive Comparison

| Capability | QA-Swarm | Applitools / Percy | SonarQube / ESLint |
| :--- | :---: | :---: | :---: |
| **Visual Anomaly Detection** | ✅ **Yes (SAM 3 Spatial BBoxes)** | ✅ Yes (DOM/Pixel diff) | ❌ No |
| **Causal Code Mapping** | ✅ **Yes (Pixel-to-Line AST Link)** | ❌ No (Visual only) | ❌ No (Static rules only) |
| **Automated Patch Generation** | ✅ **Yes (Pydantic-Validated)** | ❌ No | ⚠️ Partial (Mechanical fixes) |
| **Adversarial Chaos Vectors** | ✅ **Yes (5 Attack Categories)** | ❌ No | ❌ No |
| **Playwright Test Synthesis** | ✅ **Yes (AST Validated)** | ❌ No | ❌ No |
| **OASIS SARIF v2.1.0 Export** | ✅ **Yes (Native CodeQL)** | ❌ No | ⚠️ Plugin dependent |
| **Deterministic Offline Mode** | ✅ **Yes (`USE_MOCK=true`)** | ❌ No (SaaS cloud lock-in) | ✅ Yes (Local engine) |

---

## ⚡ Quickstart in 3 Commands

### 1. Initialize Virtual Environment
```bash
python -m venv .venv
# Linux/macOS:
source .venv/bin/activate
# Windows:
.\.venv\Scripts\Activate.ps1
```

### 2. Install Project Dependencies
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 3. Launch the Interactive Dashboard
```bash
streamlit run app/main.py
```
*Open your browser at `http://localhost:8501`. Click **"📁 Load Demo Sample"** and **"🚀 Run QA-Swarm Audit"** to experience the full multimodal healing loop.*

---

## 💻 Headless CLI & CI/CD Gateways

QA-Swarm features a full-featured CLI for CI/CD pipelines, containerized runners, and GitHub Actions workflows:

```bash
# Run headless multimodal audit with mock fallback
python -m core.cli --ui test_samples/sample_ui.png --code test_samples/broken_component.py --sarif test_samples/qa_audit.sarif --mock
```

### CLI Arguments Reference

| Flag | Type | Default | Description |
| :--- | :---: | :--- | :--- |
| `--ui` | string | `test_samples/sample_ui.png` | Path to target UI screenshot image (PNG/JPG) |
| `--code` | string | `test_samples/broken_component.py` | Path to component source code file |
| `--sarif` | string | `test_samples/qa_audit.sarif` | Destination path for OASIS SARIF v2.1.0 report |
| `--mock` | boolean | `True` | Enables deterministic evaluation without remote network calls |
| `--no-mock` | flag | — | Disables mock mode and engages live inference models |
| `--allow-blocked` | flag | `False` | Forces exit code `0` even if verdict is `BLOCK_DEPLOYMENT` |

### Exit Code Reference

| Exit Code | Verdict Status | Pipeline Behavior |
| :---: | :--- | :--- |
| **`0`** | `READY_FOR_PRODUCTION`<br>`REQUIRES_REVIEW` | **PASSED**: Quality gate passes; deployment continues smoothly. |
| **`1`** | `BLOCK_DEPLOYMENT` | **BLOCKED**: Deployment gate halts execution. SARIF report is uploaded via GitHub Actions `if: always()`. |

---

## 📂 Repository Directory Layout

```text
qa-swarm/
├── .github/
│   └── workflows/
│       └── ci.yml               # GitHub Actions CI & SARIF upload workflow
├── app/
│   ├── __init__.py
│   └── main.py                  # Streamlit multimodal dashboard
├── core/
│   ├── __init__.py
│   ├── analyzer.py              # Root cause analyzer & code patch engine
│   ├── chaos.py                 # Adversarial stress engine & resilience scorer
│   ├── cli.py                   # Headless CI/CD terminal interface
│   ├── client.py                # Deterministic client & exponential backoff
│   ├── correlator.py            # Multimodal vision-to-code causal linker
│   ├── orchestrator.py          # End-to-end swarm pipeline & SARIF exporter
│   ├── schemas.py               # Pydantic v2 data models with strict validation
│   ├── test_generator.py        # Playwright test generator & AST validator
│   └── vision.py                # Spatial bounding box renderer (#FF3B30)
├── test_samples/
│   ├── annotated_ui.png         # Generated visual overlay with bounding boxes
│   ├── broken_component.py      # Flawed component (width: 120px overflow)
│   ├── mock_audit_result.json   # Deterministic ground truth benchmark
│   ├── qa_audit.sarif           # OASIS SARIF v2.1.0 report for Code Scanning
│   ├── sample_ui.png            # 800x600 dark mode UI screenshot
│   └── test_regression.py       # Autonomous Playwright regression script
├── tests/
│   ├── test_analyzer.py         # Static analyzer unit tests (4 tests)
│   ├── test_app.py              # Streamlit dashboard AST smoke tests (2 tests)
│   ├── test_chaos.py            # Chaos Engine unit tests (4 tests)
│   ├── test_correlator.py       # Multimodal correlator tests (3 tests)
│   ├── test_generator.py        # Playwright test generator tests (4 tests)
│   ├── test_orchestrator.py     # Swarm pipeline & CLI tests (4 tests)
│   ├── test_schemas.py          # Pydantic schema validation tests (2 tests)
│   ├── test_ui_smoke.py         # Streamlit AppTest integration tests (3 tests)
│   └── test_vision.py           # Vision spatial clamping tests (3 tests)
├── .env.example                 # Environment configuration template
├── .gitignore                   # Version control exclusions (.venv, .sarif, etc.)
├── pytest.ini                   # Pytest runner configuration
├── requirements.txt             # Locked project dependencies
└── README.md                    # Enterprise architectural documentation
```

---

## 🧪 Comprehensive Unit & Integration Testing

The entire platform is backed by **29 comprehensive unit and smoke tests** with 100% pass rate:

```bash
pytest -v
```

```text
============================= test session starts =============================
platform win32 -- Python 3.12.10, pytest-9.1.1, pluggy-1.7.0
rootdir: C:\Users\frans\.gemini\antigravity\scratch\qa-swarm
configfile: pytest.ini
testpaths: tests
plugins: anyio-4.15.1
collected 29 items

tests/test_analyzer.py (4 passed)
tests/test_app.py (2 passed)
tests/test_chaos.py (4 passed)
tests/test_correlator.py (3 passed)
tests/test_generator.py (4 passed)
tests/test_orchestrator.py (4 passed)
tests/test_schemas.py (2 passed)
tests/test_ui_smoke.py (3 passed)
tests/test_vision.py (3 passed)

============================= 29 passed in 2.89s ==============================
```

---

## 📄 License

This project is licensed under the **MIT License** — see the [LICENSE](LICENSE) file for details.

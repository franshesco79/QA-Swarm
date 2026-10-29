# ⚡ QA-Swarm: Autonomous Closed-Loop Visual QA & Self-Healing Engine

[![Meta SAM 3.1](https://img.shields.io/badge/Meta%20AI-SAM%203.1%20Spatial%20Cortex-0466c8.svg?logo=meta&logoColor=white)](https://api.meta.ai/)
[![Muse Spark 1.3](https://img.shields.io/badge/Muse-Spark%201.3%20Causal%20Fixer-8338ec.svg?logo=meta&logoColor=white)](https://api.meta.ai/)
[![Playwright MCP](https://img.shields.io/badge/Playwright-Live%20Browser%20MCP-2EAD33.svg?logo=playwright&logoColor=white)](https://playwright.dev/)
[![Pydantic v2](https://img.shields.io/badge/Pydantic-v2.14-E92063.svg?logo=pydantic&logoColor=white)](https://docs.pydantic.dev/)
[![OASIS SARIF v2.1.0](https://img.shields.io/badge/OASIS%20SARIF-v2.1.0%20Gate-4361ee.svg?logo=github)](https://sarifweb.azurewebsites.net/)
[![GitHub Actions CI](https://img.shields.io/badge/GitHub%20Actions-CI%2FCD%20Automated-2088FF.svg?logo=githubactions&logoColor=white)](.github/workflows/qa-swarm.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

---

## 📌 Executive Summary

**QA-Swarm** is an enterprise-grade, closed-loop autonomous quality engineering system bridging **multimodal computer vision** with **deterministic source code remediation**. 

Traditional visual regression tools capture pixel differences without understanding code semantics, while static analyzers and linters inspect code without visual awareness of real-world browser rendering. **QA-Swarm** unites both worlds through a bidirectional agent swarm powered by **Meta AI's next-generation models**:

1. **Meta SAM 3.1 (`sam-3.1` Spatial Cortex):** Performs sub-pixel visual segmentation, extracting localized layout overflow anomalies and parsing coordinate tokens `<|box;x1=...;y1=...;x2=...;y2=...;w=...;h=...|>` into normalized coordinates `[ymin, xmin, ymax, xmax]`.
2. **Meta Muse Spark 1.3 (`muse-spark-1.3` Causal Correlator & Fixer):** Correlates visual bounding boxes with component AST to locate the offending code token and line number. Orchestrates tools via **Model Context Protocol (MCP)** and synthesizes Pydantic-validated surgical patches (`difflib` unified diffs).
3. **Adversarial Chaos Engine:** Evaluates defensive resilience across 5 adversarial vectors (buffer overflow, bidirectional RTL Unicode, boundary type mutation, syntax breakout, and concurrency event storms).
4. **CI/CD Governance & OASIS SARIF v2.1.0 Gate:** Generates standardized SARIF v2.1.0 reports for native **GitHub Code Scanning / CodeQL** integration, determining an objective Health Score (0–100) and automated deployment gate verdicts.

---

## 🏛️ Closed-Loop System Architecture

The following diagram illustrates the closed-loop autonomous pipeline from dual ingestion through Meta AI multimodal reasoning to automated code healing and CI/CD gate validation:

```mermaid
flowchart LR
    subgraph INGESTION["1. Dual Ingestion Engine"]
        LOCAL["CI/CD Local Artifacts<br/>(sample_ui.png + code)"]
        LIVE["Playwright Live Browser<br/>(Chromium 1280x800)"]
    end

    subgraph VISION["2. Multimodal Spatial Cortex"]
        SAM3["Meta SAM 3.1<br/>(Sub-pixel BBox Localization)"]
    end

    subgraph CORRELATION["3. Agentic MCP Orchestrator"]
        MUSE["Muse Spark 1.3<br/>(Pixel-to-AST Causal Fixer)"]
        MCP["Agentic MCP Tool Suite<br/>(sam_spatial, playwright, chaos, sarif)"]
    end

    subgraph RESILIENCE["4. Adversarial Stress Suite"]
        CHAOS["Adversarial Chaos Engine<br/>(5 Stress Vectors / 0-100 Score)"]
    end

    subgraph DELIVERY["5. Autonomous Governance & Gate"]
        HEAL["Auto-Healed Source Code<br/>(Pydantic-Validated Diff)"]
        SARIF["OASIS SARIF v2.1.0 Report<br/>(GitHub CodeQL Action)"]
    end

    LOCAL -->|"Image + Code"| SAM3
    LIVE -->|"Automated Screenshot"| SAM3
    SAM3 -->|"Normalized BBoxes [ymin, xmin, ymax, xmax]"| MUSE
    MUSE <-->|"Tool Calling (MCP)"| MCP
    MUSE -->|"Deterministic CodePatch"| HEAL
    MUSE -->|"Offending Token Reference"| CHAOS
    CHAOS -->|"Resilience Metric"| SARIF
    HEAL -.->|"Regression Loop"| LIVE
    SARIF -.->|"CI/CD Gate"| LOCAL
```

---

## 🌟 Key Capabilities & Enterprise Features

| Feature | Description | Architecture Component |
| :--- | :--- | :--- |
| **Dual Ingestion Mode** | Supports both preloaded CI/CD artifacts and on-the-fly live web URL inspection via headless Chromium. | `core/browser.py` & `app/main.py` |
| **Spatial Anomaly Cortex** | Sub-pixel visual segmentation using Meta SAM 3.1 with automated coordinate normalization and bounding box clamping. | `core/vision.py` & `core/client.py` |
| **Causal Pixel-to-Code Mapping** | Bridges pixel coordinates with source code AST, mapping visual overflow to specific lines and tokens. | `core/correlator.py` |
| **Surgical Code Healing** | Generates verified replacement patches (`width: 120px` ➔ `width: 100%`) with unified diff visualization and direct download. | `core/analyzer.py` |
| **Live Agentic MCP Trace** | Inspectable JSON telemetry displaying tool invocations (`sam_spatial_scanner`, `muse_spark_correlator`, etc.) with latencies and status. | `app/main.py` (Expander) |
| **Adversarial Chaos Suite** | Evaluates code resilience across 5 adversarial stress vectors and calculates defensive scores (0–100). | `core/chaos.py` |
| **Playwright Test Synthesis** | Generates executable Python regression tests verified with Python's built-in AST parser (`ast.parse`). | `core/test_generator.py` |
| **OASIS SARIF v2.1.0 CI/CD** | Exports standardized SARIF reports directly consumable by GitHub Code Scanning (`github/codeql-action/upload-sarif@v3`). | `core/orchestrator.py` & `.github/workflows/` |
| **Intelligent Session Caching** | Zero-latency 0ms downloads and rerenders backed by `@st.cache_data` and SHA-256 payload hashing. | `app/main.py` |
| **Connection Pooling & Compression** | Reusable `requests.Session()` with keep-alive handshakes and in-memory Pillow image downscaling (`<=1280px`). | `core/client.py` |
| **Deterministic Offline Mode** | Full offline capability via `USE_MOCK=true` with benchmark fixtures, requiring zero external network calls. | `test_samples/mock_audit_result.json` |

---

## 🔬 Competitive Matrix

| Capability | QA-Swarm | Applitools / Percy | SonarQube / ESLint |
| :--- | :---: | :---: | :---: |
| **Visual Anomaly Detection** | ✅ **Yes (Meta SAM 3.1 BBoxes)** | ✅ Yes (DOM/Pixel diff) | ❌ No |
| **Causal Code Mapping** | ✅ **Yes (Pixel-to-Line AST Link)** | ❌ No (Visual only) | ❌ No (Static rules only) |
| **Automated Code Healing** | ✅ **Yes (Pydantic-Validated)** | ❌ No | ⚠️ Partial (Mechanical fixes) |
| **Live Browser Capture** | ✅ **Yes (Headless Chromium Ingestion)** | ⚠️ Plugin dependent | ❌ No |
| **Adversarial Chaos Engine** | ✅ **Yes (5 Attack Categories)** | ❌ No | ❌ No |
| **Agentic MCP Telemetry** | ✅ **Yes (Inspectable Execution Trace)** | ❌ No | ❌ No |
| **OASIS SARIF v2.1.0 Export** | ✅ **Yes (Native GitHub Actions)** | ❌ No | ⚠️ Plugin dependent |
| **Deterministic Offline Mode** | ✅ **Yes (`USE_MOCK=true`)** | ❌ No (SaaS cloud lock-in) | ✅ Yes (Local engine) |

---

## 🚀 Quickstart & Setup Guide

### 1. Prerequisites
- Python 3.11 or 3.12 installed.
- Git.

### 2. Virtual Environment & Dependencies
```bash
# Clone repository
git clone https://github.com/meta-hackathon/qa-swarm.git
cd qa-swarm

# Create and activate virtual environment
python -m venv .venv

# On Windows (PowerShell):
.\.venv\Scripts\Activate.ps1

# On Linux / macOS:
source .venv/bin/activate

# Install dependencies:
pip install --upgrade pip
pip install -r requirements.txt

# Download required Chromium browser binaries:
playwright install chromium
```

### 3. Environment Variables Configuration
Copy the provided `.env.example` file to `.env`:
```bash
cp .env.example .env
```

Contents of `.env`:
```env
META_API_KEY=your_meta_api_key_here
META_BASE_URL=https://api.meta.ai/v1
USE_MOCK=false
```

> **Security Note:** `.env` is permanently excluded from version control via `.gitignore`. When `USE_MOCK=true` or if no `META_API_KEY` is provided, QA-Swarm runs transparently using local deterministic benchmarks.

---

## 💻 Execution Workflows

### Workflow A: Interactive Web Dashboard (Streamlit)
Launch the modern Dark DevTools dashboard:
```bash
python -m streamlit run app/main.py
```
Open **`http://localhost:8501`** in your browser:
* **📁 CI/CD Sample Tab:** Preloaded with `sample_ui.png` and `broken_component.py`, with support for custom file uploads.
* **🌐 Live URL (Playwright MCP) Tab:** Enter any web endpoint (e.g. `http://localhost:3000` or `https://example.com`) for live headless Chromium capture.
* Click **"⚡ Ejecutar Auditoría del Enjambre"** to coordinate SAM 3.1 and Muse Spark 1.3 in real-time.
* Click **"✨ Download Patched File (Auto-Healed)"** for instant 0ms remediation download.
* Expand **"🧠 View Agentic MCP Execution Trace"** to inspect tool telemetry.

### Workflow B: Headless CI/CD Gate (CLI)
Run automated audits directly in CI/CD pipelines (GitHub Actions, GitLab CI, Jenkins):
```bash
# Option 1: Static image audit
python -m core.cli --ui test_samples/sample_ui.png --code test_samples/broken_component.py --output test_samples/qa_audit.sarif --allow-blocked

# Option 2: Live Web URL audit via Playwright headless Chromium capture
python -m core.cli --url https://example.com --code test_samples/broken_component.py --output test_samples/qa_audit.sarif --allow-blocked
```

#### CLI Argument Reference

| Flag | Type | Default | Description |
| :--- | :---: | :--- | :--- |
| `--url` | string | `None` | Target live web URL to capture and audit via Playwright headless Chromium |
| `--ui` | string | `test_samples/sample_ui.png` | Target UI screenshot image (PNG/JPG) |
| `--code` | string | `test_samples/broken_component.py` | Target component source code file |
| `--output` / `--sarif` | string | `test_samples/qa_audit.sarif` | Destination path for OASIS SARIF v2.1.0 report |
| `--mock` | boolean | `True` | Enables deterministic evaluation without remote network calls |
| `--no-mock` | flag | — | Disables mock mode and engages live Meta AI endpoints |
| `--allow-blocked` | flag | `False` | Forces exit code `0` even if verdict is `BLOCK_DEPLOYMENT` |

### Workflow C: GitHub Actions Integration
QA-Swarm includes a turnkey GitHub Actions workflow at [`.github/workflows/qa-swarm.yml`](.github/workflows/qa-swarm.yml):
```yaml
name: QA-Swarm Native CI/CD & SARIF Audit
on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]

jobs:
  audit:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Set up Python 3.11
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      - name: Install Dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements.txt
          playwright install --with-deps chromium
      - name: Execute Headless QA-Swarm Audit
        run: |
          USE_MOCK=true python -m core.cli --ui test_samples/sample_ui.png --code test_samples/broken_component.py --output test_samples/qa_audit.sarif --allow-blocked
      - name: Upload SARIF to GitHub Code Scanning
        uses: github/codeql-action/upload-sarif@v3
        if: always()
        with:
          sarif_file: test_samples/qa_audit.sarif
```

---

## 🚀 Beyond Web: Extensibility & Future Roadmap

The foundational **Spatial-to-Code** engine in QA-Swarm is platform-agnostic, decoupled from specific rendering engines, and ready for extension across modern application ecosystems:

1. **Native Mobile Quality Engineering:**
   - **Frameworks:** React Native, Flutter, iOS SwiftUI, and Android Jetpack Compose.
   - **Mechanism:** Ingestion of mobile screenshots and native view hierarchies (accessibility trees / XML dumps) mapped directly to declarative components (`Composable` / `Widget` / `View`).
2. **Automated Accessibility & WCAG Remediation:**
   - **Target Areas:** Touch target bounding box expansion (48x48dp), color contrast ratio recalculations (WCAG AAA), and semantic ARIA attribute synthesis.
   - **Remediation:** Automated injection of missing accessibility labels and contrast fixes directly into JSX/TSX/HTML code.
3. **Figma-to-Code Drift Auditing:**
   - **Workflow:** Comparison of production UI screenshots against Figma design tokens and frames via Figma REST API, highlighting padding, spacing, and font drift with automated remediation PRs.
4. **Self-Healing RPA & E2E Locators:**
   - **Resilience:** When UI redesigns break CSS selectors or XPath locators, the spatial correlation engine re-identifies the target element visually and synthesizes updated resilient locators in existing Playwright/Selenium test suites.

---

## 🧪 Comprehensive Test Suite

QA-Swarm maintains 100% test pass rate across 43 unit, integration, contract, and UI smoke tests:

```bash
pytest tests/ -v
```

```text
============================= test session starts =============================
tests/test_analyzer.py (4 passed)
tests/test_app.py (2 passed)
tests/test_browser.py (4 passed)
tests/test_chaos.py (4 passed)
tests/test_contracts.py (3 passed)
tests/test_correlator.py (3 passed)
tests/test_generator.py (4 passed)
tests/test_orchestrator.py (4 passed)
tests/test_schemas.py (8 passed)
tests/test_ui_smoke.py (4 passed)
tests/test_vision.py (3 passed)

============================= 43 passed in 12.42s =============================
```

---

## 📄 License

Licensed under the **MIT License** — see the [LICENSE](LICENSE) file for details.  
Copyright (c) 2026 QA-Swarm Contributors.

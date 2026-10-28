---
title: QA-Swarm
emoji: ⚡
colorFrom: blue
colorTo: indigo
sdk: streamlit
app_file: app/main.py
pinned: false
license: mit
---

# ⚡ QA-Swarm: Autonomous Multimodal QA & Healing Engine

[![Meta SAM 3.1](https://img.shields.io/badge/Meta%20AI-SAM%203.1%20Spatial%20Cortex-0466c8.svg?logo=meta&logoColor=white)](https://api.meta.ai/)
[![Muse Spark 1.3](https://img.shields.io/badge/Muse-Spark%201.3%20Causal%20Fixer-8338ec.svg?logo=meta&logoColor=white)](https://api.meta.ai/)
[![MCP Orchestration](https://img.shields.io/badge/MCP-Agentic%20Tool%20Calling-FF6F00.svg)](https://modelcontextprotocol.io/)
[![Pydantic v2](https://img.shields.io/badge/Pydantic-v2.14-E92063.svg?logo=pydantic&logoColor=white)](https://docs.pydantic.dev/)
[![Playwright](https://img.shields.io/badge/Playwright-Live%20Browser%20Engine-2EAD33.svg?logo=playwright&logoColor=white)](https://playwright.dev/)
[![SARIF v2.1.0](https://img.shields.io/badge/OASIS%20SARIF-v2.1.0%20Gate-4361ee.svg?logo=github)](https://sarifweb.azurewebsites.net/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

---

## 📌 Executive Summary

**QA-Swarm** is an enterprise-grade, closed-loop autonomous quality engineering system bridging **multimodal computer vision** with **deterministic source code remediation**. 

Traditional visual regression tools merely capture pixel differences without code semantics, while static linters inspect code without visual awareness of real-world browser rendering. **QA-Swarm** unites both worlds through a bidirectional agent swarm powered by **Meta AI's next-generation models**:

1. **Meta SAM 3.1 (`sam-3.1` Spatial Cortex):** Performs sub-pixel visual segmentation, extracting localized layout overflow anomalies and parsing coordinate tokens `<|box;x1=...;y1=...;x2=...;y2=...;w=...;h=...|>` into normalized coordinates `[ymin, xmin, ymax, xmax]`.
2. **Meta Muse Spark 1.3 (`muse-spark-1.3` Causal Correlator & Code Healer):** Reasons across the visual bounding boxes and component AST to identify the exact offending code token and line number. Orchestrates tools via **Model Context Protocol (MCP)** and synthesizes Pydantic-validated surgical patches (`difflib` unified diffs).
3. **Adversarial Chaos Engine:** Evaluates defensive resilience across 5 adversarial vectors (buffer overflow, bidirectional RTL Unicode, type mutation, syntax breakout, and concurrency event storms).
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
| **Live Agentic MCP Trace** | Inspectable JSON telemetry displaying tool invocations (`sam_spatial_scanner`, `muse_spark_causal_correlator`, etc.) with latencies and status. | `app/main.py` (Expander) |
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
# Clone the repository
git clone https://github.com/meta-hackathon/qa-swarm.git
cd qa-swarm

# Create and activate virtual environment
python -m venv .venv

# On Windows (PowerShell):
.\.venv\Scripts\Activate.ps1

# On Linux / macOS:
source .venv/bin/activate

# Install essential dependencies:
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
streamlit run app/main.py
```
Open **`http://localhost:8501`** in your browser:
* **Demo & Archivos Locales Tab:** Preloaded with `sample_ui.png` and `broken_component.py`.
* **Playwright Live URL Tab:** Enter any web endpoint (e.g. `http://localhost:3000` or `https://example.com`) for live headless Chromium capture.
* Click **"⚡ Ejecutar Auditoría del Enjambre"** to trigger the multimodal swarm audit.
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
name: QA-Swarm Autonomous Multimodal Audit
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
      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      - name: Install Dependencies
        run: |
          pip install -r requirements.txt
          playwright install --with-deps chromium
      - name: Run QA-Swarm Headless Audit
        run: |
          python -m core.cli --ui test_samples/sample_ui.png --code test_samples/broken_component.py --output test_samples/qa_audit.sarif --allow-blocked
      - name: Upload SARIF to GitHub Code Scanning
        uses: github/codeql-action/upload-sarif@v3
        with:
          sarif_file: test_samples/qa_audit.sarif
```

---

## 🧪 Comprehensive Test Suite

QA-Swarm maintains 100% test pass rate across 43 unit, integration, and UI smoke tests:

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

============================= 43 passed in 12.17s =============================
```
```

---

## 📄 License

Licensed under the **MIT License** — see the [LICENSE](LICENSE) file for details.
Copyright (c) 2026 QA-Swarm Contributors.

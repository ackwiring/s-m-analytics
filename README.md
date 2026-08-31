# M & S Type Reserve Valuation & Analysis Engine

[![FastAPI](https://img.shields.io/badge/Backend-FastAPI-009688?logo=fastapi)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/Frontend-React%20%2B%20Vite-61DAFB?logo=react)](https://vitejs.dev)
[![Tailscale](https://img.shields.io/badge/Network-Tailscale-24292E?logo=tailscale)](https://tailscale.com)

A high-performance, modular valuation pipeline for mining reserve analysis. Slices multi-dimensional block models into Cut-Off Grade (COG) bins and performs N-dimensional bin collapsing to reduce complex model dimensions while preserving metallurgical grade precision and total mass parity.

---

## 🏗️ Architecture: Orchestrator + Modular Skills (v2.0.0)

Modeled after autonomous pipeline orchestrators (n8n / AM Agent style), the workflow is decoupled into five independent, pure Python skills:

1. **Ingestion & Schema Parser (skills/ingestion/)**: Parses Excel configuration workbooks and decodes raw block models (.csv, .parquet, .xlsx) with multi-encoding fallback (UTF-8-SIG, CP1252, Latin-1, ISO-8859-1).
2. **1D M-Type Baseline Slicing (skills/mtype_baseline/)**: Applies 1-dimensional Cut-Off Grade (COG) intervals across active mining dimensions to produce unreduced baseline phase data.
3. **N-D S-Type Flex Reduction (skills/stype_reduction/)**: Computes percentile cuts on target aggregation fields (e.g. d1_Ranking) and collapses low-volume bins along prioritized flex-order dimensions (FLEX UP, FLEX DOWN, STATIC).
4. **Metallurgical Audit Verification (skills/audit_verification/)**: Compares collapsed bin distributions against the baseline to verify head grade preservation and zero tonnage variance.
5. **COMET Deliverables Packager (skills/export_bundle/)**: Bundles standard M-Type files, all S-Type percentile models, and QA audit reports into a structured .zip archive.

**Known gap:** `PhasePrep_MetCoal_2021-06-03.py`, `builder.py`, and `phase_file_generator.py` at the project root are earlier, independent implementations of overlapping logic — none of the three import from or are covered by tests against the webapp/backend skills above. Treat them as legacy/reference only until reconciled; do not assume they produce identical output to the pipeline described here.

---

## 🚀 Quick Start

### 1. Prerequisites
* Python 3.10+
* Node.js 18+ (for frontend development)

### 2. Backend Setup
```bash
cd webapp/backend
pip install -r requirements.txt
python main.py
```
The server will start at http://localhost:1943.

### 3. Frontend Setup (Optional for Development)
```bash
cd webapp/frontend
npm install
npm run build
```
For hot-reload dev iteration instead of a static build, `npm run dev` starts
the Vite dev server on http://localhost:5173, proxying `/api` to the backend
at :1943 (start the backend first).

### 4. Backend Tests
```bash
cd webapp/backend
pip install -r requirements-dev.txt
pytest
```

---

## 🌐 Remote Access & Tailscale Serve
The application is pre-configured for secure network access via Tailscale:
```bash
tailscale serve --bg --https=1943 http://127.0.0.1:1943
```
Access via MagicDNS: https://<tailscale-hostname>:1943

---

## 📂 Deliverables Structure
When exporting deliverables from the web interface, the generated PhaseFiles_Export.zip contains:
```
PhaseFiles_Export.zip
├── MTYPE_PhaseFiles/
│   ├── Standard_PhaseFile_Data.csv
│   └── MTYPE_df_mtypebins.csv
└── STYPE_*pct_PhaseFiles/
    ├── STYPE_*pct_PhaseFile_Data.csv
    └── Audit_Report.txt
```

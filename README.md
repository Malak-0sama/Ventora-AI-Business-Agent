# AI Business Intelligence Agent

## Overview

AI Business Intelligence Agent is a modular machine learning platform designed to automate the complete analytical workflow for structured business datasets. The system follows a multi-agent architecture in which each agent is responsible for a specific stage of the pipeline, from dataset understanding to model training and validation.

The platform allows users to upload a dataset, automatically analyze its structure, generate an execution strategy using a large language model, preprocess the data, train an appropriate machine learning model, evaluate its performance, and save the trained model for future inference.

---

## Key Features

* Automatic dataset schema analysis
* Intelligent workflow planning using Gemini
* Automated data preprocessing
* Regression and classification support
* Automatic model selection
* Model training and validation
* Model persistence
* REST API built with FastAPI
* **Ventora Streamlit dashboard** — upload, run, and explore the full analysis in the browser
* Modular and extensible multi-agent architecture

---

## Architecture

```
Client
   │
   ▼
FastAPI
   │
   ▼
Schema Agent
   │
   ▼
LLM Planner Agent
   │
   ▼
Preprocessing Agent
   │
   ▼
Model Agent
   │
   ▼
Evaluation
   │
   ▼
Saved Model
```

The Streamlit dashboard is an additional, optional presentation layer on top
of the same agents — it does not duplicate or replace any analysis logic:

```
Streamlit (Home.py + pages/)
   │
   ▼
services/pipeline_service.py  (thin orchestration wrapper)
   │
   ├──▶ Schema Agent
   ├──▶ LLM Planner Agent
   ├──▶ Preprocessing Agent
   ├──▶ Model Agent
   └──▶ Insights Report Agent
   │
   ▼
context["report"] → rendered in AI Workspace / Analytics & Reports pages
```

---

## Project Structure

```
business-ai-agent/
│
├── Home.py                     # Streamlit entry point (upload + run)
├── pages/
│   ├── 1_AI_Workspace.py       # Dataset overview, data quality, stats, ML results
│   └── 2_Analytics_Reports.py  # Business report, technical report, export
├── services/
│   ├── pipeline_service.py         # Wraps the real agents with progress callbacks
│   └── report_export_service.py    # JSON / Markdown / PDF export of the real report
├── ui/
│   ├── theme.py                # Ventora dark BI theme (CSS)
│   └── components.py           # KPI cards, status pills, report cards
├── .streamlit/
│   └── config.toml             # Streamlit theme config (dark, primary #7C5CFF)
│
├── agents/
│   ├── schema_agent.py
│   ├── llm_planner_agent.py
│   ├── preprocessing_agent.py
│   ├── model_agent.py
│   └── insights_report_agent.py
│
├── models/
│   ├── trainer.py
│   ├── splitter.py
│   ├── validator.py
│   ├── evaluator.py
│   └── registry.py
│
├── uploads/
├── api.py                      # Existing FastAPI entry point (unchanged)
├── app.py
├── requirements.txt
└── README.md
```

---

## Components

### Schema Agent

The Schema Agent performs an initial inspection of the uploaded dataset. It extracts structural information including column names, data types, missing values, duplicate records, numerical features, categorical features, memory usage, and potential target columns.

### LLM Planner Agent

The LLM Planner Agent uses the Gemini API to analyze the dataset metadata and generate a machine learning execution plan. The generated plan includes task identification, preprocessing recommendations, algorithm suggestions, and execution reasoning.

### Preprocessing Agent

The Preprocessing Agent applies the preprocessing pipeline required by the selected machine learning task. The workflow includes handling missing values, encoding categorical variables, feature scaling, and dataset preparation before training.

### Model Agent

The Model Agent manages dataset splitting, model selection, training, validation, evaluation, and model serialization. The agent supports both regression and classification workflows.

### Insights Report Agent

The Insights Report Agent uses the Gemini API to turn the schema, plan, and
evaluation results into a structured report with two parts: a
`technical_report` (model information, performance summary, evaluation
metrics, findings, risks, improvements) and a `business_report` (executive
summary, KPI analysis, drivers, category/regional/discount/customer
analysis, risks, opportunities, management decisions, future strategy, and
a final conclusion).

### Streamlit Dashboard (Ventora)

`Home.py` and `pages/` are a presentation-only layer built on top of the
existing agents via `services/pipeline_service.py`. They upload a dataset,
run the real pipeline with live per-stage progress, and render the actual
`context` produced by the agents — dataset overview, data quality,
statistical analysis, ML results with charts, and the full business/technical
report with JSON/Markdown/PDF export. No analysis logic is duplicated or
mocked in the UI layer.

---

## Supported Machine Learning Tasks

* Regression
* Binary Classification
* Multi-class Classification

---

## Technology Stack

* Python
* FastAPI
* Pandas
* NumPy
* Scikit-learn
* CatBoost
* XGBoost
* LightGBM
* Gemini API
* Joblib
* Streamlit
* Plotly
* fpdf2

---

## Installation

Clone the repository:

```bash
git clone https://github.com/<username>/Agentic_Ai_Project.git
```

Navigate to the project directory:

```bash
cd Agentic_Ai_Project
```

Create a virtual environment:

```bash
python -m venv .venv
```

Activate the environment:

Windows

```bash
.venv\Scripts\activate
```

Linux / macOS

```bash
source .venv/bin/activate
```

Install the required dependencies:

```bash
pip install -r requirements.txt
```

---

## Running the Application

Start the API server:

```bash
uvicorn api:app --reload
```

Default endpoint:

```
http://127.0.0.1:8000
```

Interactive API documentation:

```
http://127.0.0.1:8000/docs
```

---

## Environment Variables

Create a `.env` file in the project root (a placeholder `.env` is included —
replace the value with your own key, never commit a real key):

```
GEMINI_API_KEY=your_gemini_api_key_here
GEMINI_MODEL=gemini-3.6-flash
```

* `GEMINI_API_KEY` — required. Used by `llm/gemini_provider.py` for the LLM
  Planner Agent and the Insights Report Agent.
* `GEMINI_MODEL` — the Gemini model name to call.

---

## Running the Streamlit Dashboard

From the project root, with the virtual environment activated:

```bash
python -m streamlit run Home.py
```

By default this opens the dashboard at:

```
http://localhost:8501
```

Flow: upload a CSV on **Home** → click **Run AI Analysis** → open
**AI Workspace** for dataset/data-quality/statistics/ML results, and
**Analytics & Reports** for the business + technical report and export
(JSON / Markdown / PDF).

The FastAPI server (`uvicorn api:app --reload`) and the Streamlit dashboard
both call the same underlying agents and can be run independently or side
by side.

---

## Workflow

```
Dataset Upload
      │
      ▼
Schema Analysis
      │
      ▼
LLM Planning
      │
      ▼
Data Preprocessing
      │
      ▼
Model Training
      │
      ▼
Model Validation
      │
      ▼
Evaluation
      │
      ▼
Model Persistence
```

---

## Testing Notes

The Streamlit dashboard was tested end-to-end against the real pipeline:

* All new modules import cleanly.
* The existing pipeline (`SchemaAgent` → `LLMPlannerAgent` →
  `PreprocessingAgent` → `ModelAgent` → `InsightsReportAgent`) was run on the
  bundled `uploads/Sample - Superstore.csv` dataset and verified to produce
  the expected `context` structure (`schema`, `plan`, `processed_dataframe`,
  `evaluation_results`, `best_model`, `training_results`, `report`).
* `Home.py` and both pages were exercised with Streamlit's `AppTest`,
  including a full simulated upload → "Run AI Analysis" click, and rendered
  without errors.
* The live `streamlit run` server was started and its health endpoint
  verified.
* JSON, Markdown, and PDF export were each generated and inspected.
* A pre-existing bug was found and fixed in `agents/preprocessing_agent.py`:
  it contained `from turtle import pd`, which silently binds `pd` to
  turtle's `pendown` alias instead of pandas and crashes on any headless
  machine (no `tkinter`), including a `python:3.11-slim` Docker image. This
  was corrected to `import pandas as pd`.
* **Fixed:** `python -m streamlit run Home.py` could fail at the `planning`
  stage with `httpx.ConnectError: [Errno 11001] getaddrinfo failed`, while
  `python app.py` worked fine, even though both use the exact same
  `GeminiProvider` / `config.llm_config` code path. Root cause: on Windows,
  Streamlit's server forces `WindowsSelectorEventLoopPolicy`, and in that
  process some HTTP clients (including the httpx client `google-genai`
  uses) can fail DNS resolution — `getaddrinfo failed` / WinError 11001 —
  due to a broken/absent IPv6 route being tried before IPv4. `python app.py`
  never opens a listening socket, so it isn't affected. `Home.py` now forces
  IPv4-only DNS resolution on Windows only (`if sys.platform == "win32"`),
  which is the standard fix for this class of error. `config/llm_config.py`
  was also hardened to load `.env` from an absolute, project-root-anchored
  path instead of relying on frame-based auto-discovery, so `.env` loading
  is identical and deterministic no matter which entry point starts the
  process. Neither change touches `app.py`, `api.py`, or any Gemini/LLM
  logic — if you still see this error after pulling this fix, it is a
  genuine local DNS/proxy/VPN/firewall issue on that machine, not a code
  issue (verify by running
  `python -c "import socket; print(socket.gethostbyname('generativelanguage.googleapis.com'))"`
  from the same terminal used to launch Streamlit).
* **The sandbox used to build this project has no network access to
  Google's Gemini API**, so the real `GeminiProvider.generate()` call could
  not be exercised live. Everything upstream and downstream of that call was
  verified with the real code paths; only the network call itself was
  substituted with a controlled response during testing, and the production
  code still calls the real Gemini provider — nothing in `llm/`,
  `agents/llm_planner_agent.py`, or `agents/insights_report_agent.py` was
  changed to work around this. Please verify the live Gemini call in your
  own environment.

---

## Future Work

* Hyperparameter optimization
* Explainable AI integration
* Feature engineering automation
* Time series forecasting
* Ensemble model selection
* Automated business insight generation
* Dashboard generation
* Multi-model benchmarking

---


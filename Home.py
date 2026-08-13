"""
Ventora — Business AI Agent
Home / Upload page.

This page is presentation-only: it uploads a dataset, previews it, and,
on request, runs the REAL pipeline (services.pipeline_service.PipelineService,
which wraps the existing SchemaAgent / LLMPlannerAgent / PreprocessingAgent /
ModelAgent / InsightsReportAgent). Nothing here fabricates data.
"""

from __future__ import annotations

import sys
import socket


if sys.platform == "win32":
    _orig_getaddrinfo = socket.getaddrinfo

    def _ipv4_only_getaddrinfo(host, port, family=0, type=0, proto=0, flags=0):
        return _orig_getaddrinfo(host, port, socket.AF_INET, type, proto, flags)

    socket.getaddrinfo = _ipv4_only_getaddrinfo

import io

import pandas as pd
import streamlit as st

from services.pipeline_service import PipelineService, STAGES, PipelineError
from ui.theme import inject_base_css, render_brand, page_title
from ui.components import kpi_row, render_progress_panel, empty_state

st.set_page_config(
    page_title="Ventora — Business AI Agent",
    page_icon="🟣",
    layout="wide",
    initial_sidebar_state="expanded",
)

inject_base_css()
render_brand(sidebar=True)

st.sidebar.markdown("---")
st.sidebar.caption(
    "Upload a dataset here, then open **AI Workspace** and "
    "**Analytics & Reports** from the left to explore the real "
    "pipeline output."
)

with st.sidebar.expander("Environment check", expanded=False):
    from config.llm_config import GEMINI_API_KEY, GEMINI_MODEL

    if GEMINI_API_KEY:
     st.caption("✅ GEMINI_API_KEY loaded successfully.")
    else:
     st.caption("⚠️ GEMINI_API_KEY not found in `.env`.")
    st.caption(f"GEMINI_MODEL: `{GEMINI_MODEL}`")
    st.caption(
        "These should match what `python app.py` loads. If they do and "
        "the pipeline still fails at the planning stage with a DNS/"
        "connection error, it's a local network/firewall/VPN issue, not "
        "a Ventora bug — same code path, same agents, same GeminiProvider."
    )

page_title(
    "Ventora Business AI Agent",
    subtitle="Upload a dataset and let the multi-agent pipeline analyze it, "
    "train models, and generate an executive report — end to end.",
    eyebrow="AI-Powered Business Intelligence",
)

SUPPORTED_EXTENSIONS = ["csv"]
CSV_ENCODINGS = ["utf-8", "utf-8-sig", "cp1252", "latin1"]


def load_dataset(uploaded_file) -> pd.DataFrame:
    raw = uploaded_file.getvalue()
    last_err = None
    for enc in CSV_ENCODINGS:
        try:
            return pd.read_csv(io.BytesIO(raw), encoding=enc)
        except UnicodeDecodeError as e:
            last_err = e
            continue
    raise ValueError(f"Could not decode CSV with any supported encoding: {last_err}")



# Upload

uploaded = st.file_uploader(
    "Upload your dataset",
    type=SUPPORTED_EXTENSIONS,
    help="Supported format: CSV (the pipeline reads it the same way api.py does, "
    "trying utf-8, utf-8-sig, cp1252, then latin1).",
)

if uploaded is not None:
    try:
        df = load_dataset(uploaded)
    except Exception as e:
        st.error(f"Could not read this file: {e}")
        st.stop()

    st.session_state["uploaded_filename"] = uploaded.name
    st.session_state["dataframe"] = df

    st.markdown("")
    kpi_row(
        [
            ("File", uploaded.name, f"{uploaded.size / 1024:.1f} KB"),
            ("Rows", f"{len(df):,}", None),
            ("Columns", f"{df.shape[1]:,}", None),
            (
                "Missing Cells",
                f"{int(df.isnull().sum().sum()):,}",
                f"{df.isnull().sum().sum() / (len(df) * df.shape[1]) * 100:.1f}% of cells"
                if len(df) and df.shape[1]
                else None,
            ),
        ]
    )

    st.markdown('<div class="vt-section-title">Dataset Preview</div>', unsafe_allow_html=True)
    st.dataframe(df.head(50), width='stretch', height=320)

    st.markdown('<div class="vt-section-title">Run AI Analysis</div>', unsafe_allow_html=True)
    st.caption(
        "This runs the real pipeline: Schema Agent → AI Planner (Gemini) → "
        "Preprocessing Agent → Model Agent → Insights Report Agent."
    )

    run_clicked = st.button("Run AI Analysis", type="primary", width='content')

    progress_placeholder = st.empty()

    if run_clicked:
        stage_status = {key: "pending" for key, _ in STAGES}

        def progress_callback(stage, status, detail=None):
            stage_status[stage] = status
            with progress_placeholder.container():
                render_progress_panel(stage_status)

        with progress_placeholder.container():
            render_progress_panel(stage_status)

        service = PipelineService()
        try:
            with st.spinner("Running the multi-agent pipeline..."):
                context = service.run(df, progress_callback=progress_callback)
            st.session_state["pipeline_context"] = context
            st.session_state["pipeline_error"] = None
            st.success(
                "Analysis complete. Open **AI Workspace** or "
                "**Analytics & Reports** in the sidebar to view results."
            )
        except PipelineError as e:
            st.session_state["pipeline_error"] = str(e)
            original_msg = str(e.original)
            if "getaddrinfo" in original_msg or "ConnectError" in type(e.original).__name__:
                st.error(
                    f"The pipeline failed at stage **{e.stage}** with a DNS/network "
                    f"error: {original_msg}\n\n"
                    "This means the Python process could not resolve/reach Google's "
                    "Gemini API host — it is a local network, DNS, VPN, proxy, or "
                    "firewall issue on this machine, not a bug in the pipeline or "
                    "the Streamlit integration (the code path is identical to "
                    "`python app.py`). Check the **Environment check** panel in the "
                    "sidebar, and verify this machine can reach "
                    "`generativelanguage.googleapis.com` from the terminal you "
                    "launched Streamlit from."
                )
            else:
                st.error(
                    f"The pipeline failed at stage **{e.stage}**: {original_msg}\n\n"
                    "If this is a Gemini/LLM authentication error, check the "
                    "`GEMINI_API_KEY` / `GEMINI_MODEL` values in your `.env` file."
                )
        except Exception as e:  # noqa: BLE001
            st.session_state["pipeline_error"] = str(e)
            st.error(f"Unexpected error while running the pipeline: {e}")

else:
    empty_state(
        "No dataset uploaded yet",
        "Upload a CSV file above to see dataset statistics, run the AI "
        "pipeline, and generate a full business intelligence report.",
    )
    if "dataframe" in st.session_state:
        st.info(
            f"A previous dataset (**{st.session_state.get('uploaded_filename', 'unnamed')}**) "
            "is still loaded in this session. Open **AI Workspace** to keep exploring it, "
            "or upload a new file above to replace it."
        )

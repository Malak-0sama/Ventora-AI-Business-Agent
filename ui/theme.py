"""
Ventora visual theme for the Streamlit dashboard.

Palette is derived directly from the project's own .streamlit/config.toml
(base="dark", primaryColor="#7C5CFF", backgroundColor="#0B0E14"), extended
into a small token system for cards, status pills, and typography.
"""

import streamlit as st

BG = "#0B0E14"
BG_ELEV = "#11151F"
BG_CARD = "#141926"
BORDER = "#232A3B"
TEXT = "#E7E9EE"
TEXT_MUTED = "#8B93A7"
PRIMARY = "#7C5CFF"
PRIMARY_SOFT = "rgba(124, 92, 255, 0.14)"
SUCCESS = "#3DDC97"
WARNING = "#F5A524"
DANGER = "#F65C6D"
ACCENT_TEAL = "#3FD8D4"

FONT_STACK = (
    "'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif"
)


def inject_base_css():
    st.markdown(
        f"""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500&display=swap');

        html, body, [class*="css"] {{
            font-family: {FONT_STACK};
        }}

        #MainMenu {{visibility: hidden;}}
        footer {{visibility: hidden;}}
        header[data-testid="stHeader"] {{background: transparent;}}

        .block-container {{
            padding-top: 2rem;
            padding-bottom: 3rem;
            max-width: 1200px;
        }}

        /* ---- Sidebar ---- */
        section[data-testid="stSidebar"] {{
            background: linear-gradient(180deg, {BG_ELEV} 0%, {BG} 100%);
            border-right: 1px solid {BORDER};
        }}

        /* ---- Brand header ---- */
        .ventora-brand {{
            display: flex;
            align-items: center;
            gap: 10px;
            margin-bottom: 4px;
        }}
        .ventora-mark {{
            width: 34px;
            height: 34px;
            border-radius: 9px;
            background: linear-gradient(135deg, {PRIMARY} 0%, {ACCENT_TEAL} 100%);
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: 800;
            color: #0B0E14;
            font-size: 17px;
            flex-shrink: 0;
        }}
        .ventora-name {{
            font-size: 1.15rem;
            font-weight: 800;
            letter-spacing: 0.01em;
            color: {TEXT};
            line-height: 1.1;
        }}
        .ventora-tagline {{
            font-size: 0.72rem;
            color: {TEXT_MUTED};
            text-transform: uppercase;
            letter-spacing: 0.14em;
            margin-top: 2px;
        }}

        /* ---- Page title block ---- */
        .vt-page-title {{
            font-size: 1.9rem;
            font-weight: 800;
            color: {TEXT};
            margin-bottom: 0.15rem;
            letter-spacing: -0.01em;
        }}
        .vt-page-subtitle {{
            color: {TEXT_MUTED};
            font-size: 0.95rem;
            margin-bottom: 1.6rem;
        }}
        .vt-section-title {{
            font-size: 1.05rem;
            font-weight: 700;
            color: {TEXT};
            margin: 1.6rem 0 0.7rem 0;
            display: flex;
            align-items: center;
            gap: 8px;
        }}
        .vt-eyebrow {{
            font-size: 0.68rem;
            font-weight: 700;
            letter-spacing: 0.14em;
            text-transform: uppercase;
            color: {PRIMARY};
            margin-bottom: 0.3rem;
        }}

        /* ---- KPI cards ---- */
        .vt-kpi {{
            background: {BG_CARD};
            border: 1px solid {BORDER};
            border-radius: 14px;
            padding: 16px 18px;
            height: 100%;
        }}
        .vt-kpi-label {{
            font-size: 0.72rem;
            font-weight: 600;
            color: {TEXT_MUTED};
            text-transform: uppercase;
            letter-spacing: 0.08em;
            margin-bottom: 8px;
        }}
        .vt-kpi-value {{
            font-size: 1.65rem;
            font-weight: 800;
            color: {TEXT};
            font-variant-numeric: tabular-nums;
            line-height: 1.1;
        }}
        .vt-kpi-delta {{
            font-size: 0.78rem;
            margin-top: 6px;
            color: {TEXT_MUTED};
        }}

        /* ---- Generic card ---- */
        .vt-card {{
            background: {BG_CARD};
            border: 1px solid {BORDER};
            border-radius: 14px;
            padding: 18px 20px;
            margin-bottom: 14px;
        }}
        .vt-card h4 {{
            margin-top: 0;
            color: {TEXT};
            font-size: 0.95rem;
            font-weight: 700;
        }}
        .vt-card p, .vt-card li {{
            color: #C7CCDA;
            font-size: 0.9rem;
            line-height: 1.55;
        }}

        /* ---- Status pill ---- */
        .vt-pill {{
            display: inline-flex;
            align-items: center;
            gap: 6px;
            padding: 3px 11px;
            border-radius: 999px;
            font-size: 0.72rem;
            font-weight: 700;
            letter-spacing: 0.02em;
        }}
        .vt-pill-success {{ background: rgba(61,220,151,0.14); color: {SUCCESS}; }}
        .vt-pill-running {{ background: {PRIMARY_SOFT}; color: {PRIMARY}; }}
        .vt-pill-pending {{ background: rgba(139,147,167,0.12); color: {TEXT_MUTED}; }}
        .vt-pill-failed  {{ background: rgba(246,92,109,0.14); color: {DANGER}; }}

        /* ---- Stage row ---- */
        .vt-stage-row {{
            display: flex;
            align-items: center;
            justify-content: space-between;
            padding: 10px 4px;
            border-bottom: 1px solid {BORDER};
        }}
        .vt-stage-row:last-child {{ border-bottom: none; }}
        .vt-stage-name {{
            font-size: 0.88rem;
            color: {TEXT};
            font-weight: 500;
        }}

        /* ---- Tag chip ---- */
        .vt-chip {{
            display: inline-block;
            background: {PRIMARY_SOFT};
            color: {PRIMARY};
            border-radius: 7px;
            padding: 2px 9px;
            font-size: 0.76rem;
            font-weight: 600;
            margin: 2px 4px 2px 0;
        }}
        .vt-chip-muted {{
            background: rgba(139,147,167,0.12);
            color: {TEXT_MUTED};
        }}
        .vt-chip-danger {{
            background: rgba(246,92,109,0.14);
            color: {DANGER};
        }}
        .vt-chip-success {{
            background: rgba(61,220,151,0.14);
            color: {SUCCESS};
        }}

        /* ---- Buttons ---- */
        .stButton > button {{
            border-radius: 10px;
            font-weight: 700;
            border: 1px solid {BORDER};
        }}
        .stButton > button[kind="primary"] {{
            background: linear-gradient(135deg, {PRIMARY} 0%, #6845F0 100%);
            border: none;
        }}

        /* ---- Dataframe / table polish ---- */
        [data-testid="stDataFrame"] {{
            border: 1px solid {BORDER};
            border-radius: 12px;
            overflow: hidden;
        }}

        hr {{ border-color: {BORDER}; }}
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_brand(sidebar: bool = True):
    target = st.sidebar if sidebar else st
    target.markdown(
        f"""
        <div class="ventora-brand">
            <div class="ventora-mark">V</div>
            <div>
                <div class="ventora-name">Ventora</div>
                <div class="ventora-tagline">Business AI Agent</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def page_title(title: str, subtitle: str = "", eyebrow: str = ""):
    eyebrow_html = f'<div class="vt-eyebrow">{eyebrow}</div>' if eyebrow else ""
    subtitle_html = (
        f'<div class="vt-page-subtitle">{subtitle}</div>' if subtitle else ""
    )
    st.markdown(
        f"""
        {eyebrow_html}
        <div class="vt-page-title">{title}</div>
        {subtitle_html}
        """,
        unsafe_allow_html=True,
    )


def section_title(text: str, icon: str = ""):
    st.markdown(
        f'<div class="vt-section-title">{icon} {text}</div>',
        unsafe_allow_html=True,
    )


# Shared Plotly dark template so every chart matches the dashboard theme.
PLOTLY_TEMPLATE = {
    "layout": {
        "paper_bgcolor": BG_CARD,
        "plot_bgcolor": BG_CARD,
        "font": {"color": TEXT, "family": FONT_STACK},
        "colorway": [PRIMARY, ACCENT_TEAL, SUCCESS, WARNING, DANGER, "#B39CFF"],
        "xaxis": {"gridcolor": BORDER, "zerolinecolor": BORDER},
        "yaxis": {"gridcolor": BORDER, "zerolinecolor": BORDER},
        "legend": {"bgcolor": "rgba(0,0,0,0)"},
        "margin": {"t": 40, "l": 10, "r": 10, "b": 10},
    }
}

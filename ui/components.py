"""Reusable Streamlit UI components for the Ventora dashboard."""

from __future__ import annotations

from typing import Optional

import streamlit as st

from services.pipeline_service import STAGES


def kpi_card(label: str, value: str, delta: Optional[str] = None):
    delta_html = f'<div class="vt-kpi-delta">{delta}</div>' if delta else ""
    st.markdown(
        f"""
        <div class="vt-kpi">
            <div class="vt-kpi-label">{label}</div>
            <div class="vt-kpi-value">{value}</div>
            {delta_html}
        </div>
        """,
        unsafe_allow_html=True,
    )


def kpi_row(items: list[tuple[str, str, Optional[str]]]):
    """items: list of (label, value, delta_or_None)"""
    cols = st.columns(len(items))
    for col, (label, value, delta) in zip(cols, items):
        with col:
            kpi_card(label, value, delta)


def status_pill(status: str) -> str:
    mapping = {
        "success": ("vt-pill-success", "✓ Done"),
        "running": ("vt-pill-running", "● Running"),
        "pending": ("vt-pill-pending", "○ Pending"),
        "failed": ("vt-pill-failed", "✕ Failed"),
        "skipped": ("vt-pill-pending", "– Skipped"),
    }
    cls, label = mapping.get(status, ("vt-pill-pending", status))
    return f'<span class="vt-pill {cls}">{label}</span>'


def render_progress_panel(stage_status: dict):
    """stage_status: {stage_key: status}. Renders the ordered checklist."""
    rows = []
    for key, label in STAGES:
        status = stage_status.get(key, "pending")
        rows.append(
            f'<div class="vt-stage-row">'
            f'<span class="vt-stage-name">{label}</span>'
            f'{status_pill(status)}'
            f'</div>'
        )
    st.markdown(
        f'<div class="vt-card">{"".join(rows)}</div>',
        unsafe_allow_html=True,
    )


def card(title: str, body_html: str):
    st.markdown(
        f'<div class="vt-card"><h4>{title}</h4>{body_html}</div>',
        unsafe_allow_html=True,
    )


def bullet_list_html(items) -> str:
    if not items:
        return '<p style="opacity:0.6;">No items reported.</p>'
    lis = "".join(f"<li>{i}</li>" for i in items)
    return f"<ul>{lis}</ul>"


def chip(text: str, kind: str = "") -> str:
    cls = f"vt-chip vt-chip-{kind}" if kind else "vt-chip"
    return f'<span class="{cls}">{text}</span>'


def chips_html(items, kind: str = "") -> str:
    if not items:
        return '<p style="opacity:0.6;">None reported.</p>'
    return "".join(chip(i, kind) for i in items)


def empty_state(title: str, body: str, cta: str = ""):
    cta_html = f'<p style="margin-top:10px;color:#7C5CFF;font-weight:600;">{cta}</p>' if cta else ""
    st.markdown(
        f"""
        <div class="vt-card" style="text-align:center; padding: 42px 24px;">
            <h4 style="font-size:1.05rem;">{title}</h4>
            <p>{body}</p>
            {cta_html}
        </div>
        """,
        unsafe_allow_html=True,
    )

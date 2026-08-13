"""
Export the REAL report produced by InsightsReportAgent (context["report"])
to JSON, Markdown, and PDF. No content is invented here — every export
function only reformats whatever technical_report / business_report the
pipeline actually generated.
"""

from __future__ import annotations

import json
from datetime import datetime
from typing import Any


def _fmt_dict_list(items) -> list[str]:
    """Render a list of small dicts (e.g. management_decisions) as lines."""
    lines = []
    if not items:
        return lines
    for item in items:
        if isinstance(item, dict):
            parts = [f"{k.replace('_', ' ').title()}: {v}" for k, v in item.items()]
            lines.append(" - ".join(parts))
        else:
            lines.append(str(item))
    return lines


_PDF_SAFE_REPLACEMENTS = {
    "\u2014": "-",  # em dash
    "\u2013": "-",  # en dash
    "\u2018": "'",  # left single quote
    "\u2019": "'",  # right single quote
    "\u201c": '"',  # left double quote
    "\u201d": '"',  # right double quote
    "\u2026": "...",  # ellipsis
    "\u00a0": " ",  # non-breaking space
    "\u2022": "-",  # bullet
}


def _pdf_safe(text) -> str:
    """Core PDF fonts (Helvetica) only support latin-1; strip/replace anything
    outside that range so fpdf2 never chokes on unicode punctuation."""
    text = str(text)
    for src, dst in _PDF_SAFE_REPLACEMENTS.items():
        text = text.replace(src, dst)
    return text.encode("latin-1", errors="replace").decode("latin-1")


def build_json_export(context: dict) -> str:
    report = context.get("report", {})
    payload = {
        "generated_at": datetime.utcnow().isoformat() + "Z",
        "product": "Ventora Business AI Agent",
        "best_model": _safe(context.get("best_model")),
        "report": report,
    }
    return json.dumps(payload, indent=2, ensure_ascii=False, default=str)


def _safe(obj: Any):
    """Best-effort JSON-safe conversion for numpy scalars etc."""
    try:
        json.dumps(obj)
        return obj
    except TypeError:
        if isinstance(obj, dict):
            return {k: _safe(v) for k, v in obj.items()}
        return str(obj)


def build_markdown_export(context: dict) -> str:
    report = context.get("report", {})
    tech = report.get("technical_report", {}) or {}
    biz = report.get("business_report", {}) or {}

    lines = []
    lines.append("# Ventora — AI Business Intelligence Report")
    lines.append(f"_Generated {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}_")
    lines.append("")

    # ---- Business report ----
    if biz:
        lines.append("## Executive Summary")
        lines.append(biz.get("executive_summary", "") or "_Not available._")
        lines.append("")

        if biz.get("current_company_status"):
            lines.append("## Current Company Status")
            lines.append(biz["current_company_status"])
            lines.append("")

        kpi = biz.get("business_kpi_analysis") or {}
        if kpi:
            lines.append("## Business KPI Analysis")
            for k, v in kpi.items():
                if v:
                    lines.append(f"- **{k.replace('_', ' ').title()}:** {v}")
            lines.append("")

        drivers = biz.get("sales_and_profit_drivers") or []
        if drivers:
            lines.append("## Sales & Profit Drivers")
            for d in drivers:
                if isinstance(d, dict):
                    lines.append(
                        f"- **{d.get('factor', '')}** — {d.get('impact_on_business', '')} "
                        f"→ _Recommended:_ {d.get('recommended_action', '')}"
                    )
            lines.append("")

        cat = biz.get("product_category_analysis") or {}
        if cat:
            lines.append("## Product / Category Analysis")
            for label, key in [
                ("Best performing segments", "best_performing_segments"),
                ("Weak segments", "weak_segments"),
                ("Improvement actions", "improvement_actions"),
            ]:
                for v in cat.get(key) or []:
                    lines.append(f"- **{label}:** {v}")
            lines.append("")

        reg = biz.get("regional_analysis") or {}
        if reg:
            lines.append("## Regional Analysis")
            for label, key in [
                ("Strong regions", "strong_regions"),
                ("Weak regions", "weak_regions"),
                ("Recommended actions", "recommended_actions"),
            ]:
                for v in reg.get(key) or []:
                    lines.append(f"- **{label}:** {v}")
            lines.append("")

        disc = biz.get("discount_and_pricing_analysis") or {}
        if disc:
            lines.append("## Discount & Pricing Analysis")
            for v in disc.get("observations") or []:
                lines.append(f"- {v}")
            if disc.get("business_risk"):
                lines.append(f"- **Business Risk:** {disc['business_risk']}")
            if disc.get("recommended_strategy"):
                lines.append(f"- **Recommended Strategy:** {disc['recommended_strategy']}")
            lines.append("")

        cust = biz.get("customer_analysis") or {}
        if cust:
            lines.append("## Customer Analysis")
            for v in cust.get("customer_behavior_insights") or []:
                lines.append(f"- {v}")
            for v in cust.get("customer_strategy") or []:
                lines.append(f"- **Strategy:** {v}")
            lines.append("")

        if biz.get("business_risks"):
            lines.append("## Risks")
            for v in biz["business_risks"]:
                lines.append(f"- {v}")
            lines.append("")

        if biz.get("business_opportunities"):
            lines.append("## Opportunities")
            for v in biz["business_opportunities"]:
                lines.append(f"- {v}")
            lines.append("")

        decisions = biz.get("management_decisions") or []
        if decisions:
            lines.append("## Recommended Management Decisions")
            for line in _fmt_dict_list(decisions):
                lines.append(f"- {line}")
            lines.append("")

        if biz.get("future_strategy"):
            lines.append("## Future Strategy")
            for v in biz["future_strategy"]:
                lines.append(f"- {v}")
            lines.append("")

        if biz.get("final_executive_conclusion"):
            lines.append("## Conclusion")
            lines.append(biz["final_executive_conclusion"])
            lines.append("")

    # ---- Technical report ----
    if tech:
        lines.append("---")
        lines.append("## Technical Report")

        info = tech.get("model_information") or {}
        if info:
            lines.append("")
            lines.append(f"- **Model:** {info.get('model_name', 'N/A')}")
            lines.append(f"- **Problem type:** {info.get('problem_type', 'N/A')}")
            lines.append(f"- **Target variable:** {info.get('target_variable', 'N/A')}")

        if tech.get("model_performance_summary"):
            lines.append("")
            lines.append(tech["model_performance_summary"])

        metrics = tech.get("evaluation_metrics") or {}
        if metrics:
            lines.append("")
            lines.append("| Metric | Value |")
            lines.append("|---|---|")
            for k, v in metrics.items():
                lines.append(f"| {k} | {v} |")

        for label, key in [
            ("Technical Findings", "technical_findings"),
            ("Technical Risks", "technical_risks"),
            ("Technical Improvements", "technical_improvements"),
        ]:
            vals = tech.get(key) or []
            if vals:
                lines.append("")
                lines.append(f"### {label}")
                for v in vals:
                    lines.append(f"- {v}")

    return "\n".join(lines)


def build_pdf_export(context: dict) -> bytes:
    """Render the report to PDF using fpdf2 (already a project dependency)."""
    from fpdf import FPDF

    report = context.get("report", {})
    tech = report.get("technical_report", {}) or {}
    biz = report.get("business_report", {}) or {}

    pdf = FPDF(format="A4")
    pdf.set_auto_page_break(auto=True, margin=18)
    pdf.add_page()

    def h1(text):
        pdf.set_font("Helvetica", "B", 18)
        pdf.set_text_color(20, 20, 30)
        pdf.multi_cell(0, 10, _pdf_safe(text), new_x="LMARGIN", new_y="NEXT")
        pdf.ln(1)

    def h2(text):
        pdf.set_font("Helvetica", "B", 13)
        pdf.set_text_color(70, 40, 200)
        pdf.multi_cell(0, 8, _pdf_safe(text), new_x="LMARGIN", new_y="NEXT")
        pdf.ln(1)

    def body(text):
        pdf.set_font("Helvetica", "", 10.5)
        pdf.set_text_color(30, 30, 30)
        pdf.multi_cell(0, 6, _pdf_safe(text), new_x="LMARGIN", new_y="NEXT")
        pdf.ln(1)

    def bullet(text):
        pdf.set_font("Helvetica", "", 10.5)
        pdf.set_text_color(30, 30, 30)
        pdf.multi_cell(0, 6, _pdf_safe(f"-  {text}"), new_x="LMARGIN", new_y="NEXT")

    h1("Ventora - AI Business Intelligence Report")
    pdf.set_font("Helvetica", "", 9)
    pdf.set_text_color(120, 120, 120)
    pdf.cell(0, 6, f"Generated {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(3)

    if biz.get("executive_summary"):
        h2("Executive Summary")
        body(biz["executive_summary"])

    if biz.get("current_company_status"):
        h2("Current Company Status")
        body(biz["current_company_status"])

    kpi = biz.get("business_kpi_analysis") or {}
    if kpi:
        h2("Business KPI Analysis")
        for k, v in kpi.items():
            if v:
                bullet(f"{k.replace('_', ' ').title()}: {v}")
        pdf.ln(2)

    drivers = biz.get("sales_and_profit_drivers") or []
    if drivers:
        h2("Sales & Profit Drivers")
        for d in drivers:
            if isinstance(d, dict):
                bullet(
                    f"{d.get('factor', '')} - {d.get('impact_on_business', '')} "
                    f"(Recommended: {d.get('recommended_action', '')})"
                )
        pdf.ln(2)

    if biz.get("business_risks"):
        h2("Risks")
        for v in biz["business_risks"]:
            bullet(v)
        pdf.ln(2)

    if biz.get("business_opportunities"):
        h2("Opportunities")
        for v in biz["business_opportunities"]:
            bullet(v)
        pdf.ln(2)

    decisions = biz.get("management_decisions") or []
    if decisions:
        h2("Recommended Management Decisions")
        for line in _fmt_dict_list(decisions):
            bullet(line)
        pdf.ln(2)

    if biz.get("future_strategy"):
        h2("Future Strategy")
        for v in biz["future_strategy"]:
            bullet(v)
        pdf.ln(2)

    if biz.get("final_executive_conclusion"):
        h2("Conclusion")
        body(biz["final_executive_conclusion"])

    # ---- Technical report ----
    if tech:
        pdf.add_page()
        h1("Technical Report")

        info = tech.get("model_information") or {}
        if info:
            bullet(f"Model: {info.get('model_name', 'N/A')}")
            bullet(f"Problem type: {info.get('problem_type', 'N/A')}")
            bullet(f"Target variable: {info.get('target_variable', 'N/A')}")
            pdf.ln(2)

        if tech.get("model_performance_summary"):
            h2("Performance Summary")
            body(tech["model_performance_summary"])

        metrics = tech.get("evaluation_metrics") or {}
        if metrics:
            h2("Evaluation Metrics")
            for k, v in metrics.items():
                bullet(f"{k}: {v}")
            pdf.ln(2)

        for label, key in [
            ("Technical Findings", "technical_findings"),
            ("Technical Risks", "technical_risks"),
            ("Technical Improvements", "technical_improvements"),
        ]:
            vals = tech.get(key) or []
            if vals:
                h2(label)
                for v in vals:
                    bullet(v)
                pdf.ln(2)

    return bytes(pdf.output())

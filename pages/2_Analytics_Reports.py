"""
Ventora — Analytics & Reports page.

Renders the REAL output of InsightsReportAgent: context["report"], with the
exact structure { "technical_report": {...}, "business_report": {...} }
produced by prompts.insights_report_prompt.build_insights_report_prompt.
Every section below only renders if the corresponding field is present in
the real report — nothing is invented or hardcoded.
"""

from __future__ import annotations

import streamlit as st

from ui.theme import inject_base_css, render_brand, page_title, section_title
from ui.components import card, bullet_list_html, chips_html, empty_state
from services.report_export_service import (
    build_json_export,
    build_markdown_export,
    build_pdf_export,
)

st.set_page_config(page_title="Analytics & Reports — Ventora", page_icon="🟣", layout="wide")
inject_base_css()
render_brand(sidebar=True)

page_title(
    "Analytics & Reports",
    subtitle="The executive business report and technical report generated "
    "by the Insights Report Agent for this run.",
    eyebrow="Insight Agent",
)

context = st.session_state.get("pipeline_context")

if context is None:
    empty_state(
        "No report has been generated yet",
        "Go to **Home**, upload a dataset, and click **Run AI Analysis** "
        "to generate the business and technical report.",
    )
    st.stop()

report = context.get("report")

if not report or not isinstance(report, dict):
    st.warning(
        "The pipeline ran, but no structured report was found in "
        "`context['report']`. This can happen if the Insights Report Agent "
        "returned an unexpected format."
    )
    st.stop()

business = report.get("business_report") or {}
technical = report.get("technical_report") or {}

tab_business, tab_technical, tab_export = st.tabs(
    ["📋 Business Report", "🔧 Technical Report", "⬇️ Export"]
)

# ============================================================================
# BUSINESS REPORT
# ============================================================================
with tab_business:
    if not business:
        st.info("No business report was returned for this run.")
    else:
        if business.get("executive_summary"):
            section_title("Executive Summary")
            card("", f"<p>{business['executive_summary']}</p>")

        if business.get("current_company_status"):
            section_title("Current Company Status")
            card("", f"<p>{business['current_company_status']}</p>")

        kpi_analysis = business.get("business_kpi_analysis") or {}
        if any(kpi_analysis.values()):
            section_title("Business KPI Analysis")
            cols = st.columns(2)
            labels = {
                "revenue_analysis": "Revenue",
                "profit_analysis": "Profit",
                "growth_trends": "Growth Trends",
                "operational_efficiency": "Operational Efficiency",
            }
            for i, (key, label) in enumerate(labels.items()):
                val = kpi_analysis.get(key)
                if val:
                    with cols[i % 2]:
                        card(label, f"<p>{val}</p>")

        drivers = business.get("sales_and_profit_drivers") or []
        if drivers:
            section_title("Sales & Profit Drivers")
            for d in drivers:
                if isinstance(d, dict):
                    card(
                        d.get("factor", "Driver"),
                        f"<p><strong>Impact:</strong> {d.get('impact_on_business', '')}</p>"
                        f"<p><strong>Recommended action:</strong> {d.get('recommended_action', '')}</p>",
                    )

        cat = business.get("product_category_analysis") or {}
        if any(cat.values()):
            section_title("Product / Category Analysis")
            c1, c2, c3 = st.columns(3)
            with c1:
                card("Best Performing", chips_html(cat.get("best_performing_segments"), "success"))
            with c2:
                card("Weak Segments", chips_html(cat.get("weak_segments"), "danger"))
            with c3:
                card("Improvement Actions", bullet_list_html(cat.get("improvement_actions")))

        reg = business.get("regional_analysis") or {}
        if any(reg.values()):
            section_title("Regional Analysis")
            c1, c2, c3 = st.columns(3)
            with c1:
                card("Strong Regions", chips_html(reg.get("strong_regions"), "success"))
            with c2:
                card("Weak Regions", chips_html(reg.get("weak_regions"), "danger"))
            with c3:
                card("Recommended Actions", bullet_list_html(reg.get("recommended_actions")))

        disc = business.get("discount_and_pricing_analysis") or {}
        if any(disc.values()):
            section_title("Discount & Pricing Analysis")
            body = bullet_list_html(disc.get("observations"))
            if disc.get("business_risk"):
                body += f"<p><strong>Business risk:</strong> {disc['business_risk']}</p>"
            if disc.get("recommended_strategy"):
                body += f"<p><strong>Recommended strategy:</strong> {disc['recommended_strategy']}</p>"
            card("", body)

        cust = business.get("customer_analysis") or {}
        if any(cust.values()):
            section_title("Customer Analysis", "👥")
            c1, c2 = st.columns(2)
            with c1:
                card("Behavior Insights", bullet_list_html(cust.get("customer_behavior_insights")))
            with c2:
                card("Customer Strategy", bullet_list_html(cust.get("customer_strategy")))

        if business.get("business_risks") or business.get("business_opportunities"):
            section_title("Risks & Opportunities")
            c1, c2 = st.columns(2)
            with c1:
                card("Risks", bullet_list_html(business.get("business_risks")))
            with c2:
                card("Opportunities", bullet_list_html(business.get("business_opportunities")))

        decisions = business.get("management_decisions") or []
        if decisions:
            section_title("Recommendations — Management Decisions", "✅")
            for d in decisions:
                if isinstance(d, dict):
                    card(
                        d.get("decision", "Decision"),
                        f"<p><strong>Reason:</strong> {d.get('reason', '')}</p>"
                        f"<p><strong>Expected value:</strong> {d.get('expected_business_value', '')}</p>",
                    )

        if business.get("future_strategy"):
            section_title("Action Plan — Future Strategy")
            card("", bullet_list_html(business["future_strategy"]))

        if business.get("final_executive_conclusion"):
            section_title("Conclusion", "🏁")
            card("", f"<p>{business['final_executive_conclusion']}</p>")

# ============================================================================
# TECHNICAL REPORT
# ============================================================================
with tab_technical:
    if not technical:
        st.info("No technical report was returned for this run.")
    else:
        info = technical.get("model_information") or {}
        if info:
            section_title("Model Information")
            c1, c2, c3 = st.columns(3)
            with c1:
                card("Model", f"<p>{info.get('model_name', 'N/A')}</p>")
            with c2:
                card("Problem Type", f"<p>{info.get('problem_type', 'N/A')}</p>")
            with c3:
                card("Target Variable", f"<p>{info.get('target_variable', 'N/A')}</p>")

        if technical.get("model_performance_summary"):
            section_title("Performance Summary")
            card("", f"<p>{technical['model_performance_summary']}</p>")

        metrics = technical.get("evaluation_metrics") or {}
        if metrics:
            with st.expander("Evaluation Metrics", expanded=True):
                st.table(
                    {"Metric": list(metrics.keys()), "Value": list(metrics.values())}
                )

        findings = technical.get("technical_findings") or []
        risks = technical.get("technical_risks") or []
        improvements = technical.get("technical_improvements") or []

        if findings:
            with st.expander("Technical Findings", expanded=True):
                st.markdown(bullet_list_html(findings), unsafe_allow_html=True)
        if risks:
            with st.expander("Technical Risks"):
                st.markdown(bullet_list_html(risks), unsafe_allow_html=True)
        if improvements:
            with st.expander("Technical Improvements"):
                st.markdown(bullet_list_html(improvements), unsafe_allow_html=True)

        with st.expander("Raw technical report (JSON)"):
            st.json(technical)

# ============================================================================
# EXPORT
# ============================================================================
with tab_export:
    section_title("Export This Report")
    st.caption("Every export below contains exactly the report generated for this run.")

    col1, col2, col3 = st.columns(3)

    with col1:
        json_bytes = build_json_export(context).encode("utf-8")
        st.download_button(
            "Download JSON",
            data=json_bytes,
            file_name="ventora_report.json",
            mime="application/json",
            width='stretch',
        )

    with col2:
        md_bytes = build_markdown_export(context).encode("utf-8")
        st.download_button(
            "Download Markdown",
            data=md_bytes,
            file_name="ventora_report.md",
            mime="text/markdown",
            width='stretch',
        )

    with col3:
        try:
            pdf_bytes = build_pdf_export(context)
            st.download_button(
                "Download PDF",
                data=pdf_bytes,
                file_name="ventora_report.pdf",
                mime="application/pdf",
                width='stretch',
            )
        except Exception as e:  # noqa: BLE001
            st.button("Download PDF", disabled=True, width='stretch')
            st.caption(f"PDF export unavailable: {e}")

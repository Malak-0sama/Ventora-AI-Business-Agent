"""
Ventora — AI Workspace page.

Displays REAL output from the pipeline context: schema/data-quality
(SchemaAgent), statistical analysis (computed directly on the uploaded
dataframe), and ML results (ModelAgent / ModelEvaluator). Nothing here is
mocked or hardcoded — every number comes from st.session_state["pipeline_context"],
which is produced by services.pipeline_service.PipelineService (a thin wrapper
around the existing agents).
"""

from __future__ import annotations

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from ui.theme import inject_base_css, render_brand, page_title, section_title, PLOTLY_TEMPLATE
from ui.components import kpi_row, card, empty_state

st.set_page_config(page_title="AI Workspace — Ventora", page_icon="🟣", layout="wide")
inject_base_css()
render_brand(sidebar=True)

page_title(
    "AI Workspace",
    subtitle="Schema, data quality, statistical analysis, and model results "
    "from the real pipeline run.",
    eyebrow="Analysis",
)

context = st.session_state.get("pipeline_context")

if context is None:
    empty_state(
        "No analysis has been run yet",
        "Go to **Home**, upload a dataset, and click **Run AI Analysis** "
        "to populate this workspace with real results.",
    )
    st.stop()

schema = context.get("schema", {})
original_df: pd.DataFrame = context.get("dataframe")
processed_df: pd.DataFrame = context.get("processed_dataframe", original_df)

# ============================================================================
# Dataset Overview
# ============================================================================
section_title("Dataset Overview", "📊")

dataset_meta = schema.get("dataset", {})
quality_meta = schema.get("quality", {})

kpi_row(
    [
        ("Rows", f"{dataset_meta.get('rows', len(original_df)):,}", None),
        ("Columns", f"{dataset_meta.get('columns', original_df.shape[1]):,}", None),
        ("Numeric Columns", f"{dataset_meta.get('numeric_columns', 0):,}", None),
        ("Categorical Columns", f"{dataset_meta.get('categorical_columns', 0):,}", None),
    ]
)
st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)
kpi_row(
    [
        ("Datetime Columns", f"{dataset_meta.get('datetime_columns', 0):,}", None),
        ("Duplicate Rows", f"{dataset_meta.get('duplicate_rows', 0):,}", None),
        (
            "Memory Usage",
            f"{dataset_meta.get('memory_usage_mb', 0):.2f} MB"
            if "memory_usage_mb" in dataset_meta
            else "N/A",
            None,
        ),
        ("Quality Score", f"{quality_meta.get('quality_score', 0):.1f} / 100", None),
    ]
)

# ============================================================================
# Data Quality
# ============================================================================
section_title("Data Quality", "🧪")

columns_meta = schema.get("columns", {})
if columns_meta:
    quality_rows = []
    for col, meta in columns_meta.items():
        quality_rows.append(
            {
                "Column": col,
                "Type": meta.get("semantic_type", meta.get("dtype", "")),
                "Missing": meta.get("missing_count", 0),
                "Missing %": round(meta.get("missing_ratio", 0) * 100, 2),
                "Unique": meta.get("unique_count", 0),
                "Constant": meta.get("is_constant", False),
                "Has Outliers": meta.get("has_outliers", False),
                "Identifier-like": meta.get("is_identifier", False),
            }
        )
    quality_df = pd.DataFrame(quality_rows)

    left, right = st.columns([3, 2])
    with left:
        st.dataframe(quality_df, width='stretch', height=340)
    with right:
        missing_top = quality_df[quality_df["Missing"] > 0].sort_values(
            "Missing", ascending=False
        ).head(15)
        if not missing_top.empty:
            fig = px.bar(
                missing_top,
                x="Missing",
                y="Column",
                orientation="h",
                title="Missing Values by Column",
            )
            fig.update_layout(**PLOTLY_TEMPLATE["layout"], height=340)
            fig.update_yaxes(autorange="reversed")
            st.plotly_chart(fig, width='stretch')
        else:
            card("Missing Values", "<p>No missing values detected in this dataset.</p>")

    issues = []
    if quality_meta.get("duplicate_rows", 0) > 0:
        issues.append(f"{quality_meta['duplicate_rows']} duplicate row(s) detected.")
    constant_cols = [c for c, m in columns_meta.items() if m.get("is_constant")]
    if constant_cols:
        issues.append(f"Constant columns (no variance): {', '.join(constant_cols)}")
    high_missing = [
        c for c, m in columns_meta.items() if m.get("missing_ratio", 0) > 0.3
    ]
    if high_missing:
        issues.append(f"Columns with >30% missing values: {', '.join(high_missing)}")

    if issues:
        card("Data Quality Issues", "<ul>" + "".join(f"<li>{i}</li>" for i in issues) + "</ul>")
else:
    st.info("Schema Agent did not return column-level metadata for this dataset.")

# ============================================================================
# Statistical Analysis
# ============================================================================
section_title("Statistical Analysis", "📈")

numeric_cols = original_df.select_dtypes(include="number").columns.tolist()
categorical_cols = [
    c for c in original_df.select_dtypes(include=["object", "category", "string"]).columns
]

tab_desc, tab_dist, tab_corr, tab_cat = st.tabs(
    ["Descriptive Stats", "Distributions", "Correlation", "Categorical Breakdown"]
)

with tab_desc:
    if numeric_cols:
        st.dataframe(original_df[numeric_cols].describe().T, width='stretch')
    else:
        st.info("No numeric columns found in this dataset.")

with tab_dist:
    if numeric_cols:
        selected_num = st.selectbox("Column", numeric_cols, key="dist_col")
        fig = px.histogram(original_df, x=selected_num, nbins=40, marginal="box")
        fig.update_layout(**PLOTLY_TEMPLATE["layout"], height=380)
        st.plotly_chart(fig, width='stretch')
    else:
        st.info("No numeric columns available for distribution plots.")

with tab_corr:
    if len(numeric_cols) >= 2:
        corr = original_df[numeric_cols].corr(numeric_only=True)
        fig = px.imshow(
            corr,
            text_auto=".2f",
            color_continuous_scale="RdBu",
            zmin=-1,
            zmax=1,
            aspect="auto",
        )
        fig.update_layout(**PLOTLY_TEMPLATE["layout"], height=min(140 + 40 * len(numeric_cols), 700))
        st.plotly_chart(fig, width='stretch')
    else:
        st.info("Need at least two numeric columns to compute a correlation matrix.")

with tab_cat:
    if categorical_cols:
        selected_cat = st.selectbox("Column", categorical_cols, key="cat_col")
        counts = original_df[selected_cat].value_counts().head(20).reset_index()
        counts.columns = [selected_cat, "Count"]
        fig = px.bar(counts, x=selected_cat, y="Count")
        fig.update_layout(**PLOTLY_TEMPLATE["layout"], height=380)
        st.plotly_chart(fig, width='stretch')
    else:
        st.info("No categorical columns found in this dataset.")

# ============================================================================
# ML Results
# ============================================================================
section_title("ML Results", "🤖")

evaluation_results = context.get("evaluation_results", {})
best_model = context.get("best_model")
training_results = context.get("training_results", {})
plan = context.get("plan", {})

if not evaluation_results or best_model is None:
    st.info("No model evaluation results are available for this run.")
else:
    target_col = (
        plan.get("target", {}).get("column")
        if isinstance(plan.get("target"), dict)
        else plan.get("target")
    )
    task_type = plan.get("task", {}).get("type", "N/A")

    kpi_row(
        [
            ("Best Model", str(best_model.get("model_name", "N/A")), None),
            ("Target Variable", str(target_col or "N/A"), None),
            ("Task Type", str(task_type), None),
            (
                f"Primary Metric ({best_model.get('metric', '')})",
                f"{best_model.get('score'):.4f}"
                if isinstance(best_model.get("score"), (int, float, np.floating))
                else str(best_model.get("score")),
                None,
            ),
        ]
    )

    st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)

    rows = []
    for name, result in evaluation_results.items():
        if name.startswith("_"):
            continue
        row = {"Model": name, "Status": result.get("status")}
        if result.get("status") == "success":
            row["Train Time (s)"] = result.get("train_time")
            for metric_name, metric_val in (result.get("metrics") or {}).items():
                if isinstance(metric_val, (int, float, np.floating)):
                    row[metric_name] = round(float(metric_val), 4)
        else:
            row["Error"] = result.get("error")
        rows.append(row)

    if rows:
        st.dataframe(pd.DataFrame(rows), width='stretch')

    # ---- Feature importance ----
    best_name = best_model.get("model_name")
    best_train = training_results.get(best_name, {})
    trained_model = best_train.get("model")
    X_train = best_train.get("X_train")

    col_fi, col_pred = st.columns(2)

    with col_fi:
        if (
            trained_model is not None
            and X_train is not None
            and hasattr(trained_model, "feature_importances_")
        ):
            importances = pd.Series(
                trained_model.feature_importances_, index=X_train.columns
            ).sort_values(ascending=False).head(15)
            fig = px.bar(
                importances[::-1],
                orientation="h",
                title=f"Feature Importance — {best_name}",
                labels={"value": "Importance", "index": "Feature"},
            )
            fig.update_layout(**PLOTLY_TEMPLATE["layout"], height=420, showlegend=False)
            st.plotly_chart(fig, width='stretch')
        elif (
            trained_model is not None
            and X_train is not None
            and hasattr(trained_model, "coef_")
        ):
            coefs = np.ravel(trained_model.coef_)
            importances = pd.Series(coefs, index=X_train.columns).abs().sort_values(
                ascending=False
            ).head(15)
            fig = px.bar(
                importances[::-1],
                orientation="h",
                title=f"Coefficient Magnitude — {best_name}",
                labels={"value": "|Coefficient|", "index": "Feature"},
            )
            fig.update_layout(**PLOTLY_TEMPLATE["layout"], height=420, showlegend=False)
            st.plotly_chart(fig, width='stretch')
        else:
            card(
                "Feature Importance",
                "<p>This model does not expose feature importances or coefficients.</p>",
            )

    with col_pred:
        y_test = best_train.get("y_test")
        X_test = best_train.get("X_test")
        if trained_model is not None and X_test is not None and y_test is not None:
            try:
                y_pred = trained_model.predict(X_test)
                task_lower = str(task_type).lower()
                if task_lower == "regression":
                    fig = go.Figure()
                    fig.add_trace(
                        go.Scatter(
                            x=y_test, y=y_pred, mode="markers", name="Predictions",
                            marker=dict(color="#7C5CFF", size=6, opacity=0.65),
                        )
                    )
                    lo, hi = float(np.min(y_test)), float(np.max(y_test))
                    fig.add_trace(
                        go.Scatter(
                            x=[lo, hi], y=[lo, hi], mode="lines", name="Ideal",
                            line=dict(color="#3FD8D4", dash="dash"),
                        )
                    )
                    fig.update_layout(
                        title=f"Actual vs Predicted — {best_name}",
                        xaxis_title="Actual",
                        yaxis_title="Predicted",
                        **PLOTLY_TEMPLATE["layout"],
                    )
                    fig.update_layout(height=420)
                    st.plotly_chart(fig, width='stretch')
                else:
                    from sklearn.metrics import confusion_matrix

                    cm = confusion_matrix(y_test, y_pred)
                    fig = px.imshow(
                        cm,
                        text_auto=True,
                        color_continuous_scale="Purples",
                        labels=dict(x="Predicted", y="Actual"),
                        title=f"Confusion Matrix — {best_name}",
                    )
                    fig.update_layout(**PLOTLY_TEMPLATE["layout"], height=420)
                    st.plotly_chart(fig, width='stretch')
            except Exception as e:  # noqa: BLE001
                card("Prediction Plot", f"<p>Could not render predictions: {e}</p>")
        else:
            card("Prediction Plot", "<p>Test set predictions are not available.</p>")

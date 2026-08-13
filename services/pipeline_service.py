"""
Pipeline service — presentation-layer wrapper around the REAL agent pipeline.

This module does not reimplement any analysis logic. It instantiates the
existing agents (SchemaAgent, LLMPlannerAgent, PreprocessingAgent, ModelAgent,
InsightsReportAgent) exactly as core/workflow.AgentWorkflow does, and simply
adds an optional progress callback so the Streamlit UI can render live
pipeline status. core/workflow.py and api.py are untouched and keep working
exactly as before — this is an additive, backward-compatible wrapper.

Stage order mirrors core/workflow.AgentWorkflow.run():
    dataset_loaded -> schema_analysis -> planning -> data_processing
    -> ml_analysis -> insight_generation -> report_generation
"""

from __future__ import annotations

import traceback
from typing import Any, Callable, Optional

from agents.schema_agent import SchemaAgent
from agents.llm_planner_agent import LLMPlannerAgent
from agents.preprocessing_agent import PreprocessingAgent
from agents.model_agent import ModelAgent
from agents.insights_report_agent import InsightsReportAgent


STAGES = [
    ("dataset_loaded", "Dataset Loaded"),
    ("schema_analysis", "Schema Analysis"),
    ("planning", "AI Planning"),
    ("data_processing", "Data Processing"),
    ("ml_analysis", "ML Analysis"),
    ("insight_generation", "Insight Generation"),
    ("report_generation", "Report Generation"),
]

ProgressCallback = Callable[[str, str, Optional[str]], None]


class PipelineError(RuntimeError):
    """Raised when a pipeline stage fails, carrying the failed stage key."""

    def __init__(self, stage: str, original: BaseException):
        self.stage = stage
        self.original = original
        super().__init__(f"Pipeline failed at stage '{stage}': {original}")


class PipelineService:
    """Thin orchestration layer that runs the real multi-agent pipeline."""

    def __init__(self):
        self.schema_agent = SchemaAgent()
        self.planner_agent = LLMPlannerAgent()
        self.preprocessing_agent = PreprocessingAgent()
        self.model_agent = ModelAgent()
        self.report_agent = InsightsReportAgent()

    def run(
        self,
        dataframe,
        progress_callback: Optional[ProgressCallback] = None,
    ) -> dict:
        """
        Run the real pipeline end-to-end.

        progress_callback(stage_key, status, detail) is invoked with
        status in {"running", "success", "failed"}. detail carries an
        error message when status == "failed".
        """

        def notify(stage: str, status: str, detail: Optional[str] = None):
            if progress_callback:
                progress_callback(stage, status, detail)

        context: dict[str, Any] = {"dataframe": dataframe}

        notify("dataset_loaded", "running")
        notify("dataset_loaded", "success")

        try:
            notify("schema_analysis", "running")
            context = self.schema_agent.run(context)
            notify("schema_analysis", "success")

            notify("planning", "running")
            context = self.planner_agent.run(context)
            notify("planning", "success")

            notify("data_processing", "running")
            context = self.preprocessing_agent.run(context)
            notify("data_processing", "success")

            notify("ml_analysis", "running")
            context = self.model_agent.run(context)
            notify("ml_analysis", "success")

            notify("insight_generation", "running")
            context = self.report_agent.run(context)
            notify("insight_generation", "success")

            notify("report_generation", "running")
            notify("report_generation", "success")

        except Exception as exc:  
            failed_stage = self._infer_failed_stage(context)
            notify(failed_stage, "failed", str(exc))
            traceback.print_exc()
            raise PipelineError(failed_stage, exc) from exc

        return context

    @staticmethod
    def _infer_failed_stage(context: dict) -> str:
        if "schema" not in context:
            return "schema_analysis"
        if "plan" not in context:
            return "planning"
        if "processed_data" not in context:
            return "data_processing"
        if "evaluation_results" not in context:
            return "ml_analysis"
        if "report" not in context:
            return "insight_generation"
        return "report_generation"

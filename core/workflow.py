from agents.schema_agent import SchemaAgent
from agents.llm_planner_agent import LLMPlannerAgent
from agents.preprocessing_agent import PreprocessingAgent
from agents.model_agent import ModelAgent
from agents.insights_report_agent import InsightsReportAgent


class AgentWorkflow:

    def __init__(self):

        self.schema_agent = SchemaAgent()
        self.planner_agent = LLMPlannerAgent()
        self.preprocessing_agent = PreprocessingAgent()
        self.model_agent = ModelAgent()
        self.report_agent = InsightsReportAgent()

    def run(self, dataframe):

        context = {
            "dataframe": dataframe
        }

        print("\n" + "=" * 70)
        print("BUSINESS AI AGENT WORKFLOW".center(70))
        print("=" * 70)

        print("Running Schema Agent...")
        context = self.schema_agent.run(context)

        print("Running Planner Agent...")
        context = self.planner_agent.run(context)

        print("Running Preprocessing Agent...")
        context = self.preprocessing_agent.run(context)

        print("Running Model Agent...")
        context = self.model_agent.run(context)

        print("Running Report Agent...")
        context = self.report_agent.run(context)

        print("\n" + "=" * 70)
        print("WORKFLOW FINISHED".center(70))
        print("=" * 70)

        return context
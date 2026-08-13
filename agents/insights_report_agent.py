import json

from agents.base_agent import BaseAgent
from llm.gemini_provider import GeminiProvider
from prompts.insights_report_prompt import build_insights_report_prompt


class InsightsReportAgent(BaseAgent):

    def __init__(self):
        self.llm = GeminiProvider()


    def run(self, context):

        evaluation = context["evaluation_results"]

        best = context["best_model"]

        plan = context["plan"]


        best_model_name = best["model_name"]


        best_result = evaluation[best_model_name]

        metrics = best_result["metrics"]



        
        task_info = plan.get("task", {})


        task_type = task_info.get(
            "type",
            "Unknown"
        )


        
        target_variable = (
            task_info.get("target")
            or
            task_info.get("target_column")
            or
            plan.get("target")
            or
            plan.get("target_column")
            or
            "Unknown"
        )



        results = {

            "model_information": {

                "model_name": best_model_name,

                "problem_type": task_type,

                "target_variable": target_variable

            },


            "model_performance": {

                "primary_metric": best["metric"],

                "primary_score": best["score"],

                "metrics": metrics

            },


            "task_information": {

                "task_type": task_type,

                "target": target_variable

            }

        }



        prompt = build_insights_report_prompt(results)



        response = self.llm.generate(prompt)



        response = (
            response
            .strip()
            .replace("```json", "")
            .replace("```", "")
            .strip()
        )



        try:

            insights_report = json.loads(response)


        except json.JSONDecodeError:

            print("Invalid JSON returned from LLM:")

            print(response)

            raise



        

        context["report"] = insights_report


        return context
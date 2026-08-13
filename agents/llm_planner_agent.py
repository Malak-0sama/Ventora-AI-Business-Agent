import json
from agents.base_agent import BaseAgent
from llm.gemini_provider import GeminiProvider
from prompts.planner_prompt import build_planner_prompt


class LLMPlannerAgent(BaseAgent):

    def __init__(self):

        self.llm = GeminiProvider()

    def run(self, context: dict):

        schema = context["schema"]

        prompt = build_planner_prompt(schema)

        response = self.llm.generate(prompt)

        plan = self._parse_json(response)

        context["plan"] = plan

        return context

    def _parse_json(self, response: str):

        response = response.replace("```json", "")
        response = response.replace("```", "")
        response = response.strip()

        start = response.find("{")
        end = response.rfind("}")

        if start == -1 or end == -1:
            raise ValueError("No JSON found in Gemini response.")

        response = response[start:end + 1]

        try:
            return json.loads(response)

        except Exception:

          
            while response.endswith("}}"):
                response = response[:-1]
                try:
                    return json.loads(response)
                except:
                    pass

            print("\n========== RAW GEMINI RESPONSE ==========\n")
            print(response)

            raise
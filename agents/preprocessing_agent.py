from copy import deepcopy
import pandas as pd

from agents.base_agent import BaseAgent
from agents.tool_registry import TOOL_REGISTRY


class PreprocessingAgent(BaseAgent):

    def run(self, context: dict):

        df = deepcopy(context["dataframe"])
        plan = context["plan"]
        history = []

        print("\n" + "=" * 70)
        print("PREPROCESSING AGENT".center(70))
        print("=" * 70)

        df = self._execute_operations(
            df=df,
            operations=plan["preprocessing"],
            history=history,
        )

        df = self._execute_operations(
            df=df,
            operations=plan["feature_engineering"],
            history=history,
        )

        context["processed_dataframe"] = df
        context["processed_data"] = df
        context["processing_history"] = history
        for col in df.columns:
          if "date" in col.lower():
            try:
                 df[col] = pd.to_datetime(df[col], errors="coerce")
            except Exception:
             pass
        self._print_summary(history)

        return context

    def _execute_operations(
        self,
        df,
        operations,
        history,
    ):

        for operation in operations:

            op_name = operation["operation"]
            params = dict(operation.get("parameters", {}))

            print(f"\nRunning -> {op_name}")

            valid, params = self._validate_parameters(df, params)

            if not valid:
                history.append({
                    "operation": op_name,
                    "status": "skipped",
                    "reason": "Invalid Parameters",
                })
                print("Skipped")
                continue

            tool = TOOL_REGISTRY.get(op_name)

            if tool is None:
                history.append({
                    "operation": op_name,
                    "status": "skipped",
                    "reason": "Tool Not Found",
                })
                print("Tool Not Found")
                continue

            try:
                df = tool(df, **params)
                history.append({
                    "operation": op_name,
                    "status": "success",
                    "parameters": params,
                })
                print("Success")

            except Exception as e:
                history.append({
                    "operation": op_name,
                    "status": "failed",
                    "parameters": params,
                    "error": str(e),
                })
                print(e)

        return df

    def _validate_parameters(self, df, parameters):

        params = dict(parameters)

        for key, value in params.items():

            if isinstance(value, list):
                filtered = []

                for item in value:
                    if isinstance(item, str):
                        if item in df.columns:
                            filtered.append(item)
                    else:
                        filtered.append(item)

                params[key] = filtered

            elif isinstance(value, str):

                reserved = {
                    "mean",
                    "median",
                    "mode",
                    "most_frequent",
                    "standard",
                    "robust",
                    "minmax",
                }

                if value in reserved:
                    continue

                if value not in df.columns:
                    return False, params

        return True, params

    def _print_summary(self, history):

        success = sum(h["status"] == "success" for h in history)
        skipped = sum(h["status"] == "skipped" for h in history)
        failed = sum(h["status"] == "failed" for h in history)

        print("\n" + "=" * 70)
        print("PREPROCESSING SUMMARY".center(70))
        print("=" * 70)

        print(f"Successful Operations : {success}")
        print(f"Skipped Operations    : {skipped}")
        print(f"Failed Operations     : {failed}")

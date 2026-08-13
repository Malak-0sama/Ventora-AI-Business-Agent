from fastapi import FastAPI, UploadFile, File, HTTPException
import pandas as pd
import traceback

from core.workflow import AgentWorkflow

app = FastAPI(
    title="Business AI Agent API",
    version="1.0.0"
)


@app.get("/")
def home():
    return {
        "message": "Business AI Agent API is running successfully."
    }


def load_uploaded_csv(file):

    encodings = [
        "utf-8",
        "utf-8-sig",
        "cp1252",
        "latin1",
    ]

    for enc in encodings:

        file.file.seek(0)

        try:
            return pd.read_csv(
                file.file,
                encoding=enc
            )

        except UnicodeDecodeError:
            continue

    raise ValueError("Cannot read uploaded CSV.")


@app.post("/analyze")
async def analyze_dataset(file: UploadFile = File(...)):

    try:

        print("=" * 70)
        print("NEW REQUEST")
        print("=" * 70)

        df = load_uploaded_csv(file)

        print("CSV Loaded Successfully")

        workflow = AgentWorkflow()

        context = workflow.run(df)

        print("Workflow Finished Successfully")

        response = {

            "filename": file.filename,

            "dataset": {
                "rows": len(df),
                "columns": len(df.columns),
                "column_names": list(df.columns)
            },

            "schema": context.get("schema"),

            "plan": context.get("plan"),

            "best_model": context.get("best_model"),

            "insights_report": context.get("insights_report"),
        }

        if "evaluation_results" in context:

            evaluation = {}

            for name, result in context["evaluation_results"].items():

                if name.startswith("_"):
                    continue

                evaluation[name] = {

                    "status": result.get("status"),

                    "train_time": result.get("train_time"),

                    "metrics": result.get("metrics"),

                    "error": result.get("error")

                }

            response["evaluation_results"] = evaluation

        return response

    except Exception as e:

        traceback.print_exc()

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )
import json
import pandas as pd

from agents.model_agent import ModelAgent
from agents.schema_agent import SchemaAgent
from agents.llm_planner_agent import LLMPlannerAgent
from agents.preprocessing_agent import PreprocessingAgent
from agents.insights_report_agent import InsightsReportAgent


DATASET_PATH = r"C:\Users\workstation\Desktop\business-ai-agent\uploads\Sample - Superstore.csv"


def load_dataset(path):

    encodings = [
        "utf-8",
        "utf-8-sig",
        "cp1252",
        "latin1",
    ]

    for enc in encodings:

        try:

            df = pd.read_csv(
                path,
                encoding=enc,
            )

            print(f"\nDataset loaded using {enc}")

            return df

        except UnicodeDecodeError:
            pass

    raise Exception("Cannot read dataset.")



def separator(title):

    print("\n")
    print("=" * 70)
    print(title.center(70))
    print("=" * 70)



def main():

    df = load_dataset(DATASET_PATH)

    context = {
        "dataframe": df
    }


    #######################################################
    # Schema Agent
    #######################################################

    schema_agent = SchemaAgent()

    context = schema_agent.run(context)

    schema = context["schema"]

    separator("SCHEMA SUMMARY")

    dataset = schema["dataset"]
    quality = schema["quality"]

    print("Rows :", dataset["rows"])
    print("Columns :", dataset["columns"])
    print("Numeric :", dataset["numeric_columns"])
    print("Categorical :", dataset["categorical_columns"])
    print("Datetime :", dataset["datetime_columns"])

    print()

    print("Quality :", quality["quality_score"])



    #######################################################
    # Planner Agent
    #######################################################

    planner = LLMPlannerAgent()

    context = planner.run(context)


    separator("EXECUTION PLAN")

    print(
        json.dumps(
            context["plan"],
            indent=4,
            ensure_ascii=False
        )
    )



    #######################################################
    # Preprocessing Agent
    #######################################################

    preprocessing = PreprocessingAgent()

    context = preprocessing.run(context)

    processed = context["processed_dataframe"]


    separator("PROCESSED DATASET")

    print(processed.head())

    print()

    print("Shape :", processed.shape)

    print()

    processed.info()



    #######################################################
    # Model Agent
    #######################################################

    model_agent = ModelAgent()

    context = model_agent.run(context)


    separator("BEST MODEL")

    best = context["best_model"]

    print(f"Model  : {best['model_name']}")
    print(f"Metric : {best['metric']}")
    print(f"Score  : {best['score']}")



    #######################################################
    # Evaluation Results
    #######################################################

    separator("MODEL EVALUATION")


    results = context["evaluation_results"]


    for name, result in results.items():

        if name.startswith("_"):
            continue


        print("\n" + "-" * 50)

        print(name)

        print("-" * 50)


        print("Status :", result["status"])


        if result["status"] == "failed":

            print("Error :", result["error"])

            continue


        print("Training Time :", result["train_time"])

        print()


        metrics = result["metrics"]


        for metric, value in metrics.items():

            if isinstance(value, (int, float)):

                print(f"{metric:<15}: {value:.4f}")



    #######################################################
    # Insights Report Agent
    #######################################################

    report_agent = InsightsReportAgent()

    context = report_agent.run(context)



    #######################################################
    # Final Business Report
    #######################################################

    separator("BUSINESS REPORT")


    report = context["report"]


    if isinstance(report, dict):

        print(
            json.dumps(
                report,
                indent=4,
                ensure_ascii=False
            )
        )

    else:

        print(report)



#######################################################

if __name__ == "__main__":

    main()
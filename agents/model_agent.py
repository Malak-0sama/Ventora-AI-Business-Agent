

from agents.base_agent import BaseAgent

from models.validator import DataValidator
from models.splitter import DataSplitter
from models.registry import ModelRegistry
from models.trainer import ModelTrainer
from models.evaluator import ModelEvaluator


class ModelAgent(BaseAgent):

    def __init__(self):
        self.validator = DataValidator()
        self.splitter = DataSplitter()
        self.registry = ModelRegistry()
        self.trainer = ModelTrainer()
        self.evaluator = ModelEvaluator()

    def run(self, context):

        if "processed_data" not in context:
            raise ValueError("processed_data not found in context.")

        if "plan" not in context:
            raise ValueError("plan not found in context.")

        df = context["processed_data"]
        plan = context["plan"]

        target = plan["target"]["column"]

        print("\n" + "=" * 70)
        print("MODEL AGENT")
        print("=" * 70)
        
        id_columns = ["Order ID", "Row ID"]

        existing = [col for col in id_columns if col in df.columns]

        if existing:
         df = df.drop(columns=existing)
        print("\n[1/5] Validating dataset...")
        X, y = self.validator.validate(df, target)

        print("\n[2/5] Splitting dataset...")
        split = self.splitter.split(X, y, plan)

        print("\n[3/5] Loading models...")
        models = self.registry.get_models(plan)
        print(f"Loaded {len(models)} model(s).")

        print("\n[4/5] Training...")
        training_results = self.trainer.train(models, split)
        self.trainer.summary()

        print("\n[5/5] Evaluating...")
        evaluation_results = self.evaluator.evaluate(training_results, plan)
        self.evaluator.summary()

        context["X"] = X
        context["y"] = y
        context["split"] = split
        context["models"] = models
        context["training_results"] = training_results
        context["evaluation_results"] = evaluation_results
        context["best_model"] = evaluation_results.get("_best_model")

        print("\n" + "=" * 70)
        print("MODEL AGENT FINISHED")
        print("=" * 70)

        return context

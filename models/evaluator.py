

from __future__ import annotations
from typing import Dict, Any
import numpy as np

from sklearn.metrics import (
    mean_absolute_error,
    mean_squared_error,
    r2_score,
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score,
    classification_report,
    confusion_matrix,
)


class ModelEvaluator:

    def __init__(self):
        self.results: Dict[str, Any] = {}

    def evaluate(self, training_results: Dict[str, Any], plan: Dict[str, Any]) -> Dict[str, Any]:
        task = plan["task"]["type"].lower()
        primary = plan.get("evaluation", {}).get(
            "primary_metric",
            "RMSE" if task == "regression" else "F1"
        ).upper()

        self.results = {}

        for name, result in training_results.items():

            if result["status"] != "success":
                self.results[name] = result
                continue

            model = result["model"]
            X_test = result["X_test"]
            y_true = result["y_test"]

            y_pred = model.predict(X_test)

            metrics = (
                self._regression_metrics(y_true, y_pred)
                if task == "regression"
                else self._classification_metrics(model, X_test, y_true, y_pred)
            )

            self.results[name] = {
                **result,
                "metrics": metrics
            }

        self.results["_best_model"] = self._best_model(primary)
        return self.results

    def _regression_metrics(self, y_true, y_pred):

        mse = mean_squared_error(y_true, y_pred)

        return {
            "MAE": mean_absolute_error(y_true, y_pred),
            "MSE": mse,
            "RMSE": np.sqrt(mse),
            "R2": r2_score(y_true, y_pred),
        }

    def _classification_metrics(self, model, X_test, y_true, y_pred):

        metrics = {
            "Accuracy": accuracy_score(y_true, y_pred),
            "Precision": precision_score(y_true, y_pred, average="weighted", zero_division=0),
            "Recall": recall_score(y_true, y_pred, average="weighted", zero_division=0),
            "F1": f1_score(y_true, y_pred, average="weighted", zero_division=0),
            "ConfusionMatrix": confusion_matrix(y_true, y_pred).tolist(),
            "ClassificationReport": classification_report(
                y_true,
                y_pred,
                zero_division=0,
                output_dict=True,
            ),
        }

        if hasattr(model, "predict_proba"):
            try:
                proba = model.predict_proba(X_test)
                if proba.shape[1] == 2:
                    metrics["ROC_AUC"] = roc_auc_score(y_true, proba[:, 1])
            except Exception:
                pass

        return metrics

    def _best_model(self, metric):

        candidates = []

        for name, result in self.results.items():

            if name.startswith("_"):
                continue

            if result["status"] != "success":
                continue

            value = result["metrics"].get(metric)

            if value is None:
                continue

            candidates.append((name, value))

        if not candidates:
            return None

        lower_is_better = {"RMSE", "MAE", "MSE"}

        if metric in lower_is_better:
            best = min(candidates, key=lambda x: x[1])
        else:
            best = max(candidates, key=lambda x: x[1])

        return {
            "model_name": best[0],
            "metric": metric,
            "score": best[1],
        }

    def summary(self):
        print("=" * 60)
        print("EVALUATION SUMMARY")
        print("=" * 60)

        for name, result in self.results.items():
            if name.startswith("_"):
                continue
            print(f"{name}: {result['status']}")

        print("\nBest Model:")
        print(self.results.get("_best_model"))

    def get_results(self):
        return self.results

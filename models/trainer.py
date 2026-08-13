

from __future__ import annotations
import time
import traceback
from typing import Dict, Any


class ModelTrainer:
    def __init__(self):
        self.training_results: Dict[str, Any] = {}

    def train(self, models: Dict[str, Any], split: Dict[str, Any]) -> Dict[str, Any]:
        self.training_results = {}

        for name, model in models.items():
            self.training_results[name] = self._fit(
                model_name=name,
                model=model,
                split=split
            )

        return self.training_results

    def _fit(self, model_name: str, model: Any, split: Dict[str, Any]) -> Dict[str, Any]:

        X_train = split["X_train"]
        X_test = split["X_test"]
        y_train = split["y_train"]
        y_test = split["y_test"]

        start = time.time()

        try:
            model.fit(X_train, y_train)

            train_time = round(time.time() - start, 3)

            return {
                "status": "success",
                "model_name": model_name,
                "model": model,
                "X_train": X_train,
                "X_test": X_test,
                "y_train": y_train,
                "y_test": y_test,
                "train_time": train_time,
                "error": None,
            }

        except Exception as e:
            traceback.print_exc()

            return {
                "status": "failed",
                "model_name": model_name,
                "model": None,
                "X_train": X_train,
                "X_test": X_test,
                "y_train": y_train,
                "y_test": y_test,
                "train_time": None,
                "error": str(e),
            }

    def successful_models(self):
        return {
            k: v for k, v in self.training_results.items()
            if v["status"] == "success"
        }

    def failed_models(self):
        return {
            k: v for k, v in self.training_results.items()
            if v["status"] == "failed"
        }

    def summary(self):
        success = len(self.successful_models())
        failed = len(self.failed_models())

        print("\n" + "=" * 60)
        print("TRAINING SUMMARY")
        print("=" * 60)
        print(f"Successful : {success}")
        print(f"Failed     : {failed}")

        for name, result in self.training_results.items():
            print(f"{name:30} -> {result['status']}")

    def get_results(self):
        return self.training_results

    def clear(self):
        self.training_results = {}

from agents.base_agent import BaseAgent


class PlannerAgent(BaseAgent):

    def run(self, context):

        schema = context["schema"]

        plan = self.build_plan(schema)

        context["plan"] = plan

        return context

    def build_plan(self, schema):

        dataset = schema["dataset"]

        columns = schema["columns"]

        quality = schema["quality"]

        target = self.detect_target(columns)

        task = self.detect_task(
            columns,
            target
        )

        preprocessing = self.recommend_preprocessing(
            columns,
            quality,
            task
        )

        models = self.recommend_models(task)

        metrics = self.recommend_metrics(task)

        confidence = self.calculate_target_confidence(
            target
        )

        warnings = self.build_warnings(
            dataset,
            columns,
            quality
        )

        recommendations = self.build_recommendations(
            dataset,
            columns,
            quality
        )

        reasoning = self.build_reasoning(
            target,
            task,
            models
        )

        return {

            "dataset": dataset,

            "target": target,

            "task": task,

            "preprocessing": preprocessing,

            "recommended_models": models,

            "evaluation_metrics": metrics,

            "warnings": warnings,

            "recommendations": recommendations,

            "reasoning": reasoning,

            "confidence": confidence

        }

    def detect_target(self, columns):

     candidates = []

     for column_name, metadata in columns.items():

        if metadata["is_identifier"]:
            continue

        if metadata["is_constant"]:
            continue

        score, reasons = self.score_target_column(
            column_name,
            metadata
        )

        candidates.append({

            "column": column_name,

            "score": score,

            "reasons": reasons

        })

     if len(candidates) == 0:

        return None

     candidates.sort(
        key=lambda x: x["score"],
        reverse=True
    )

     best = candidates[0]

     return best

    def score_target_column(
    
    self,
    column_name,
    metadata
):

     score = 0

     reasons = []

     column = column_name.lower()

    
     keywords = {

        "target": 12,
        "label": 12,
        "class": 12,
        "price": 10,
        "sale": 10,
        "sales": 10,
        "profit": 10,
        "income": 10,
        "revenue": 10,
        "cost": 8,
        "amount": 8,
        "value": 7,
        "score": 6,
        "rating": 6,
        "y": 5

    }

     for keyword, points in keywords.items():

        if keyword in column:

            score += points

            reasons.append(
                f"Matched keyword '{keyword}' (+{points})"
            )

            break

    
     semantic = metadata["semantic_type"]

     if semantic == "numeric":

        score += 2

        reasons.append(
            "Numeric column (+2)"
        )

     elif semantic == "categorical":

        score += 1

        reasons.append(
            "Categorical column (+1)"
        )

    
     if metadata["missing_ratio"] == 0:

        score += 2

        reasons.append(
            "No missing values (+2)"
        )

   
     score += 3

     reasons.append(
        "Candidate column (+3)"
    )

    
     ratio = metadata["unique_ratio"]

     if semantic == "numeric":

        if ratio > 0.30:

            score += 2

            reasons.append(
                "Continuous values (+2)"
            )

     elif semantic == "categorical":

        if ratio < 0.20:

            score += 2

            reasons.append(
                "Discrete values (+2)"
            )

     return score, reasons

    def detect_task(
    self,
    columns,
    target
):

     if target is None:

        return {

            "type": "clustering",

            "reason": "No suitable target column found."

        }

     target_column = target["column"]

     metadata = columns[target_column]

     semantic = metadata["semantic_type"]

     unique_ratio = metadata["unique_ratio"]

     unique_count = metadata["unique_count"]

   
     if semantic == "numeric":

        if unique_ratio > 0.30:

            return {

                "type": "regression",

                "reason": "Target is numeric with many unique values."

            }

        return {

            "type": "classification",

            "reason": "Target is numeric with limited unique values."

        }

    
     if semantic == "categorical":

        if unique_count <= 30:

            return {

                "type": "classification",

                "reason": "Target is categorical."

            }

        return {

            "type": "clustering",

            "reason": "Categorical target has very high cardinality."

        }

    
     if semantic == "datetime":

        return {

            "type": "time_series",

            "reason": "Target is datetime."

        }

     return {

        "type": "unknown",

        "reason": "Unable to determine task."

    }

    def calculate_target_confidence(
    self,
    target
):

     if target is None:

        return 0.0

     max_score = 20

     confidence = target["score"] / max_score

     confidence = min(
        confidence,
        1.0
    )

     return round(
        confidence,
        2
    )

    def recommend_preprocessing(
    self,
    columns,
    quality,
    task
):

     steps = []

    
     if quality["missing_cells"] > 0:

        steps.append(
            "Handle Missing Values"
        )

     categorical_exists = any(

        column["semantic_type"] == "categorical"

        for column in columns.values()

    )

     if categorical_exists:

        steps.append(
            "Encode Categorical Features"
        )

     datetime_exists = any(

        column["semantic_type"] == "datetime"

        for column in columns.values()

    )

     if datetime_exists:

        steps.append(
            "Extract Datetime Features"
        )

     if task["type"] in [

        "regression",

        "classification"

    ]:

        steps.append(
            "Scale Numeric Features"
        )

   
     outliers_exist = any(

        column["has_outliers"]

        for column in columns.values()

    )

     if outliers_exist:

        steps.append(
            "Handle Outliers"
        )

     return steps

    def recommend_models(
    self,
    task
):

     if task["type"] == "regression":

        return [

            "Random Forest Regressor",

            "XGBoost Regressor",

            "LightGBM Regressor"

        ]

     if task["type"] == "classification":

        return [

            "Random Forest Classifier",

            "XGBoost Classifier",

            "LightGBM Classifier"

        ]

     if task["type"] == "clustering":

        return [

            "K-Means",

            "DBSCAN",

            "Hierarchical Clustering"

        ]

     if task["type"] == "time_series":

        return [

            "Prophet",

            "ARIMA",

            "LSTM"

        ]

     return []

    def recommend_metrics(
    self,
    task
):

     if task["type"] == "regression":

        return [

            "MAE",

            "RMSE",

            "R² Score"

        ]

     if task["type"] == "classification":

        return [

            "Accuracy",

            "Precision",

            "Recall",

            "F1 Score",

            "ROC AUC"

        ]

     if task["type"] == "clustering":

        return [

            "Silhouette Score",

            "Davies-Bouldin Index"

        ]

     if task["type"] == "time_series":

        return [

            "MAE",

            "RMSE",

            "MAPE"

        ]

     return []

    def build_reasoning(
    self,
    target,
    task,
    models
):

     reasoning = []

     if target is not None:

        reasoning.append(
            f"Selected target column: {target['column']}"
        )

        reasoning.extend(
            target["reasons"]
        )

     reasoning.append(
        f"Detected task: {task['type']}"
    )

     reasoning.append(
        task["reason"]
    )

     reasoning.append(

        "Recommended models: "

        + ", ".join(models)

    )

     return reasoning

    def build_warnings(
    self,
    dataset,
    columns,
    quality
):

     warnings = []

    
     if quality["missing_cells"] > 0:

        warnings.append(
            "Dataset contains missing values."
        )

  
     if quality["duplicate_rows"] > 0:

        warnings.append(
            "Dataset contains duplicate rows."
        )

     if any(

        column["has_outliers"]

        for column in columns.values()

    ):

        warnings.append(
            "Outliers detected in one or more numeric columns."
        )

   
     if quality["quality_score"] < 80:

        warnings.append(
            "Dataset quality is below the recommended threshold."
        )

     return warnings

    def build_recommendations(
    self,
    dataset,
    columns,
    quality
):

     recommendations = []

     if quality["missing_cells"] > 0:

        recommendations.append(
            "Handle missing values before training."
        )

     if any(

        column["has_outliers"]

        for column in columns.values()

    ):

        recommendations.append(
            "Consider handling outliers."
        )

     if any(

        column["semantic_type"] == "categorical"

        for column in columns.values()

    ):

        recommendations.append(
            "Encode categorical features."
        )

     if any(

        column["semantic_type"] == "datetime"

        for column in columns.values()

    ):

        recommendations.append(
            "Extract useful datetime features."
        )

     if dataset["rows"] > 100000:

        recommendations.append(
            "Large dataset detected. Prefer scalable algorithms."
        )

     return recommendations


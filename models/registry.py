

from sklearn.linear_model import (
    LinearRegression,
    LogisticRegression
)

from sklearn.ensemble import (
    RandomForestRegressor,
    RandomForestClassifier,
    ExtraTreesRegressor,
    ExtraTreesClassifier
)

from sklearn.tree import (
    DecisionTreeRegressor,
    DecisionTreeClassifier
)

from sklearn.svm import (
    SVR,
    SVC
)

from xgboost import (
    XGBRegressor,
    XGBClassifier
)

from lightgbm import (
    LGBMRegressor,
    LGBMClassifier
)

from catboost import (
    CatBoostRegressor,
    CatBoostClassifier
)


class ModelRegistry:

    RANDOM_STATE = 42

    
    # Regression Models
   

    REGRESSION_MODELS = {

        "LinearRegression":
            lambda:
                LinearRegression(),

        "RandomForestRegressor":
            lambda:
                RandomForestRegressor(
                    random_state=42
                ),

        "ExtraTreesRegressor":
            lambda:
                ExtraTreesRegressor(
                    random_state=42
                ),

        "DecisionTreeRegressor":
            lambda:
                DecisionTreeRegressor(
                    random_state=42
                ),

        "SVR":
            lambda:
                SVR(),

        "XGBoost":
            lambda:
                XGBRegressor(
                    random_state=42,
                    verbosity=0
                ),

        "LightGBM":
            lambda:
                LGBMRegressor(
                    random_state=42,
                    verbose=-1
                ),

        "CatBoostRegressor":
            lambda:
                CatBoostRegressor(
                    random_seed=42,
                    verbose=False
                )

    }

    
    # Classification Models
    

    CLASSIFICATION_MODELS = {

        "LogisticRegression":
            lambda:
                LogisticRegression(
                    random_state=42,
                    max_iter=1000
                ),

        "RandomForestClassifier":
            lambda:
                RandomForestClassifier(
                    random_state=42
                ),

        "ExtraTreesClassifier":
            lambda:
                ExtraTreesClassifier(
                    random_state=42
                ),

        "DecisionTreeClassifier":
            lambda:
                DecisionTreeClassifier(
                    random_state=42
                ),

        "SVC":
            lambda:
                SVC(
                    probability=True
                ),

        "XGBoost":
            lambda:
                XGBClassifier(
                    random_state=42,
                    verbosity=0
                ),

        "LightGBM":
            lambda:
                LGBMClassifier(
                    random_state=42,
                    verbose=-1
                ),

        "CatBoostClassifier":
            lambda:
                CatBoostClassifier(
                    random_seed=42,
                    verbose=False
                )

    }

   
    # Get Models
    

    @classmethod
    def get_models(cls, plan):

        task = plan["task"]["type"].lower()

        recommendations = plan["recommended_models"]

        loaded_models = {}

        if task == "regression":

            registry = cls.REGRESSION_MODELS

        elif task == "classification":

            registry = cls.CLASSIFICATION_MODELS

        else:

            raise ValueError(
                f"Unsupported task type : {task}"
            )

        for model in recommendations:

            model_name = model["name"]

            if model_name not in registry:

                print(
                    f"Warning : {model_name} not supported."
                )

                continue

            loaded_models[model_name] = registry[
                model_name
            ]()

        if len(loaded_models) == 0:

            raise ValueError(
                "No valid models were loaded."
            )

        return loaded_models

    # Show Available Models
    

    @classmethod
    def available_models(cls):

        return {

            "Regression": list(
                cls.REGRESSION_MODELS.keys()
            ),

            "Classification": list(
                cls.CLASSIFICATION_MODELS.keys()
            )

        }
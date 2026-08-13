import json


def build_planner_prompt(schema: dict) -> str:

    schema_json = json.dumps(schema, indent=4)

    return f"""
You are a Senior Machine Learning Architect and Data Scientist.

Your task is to analyze the dataset schema and generate a COMPLETE machine learning execution plan.

Dataset Schema:

{schema_json}

====================================================
GENERAL RULES
====================================================

1. Return ONLY valid JSON.
2. Do NOT use markdown.
3. Do NOT write explanations outside JSON.
4. The JSON must be directly parseable using json.loads().
5. Every preprocessing step MUST be represented as an operation.
6. Every feature engineering step MUST be represented as an operation.
7. Every operation MUST contain:
   - operation
   - parameters
8. Never invent column names.
9. Use only columns that exist in the provided schema.

====================================================
AVAILABLE PREPROCESSING OPERATIONS
====================================================

DROP_COLUMNS

CONVERT_DATETIME

FILL_MISSING_VALUES

REMOVE_DUPLICATES

ONE_HOT_ENCODING

LABEL_ENCODING

TARGET_ENCODING

FREQUENCY_ENCODING

STANDARD_SCALER

MINMAX_SCALER

ROBUST_SCALER

LOG_TRANSFORM

REMOVE_OUTLIERS

====================================================
AVAILABLE FEATURE ENGINEERING OPERATIONS
====================================================

CREATE_SHIPPING_DELAY

EXTRACT_YEAR

EXTRACT_MONTH

EXTRACT_DAY

EXTRACT_DAY_OF_WEEK

EXTRACT_QUARTER

CREATE_UNIT_PRICE

CREATE_INTERACTION_FEATURE

CREATE_RATIO_FEATURE

====================================================
MANDATORY PREPROCESSING RULES
====================================================

These rules are REQUIRED.

1. Every datetime column MUST first use CONVERT_DATETIME.

2. After converting datetime columns, extract useful features when appropriate.

3. Every categorical feature used for training MUST be encoded.

4. Never leave any feature with dtype object or category before model training.

5. Use ONE_HOT_ENCODING for low-cardinality categorical columns.

6. Use FREQUENCY_ENCODING or TARGET_ENCODING for high-cardinality categorical columns.

7. Identifier columns that do not carry predictive information must be removed.

Examples:
- Row ID
- Customer ID
- Product ID
- Order ID

8. Do NOT remove target columns.

9. The final processed dataset MUST contain only numeric features (except the target if necessary).

10. Every preprocessing operation must include all required parameters.

11. Do NOT recommend preprocessing operations that are unnecessary.

====================================================
MODEL SELECTION RULES
====================================================

- Detect automatically whether the task is:
  - Regression
  - Classification
  - Clustering

- Recommend the best models for the detected task.

- Prioritize robust tree-based models whenever appropriate.

====================================================
OUTPUT FORMAT
====================================================

{{
    "target": {{
        "column": "...",
        "reason": "..."
    }},

    "task": {{
        "type": "...",
        "reason": "..."
    }},

    "preprocessing": [

        {{
            "operation": "DROP_COLUMNS",
            "parameters": {{
                "columns": []
            }}
        }},

        {{
            "operation": "CONVERT_DATETIME",
            "parameters": {{
                "columns": []
            }}
        }},

        {{
            "operation": "ONE_HOT_ENCODING",
            "parameters": {{
                "columns": []
            }}
        }}

    ],

    "feature_engineering": [

        {{
            "operation": "CREATE_SHIPPING_DELAY",
            "parameters": {{
                "order_date": "",
                "ship_date": ""
            }}
        }}

    ],

    "recommended_models":[

        {{
            "name":"LightGBM",
            "priority":1
        }},

        {{
            "name":"CatBoost",
            "priority":2
        }},

        {{
            "name":"RandomForest",
            "priority":3
        }}

    ],

    "evaluation":{{
        "metrics":[
            "MAE",
            "RMSE",
            "R2"
        ],
        "validation":"TimeSeriesSplit"
    }},

    "warnings":[
        "..."
    ],

    "recommendations":[
        "..."
    ],

    "reasoning":[
        "..."
    ],

    "confidence":0.95
}}

====================================================
FINAL CHECKLIST
====================================================

Before returning the JSON, verify that:

- Every datetime column is handled.
- Every categorical column is either encoded or dropped.
- No object columns remain for model training.
- All operations have valid parameters.
- The JSON is syntactically valid.
- The preprocessing pipeline can be executed directly without modification.

Return ONLY the JSON.
"""
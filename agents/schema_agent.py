import pandas as pd
from agents.base_agent import BaseAgent
from utils.column_utils import (
    detect_column_type,
    unique_ratio,
    missing_ratio,
    has_outliers,
    is_identifier,
    is_constant,
    column_memory,
)
class SchemaAgent(BaseAgent):

    def run(self, context):

        df = context["dataframe"]

        context["schema"] = self.build_schema(df)

        return context

    def build_schema(self, df):

        return {
            "dataset": self.build_dataset_metadata(df),
            "columns": self.build_columns_metadata(df),
            "quality": self.build_quality_metadata(df),
        }

    def build_dataset_metadata(self, df):

        
        datetime_cols = [
            col for col in df.columns
            if detect_column_type(df[col]) == "datetime"
        ]
        datetime_set = set(datetime_cols)

        categorical_like = df.select_dtypes(
            include=["object", "category", "string", "str"]
        ).columns
        categorical_cols = [
            col for col in categorical_like if col not in datetime_set
        ]

        return {

            "rows": len(df),

            "columns": len(df.columns),

            "memory_usage_mb": float(round(
                df.memory_usage(deep=True).sum() / (1024 ** 2),
                2,
            )),

            "duplicate_rows": int(df.duplicated().sum()),

            "numeric_columns": len(
                df.select_dtypes(include="number").columns
            ),

            "categorical_columns": len(categorical_cols),

            "datetime_columns": len(datetime_cols),
        }

    def build_columns_metadata(self, df):

        columns = {}

        for column in df.columns:

            series = df[column]

            columns[column] = {

                "dtype": str(series.dtype),

                "semantic_type": detect_column_type(series),

                "nullable": bool(series.isnull().any()),

                "missing_count": int(series.isnull().sum()),

                "missing_ratio": round(
                    missing_ratio(series),
                    4,
                ),

                "unique_count": int(
                    series.nunique(dropna=True)
                ),

                "unique_ratio": round(
                    unique_ratio(series),
                    4,
                ),

                "memory_bytes": column_memory(series),

                "is_constant": is_constant(series),

                "has_outliers": has_outliers(series),

                "is_identifier": is_identifier(
                    column,
                    series,
                ),

                "sample_values": (
                    series.dropna()
                    .astype(str)
                    .head(5)
                    .tolist()
                ),
            }

        return columns

    def build_quality_metadata(self, df):

        total_missing = int(
            df.isnull().sum().sum()
        )

        total_cells = len(df) * len(df.columns)

        return {

            "missing_cells": total_missing,

            "missing_ratio": round(
                total_missing / total_cells,
                4,
            ),

            "duplicate_rows": int(
                df.duplicated().sum()
            ),

            "quality_score": self.calculate_quality_score(df),
        }

    def calculate_quality_score(self, df):

        score = 100

        missing = (
            df.isnull().sum().sum()
            / (len(df) * len(df.columns))
        )

        duplicates = (
            df.duplicated().sum()
            / len(df)
        )

        constant = sum(
            is_constant(df[col])
            for col in df.columns
        ) / len(df.columns)

        score -= missing * 40

        score -= duplicates * 30

        score -= constant * 30

        return round(max(score, 0), 2)
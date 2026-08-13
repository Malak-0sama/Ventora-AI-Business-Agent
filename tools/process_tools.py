from __future__ import annotations
import numpy as np
import category_encoders as ce
from pathlib import Path
from sklearn.preprocessing import (
    StandardScaler,
    MinMaxScaler,
    RobustScaler,
)

import pandas as pd


class DataProcessingTools:
    
    @staticmethod
    def load_csv(path: str) -> pd.DataFrame:
        """
        Load CSV file.
        """
        return pd.read_csv(path)

    @staticmethod
    def load_excel(path: str) -> pd.DataFrame:
        """
        Load Excel file.
        """
        return pd.read_excel(path)

    @staticmethod
    def save_csv(df: pd.DataFrame, path: str) -> None:
        
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        df.to_csv(path, index=False)

    @staticmethod
    def copy(df: pd.DataFrame) -> pd.DataFrame:
        
        return df.copy()

    @staticmethod
    def drop_columns(
        df: pd.DataFrame,
        columns: list[str],
    ) -> pd.DataFrame:
        
        return df.drop(columns=columns, errors="ignore")

    @staticmethod
    def drop_rows(
        df: pd.DataFrame,
        rows: list[int],
    ) -> pd.DataFrame:
        
        return df.drop(index=rows, errors="ignore")

    @staticmethod
    def remove_duplicates(
        df: pd.DataFrame,
    ) -> pd.DataFrame:
        
        return df.drop_duplicates()

    @staticmethod
    def rename_columns(
        df: pd.DataFrame,
        mapping: dict,
    ) -> pd.DataFrame:
        
        return df.rename(columns=mapping)

    @staticmethod
    def change_column_type(
        df: pd.DataFrame,
        column: str,
        dtype: str,
    ) -> pd.DataFrame:
      
        df = df.copy()
        df[column] = df[column].astype(dtype)
        return df

    @staticmethod
    def sort_values(
        df: pd.DataFrame,
        by: str,
        ascending: bool = True,
    ) -> pd.DataFrame:
        
        return df.sort_values(by=by, ascending=ascending)

    @staticmethod
    def sample(
        df: pd.DataFrame,
        n: int = 5,
    ) -> pd.DataFrame:
        
        return df.sample(n=min(n, len(df)), random_state=42)

    @staticmethod
    def reset_index(
        df: pd.DataFrame,
    ) -> pd.DataFrame:
        
        return df.reset_index(drop=True)

    @staticmethod
    def fill_missing_mean(
     df: pd.DataFrame,
    columns: list[str],
) -> pd.DataFrame:

     df = df.copy()

     for col in columns:

        if col in df.columns:
            df[col] = df[col].fillna(df[col].mean())

     return df

    @staticmethod
    def fill_missing_median(
     df: pd.DataFrame,
     columns: list[str],
) -> pd.DataFrame:

     df = df.copy()

     for col in columns:

        if col in df.columns:
            df[col] = df[col].fillna(df[col].median())

     return df

    @staticmethod
    def fill_missing_mode(
    df: pd.DataFrame,
    columns: list[str],
) -> pd.DataFrame:

     df = df.copy()

     for col in columns:

        if col in df.columns:

            mode = df[col].mode()

            if not mode.empty:
                df[col] = df[col].fillna(mode.iloc[0])

     return df

    @staticmethod
    def drop_missing(
    df: pd.DataFrame,
) -> pd.DataFrame:

     return df.dropna()


    @staticmethod
    def convert_datetime(
    df: pd.DataFrame,
    columns: list[str],
) -> pd.DataFrame:

     df = df.copy()

     for col in columns:

        if col in df.columns:

            df[col] = pd.to_datetime(
                df[col],
                errors="coerce",
            )

     return df


    @staticmethod
    def extract_datetime_features(
    df: pd.DataFrame,
    column: str,
) -> pd.DataFrame:

     df = df.copy()

     if column not in df.columns:
        return df

     df[f"{column}_year"] = df[column].dt.year

     df[f"{column}_month"] = df[column].dt.month

     df[f"{column}_day"] = df[column].dt.day

     df[f"{column}_dayofweek"] = df[column].dt.dayofweek

     df[f"{column}_quarter"] = df[column].dt.quarter

     return df

    @staticmethod
    def create_shipping_delay(
    df: pd.DataFrame,
    order_date: str,
    ship_date: str,
) -> pd.DataFrame:

     df = df.copy()

     if (
        order_date in df.columns
        and ship_date in df.columns
    ):

        df["Shipping Delay"] = (
            df[ship_date] - df[order_date]
        ).dt.days

     return df



    @staticmethod
    def standard_scale(
    df: pd.DataFrame,
    columns: list[str],
) -> pd.DataFrame:

     df = df.copy()

     scaler = StandardScaler()

     df[columns] = scaler.fit_transform(df[columns])

     return df


    @staticmethod
    def minmax_scale(
    df: pd.DataFrame,
    columns: list[str],
) -> pd.DataFrame:

     df = df.copy()

     scaler = MinMaxScaler()

     df[columns] = scaler.fit_transform(df[columns])

     return df


    @staticmethod
    def robust_scale(
    df: pd.DataFrame,
    columns: list[str],
) -> pd.DataFrame:

     df = df.copy()

     scaler = RobustScaler()

     df[columns] = scaler.fit_transform(df[columns])

     return df


    @staticmethod
    def log_transform(
    df: pd.DataFrame,
    columns: list[str],
) -> pd.DataFrame:

     df = df.copy()

     for col in columns:

        if col in df.columns:

            df[col] = np.log1p(df[col])

     return df


    @staticmethod
    def remove_outliers_iqr(
    df: pd.DataFrame,
    columns: list[str],
) -> pd.DataFrame:

     df = df.copy()

     for col in columns:

        if col not in df.columns:
            continue

        Q1 = df[col].quantile(0.25)

        Q3 = df[col].quantile(0.75)

        IQR = Q3 - Q1

        lower = Q1 - 1.5 * IQR

        upper = Q3 + 1.5 * IQR

        df = df[
            (df[col] >= lower)
            &
            (df[col] <= upper)
        ]

     return df


    @staticmethod
    def clip_outliers(
    df: pd.DataFrame,
    columns: list[str],
) -> pd.DataFrame:

     df = df.copy()

     for col in columns:

        if col not in df.columns:
            continue

        Q1 = df[col].quantile(.25)

        Q3 = df[col].quantile(.75)

        IQR = Q3 - Q1

        lower = Q1 - 1.5 * IQR

        upper = Q3 + 1.5 * IQR

        df[col] = df[col].clip(lower, upper)

     return df

    @staticmethod
    def create_unit_price(
    df,
    sales,
    quantity,
):
     df = df.copy()

     df["Unit Price"] = df[sales] / df[quantity]

     return df


    @staticmethod
    def create_ratio_feature(
    df: pd.DataFrame,
    numerator: str,
    denominator: str,
    new_column: str,
) -> pd.DataFrame:

     df = df.copy()

     df[new_column] = (
        df[numerator]
        /
        df[denominator]
    )

     return df


    @staticmethod
    def create_difference_feature(
    df: pd.DataFrame,
    col1: str,
    col2: str,
    new_column: str,
) -> pd.DataFrame:

     df = df.copy()

     df[new_column] = (
        df[col1]
        -
        df[col2]
    )

     return df


    @staticmethod
    def create_interaction_feature(
    df: pd.DataFrame,
    column_1: str,
    column_2: str,
) -> pd.DataFrame:

     df = df.copy()

     new_name = f"{column_1}_{column_2}"

     df[new_name] = (
        df[column_1]
        *
        df[column_2]
    )

     return df


    @staticmethod
    def one_hot_encode(
     df,
    columns: list[str],
):
     """
     One Hot Encoding
     """

     columns = [c for c in columns if c in df.columns]

     if not columns:
        return df

     return pd.get_dummies(
        df,
        columns=columns,
        drop_first=True,
    )

    @staticmethod
    def target_encode(
     df,
    columns: list[str],
    target: str,
):
     """
    Target Encoding
    """

     columns = [c for c in columns if c in df.columns]

     if not columns:
        return df

     encoder = ce.TargetEncoder(
        cols=columns,
    )

     df[columns] = encoder.fit_transform(
        df[columns],
        df[target],
    )

     return df

    @staticmethod
    def frequency_encode(
     df,
    columns: list[str],
):
     """
    Frequency Encoding
    """

     for col in columns:

        if col not in df.columns:
            continue

        freq = df[col].value_counts(normalize=True)

        df[col] = df[col].map(freq)

     return df


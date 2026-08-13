

import numpy as np
import pandas as pd


class DataValidator:

    @staticmethod
    def validate(df, target):

        print("\n" + "-" * 60)
        print("Validating Processed Dataset")
        print("-" * 60)

        df = df.copy()

        
        # Target Exists
        

        if target not in df.columns:

            raise ValueError(
                f"Target column '{target}' not found."
            )

        
        # Replace Infinity
       

        numeric_df = df.select_dtypes(include=np.number)

        inf_count = np.isinf(numeric_df).sum().sum()

        if inf_count > 0:

            print(f"Infinity values found : {inf_count}")

            df.replace(
                [np.inf, -np.inf],
                np.nan,
                inplace=True
            )

        
        # Missing Values
        

        missing = df.isnull().sum().sum()

        if missing > 0:

            print(f"Missing values found : {missing}")

            numeric_cols = df.select_dtypes(
                include=np.number
            ).columns

            categorical_cols = df.select_dtypes(
                exclude=np.number
            ).columns

            for col in numeric_cols:

                df[col] = df[col].fillna(
                    df[col].median()
                )

            for col in categorical_cols:

                df[col] = df[col].fillna(
                    df[col].mode()[0]
                )

        
        # Boolean Columns
        

        bool_cols = df.select_dtypes(
            include="bool"
        ).columns

        if len(bool_cols) > 0:

            print(
                f"Converting {len(bool_cols)} boolean columns..."
            )

            df[bool_cols] = df[bool_cols].astype(int)

        
        # Datetime Columns
      

        datetime_cols = df.select_dtypes(
            include=["datetime", "datetime64[ns]"]
        ).columns

        if len(datetime_cols) > 0:

            print(
                "Extracting datetime features..."
            )

            for col in datetime_cols:

                df[f"{col}_Year"] = df[col].dt.year

                df[f"{col}_Month"] = df[col].dt.month

                df[f"{col}_Day"] = df[col].dt.day

                df[f"{col}_DayOfWeek"] = (
                    df[col].dt.dayofweek
                )

            df.drop(
                columns=datetime_cols,
                inplace=True
            )

        
        # Feature / Target Split
        

        X = df.drop(columns=[target])

        y = df[target]

        
        # Final Check
        

        non_numeric = X.select_dtypes(
            exclude=np.number
        ).columns

        if len(non_numeric) > 0:

            raise ValueError(
                f"Non-numeric columns remain: "
                f"{list(non_numeric)}"
            )

        print("\nDataset Validation Passed")

        print(f"Features : {X.shape[1]}")

        print(f"Rows     : {X.shape[0]}")

        return X, y
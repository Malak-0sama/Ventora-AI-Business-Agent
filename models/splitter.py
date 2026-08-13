

from sklearn.model_selection import (
    train_test_split,
    TimeSeriesSplit
)


class DataSplitter:

    DEFAULT_TEST_SIZE = 0.20
    RANDOM_STATE = 42

    @classmethod
    def split(
        cls,
        X,
        y,
        plan
    ):

        print("\n" + "-" * 60)
        print("Splitting Dataset")
        print("-" * 60)

        task = plan["task"]["type"].lower()

        validation = (
            plan
            .get("evaluation", {})
            .get("validation", "TrainTestSplit")
        )

        validation = validation.lower()

     
        # Time Series Split
     

        if validation == "timeseriessplit":

            print("Strategy : TimeSeriesSplit")

            splitter = TimeSeriesSplit(
                n_splits=5
            )

            train_index, test_index = list(
                splitter.split(X)
            )[-1]

            X_train = X.iloc[train_index]
            X_test = X.iloc[test_index]

            y_train = y.iloc[train_index]
            y_test = y.iloc[test_index]

       
        # Classification
      

        elif task == "classification":

            print("Strategy : Stratified Train/Test Split")

            X_train, X_test, y_train, y_test = train_test_split(

                X,

                y,

                test_size=cls.DEFAULT_TEST_SIZE,

                random_state=cls.RANDOM_STATE,

                stratify=y

            )

        
        # Regression
      

        else:

            print("Strategy : Train/Test Split")

            X_train, X_test, y_train, y_test = train_test_split(

                X,

                y,

                test_size=cls.DEFAULT_TEST_SIZE,

                random_state=cls.RANDOM_STATE

            )

        print()

        print(f"Train Samples : {len(X_train)}")

        print(f"Test Samples  : {len(X_test)}")

        print()

        return {

            "X_train": X_train,

            "X_test": X_test,

            "y_train": y_train,

            "y_test": y_test

        }

   
    # Summary
    

    @staticmethod
    def summary(split):

        print("\n" + "-" * 60)

        print("Split Summary")

        print("-" * 60)

        print()

        print("X Train :", split["X_train"].shape)

        print("X Test  :", split["X_test"].shape)

        print("y Train :", split["y_train"].shape)

        print("y Test  :", split["y_test"].shape)
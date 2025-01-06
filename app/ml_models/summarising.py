import json

import numpy as np
import pandas as pd


def summerise_cluster(
    file_path: str, filename_feature_descriptions_csv: str, filename_feature_descriptions_json: str
):
    df = pd.read_csv(file_path)

    if "amount_paid" in df.columns:
        df["amount_paid"] = pd.to_numeric(df["amount_paid"], errors="coerce")

    if "created_date" in df.columns:
        df.drop(columns=["created_date"], inplace=True)

    cat_features = [feature for feature in df.columns if df[feature].dtype == "O"]
    num_features = [
        feature
        for feature in df.columns
        if df[feature].dtype in ["int32", "int64", "float64", "float32"]
    ]

    output_data = []

    for cat in cat_features:
        value_counts = df[cat].value_counts()
        top_values = value_counts.head(3)

        for idx, (value, count) in enumerate(top_values.items()):
            output_data.append(
                {
                    "Feature": cat,
                    "Type": "Categorical",
                    "Statistic": f"Top {idx + 1} Value",
                    "Value": value,
                    "Count": count,
                    "Mean": np.nan,
                    "Sum": np.nan,
                }
            )

        if len(value_counts) > 1:
            lowest_value = value_counts.iloc[-1]
            output_data.append(
                {
                    "Feature": cat,
                    "Type": "Categorical",
                    "Statistic": "Lowest Value",
                    "Value": value_counts.index[-1],
                    "Count": lowest_value,
                    "Mean": np.nan,
                    "Sum": np.nan,
                }
            )

    for num in num_features:
        unique_count = len(df[num].unique())

        if unique_count > 25:

            mean_value = df[num].mean()
            sum_value = df[num].sum()
            mean_count = df[num].count()

            output_data.append(
                {
                    "Feature": num,
                    "Type": "Numerical (>25 unique)",
                    "Statistic": "Mean",
                    "Value": "",
                    "Count": mean_count,
                    "Mean": mean_value,
                    "Sum": np.nan,
                }
            )
            output_data.append(
                {
                    "Feature": num,
                    "Type": "Numerical (>25 unique)",
                    "Statistic": "Sum",
                    "Value": "",
                    "Count": mean_count,
                    "Mean": np.nan,
                    "Sum": sum_value,
                }
            )
        else:
            value_counts = df[num].value_counts()
            top_values = value_counts.head(3)

            for idx, (value, count) in enumerate(top_values.items()):
                output_data.append(
                    {
                        "Feature": num,
                        "Type": "Numerical (<=25 unique)",
                        "Statistic": f"Top {idx + 1} Value",
                        "Value": value,
                        "Count": count,
                        "Mean": np.nan,
                        "Sum": np.nan,
                    }
                )

            if len(value_counts) > 1:
                lowest_value = value_counts.iloc[-1]
                output_data.append(
                    {
                        "Feature": num,
                        "Type": "Numerical (<=25 unique)",
                        "Statistic": "Lowest Value",
                        "Value": value_counts.index[-1],
                        "Count": lowest_value,
                        "Mean": np.nan,
                        "Sum": np.nan,
                    }
                )

    output_df = pd.DataFrame(output_data)
    output_df.to_csv(filename_feature_descriptions_csv, index=False)
    output_df.to_json(filename_feature_descriptions_json, orient="records", lines=True)
    json_data = output_df.to_json(orient="records")
    return json.loads(json_data)

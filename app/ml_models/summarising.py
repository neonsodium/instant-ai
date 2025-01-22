import json

import numpy as np
import pandas as pd


def summerise_cluster(
    file_path: str, filename_feature_descriptions_csv: str, filename_feature_descriptions_json: str
):
    """
    Process a given cluster CSV file to generate descriptive statistics for
    categorical and numerical features, and save the results as CSV and JSON.

    Args:
    - file_path (str): Path to the cluster CSV file.

    Saves:
    - 'feature_descriptions.csv': CSV file with feature descriptions.
    - 'feature_descriptions.json': JSON file with feature descriptions.
    """

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
        total_count = len(df[cat])
        top_values = value_counts.head(3)

        for idx, (value, count) in enumerate(top_values.items()):
            output_data.append(
                {
                    "Feature": cat,
                    "Type": "Categorical",
                    "Statistic": f"Top {idx + 1} Value",
                    "Value": value,
                    "Count": count,
                    "Percentage": f"{(count / total_count) * 100:.2f}%",
                    "Mean": np.nan,
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
                    "Percentage": f"{(lowest_value / total_count) * 100:.2f}%",
                    "Mean": np.nan,
                }
            )

    for num in num_features:
        mean_value = df[num].mean()
        total_count = df[num].count()
        output_data.append(
            {
                "Feature": num,
                "Type": "Numerical",
                "Statistic": "Mean",
                "Value": "",
                "Count": total_count,
                "Percentage": "",
                "Mean": mean_value,
            }
        )

    output_df = pd.DataFrame(output_data)
    output_df.to_csv(filename_feature_descriptions_csv, index=False)
    output_df.to_json(filename_feature_descriptions_json, orient="records", lines=True)
    json_data = output_df.to_json(orient="records")
    return json.loads(json_data)

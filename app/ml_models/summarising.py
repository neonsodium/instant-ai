import numpy as np
import pandas as pd


def summerise_cluster(
    file_path: str,
    filename_feature_descriptions_csv: str,
    filename_feature_descriptions_json: str,
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
                }
            )

    for num in num_features:
        unique_count = len(df[num].unique())

        if unique_count > 25:

            mean_value = df[num].mean()
            mean_count = df[num].count()
            output_data.append(
                {
                    "Feature": num,
                    "Type": "Numerical (>25 unique)",
                    "Statistic": "Mean",
                    "Value": "",
                    "Count": mean_count,
                    "Mean": mean_value,
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
                    }
                )

    output_df = pd.DataFrame(output_data)
    output_df.to_csv(filename_feature_descriptions_csv, index=False)
    output_df.to_json(filename_feature_descriptions_json, orient="records", lines=True)


# import pandas as pd
# import numpy as np


# def summary_cluster(file_path):
#     """
#     Process a given cluster CSV file to generate descriptive statistics for
#     categorical and numerical features, and save the results as CSV and JSON.

#     Args:
#     - file_path (str): Path to the cluster CSV file.

#     Saves:
#     - 'feature_descriptions.csv': CSV file with feature descriptions.
#     - 'feature_descriptions.json': JSON file with feature descriptions.
#     """
#     # Load the data
#     df = pd.read_csv(file_path)

#     # Convert 'amount_paid' to numerical
#     if "amount_paid" in df.columns:
#         df["amount_paid"] = pd.to_numeric(df["amount_paid"], errors="coerce")

#     # Drop 'created_date' column if it exists
#     if "created_date" in df.columns:
#         df.drop(columns=["created_date"], inplace=True)

#     # Identify categorical and numerical features
#     cat_features = [feature for feature in df.columns if df[feature].dtype == "O"]
#     num_features = [
#         feature
#         for feature in df.columns
#         if df[feature].dtype in ["int32", "int64", "float64", "float32"]
#     ]

#     # Initialize lists to store data for CSV and JSON
#     output_data = []

#     # Process categorical features with value counts
#     for cat in cat_features:
#         value_counts = df[cat].value_counts()
#         top_values = value_counts.head(3)

#         # Display top 3 highest value counts
#         for idx, (value, count) in enumerate(top_values.items()):
#             output_data.append(
#                 {
#                     "Feature": cat,
#                     "Type": "Categorical",
#                     "Statistic": f"Top {idx + 1} Value",
#                     "Value": value,
#                     "Count": count,
#                     "Mean": np.nan,
#                 }
#             )

#         # Display lowest value count if available
#         if len(value_counts) > 1:
#             lowest_value = value_counts.iloc[-1]
#             output_data.append(
#                 {
#                     "Feature": cat,
#                     "Type": "Categorical",
#                     "Statistic": "Lowest Value",
#                     "Value": value_counts.index[-1],
#                     "Count": lowest_value,
#                     "Mean": np.nan,
#                 }
#             )

#     # Process numerical features based on unique value counts
#     for num in num_features:
#         unique_count = len(df[num].unique())

#         if unique_count > 25:
#             # If unique values are greater than 25, calculate and store the mean and its count
#             mean_value = df[num].mean()
#             mean_count = df[num].count()
#             output_data.append(
#                 {
#                     "Feature": num,
#                     "Type": "Numerical (>25 unique)",
#                     "Statistic": "Mean",
#                     "Value": "",
#                     "Count": mean_count,
#                     "Mean": mean_value,
#                 }
#             )
#         else:
#             # If unique values are 25 or fewer, store the top 3 and lowest value counts
#             value_counts = df[num].value_counts()
#             top_values = value_counts.head(3)

#             for idx, (value, count) in enumerate(top_values.items()):
#                 output_data.append(
#                     {
#                         "Feature": num,
#                         "Type": "Numerical (<=25 unique)",
#                         "Statistic": f"Top {idx + 1} Value",
#                         "Value": value,
#                         "Count": count,
#                         "Mean": np.nan,
#                     }
#                 )

#             if len(value_counts) > 1:
#                 lowest_value = value_counts.iloc[-1]
#                 output_data.append(
#                     {
#                         "Feature": num,
#                         "Type": "Numerical (<=25 unique)",
#                         "Statistic": "Lowest Value",
#                         "Value": value_counts.index[-1],
#                         "Count": lowest_value,
#                         "Mean": np.nan,
#                     }
#                 )

#     # Convert to DataFrame and save as CSV and JSON
#     output_df = pd.DataFrame(output_data)
#     output_csv_path = "feature_descriptions.csv"
#     output_json_path = "feature_descriptions.json"
#     output_df.to_csv(output_csv_path, index=False)
#     output_df.to_json(output_json_path, orient="records", lines=True)

#     print(f"Descriptions saved to {output_csv_path} and {output_json_path}")

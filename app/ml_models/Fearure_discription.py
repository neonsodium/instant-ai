import numpy as np
import pandas as pd


def process_and_describe_features(
    file_path,
    csv_output="feature_descriptions.csv",
    json_output="feature_descriptions.json",
):
    """
    Processes a dataset to describe categorical and numerical features, including their value counts and statistics.

    Parameters:
        file_path (str): Path to the input CSV file.
        csv_output (str): Path to save the output CSV file.
        json_output (str): Path to save the output JSON file.

    Outputs:
        Saves processed feature descriptions to specified CSV and JSON files.

    Example usage:
        process_and_describe_features( "cluster1.csv", "feature_descriptions.csv", "feature_descriptions.json" )
    """
    # Load the data
    df = pd.read_csv(file_path)

    # Convert 'amount_paid' to numerical if it exists
    if "amount_paid" in df.columns:
        df["amount_paid"] = pd.to_numeric(df["amount_paid"], errors="coerce")

    # Drop 'created_date' column if it exists
    if "created_date" in df.columns:
        df.drop(columns=["created_date"], inplace=True)

    # Identify categorical and numerical features
    cat_features = [feature for feature in df.columns if df[feature].dtype == "O"]
    num_features = [
        feature
        for feature in df.columns
        if df[feature].dtype in ["int32", "int64", "float64", "float32"]
    ]

    # Initialize lists to store data for CSV and JSON
    output_data = []

    # Process categorical features with value counts
    for cat in cat_features:
        value_counts = df[cat].value_counts()
        top_values = value_counts.head(3)

        # Add top 3 highest value counts
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

        # Add lowest value count if available
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

    # Process numerical features based on unique value counts
    for num in num_features:
        unique_count = len(df[num].unique())

        if unique_count > 25:
            # For numerical features with >25 unique values, add mean and count
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
            # For numerical features with <=25 unique values, add top 3 and lowest value counts
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

    # Convert the output to a DataFrame
    output_df = pd.DataFrame(output_data)

    # Save the DataFrame to CSV and JSON
    output_df.to_csv(csv_output, index=False)
    output_df.to_json(json_output, orient="records", lines=True)

    print(f"Descriptions saved to {csv_output} and {json_output}")

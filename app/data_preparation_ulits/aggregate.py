import pandas as pd


def aggregate_columns_by_date(df, date_column="created_date"):
    # Check if df is a DataFrame
    if not isinstance(df, pd.DataFrame):
        raise ValueError("The provided input is not a valid pandas DataFrame")

    # Automatically detect numeric columns (excluding the date column)
    numeric_columns = df.select_dtypes(include=["number"]).columns.tolist()

    # Exclude the date column from the list of numeric columns
    numeric_columns = [col for col in numeric_columns if col != date_column]

    # Define the aggregation dictionary with 'sum' for each numeric column
    agg_dict = {col: "sum" for col in numeric_columns}

    # Group by the date column and aggregate using the defined dictionary
    aggregated_df = df.groupby(date_column).agg(agg_dict).reset_index()

    return aggregated_df

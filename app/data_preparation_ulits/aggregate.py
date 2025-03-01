import pandas as pd


def aggregate_columns_by_date_old(df, date_column="created_date"):
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


def aggregate_columns_by_date(df, date_column="Order_Date"):
    """
    Aggregates the specified numeric columns of the DataFrame by summing them,
    grouped by the date column.

    Parameters:
        df (pd.DataFrame): The input DataFrame.
        date_column (str): The column name to group by.

    Returns:
        pd.DataFrame: The aggregated DataFrame with summed values.
    """
    # Debug: Print all columns in the DataFrame
    print("Available columns in the DataFrame:", df.columns.tolist())

    if date_column not in df.columns:
        print(f"DEBUG: Column '{date_column}' is NOT present in the DataFrame!")
    else:
        print(f"DEBUG: Column '{date_column}' is present in the DataFrame.")

    # Debug: Check for duplicate columns
    duplicates = df.columns[df.columns.duplicated()].tolist()
    if duplicates:
        print("DEBUG: Duplicate columns found:", duplicates)
    else:
        print("DEBUG: No duplicate columns found.")

    # Automatically detect numeric columns (excluding the date column)
    numeric_columns = df.select_dtypes(include=["number"]).columns.tolist()
    numeric_columns = [col for col in numeric_columns if col != date_column]
    print("DEBUG: Numeric columns to aggregate:", numeric_columns)

    # Define the aggregation dictionary with 'sum' for each numeric column
    agg_dict = {col: "sum" for col in numeric_columns}

    # Force the grouping key to be a Series constructed from the column's values
    grouping_series = pd.Series(df[date_column].values, name=date_column)
    print("DEBUG: Type of grouping_series:", type(grouping_series))

    # Group by the date column (using the Series) and aggregate using the defined dictionary
    aggregated_df = df.groupby(grouping_series).agg(agg_dict).reset_index()

    # Ensure the grouping key column is named as expected
    if aggregated_df.columns[0] != date_column:
        aggregated_df = aggregated_df.rename(columns={aggregated_df.columns[0]: date_column})

    return aggregated_df

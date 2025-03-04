import pandas as pd


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
    # Automatically detect numeric columns (excluding the date column)
    numeric_columns = df.select_dtypes(include=["number"]).columns.tolist()
    numeric_columns = [col for col in numeric_columns if col != date_column]

    # Group by the date column and sum only the numeric columns
    aggregated_df = df.groupby(date_column)[numeric_columns].sum().reset_index()

    return aggregated_df

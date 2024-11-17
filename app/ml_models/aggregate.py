import pandas as pd


def aggregate_columns_by_date(df, date_column="created_date"):
    """
    Aggregates the specified numeric columns of the DataFrame by summing them, grouped by the date column.

    Parameters:
        df (pd.DataFrame): The input DataFrame.
        date_column (str): The column name to group by (default is 'created_date').

    Returns:
        pd.DataFrame: The aggregated DataFrame with summed values.

    Example Usage:
        aggregated_df = aggregate_columns_by_date(df)
    """

    numeric_columns = df.select_dtypes(include=["number"]).columns.tolist()
    numeric_columns = [col for col in numeric_columns if col != date_column]
    agg_dict = {col: "sum" for col in numeric_columns}
    aggregated_df = df.groupby(date_column).agg(agg_dict).reset_index()
    return aggregated_df

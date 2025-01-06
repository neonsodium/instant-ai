import numpy as np
import pandas as pd


def validate_df(df):
    """
    Validates the input DataFrame and reports data quality issues.
    If no issues are found, confirms that the data is clean.

    Parameters:
        df (pd.DataFrame): The DataFrame to validate.

    Returns:
        dict: A dictionary containing validation reports.
    """
    report = {}

    missing_values = df.isnull().sum()
    missing_values = missing_values[missing_values > 0]
    if not missing_values.empty:
        report["Missing Values"] = missing_values.to_dict()

    mixed_type_columns = []
    for col in df.columns:
        types_in_col = df[col].dropna().apply(lambda x: type(x).__name__)
        unique_types = types_in_col.unique()
        if len(unique_types) > 1:

            mixed_type_columns.append(col)
            type_counts = types_in_col.value_counts()
            total_non_null = len(types_in_col)
            data_type_info = {}
            for dtype, count in type_counts.items():
                percentage = (count / total_non_null) * 100
                data_type_info[dtype] = {"count": count, "percentage": percentage}
            key = f'Mixed Types in Column "{col}"'
            report[key] = {"Data Types": data_type_info}
    if mixed_type_columns:
        for col in mixed_type_columns:
            key = f'Mixed Types in Column "{col}"'
            data_types = report[key]["Data Types"]
            for dtype, info in data_types.items():
                count = info["count"]
                percentage = info["percentage"]
                if count <= 10:
                    rows_with_dtype = df[
                        df[col].dropna().apply(lambda x: type(x).__name__) == dtype
                    ].index.tolist()

    duplicate_rows = df[df.duplicated()]
    if not duplicate_rows.empty:
        report["Duplicate Rows"] = {
            "Row Numbers": duplicate_rows.index.tolist(),
            "Count": duplicate_rows.shape[0],
        }
        if duplicate_rows.shape[0] <= 10:
            pass
        else:
            percentage = (duplicate_rows.shape[0] / df.shape[0]) * 100

    constant_columns = [col for col in df.columns if df[col].nunique(dropna=False) == 1]
    if constant_columns:
        report["Constant Columns"] = constant_columns

    return report

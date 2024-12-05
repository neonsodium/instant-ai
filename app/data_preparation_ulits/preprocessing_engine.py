import numpy as np
import pandas as pd


def validate_dataset(df):
    """
    Validates the input DataFrame and reports data quality issues.
    If no issues are found, confirms that the data is clean.

    Parameters:
        df (pd.DataFrame): The DataFrame to validate.

    Returns:
        dict: A dictionary containing validation reports.
    """
    report = {}
    issues_found = False  # Flag to track if any issues are found

    # 1. Missing Values
    missing_values = df.isnull().sum()
    missing_values = missing_values[missing_values > 0]
    if not missing_values.empty:
        issues_found = True
        report["Missing Values"] = missing_values.to_dict()
        print("Missing Values per Column:")
        print(missing_values)
    else:
        print("No missing values found.")

    # 2. Mixed Data Types
    mixed_type_columns = []
    for col in df.columns:
        # Get the data types in the column
        types_in_col = df[col].dropna().apply(lambda x: type(x).__name__)
        unique_types = types_in_col.unique()
        if len(unique_types) > 1:
            issues_found = True
            # Collect columns with mixed data types
            mixed_type_columns.append(col)
            # Count occurrences of each data type
            type_counts = types_in_col.value_counts()
            total_non_null = len(types_in_col)
            # Prepare data type information
            data_type_info = {}
            for dtype, count in type_counts.items():
                percentage = (count / total_non_null) * 100
                data_type_info[dtype] = {"count": count, "percentage": percentage}
            # Store in report
            key = f'Mixed Types in Column "{col}"'
            report[key] = {"Data Types": data_type_info}
    if mixed_type_columns:
        print("\nColumns with Mixed Data Types:")
        for col in mixed_type_columns:
            key = f'Mixed Types in Column "{col}"'
            data_types = report[key]["Data Types"]
            total_types = len(data_types)
            total_rows = df.shape[0]
            print(f"- {col} has {total_types} data types:")
            for dtype, info in data_types.items():
                count = info["count"]
                percentage = info["percentage"]
                # Decide whether to show row numbers or percentages
                if count <= 10:
                    # Get row indices for this data type
                    rows_with_dtype = df[
                        df[col].dropna().apply(lambda x: type(x).__name__) == dtype
                    ].index.tolist()
                    print(
                        f"  - Data type '{dtype}' occurs {count} times at rows: {rows_with_dtype}"
                    )
                else:
                    print(
                        f"  - Data type '{dtype}' occurs {count} times ({percentage:.2f}%)"
                    )
    else:
        print("\nNo columns with mixed data types found.")

    # 3. Duplicate Rows
    duplicate_rows = df[df.duplicated()]
    if not duplicate_rows.empty:
        issues_found = True
        report["Duplicate Rows"] = {
            "Row Numbers": duplicate_rows.index.tolist(),
            "Count": duplicate_rows.shape[0],
        }
        print(f"\nDuplicate Rows Found: {duplicate_rows.shape[0]}")
        if duplicate_rows.shape[0] <= 10:
            print(f"Row Numbers: {duplicate_rows.index.tolist()}")
        else:
            percentage = (duplicate_rows.shape[0] / df.shape[0]) * 100
            print(f"Duplicate rows constitute {percentage:.2f}% of the dataset.")
    else:
        print("\nNo duplicate rows found.")

    # 4. Constant Columns
    constant_columns = [col for col in df.columns if df[col].nunique(dropna=False) == 1]
    if constant_columns:
        issues_found = True
        report["Constant Columns"] = constant_columns
        print("\nColumns with a Single Unique Value (Constant Columns):")
        for col in constant_columns:
            print(f"- {col}")
    else:
        print("\nNo constant columns found.")

    # Final Clean Data Check
    if not issues_found:
        print("\nData is clean and can proceed for analysis.")

    return report


# Example Usage:
# df = pd.read_csv('your_dataset.csv')
# validation_report = validate_dataset(df)


# df = pd.read_csv("JB_DATA_CLEAN.csv")


# validation_report = validate_dataset(df)

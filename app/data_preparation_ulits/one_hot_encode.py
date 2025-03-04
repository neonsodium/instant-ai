import pickle

import pandas as pd
from sklearn.preprocessing import OneHotEncoder


def one_hot_encode_data(
    input_file_path: str, output_one_hot_mapping_path: str, output_file_path: str
):
    df = pd.read_csv(input_file_path)
    df_encoded, encoder = apply_one_hot_encoding(df)
    df_encoded.to_csv(output_file_path, index=False)
    with open(output_one_hot_mapping_path, "wb") as file:
        pickle.dump(encoder, file)


def apply_one_hot_encoding(df, datetime_threshold=0.9, low_unique_threshold=15):
    import pandas as pd
    from sklearn.preprocessing import OneHotEncoder

    categorical_columns = []
    for col in df.select_dtypes(include=["object"]).columns:
        dt_series = pd.to_datetime(df[col], errors="coerce")
        # If most values can be converted to datetime...
        if dt_series.notna().sum() / len(df[col]) >= datetime_threshold:
            # ...but there are few unique dates (e.g., a month column), treat it as categorical.
            if dt_series.nunique() < low_unique_threshold:
                categorical_columns.append(col)
            # Otherwise, assume it is a genuine datetime and skip encoding.
        else:
            categorical_columns.append(col)

    if categorical_columns:
        encoder = OneHotEncoder(sparse_output=False)
        encoded_data = encoder.fit_transform(df[categorical_columns])
        # Create new feature names: take the part after the underscore.
        new_feature_names = [
            name.split("_")[-1] for name in encoder.get_feature_names_out(categorical_columns)
        ]

        # Ensure feature names are unique
        if len(set(new_feature_names)) != len(new_feature_names):
            unique_names = []
            counts = {}
            for name in new_feature_names:
                if name in counts:
                    counts[name] += 1
                    unique_names.append(f"{name}_{counts[name]}")
                else:
                    counts[name] = 0
                    unique_names.append(name)
            new_feature_names = unique_names

        encoded_df = pd.DataFrame(encoded_data, columns=new_feature_names, index=df.index)
        df_encoded = pd.concat([df.drop(categorical_columns, axis=1), encoded_df], axis=1)
    else:
        df_encoded = df.copy()
        encoder = None

    return df_encoded, encoder


import numpy as np
import pandas as pd
from sklearn.preprocessing import OneHotEncoder


def prepare_data_for_feature_ranking(
    df, target_col, datetime_threshold=0.9, low_unique_threshold=15, drop_original_dates=True
):
    """
    Prepares a DataFrame for feature ranking or ML by:
      1. Converting genuine date columns to numeric ordinal columns.
      2. One-hot encoding object columns that are not genuine datetime.
      3. (Optionally) dropping the original date columns if drop_original_dates=True.
      4. Removing any remaining object columns that might still contain strings.

    Returns a fully numeric DataFrame, ready for modeling or feature ranking.

    Parameters:
    -----------
    df : pd.DataFrame
        Input DataFrame containing your features and target.
    target_col : str
        The name of the target column in df.
    datetime_threshold : float, default 0.9
        Proportion of values in a column that must be successfully parsed as dates
        to consider the column as a genuine datetime column.
    low_unique_threshold : int, default 15
        If a date-parsed column has fewer than this many unique values, it is treated
        as categorical (like months or categories).
    drop_original_dates : bool, default True
        Whether to drop the original string-based date columns after creating
        their numeric ⁠ _ordinal ⁠ versions.

    Returns:
    --------
    df_numeric : pd.DataFrame
        A DataFrame containing only numeric and one-hot encoded categorical columns,
        along with the target column.
    """

    # --- Step A: Convert genuine datetime columns to ordinal, optionally dropping the originals ---
    date_cols = []
    for col in df.select_dtypes(include=["object"]).columns:
        dt_series = pd.to_datetime(df[col], errors="coerce")
        # If col is recognized as a genuine datetime (many unique parsed values)...
        if (
            dt_series.notna().sum() / len(df[col]) >= datetime_threshold
            and dt_series.nunique() >= low_unique_threshold
        ):
            new_col = col + "_ordinal"
            df[new_col] = dt_series.map(lambda x: x.toordinal() if pd.notnull(x) else np.nan)
            date_cols.append(col)

    # Optionally drop original date columns
    if drop_original_dates:
        df.drop(columns=date_cols, inplace=True, errors="ignore")

    # --- Step B: One-hot encode the remaining object columns that are not genuine datetimes ---
    categorical_columns = []
    for col in df.select_dtypes(include=["object"]).columns:
        dt_series = pd.to_datetime(df[col], errors="coerce")
        # If it's not mostly parseable as date, or is parseable but has few unique values, treat as categorical
        if dt_series.notna().sum() / len(df[col]) >= datetime_threshold:
            if dt_series.nunique() < low_unique_threshold:
                categorical_columns.append(col)
        else:
            categorical_columns.append(col)

    if categorical_columns:
        encoder = OneHotEncoder(sparse_output=False)
        encoded_data = encoder.fit_transform(df[categorical_columns])

        # Create feature names from the encoder
        new_feature_names = []
        feature_names_out = encoder.get_feature_names_out(categorical_columns)
        for name in feature_names_out:
            # Keep only the part after the underscore for clarity
            # but remain cautious about duplicates
            category_val = name.split("_", 1)[-1]
            new_feature_names.append(category_val)

        # Ensure uniqueness if duplicates occur
        if len(set(new_feature_names)) != len(new_feature_names):
            counts = {}
            for i in range(len(new_feature_names)):
                val = new_feature_names[i]
                if val in counts:
                    counts[val] += 1
                    new_feature_names[i] = f"{val}_{counts[val]}"
                else:
                    counts[val] = 0

        encoded_df = pd.DataFrame(encoded_data, columns=new_feature_names, index=df.index)

        # Drop original categorical columns and add the encoded columns
        df = pd.concat([df.drop(categorical_columns, axis=1), encoded_df], axis=1)

    # --- Step C: Remove any remaining object columns that can't be converted to numeric ---
    # (e.g., partially missing data that wasn't dropped)
    # We'll do this except for the target if it's numeric or something else.
    # If the target is also object, convert it to numeric if possible.
    object_cols = df.select_dtypes(include=["object"]).columns.tolist()
    if target_col in object_cols:
        # Attempt to convert target to numeric
        df[target_col] = pd.to_numeric(df[target_col], errors="coerce")
        if df[target_col].isna().any():
            raise ValueError(
                f"Target column '{target_col}' could not be fully converted to numeric."
            )
        object_cols.remove(target_col)  # no longer an object col if conversion succeeded

    # Drop any other object columns that remain (these cannot be used by the model)
    if object_cols:
        df.drop(columns=object_cols, inplace=True)

    return df

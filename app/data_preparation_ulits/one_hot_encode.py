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


def apply_one_hot_encoding_OLD(df):
    """
    Applies OneHotEncoding to all object-type columns in the DataFrame.

    Parameters:
        df (pd.DataFrame): The input DataFrame.

    Returns:
        pd.DataFrame: The DataFrame with OneHotEncoded columns.
        OneHotEncoder: The fitted OneHotEncoder object for potential reverse transformation.
    Example Usage:
        df_encoded, encoder = apply_one_hot_encoding(df)
    """
    categorical_columns = df.select_dtypes(include=["object"]).columns.tolist()
    encoder = OneHotEncoder(sparse_output=False)
    encoded_data = encoder.fit_transform(df[categorical_columns])
    encoded_columns = encoder.get_feature_names_out(categorical_columns)
    encoded_df = pd.DataFrame(encoded_data, columns=encoded_columns, index=df.index)
    df_encoded = pd.concat([df.drop(categorical_columns, axis=1), encoded_df], axis=1)

    return df_encoded, encoder


def apply_one_hot_encoding(df):
    """
    Applies OneHotEncoding to all object-type columns in the DataFrame.

    Parameters:
        df (pd.DataFrame): The input DataFrame.

    Returns:
        pd.DataFrame: The DataFrame with OneHotEncoded columns.
        OneHotEncoder: The fitted OneHotEncoder object for potential reverse transformation.
    """
    # Identify categorical columns (object type)
    categorical_columns = df.select_dtypes(include=["object"]).columns.tolist()

    # Initialize the OneHotEncoder without dropping the first category
    encoder = OneHotEncoder(sparse_output=False)

    # Fit and transform the categorical columns
    encoded_data = encoder.fit_transform(df[categorical_columns])

    # Get the feature names for the encoded columns
    encoded_columns = encoder.get_feature_names_out(categorical_columns)

    # Create a DataFrame with the encoded data
    encoded_df = pd.DataFrame(encoded_data, columns=encoded_columns, index=df.index)

    # Concatenate the original DataFrame (excluding the categorical columns) with the encoded columns
    df_encoded = pd.concat([df.drop(categorical_columns, axis=1), encoded_df], axis=1)

    return df_encoded, encoder

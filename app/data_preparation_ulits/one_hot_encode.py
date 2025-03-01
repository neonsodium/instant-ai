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


def apply_one_hot_encoding(df, datetime_threshold=0.9):

    categorical_columns = []
    for col in df.select_dtypes(include=["object"]).columns:
        dt_series = pd.to_datetime(df[col], errors="coerce")
        if dt_series.notna().sum() / len(df[col]) >= datetime_threshold:
            continue
        else:
            categorical_columns.append(col)

    if categorical_columns:
        encoder = OneHotEncoder(sparse_output=False)
        encoded_data = encoder.fit_transform(df[categorical_columns])

        encoded_columns = [
            name.split("_")[-1] for name in encoder.get_feature_names_out(categorical_columns)
        ]
        encoded_df = pd.DataFrame(encoded_data, columns=encoded_columns, index=df.index)

        df_encoded = pd.concat([df.drop(categorical_columns, axis=1), encoded_df], axis=1)
    else:
        df_encoded = df.copy()
        encoder = None

    return df_encoded, encoder

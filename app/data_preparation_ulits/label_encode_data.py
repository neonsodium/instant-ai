import pickle

import pandas as pd
from pandas import DataFrame
from sklearn.preprocessing import LabelEncoder


def label_encode_data(
    input_csv_file_path: str,
    output_label_encoded_path: str,
    output_labels_path: str,
    output_label_encoded_mapping_path: str,
):
    df = pd.read_csv(input_csv_file_path)
    df_encoded, label_encoders, label_encoded_mapping = apply_label_encoding(df)
    df_encoded.to_csv(output_label_encoded_path, index=False)
    with open(output_labels_path, "wb") as file:
        pickle.dump(label_encoders, file)
    label_encoded_mapping.to_csv(output_label_encoded_mapping_path, index=False)


def apply_label_encoding(df):
    """
    Apply label encoding
        encoded_df, encoders = apply_label_encoding(df)
    """
    object_columns = df.select_dtypes(include=["object"]).columns
    label_encoders = {}

    for col in object_columns:
        le = LabelEncoder()
        df[col] = le.fit_transform(df[col].astype(str))
        label_encoders[col] = dict(zip(le.classes_, le.transform(le.classes_)))

    label_encoded_mapping = pd.DataFrame.from_dict(label_encoders, orient="index").T
    label_encoded_mapping = label_encoded_mapping.reset_index().rename(
        columns={"index": "Original"}
    )

    return df, label_encoders, label_encoded_mapping


def reverse_label_encoding(df, label_encoders) -> DataFrame:
    """
    Reverse label encoding:
        decoded_df = reverse_label_encoding(encoded_df, label_encoders)
    """
    for col, mapping in label_encoders.items():
        reverse_mapping = {v: k for k, v in mapping.items()}
        df[col] = df[col].map(reverse_mapping)

    return df

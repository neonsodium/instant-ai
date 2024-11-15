import pickle

import numpy as np
import pandas as pd
from sklearn.preprocessing import LabelEncoder


def label_encode_data(
    input_csv_file_path: str,
    output_label_encoded_path: str,
    output_label_encoded_mapping_path: str,
):
    df = pd.read_csv(input_csv_file_path)
    object_columns = df.select_dtypes(include=["object"]).columns
    label_encoders = {}
    for col in object_columns:
        le = LabelEncoder()
        df[col] = le.fit_transform(df[col].astype(str))
        label_encoders[col] = dict(zip(le.classes_, le.transform(le.classes_)))
    df.to_csv(output_label_encoded_path, index=False)

    for col, mapping in label_encoders.items():
        reverse_mapping = {v: k for k, v in mapping.items()}
        df[col] = df[col].map(reverse_mapping)

    label_encoded_mapping = pd.DataFrame.from_dict(label_encoders, orient="index").T
    label_encoded_mapping = label_encoded_mapping.reset_index().rename(
        columns={"index": "Original"}
    )
    label_encoded_mapping.to_csv(output_label_encoded_mapping_path, index=False)

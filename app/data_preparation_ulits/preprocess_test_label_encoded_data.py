import pandas as pd


def preprocess_label_encoded_data(input_file_path: str, output_file_path: str):
    df = pd.read_csv(input_file_path)
    df["created_date"] = pd.to_datetime(df["# created_date"])
    df.sort_values(by="created_date", inplace=True)
    df.drop("created_date", axis=1, inplace=True)
    df["transaction_type_id"].fillna(df["transaction_type_id"].mode()[0], inplace=True)
    df["branch_type"].fillna(df["branch_type"].mode()[0], inplace=True)
    df.to_csv(output_file_path, index=False)

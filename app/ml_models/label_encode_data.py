from sklearn.preprocessing import LabelEncoder
from sklearn.impute import SimpleImputer
import numpy as np
import pandas as pd

def label_encode_data(input_file_path: str,output_file_path: str):
    # Load data
    df = pd.read_csv(input_file_path)
    for col in df.select_dtypes(include=['object']).columns:
        df[col] = LabelEncoder().fit_transform(df[col].astype(str))
    pd.DataFrame(
        SimpleImputer(missing_values=np.nan, strategy='mean').fit_transform(df), 
        columns=df.columns
    ).to_csv(output_file_path, index=False)

# generate_label_encode_data("sales_data.csv","encoded_file.csv")
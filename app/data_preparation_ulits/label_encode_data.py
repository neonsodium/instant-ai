from sklearn.preprocessing import LabelEncoder
from sklearn.impute import SimpleImputer
import numpy as np
import pandas as pd
import pickle

def label_encode_data(input_csv_file_path: str,output_label_encoded_path: str,output_rev_label_encoded_path: str):
    df = pd.read_csv(input_csv_file_path)
    object_columns = df.select_dtypes(include=['object']).columns
    for col in object_columns:
        le = LabelEncoder()
        df[col] = le.fit_transform(df[col].astype(str))
        label_encoders = {}
        label_encoders[col] = dict(zip(le.classes_, le.transform(le.classes_)))  # Save original names
        with open(output_rev_label_encoded_path, "wb") as file:
            pickle.dump(label_encoders, file)
    
    df.to_csv(output_label_encoded_path,index=False)


# label_encode_data("sales_data.csv","encoded_file.csv")

# for col in df.select_dtypes(include=['object']).columns:
#     df[col] = LabelEncoder().fit_transform(df[col].astype(str))

# pd.DataFrame(
#     SimpleImputer(missing_values=np.nan, strategy='mean').fit_transform(df), 
#     columns=df.columns
# ).to_csv(output_file_path, index=False)
#Code for converting it into label encoding 
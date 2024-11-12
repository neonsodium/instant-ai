from sklearn.preprocessing import OneHotEncoder
import pandas as pd

def one_hot_encode_data(input_file_path: str,output_file_path: str):
    df = pd.read_csv(input_file_path)
    categorical_columns =  df.select_dtypes(include=['object']).columns
    encoder = OneHotEncoder(sparse_output=False)
    encoded_data = encoder.fit_transform(df[categorical_columns])
    encoded_columns = encoder.get_feature_names_out(categorical_columns)
    encoded_df = pd.DataFrame(encoded_data, columns=encoded_columns, index=df.index)
    df_one_hot_encoded = pd.concat([df, encoded_df], axis=1)
    df_one_hot_encoded.drop(categorical_columns, axis=1, inplace=True)
    df_one_hot_encoded.drop('Number_of_Months_avrmurthy83@gmail.com',axis=1,inplace=True)
    df_one_hot_encoded.to_csv(output_file_path, index=False)
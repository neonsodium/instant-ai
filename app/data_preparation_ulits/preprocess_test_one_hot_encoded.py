import pandas as pd

def preprocess_one_hot_data(input_file_path: str,output_file_path: str):
    df = pd.read_csv(input_file_path)
    df['amount_paid'] = pd.to_numeric(df['amount_paid'], errors='coerce').astype('Int64')
    df['share_percentage'] = pd.to_numeric(df['share_percentage'], errors='coerce').astype('Int64')
    df['primus_amount'] = pd.to_numeric(df['primus_amount'], errors='coerce').astype('Int64')
    df['Renewal_Amount'] = pd.to_numeric(df['Renewal_Amount'], errors='coerce').astype('Int64')
    df['transaction_type_id'] = df['transaction_type_id'].astype('object')
    df.drop('Membership_expiry_date',axis=1,inplace=True)
    df.to_csv(output_file_path, index=False)
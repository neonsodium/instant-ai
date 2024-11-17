import pandas as pd


def drop_columns_df(
    input_file_path: str,
    output_file_path: str,
    drop_list_columns: list = [
        "branch_email",
        "Message_Status",
        "User_Name",
        "transaction",
        "id.1",
        "Month_Last_Date",
        "TAX_TYPE",
        "GST_AMOUNT",
        "SGST_AMOUNT",
        "CGST_AMOUNT",
        "IGST_AMOUNT",
        "created_by",
        "id",
        "Member_Name",
        "email",
        "transaction_date",
        "payable_amount",
        "reversed",
        "referred_by",
        "locality",
        "last_card_number",
        "security_deposit.1",
        "subscription_id",
        "Unnamed: 55",
        "TAX_STATE",
    ],
):
    df = pd.read_csv(input_file_path)
    df["created_date"] = pd.to_datetime(df["# created_date"])
    df.drop(
        drop_list_columns,
        axis=1,
        inplace=True,
    )
    df.to_csv(output_file_path, index=False)


"""            [
            "branch_email",
            "Message_Status",
            "User_Name",
            "transaction",
            "id.1",
            "Month_Last_Date",
            "TAX_TYPE",
            "GST_AMOUNT",
            "SGST_AMOUNT",
            "CGST_AMOUNT",
            "IGST_AMOUNT",
            "created_by",
            "id",
            "Member_Name",
            "email",
            "transaction_date",
            "payable_amount",
            "reversed",
            "referred_by",
            "locality",
            "last_card_number",
            "security_deposit.1",
            "subscription_id",
            "Unnamed: 55",
            "TAX_STATE",
        ]
        """

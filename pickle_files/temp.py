import pandas as pd

# Sample data
data = {
    "Feature": [
        "reading_fee_paid",
        "Number_of_Months",
        "amount_paid",
        "Coupon_Discount",
        "payable_amount",
        "num_books",
        "id",
        "reading_fee_adjustment_amount",
        "Transaction_Year",
        "subscription_id",
        "transaction_type_id",
        "dailysales",
        "member_card",
        "created_name",
        "transaction",
        "magazine_fee_paid",
        "created_by",
        "transaction_branch_id",
        "security_deposit",
        "member_branch_id",
        "Percentage_Share",
        "Transaction_Month",
        "display_name",
        "share_percentage",
        "num_magazine",
        "Membership_expiry_date",
        "email",
        "Member_Name",
        "branch_name",
        "last_card_number",
    ],
    "Final_Rank": [
        3.000000,
        3.333333,
        3.400000,
        3.666667,
        4.250000,
        9.000000,
        9.250000,
        11.000000,
        11.666667,
        12.500000,
        12.666667,
        13.500000,
        14.500000,
        14.750000,
        15.666667,
        16.333333,
        16.500000,
        18.666667,
        19.000000,
        19.333333,
        19.666667,
        20.000000,
        22.333333,
        24.333333,
        24.750000,
        25.333333,
        26.000000,
        26.000000,
        26.333333,
        26.333333,
    ],
}

# Create the DataFrame
df = pd.DataFrame(data)

# Features to select
features_to_select = [
    "over_due_adjustment_amount",
    "security_deposit",
    "Percentage_Share",
    "Coupon_Discount",
    "reading_fee_paid",
    "Number_of_Months",
]

# Filter the DataFrame
filtered_df = df[df["Feature"].isin(features_to_select)]

# Save the filtered DataFrame as a pickle file
filtered_df.to_pickle("filtered_dataframe.pkl")

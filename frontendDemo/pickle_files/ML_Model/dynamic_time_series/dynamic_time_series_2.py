import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
import matplotlib.pyplot as plt
from sklearn.preprocessing import LabelEncoder
from prophet import Prophet
from sklearn.metrics import mean_absolute_error


df=pd.read_csv('sales_data.csv')
df.head()

regressors= ['id', 'Transaction_Year', 'Transaction_Year', 'subscription_id', 'Transaction_Month']
columns_keep= ['# created_date', 'id', 'created_by', 'transaction_branch_id', 'transaction_type_id',
               'amount_paid', 'Coupon_Discount', 'magazine_fee_paid', 'payable_amount',
               'reading_fee_paid', 'reversed', 'over_due_adjustment_amount', 'last_card_number',
               'primus_amount', 'adjustment_amount', 'security_deposit', 'Percentage_Share',
               'subscription_id', 'member_branch_id', 'transaction', 'Transaction_Month', 'Transaction_Year',
               'created_name', 'branch_name', 'branch_type', 'member_card', 'Member_Name', 'email',
               'Number_of_Months', 'display_name', 'Renewal_Amount', 'Message_Status', 'Membership_expiry_date', 'User_Name']
df_fin=df[columns_keep]

df_fin['created_date'] = pd.to_datetime(df['# created_date'],format="%d-%m-%Y")

daily_data=df_fin.groupby('created_date').agg({
    'id': 'first',
    'created_by': 'first',
    'transaction_branch_id': lambda x: x.mode()[0],
    'transaction_type_id': 'first',
    'amount_paid': 'sum',
    'Coupon_Discount': 'sum',
    'magazine_fee_paid': 'sum',
    'payable_amount': 'sum',
    'reading_fee_paid': 'sum',
    'reversed': 'first',
    'over_due_adjustment_amount': 'sum',
    'last_card_number': 'first',
    'primus_amount': 'sum',
    'adjustment_amount': 'sum',
    'security_deposit': 'sum',
    'Percentage_Share': 'sum',
    'subscription_id': 'first',
    'member_branch_id': 'first',
    'transaction': 'first',
    'Transaction_Month': 'first',
    'Transaction_Year': 'first',
    'created_name': 'first',
    'branch_name': 'first',
    'branch_type': 'first',
    'member_card': 'first',
    'Member_Name': 'first',
    'email': 'first',
    'Number_of_Months': lambda x: x.mode()[0],  # Most frequent value
    'display_name': 'first',
    'Renewal_Amount': 'sum',
    'Message_Status': 'first',
    'Membership_expiry_date': 'first',
    'User_Name': 'first'
}).reset_index()

daily_data.rename(columns={'created_date': 'ds', 'magazine_fee_paid': 'y'}, inplace=True)

model = Prophet()
for regressor in regressors:
    model.add_regressor(regressor)


import pandas as pd

# Create and fit the model
model = Prophet(daily_seasonality=True, weekly_seasonality=True, yearly_seasonality=True)

# List to hold the valid numeric regressors
valid_regressors = []

# Check the regressors and add only numeric ones
for regressor in regressors:
    if pd.api.types.is_numeric_dtype(daily_data[regressor]):
        model.add_regressor(regressor)
        valid_regressors.append(regressor)

# Display which regressors are being used
print(f"Using regressors: {valid_regressors}")

# Fit the model using the selected columns
model.fit(daily_data[['ds', 'y'] + valid_regressors])



import pandas as pd
import numpy as np
from datetime import datetime

# Function to calculate historical daily averages for each month in the period
def calculate_daily_averages(df, month, year, regressors):
    # Determine the range of years in the historical data
    min_year = df['ds'].dt.year.min()
    max_year = df['ds'].dt.year.max()

    # Calculate weights dynamically based on available years
    weights = {y: 1 / (year - y + 1) for y in range(min_year, max_year + 1)}

    daily_averages = {}
    for regressor in regressors:
        daily_values = []
        for day in range(1, 32):  # Assuming up to 31 days in a month
            day_values = []
            for y, weight in weights.items():
                day_data = df[(df['ds'].dt.month == month) &
                              (df['ds'].dt.year == y) &
                              (df['ds'].dt.day == day)]

                if not day_data.empty:
                    # Check if the column is numeric before calculating the mean
                    if pd.api.types.is_numeric_dtype(day_data[regressor]):
                        day_avg = day_data[regressor].mean() * weight
                        day_values.append(day_avg)

            if day_values:
                # Convert weights.values() to a list and then sum
                total_weight = sum(weights.values())
                weighted_average = np.sum(day_values) / total_weight
            else:
                weighted_average = np.nan  # Handle cases where there is no data for that day
            daily_values.append(weighted_average)

        daily_averages[regressor] = daily_values

    return daily_averages

# Historical Data (Assume you have it in 'daily_data')
historical_data = daily_data.copy()

# Predicting for the next 3 months starting from August 2024
start_date = datetime(2024, 8, 15)
end_date = datetime(2024, 10, 31)

# Regressors(Change it according to the variable you are forecasting for, all regressors are mentioned above)


regressors_2= [ 'date_create','Membership_expiry_date', 'id','membership_start_date','dailysales','subscription_id','Transaction_Month']

regressors = regressors_2
# Generate future DataFrame for the prediction period
future_dates = pd.date_range(start=start_date, end=end_date)
future_df = pd.DataFrame({'ds': future_dates})

# Loop through each month in the prediction period
for current_month in range(start_date.month, end_date.month + 1):
    # Calculate daily averages for the current month
    daily_averages = calculate_daily_averages(historical_data, current_month, start_date.year, regressors_2)

    # Assign daily averages to the corresponding dates in future_df
    month_mask = future_df['ds'].dt.month == current_month
    for regressor in regressors:
        future_df.loc[month_mask, regressor] = daily_averages[regressor][:sum(month_mask)]

# Optional: Adjust for day of the week effect
future_df['day_of_week'] = future_df['ds'].dt.dayofweek
weekend_factor = 0.9  # Example adjustment for weekends

for regressor in regressors:
    future_df.loc[future_df['day_of_week'] >= 5, regressor] *= weekend_factor

forecast = model.predict(future_df)

# Prepare details as a DataFrame
details_df = pd.DataFrame({
    'Detail': ['Forecasting Period', 'Regressors', 'Number of Days in future_df', 'Weekend Adjustment Factor'],
    'Value': [
        f"{start_date} to {end_date}",
        ", ".join(regressors),
        len(future_df),
        weekend_factor
    ]
})

combined_df = pd.concat([details_df, future_df, forecast], axis=1)


combined_file = 'reading_fee_paid/forecast_data_1.csv'
combined_df.to_csv(combined_file, index=False)


import plotly.graph_objects as go

# Create the figure
fig = go.Figure()

# Add forecast line
fig.add_trace(go.Scatter(x=forecast['ds'], y=forecast['yhat'], mode='lines', name='Forecast', line=dict(color='red')))

# Add uncertainty interval (optional)
fig.add_trace(go.Scatter(x=forecast['ds'], y=forecast['yhat_upper'], fill=None, mode='lines', line_color='red', line=dict(dash='dash'), name='Upper Bound'))
fig.add_trace(go.Scatter(x=forecast['ds'], y=forecast['yhat_lower'], fill='tonexty', mode='lines', line_color='red', line=dict(dash='dash'), name='Lower Bound'))

# Update layout
fig.update_layout(title='Forecasted Values with Prophet',
                  xaxis_title='Date',
                  yaxis_title='Forecasted Value',
                  legend_title='Legend')
fig.show()

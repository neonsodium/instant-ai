import numpy as np 
import pandas as pd
import matplotlib.pyplot as plt
from prophet import Prophet
from datetime import datetime

df=pd.read_csv('amount_paid.csv')
df['created_date'] = pd.to_datetime(df['# created_date'],format="%d-%m-%Y")


daily_data = df.groupby('created_date').agg({
    'created_by': 'first',
    'transaction_type_id': 'first',
    'over_due_adjustment_amount': 'sum',
    'security_deposit': 'sum',
    'Percentage_Share': 'sum',
    'member_branch_id': 'first',
    'branch_name': 'first',
    'branch_type': 'first',
    'Member_Name': 'first',
    'Coupon_Discount': 'sum',
    'transaction_branch_id': lambda x: x.mode()[0],  
    'reading_fee_paid': 'sum',
    'amount_paid': 'sum',
    'Number_of_Months': lambda x: x.mode()[0]
}).reset_index()

daily_data.rename(columns={'created_date': 'ds', 'amount_paid': 'y'}, inplace=True)
regressors = ['over_due_adjustment_amount', 'security_deposit', 'Percentage_Share',
              'Coupon_Discount', 'reading_fee_paid', 'Number_of_Months']

model = Prophet()
for regressor in regressors:
    model.add_regressor(regressor)


model.fit(daily_data[['ds', 'y'] + regressors])


# Create and fit the model
model = Prophet(daily_seasonality=True, weekly_seasonality=True, yearly_seasonality=True)
for regressor in regressors:
    model.add_regressor(regressor)
model.fit(daily_data[['ds', 'y'] + regressors])




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
start_date = datetime(2024, 5, 15)
end_date = datetime(2024, 10, 31)

# Regressors
regressors = ['over_due_adjustment_amount', 'security_deposit', 'Percentage_Share', 'Coupon_Discount', 'reading_fee_paid', 'Number_of_Months']

# Generate future DataFrame for the prediction period
future_dates = pd.date_range(start=start_date, end=end_date)
future_df = pd.DataFrame({'ds': future_dates})

# Loop through each month in the prediction period
for current_month in range(start_date.month, end_date.month + 1):
    # Calculate daily averages for the current month
    daily_averages = calculate_daily_averages(historical_data, current_month, start_date.year, regressors)
    
    # Assign daily averages to the corresponding dates in future_df
    month_mask = future_df['ds'].dt.month == current_month
    for regressor in regressors:
        future_df.loc[month_mask, regressor] = daily_averages[regressor][:sum(month_mask)]

# Optional: Adjust for day of the week effect
future_df['day_of_week'] = future_df['ds'].dt.dayofweek
weekend_factor = 0.9  # Example adjustment for weekends

for regressor in regressors:
    future_df.loc[future_df['day_of_week'] >= 5, regressor] *= weekend_factor

# Now you can use 'future_df' with the Prophet model to predict values for the next 3 months
forecast = model.predict(future_df)


import matplotlib.pyplot as plt

# Use Prophet's built-in function to plot components
fig = model.plot_components(forecast)
plt.show()

import plotly.graph_objs as go

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

# Show the plot
fig.show()

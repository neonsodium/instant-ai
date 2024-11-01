import numpy as np
import pandas as pd
from prophet import Prophet
from datetime import datetime
import matplotlib.pyplot as plt
import plotly.graph_objs as go
import pickle

# Pure function to load and preprocess data
def load_and_preprocess_data(file_path):
    df = pd.read_csv(file_path)
    df['created_date'] = pd.to_datetime(df['# created_date'], format="%d-%m-%Y")
    return df

def clean_data(df, regressors):
    # Loop through each regressor column
    for regressor in regressors:
        # Convert to numeric, forcing non-numeric values to NaN
        df[regressor] = pd.to_numeric(df[regressor], errors='coerce')
    
    # Option 1: Drop rows with NaN values in any regressor columns
    df = df.dropna(subset=regressors)
    
    # Option 2: Alternatively, you can fill NaN values with a specific value (e.g., 0)
    # df[regressors] = df[regressors].fillna(0)
    
    return df

# Pure function to aggregate daily data
def aggregate_daily_data(df,to_find):
    # daily_data = df.groupby('created_date').agg({
    #     'created_by': 'first',
    #     'transaction_type_id': 'first',
    #     'over_due_adjustment_amount': 'sum',
    #     'security_deposit': 'sum',
    #     'Percentage_Share': 'sum',
    #     'member_branch_id': 'first',
    #     'branch_name': 'first',
    #     'branch_type': 'first',
    #     'Member_Name': 'first',
    #     'Coupon_Discount': 'sum',
    #     'transaction_branch_id': lambda x: x.mode()[0],  
    #     'reading_fee_paid': 'sum',
    #     'amount_paid': 'sum',
    #     'Number_of_Months': lambda x: x.mode()[0]
    # }).reset_index()
    daily_data=df.groupby('created_date').agg({
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
    daily_data.rename(columns={'created_date': 'ds', to_find: 'y'}, inplace=True)
    return daily_data

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

# Pure function to calculate daily averages
def calculate_daily_averages_2(df, month, year, regressors):
    min_year = df['ds'].dt.year.min()
    max_year = df['ds'].dt.year.max()
    weights = {y: 1 / (year - y + 1) for y in range(min_year, max_year + 1)}
    
    def weighted_average_for_day(day, regressor):
        day_values = [
            df[(df['ds'].dt.month == month) & 
               (df['ds'].dt.year == y) & 
               (df['ds'].dt.day == day)][regressor].mean() * weight
            for y, weight in weights.items()
            if not df[(df['ds'].dt.month == month) & (df['ds'].dt.year == y) & (df['ds'].dt.day == day)].empty
        ]
        return np.nan if not day_values else np.sum(day_values) / sum(weights.values())
    
    return {regressor: [weighted_average_for_day(day, regressor) for day in range(1, 32)] for regressor in regressors}

# Pure function to create future DataFrame and populate it with daily averages
def create_future_df(start_date, end_date, historical_data, regressors):
    future_dates = pd.date_range(start=start_date, end=end_date)
    future_df = pd.DataFrame({'ds': future_dates})
    
    for current_month in range(start_date.month, end_date.month + 1):
        daily_averages = calculate_daily_averages(historical_data, current_month, start_date.year, regressors)
        month_mask = future_df['ds'].dt.month == current_month
        for regressor in regressors:
            future_df.loc[month_mask, regressor] = daily_averages[regressor][:sum(month_mask)]
    
    return future_df

# Pure function to adjust future DataFrame for day of the week effect
def adjust_for_weekend_effect(future_df, regressors, weekend_factor=0.9):
    future_df['day_of_week'] = future_df['ds'].dt.dayofweek
    adjusted_df = future_df.copy()
    for regressor in regressors:
        adjusted_df.loc[adjusted_df['day_of_week'] >= 5, regressor] *= weekend_factor
    return adjusted_df

# Pure function to create and fit Prophet model
def create_and_fit_prophet_model(daily_data, regressors):
    model = Prophet(daily_seasonality=True, weekly_seasonality=True, yearly_seasonality=True)
    for regressor in regressors:
        model.add_regressor(regressor)
    model.fit(daily_data[['ds', 'y'] + regressors])
    return model

# Pure function to generate forecast using Prophet
def generate_forecast(model, future_df):
    return model.predict(future_df)

# Main function to encapsulate the entire process
def main():
    # # File path
    file_path = 'amount_paid.csv'
    # file_path = 'reading_fee_paid/forecast_data_1.csv'

    # # Load and preprocess data
    df = load_and_preprocess_data(file_path)

    columns_keep= ['# created_date', 'id', 'created_by', 'transaction_branch_id', 'transaction_type_id',
               'amount_paid', 'Coupon_Discount', 'magazine_fee_paid', 'payable_amount',
               'reading_fee_paid', 'reversed', 'over_due_adjustment_amount', 'last_card_number',
               'primus_amount', 'adjustment_amount', 'security_deposit', 'Percentage_Share',
               'subscription_id', 'member_branch_id', 'transaction', 'Transaction_Month', 'Transaction_Year',
               'created_name', 'branch_name', 'branch_type', 'member_card', 'Member_Name', 'email',
               'Number_of_Months', 'display_name', 'Renewal_Amount', 'Message_Status', 'Membership_expiry_date', 'User_Name']
    df=df[columns_keep]
    
    # # Aggregate daily data
    
    
    # Define regressors for amount_paided
    # regressors = [
    #     'over_due_adjustment_amount', 
    #     'security_deposit', 
    #     'Percentage_Share',
    #     'Coupon_Discount', 
    #     'reading_fee_paid', 
    #     'Number_of_Months'
    # ]

    #regressor for magazine_fee_paid:
    # y = 'magazine_fee_paid'
    # regressors = ['amount_paid', 'reading_fee_paid', 'payable_amount','Coupon_Discount','subscription_id','id']

    # # y = 'reading_fee_paid'
    # # regressors = ['amount_paid', 'Number_of_Months', 'Coupon_Discount', 'payable_amount', 'id', 'Transaction_Year', 'transaction_type_id', 'magazine_fee_paid']

    # y = 'Coupon_Discount'
    # regressors = ['amount_paid', 'Number_of_Months', 'reading_fee_paid', 'payable_amount', 'id', 'Transaction_Year']

    y = "Number_of_Months"
    regressors = ['reading_fee_paid', 'amount_paid', 'Coupon_Discount', 'payable_amount', 'transaction_type_id', 'transaction', 'member_branch_id']

    models = [
        {
            'y': 'magazine_fee_paid',
            'regressors': ['amount_paid', 'reading_fee_paid', 'payable_amount', 'Coupon_Discount', 'subscription_id', 'id']
        },
        {
            'y': 'reading_fee_paid',
            'regressors': ['amount_paid', 'Number_of_Months', 'Coupon_Discount', 'payable_amount', 'id', 'Transaction_Year', 'transaction_type_id', 'magazine_fee_paid']
        },
        {
            'y': 'Coupon_Discount',
            'regressors': ['amount_paid', 'Number_of_Months', 'reading_fee_paid', 'payable_amount', 'id', 'Transaction_Year']
        },
        {
            'y': 'Number_of_Months',
            'regressors': ['reading_fee_paid', 'amount_paid', 'Coupon_Discount', 'payable_amount', 'transaction_type_id', 'transaction', 'member_branch_id']
        }
    ]

    # for model_def in models:

    # y = model_def['y']
    # regressors = model_def['regressors']
    daily_data = aggregate_daily_data(df,y)
    # print(f"Data after aggregation: {daily_data.shape[0]} rows")
    # for regressor in regressors:
    #     print(f"Unique values in {regressor}: {daily_data[regressor].unique()}")

    # Create and fit Prophet model
    model = create_and_fit_prophet_model(daily_data, regressors)

    
    # # Historical data for reference
    historical_data = daily_data.copy()

    pickle_file = f'{y}_prophet_model_and_data.pkl'

    with open(pickle_file, 'wb') as file:
        pickle.dump({'model': model, 'historical_data': historical_data}, file)
        print("Model and historical data saved to pickle file")

    # Store the model and historical data into a pickle file
    # with open(pickle_file, 'rb') as file:
    #     data = pickle.load(file)
    #     model = data['model']
    #     historical_data = data['historical_data']

    # print("Model and historical data loaded from pickle file")

    # Define prediction period
    start_date = datetime(2024, 5, 15)
    end_date = datetime(2024, 10, 31)

    # Create future DataFrame and adjust for weekend effect
    future_df = create_future_df(start_date, end_date, historical_data, regressors)
    future_df = adjust_for_weekend_effect(future_df, regressors)
    
    # Generate forecast
    forecast = generate_forecast(model, future_df)
    
    # Plot components using Prophet's built-in function
    model.plot_components(forecast)
    plt.show()

    # Plot forecast with Plotly
    fig = go.Figure()

    # Forecast line
    fig.add_trace(go.Scatter(x=forecast['ds'], y=forecast['yhat'], mode='lines', 
                             name='Forecast', line=dict(color='red')))

    # Uncertainty interval
    fig.add_trace(go.Scatter(x=forecast['ds'], y=forecast['yhat_upper'], fill=None, 
                             mode='lines', line_color='red', line=dict(dash='dash'), 
                             name='Upper Bound'))
    fig.add_trace(go.Scatter(x=forecast['ds'], y=forecast['yhat_lower'], fill='tonexty', 
                             mode='lines', line_color='red', line=dict(dash='dash'), 
                             name='Lower Bound'))

    # Update layout
    fig.update_layout(
        title='Forecasted Values with Prophet',
        xaxis_title='Date',
        yaxis_title='Forecasted Value',
        legend_title='Legend'
    )

    # Show the plot
    fig.show()

# Run the main function
if __name__ == "__main__":
    main()
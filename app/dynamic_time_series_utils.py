import pickle
from datetime import datetime

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import plotly.graph_objs as go


# Pure function to calculate daily averages
def calculate_daily_averages_2(df, month, year, regressors):
    min_year = df["ds"].dt.year.min()
    max_year = df["ds"].dt.year.max()
    weights = {y: 1 / (year - y + 1) for y in range(min_year, max_year + 1)}

    def weighted_average_for_day(day, regressor):
        day_values = [
            df[
                (df["ds"].dt.month == month)
                & (df["ds"].dt.year == y)
                & (df["ds"].dt.day == day)
            ][regressor].mean()
            * weight
            for y, weight in weights.items()
            if not df[
                (df["ds"].dt.month == month)
                & (df["ds"].dt.year == y)
                & (df["ds"].dt.day == day)
            ].empty
        ]
        return np.nan if not day_values else np.sum(day_values) / sum(weights.values())

    return {
        regressor: [weighted_average_for_day(day, regressor) for day in range(1, 32)]
        for regressor in regressors
    }


def calculate_daily_averages(df, month, year, regressors):
    # Determine the range of years in the historical data
    min_year = df["ds"].dt.year.min()
    max_year = df["ds"].dt.year.max()

    # Calculate weights dynamically based on available years
    weights = {y: 1 / (year - y + 1) for y in range(min_year, max_year + 1)}

    daily_averages = {}
    for regressor in regressors:
        daily_values = []
        for day in range(1, 32):  # Assuming up to 31 days in a month
            day_values = []
            for y, weight in weights.items():
                day_data = df[
                    (df["ds"].dt.month == month)
                    & (df["ds"].dt.year == y)
                    & (df["ds"].dt.day == day)
                ]

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
                weighted_average = (
                    np.nan
                )  # Handle cases where there is no data for that day
            daily_values.append(weighted_average)

        daily_averages[regressor] = daily_values

    return daily_averages


# Pure function to create future DataFrame and populate it with daily averages
def create_future_df(start_date, end_date, historical_data, regressors):
    future_dates = pd.date_range(start=start_date, end=end_date)
    future_df = pd.DataFrame({"ds": future_dates})

    for current_month in range(start_date.month, end_date.month + 1):
        daily_averages = calculate_daily_averages(
            historical_data, current_month, start_date.year, regressors
        )
        month_mask = future_df["ds"].dt.month == current_month
        for regressor in regressors:
            future_df.loc[month_mask, regressor] = daily_averages[regressor][
                : sum(month_mask)
            ]

    return future_df


# Pure function to adjust future DataFrame for day of the week effect
def adjust_for_weekend_effect(future_df, regressors, weekend_factor=0.9):
    future_df["day_of_week"] = future_df["ds"].dt.dayofweek
    adjusted_df = future_df.copy()
    for regressor in regressors:
        adjusted_df.loc[adjusted_df["day_of_week"] >= 5, regressor] *= weekend_factor
    return adjusted_df


# Pure function to generate forecast using Prophet
def generate_forecast(model, future_df):
    return model.predict(future_df)


# Main function to encapsulate the entire process
def main():
    regressors = [
        "over_due_adjustment_amount",
        "security_deposit",
        "Percentage_Share",
        "Coupon_Discount",
        "reading_fee_paid",
        "Number_of_Months",
    ]

    pickle_file = "prophet_model_and_data.pkl"

    # Store the model and historical data into a pickle file
    with open(pickle_file, "rb") as file:
        data = pickle.load(file)
        model = data["model"]
        historical_data = data["historical_data"]

    print("Model and historical data loaded from pickle file")

    # Define prediction period
    start_date = datetime(2024, 8, 15)
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
    fig.add_trace(
        go.Scatter(
            x=forecast["ds"],
            y=forecast["yhat"],
            mode="lines",
            name="Forecast",
            line=dict(color="red"),
        )
    )

    # Uncertainty interval
    fig.add_trace(
        go.Scatter(
            x=forecast["ds"],
            y=forecast["yhat_upper"],
            fill=None,
            mode="lines",
            line_color="red",
            line=dict(dash="dash"),
            name="Upper Bound",
        )
    )
    fig.add_trace(
        go.Scatter(
            x=forecast["ds"],
            y=forecast["yhat_lower"],
            fill="tonexty",
            mode="lines",
            line_color="red",
            line=dict(dash="dash"),
            name="Lower Bound",
        )
    )

    # Update layout
    fig.update_layout(
        title="Forecasted Values with Prophet",
        xaxis_title="Date",
        yaxis_title="Forecasted Value",
        legend_title="Legend",
    )

    # Show the plot
    fig.show()

import pandas as pd
import plotly.graph_objects as go
from prophet import Prophet

from app.data_preparation_ulits.aggregate import aggregate_columns_by_date
from app.data_preparation_ulits.one_hot_encode import apply_one_hot_encoding
from app.ml_models.feature_rank import compute_feature_rankings


def time_series_analysis(
    directory_project,
    input_file_path_raw_data_csv,
    modified_regressors,
    target_var,
    start_date,
    end_date,
    increase_factor,
    zero_value_replacement,
):

    date_column = "# created_date"
    date_column = "created_date"
    print(input_file_path_raw_data_csv)
    # df = pd.read_csv(input_file_path_raw_data_csv)
    df = pd.read_csv("/Users/vedanths/Downloads/cluster2.csv")
    print(df.head())
    df[date_column] = pd.to_datetime(df[date_column])
    df.drop("member_card", axis=1, inplace=True)
    df.drop("Membership_expiry_date", axis=1, inplace=True)

    forecast_periods = (end_date - df[date_column].max()).days + 30
    df, encoder = apply_one_hot_encoding(df)
    df = aggregate_columns_by_date(df, date_column=date_column)
    df_ts = df
    del df
    # regressors_df = compute_feature_rankings(df_ts, target_var, [])
    # regressors = regressors_df["Feature"].to_list()
    regressors = [
        "Coupon_Discount",
        "magazine_fee_paid",
        "reading_fee_paid",
        "over_due_adjustment_amount",
        "security_deposit",
        "reward_points",
        "num_books",
        "num_magazine",
        "primus_amount",
        "adjustment_amount",
        "basic_price_for_book",
        "basic_price_for_magazine",
        "Renewal_Amount",
        "taxable_amount",
        "TAX_AMOUNT",
    ]
    print(regressors)
    df_prophet = prepare_prophet_data(df_ts, date_column, target_var, regressors)
    model = Prophet(
        n_changepoints=100,
        changepoint_prior_scale=0.2,
        seasonality_mode="multiplicative",
        yearly_seasonality=True,
        weekly_seasonality=True,
        daily_seasonality=True,
    )

    for regressor in regressors:
        model.add_regressor(regressor)

    model.fit(df_prophet)

    forecasted_regressors_df = forecast_regressors_for_date_range(
        start_date, end_date, df_ts, regressors, forecast_periods
    )

    modified_forecasted_regressors_df = modify_forecast_and_prepare_dataset(
        forecasted_regressors_df,
        modified_regressors,
        increase_factor=increase_factor,
        zero_value_replacement=zero_value_replacement,
    )

    future_revenue_modified = modified_forecasted_regressors_df[["ds"]].copy()

    fig = plot_actual_vs_forecast(
        historical_data=df_ts,
        forecasted_values_df=forecasted_regressors_df,
        modified_forecast_df=modified_forecasted_regressors_df,
        model=model,
        past_months=12,
        forecast_months=12,
    )

    return fig


def prepare_prophet_data(df, date_column, target_column, regressors):
    """#DATA FOR TRAINING
    df -> Time series data (from Aggragator)
    date_column -> hard code
    target_column -> one KPI (user input)
    regressors -> feature ranking algo
    """
    df[date_column] = pd.to_datetime(df[date_column])

    df_prophet = df[[date_column, target_column]].rename(
        columns={date_column: "ds", target_column: "y"}
    )

    for regressor in regressors:
        if regressor in df.columns:
            df_prophet[regressor] = df[regressor]
        else:
            raise ValueError(f"Regressor '{regressor}' not found in the dataframe.")

    return df_prophet


def forecast_regressors_for_date_range(
    start_date, end_date, training_data, regressors, forecast_periods=180
):
    """
    date -> user input date
    training_data -> time series data df
    regressors -> feature ranking algo
    forecast_periods -> user input days
    """
    future_regressor_values = {}

    for regressor in regressors:
        df_regressor = training_data[["created_date", regressor]].rename(
            columns={"created_date": "ds", regressor: "y"}
        )

        regressor_model = Prophet(changepoint_prior_scale=0.7)
        regressor_model.fit(df_regressor)

        last_date = df_regressor["ds"].max()
        future_regressor = regressor_model.make_future_dataframe(periods=forecast_periods)
        forecast_regressor = regressor_model.predict(future_regressor)

        future_values = forecast_regressor[
            (forecast_regressor["ds"] > last_date)
            & (forecast_regressor["ds"] >= start_date)
            & (forecast_regressor["ds"] <= end_date)
        ][["ds", "yhat"]]

        future_values["yhat"] = future_values["yhat"].astype(int)
        future_regressor_values[regressor] = future_values.set_index("ds")

    future_df = pd.DataFrame({"ds": pd.date_range(start=start_date, end=end_date)})

    for regressor in regressors:
        regressor_values = future_regressor_values[regressor]

        future_df = future_df.merge(
            regressor_values["yhat"], left_on="ds", right_index=True, how="left"
        )

        future_df[regressor] = future_df["yhat"].fillna(future_df["yhat"].mean())
        future_df = future_df.drop(columns="yhat").rename(columns={regressor: regressor})

    return future_df


def modify_forecast_and_prepare_dataset(
    forecasted_values_df, modified_regressors, increase_factor=4.80, zero_value_replacement=3.80
):
    """
    forecasted_values_df -> forcasted_regressor (def forecast_regressors_for_date_range )
    modified_regressors -> user input
    increase_factor -> user input
    zero_value_replacement -> user input
    """
    modified_forecast_df = forecasted_values_df.copy()

    modified_forecast_df = modified_forecast_df.fillna(0)

    for regressor in modified_regressors:
        if regressor in modified_forecast_df.columns:
            modified_forecast_df[regressor] = modified_forecast_df[regressor].apply(
                lambda x: x * increase_factor if x != 0 else zero_value_replacement
            )
        else:
            raise ValueError(f"Regressor '{regressor}' is not found in the DataFrame.")

    return modified_forecast_df


def plot_actual_vs_forecast(
    historical_data,
    forecasted_values_df,
    modified_forecast_df,
    model,
    past_months=12,
    forecast_months=12,
):
    historical_data["created_date"] = pd.to_datetime(historical_data["created_date"])
    last_actual_data = (
        historical_data.set_index("created_date").last(f"{past_months}M").resample("M").sum()
    )
    forecast_original = model.predict(forecasted_values_df.rename(columns={"ds": "ds"}))
    forecast_original["ds"] = pd.to_datetime(forecast_original["ds"])
    forecast_original_monthly = forecast_original.set_index("ds").resample("M").sum()
    forecast_modified = model.predict(modified_forecast_df.rename(columns={"ds": "ds"}))
    forecast_modified["ds"] = pd.to_datetime(forecast_modified["ds"])
    forecast_modified_monthly = forecast_modified.set_index("ds").resample("M").sum()
    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=last_actual_data.index,
            y=last_actual_data["amount_paid"],
            mode="lines+markers",
            name=f"Actual Revenue (Last {past_months} Months)",
            line=dict(color="green"),
        )
    )
    fig.add_trace(
        go.Scatter(
            x=forecast_original_monthly.index[:forecast_months],
            y=forecast_original_monthly["yhat"][:forecast_months],
            mode="lines+markers",
            name=f"Forecasted Revenue (Original, Next {forecast_months} Months)",
            line=dict(color="blue"),
        )
    )
    fig.add_trace(
        go.Scatter(
            x=forecast_modified_monthly.index[:forecast_months],
            y=forecast_modified_monthly["yhat"][:forecast_months],
            mode="lines+markers",
            name=f"Forecasted Revenue (Modified, Next {forecast_months} Months)",
            line=dict(color="red"),
        )
    )
    fig.update_layout(
        title="Revenue Comparison: Actual vs. Forecast (Original & Modified)",
        xaxis_title="Date",
        yaxis_title="Monthly Revenue",
        template="plotly_white",
    )
    return fig

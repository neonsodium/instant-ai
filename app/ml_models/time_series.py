import pandas as pd
import plotly.graph_objects as go
from dateutil.relativedelta import relativedelta
from prophet import Prophet

from app.data_preparation_ulits.aggregate import aggregate_columns_by_date
from app.data_preparation_ulits.one_hot_encode import apply_one_hot_encoding
from app.ml_models.feature_ranking_ulits.feature_ranking_time_series import (
    ensemble_feature_importance_auto,
)


def time_series_analysis(
    directory_project: str,
    input_file_path_raw_data_csv: str,
    kpi: str,
    no_of_months,
    date_column: str,
    adjustments: dict,
    regressors: list,
):
    df = pd.read_csv(input_file_path_raw_data_csv)
    df[date_column] = pd.to_datetime(df[date_column])

    start_date = df[date_column].max()
    end_date = start_date + relativedelta(months=no_of_months)
    forecast_periods = (end_date - start_date).days + 30
    df, encoder = apply_one_hot_encoding(df)
    # regressors = ensemble_feature_importance_auto(df, kpi)  # feature
    df = aggregate_columns_by_date(df, date_column=date_column)
    df_ts = df
    del df, encoder
    df = df_ts.drop(date_column, axis=1, inplace=False)

    df_prophet = prepare_prophet_data(df_ts, date_column, kpi, regressors)
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
        start_date, end_date, df_ts, regressors, date_column, forecast_periods
    )

    df_new = adjust_columns(df_ts, forecasted_regressors_df, adjustments)

    fig = plot_actual_vs_forecast(
        historical_data=df_ts,
        forecasted_values_df=forecasted_regressors_df,
        modified_forecast_df=df_new,  # adjustment_df <- modified_forecasted_regressors_df
        model=model,
        kpi=kpi,
        date_column=date_column,
        past_months=no_of_months,
        forecast_months=no_of_months,
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
    start_date, end_date, training_data, regressors, date_column, forecast_periods=180
):
    """
    date -> user input date
    training_data -> time series data df
    regressors -> feature ranking algo
    forecast_periods -> user input days
    """
    future_regressor_values = {}

    for regressor in regressors:
        df_regressor = training_data[[date_column, regressor]].rename(
            columns={date_column: "ds", regressor: "y"}
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


def plot_actual_vs_forecast(
    historical_data,
    forecasted_values_df,
    modified_forecast_df,
    model,
    kpi,
    date_column,
    past_months=12,
    forecast_months=12,
):
    historical_data[date_column] = pd.to_datetime(historical_data[date_column])
    last_actual_data = (
        historical_data.set_index(date_column).last(f"{past_months}M").resample("M").sum()
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
            y=last_actual_data[kpi],
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


def adjust_columns(df, forecasted_regressors_df, adjustments):
    """
    Adjusts numeric columns in a DataFrame based on given rules.

    - "+23%" increases column values by 23%.
    - "-10%" decreases column values by 10%.
    - "+5" adds 5 to column values.
    - "-2" subtracts 2 from column values.

    Parameters:
    df (pd.DataFrame): Input DataFrame
    adjustments (dict): Column adjustments with percentage/absolute changes

    Returns:
    pd.DataFrame: Updated DataFrame
    """
    df = forecasted_regressors_df.copy()  # renamed from forecasted_values_df

    for col, adjustment in adjustments.items():
        if col not in df.columns:
            print(f"Warning: Column '{col}' not found in DataFrame, skipping.")
            continue

        if isinstance(adjustment, str):
            if adjustment.endswith("%"):
                # Percentage change
                percent_value = float(adjustment.strip("%")) / 100.0
                df[col] = df[col] * (1 + percent_value)
            else:
                # Absolute change
                abs_value = float(adjustment)
                df[col] = df[col] + abs_value

    return df

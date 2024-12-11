import json
import pickle

import matplotlib
from flask import current_app, flash, redirect, session, url_for

matplotlib.use("agg")  # Set the backend before importing pyplot
import io
import os
from datetime import datetime

import matplotlib.pyplot as plt
import plotly.graph_objs as go
from flask import Blueprint, render_template, request, send_file
from prophet import Prophet  # Dont remove

from app.dynamic_time_series_utils import (adjust_for_weekend_effect,
                                           create_future_df, generate_forecast)

old_routes = Blueprint("old_routes", __name__)
json_section_file = "static/json/section.json"
# static/pickle_files/

models = [
    {
        "y": "amount_paid",
        "regressors": [
            "over_due_adjustment_amount",
            "security_deposit",
            "Percentage_Share",
            "Coupon_Discount",
            "reading_fee_paid",
            "Number_of_Months",
        ],
    },
    {
        "y": "magazine_fee_paid",
        "regressors": [
            "amount_paid",
            "reading_fee_paid",
            "payable_amount",
            "Coupon_Discount",
            "subscription_id",
            "id",
        ],
    },
    {
        "y": "reading_fee_paid",
        "regressors": [
            "amount_paid",
            "Number_of_Months",
            "Coupon_Discount",
            "payable_amount",
            "id",
            "Transaction_Year",
            "transaction_type_id",
            "magazine_fee_paid",
        ],
    },
    {
        "y": "Coupon_Discount",
        "regressors": [
            "amount_paid",
            "Number_of_Months",
            "reading_fee_paid",
            "payable_amount",
            "id",
            "Transaction_Year",
        ],
    },
    {
        "y": "Number_of_Months",
        "regressors": [
            "reading_fee_paid",
            "amount_paid",
            "Coupon_Discount",
            "payable_amount",
            "transaction_type_id",
            "transaction",
            "member_branch_id",
        ],
    },
]


def get_regressors(target_y, models):
    # Loop through the list of models
    for model in models:
        # Check if the 'y' value matches the target
        if model["y"] == target_y:
            return model["regressors"]
    # If no matching model is found, return None or an empty list
    return None


with open(json_section_file) as f:
    data = json.load(f)


def build_dynamic_time_series_dict() -> dict:
    return {
        section["endpoint"]: url_for("old_routes.dynamic_time_series", target=section["endpoint"])
        for section in data["sections"]
    }


def is_logged_in():
    if session.get("username"):
        return redirect(url_for("old_routes.index"))
    else:
        return redirect(url_for("old_routes.login"))


# @app.before_request
def login_check():
    if session.get("username"):
        return redirect(url_for("old_routes.index"))
    else:
        return redirect(url_for("old_routes.login"))


# Login Page
@old_routes.route("/login")
def login():
    """Renders the login page."""
    if not current_app.config.get("LOGIN_REQUIRED", True):
        return redirect(url_for("old_routes.index"))
    if session.get("username"):
        return redirect(url_for("old_routes.index"))
    return render_template("login.html")


def generate_section_urls(data):
    return [
        {"url": section["endpoint"], "title": section["title"], "subtitle": section["subtitle"]}
        for section in data["sections"]
    ]


# Home page
@old_routes.route("/index")
def index():
    return render_template("index.html", sections=generate_section_urls(data))


# Auth API
@old_routes.route("/auth", methods=["POST"])
def auth():
    if current_app.config.get("PASSWORD") == request.form["password"] and current_app.config.get(
        "USERNAME"
    ):
        session["username"] = request.form["username"]
        return redirect(url_for("old_routes.index"))
    else:
        flash("Invalid username or password", "error")
        return redirect(url_for("old_routes.login"))


def read_rank_data(target):
    # Define the file name based on the target variable
    pickle_file_name = f"static/pickle_files/rank_data_{target}.pkl"

    # Open the pickle file and load the DataFrame
    with open(pickle_file_name, "rb") as pickle_file:
        return pickle.load(pickle_file)


def model_pickle_file(target):
    return f"static/pickle_files/{target}_prophet_model_and_data.pkl"


def load_model_and_data(pickle_file):
    try:
        with open(pickle_file, "rb") as file:
            data = pickle.load(file)
            return data["model"], data["historical_data"]
    except Exception as e:
        print(f"Pickle file for target variable '{pickle_file}' not found.", f"Error: {e}")


def get_top_15_features(df, target):
    id_fields = [
        "id",
        "transaction_branch_id",
        "transaction_type_id",
        "subscription_id",
        "member_branch_id",
        "last_card_number",
        "member_card",
    ]
    return df[(df["Feature"] != target) & (~df["Feature"].isin(id_fields))].head(15)


@old_routes.route("/cluster")
def cluster_data():
    catagories = [
        "Non_Fiction",
        "Teens",
        "Self_Help",
        "Fiction",
        "Kids",
        "GK",
        "Languages",
        "Entertainment",
    ]
    return render_template("cluster.html", category=catagories)


@old_routes.route("/cluster/<target>")
def cluster_data_downlaod(target):
    catagories = [
        "Non_Fiction",
        "Teens",
        "Self_Help",
        "Fiction",
        "Kids",
        "GK",
        "Languages",
        "Entertainment",
    ]
    if target not in catagories:
        return
    with open(f"static/pickle_files/cluster_model_{target}.pkl", "rb") as file:
        loaded_data = pickle.load(file)
    output = io.StringIO()
    loaded_data.to_csv(output, index=False)
    output.seek(0)
    return send_file(
        io.BytesIO(output.getvalue().encode()),
        mimetype="text/csv",
        as_attachment=True,
        download_name="cluster_data.csv",
    )


@old_routes.route("/index/<target>")
def rank_data(target):
    try:
        if target == "revenue":
            return render_template(
                "rank_data_revenue.html",
                target=target,
                rank_data=get_top_15_features(read_rank_data(target), target),
                dynamic_time_series_endpoint=build_dynamic_time_series_dict().get(target),
            )
        return render_template(
            "rank_data.html",
            target=target,
            rank_data=get_top_15_features(read_rank_data(target), target),
            dynamic_time_series_endpoint=build_dynamic_time_series_dict().get(target),
        )
    except FileNotFoundError:
        print(f"Pickle file for target variable '{target}' not found.")
        return render_template(
            "rank_data.html", error=f"Pickle file for target variable '{target}' not found."
        )


def create_future_forecast(model, historical_data, regressors, start_date, end_date):
    future_df = create_future_df(start_date, end_date, historical_data, regressors)
    future_df = adjust_for_weekend_effect(future_df, regressors)
    return generate_forecast(model, future_df)


def generate_matplotlib_plot(model, forecast):
    fig, ax = plt.subplots(figsize=(10, 6))
    model.plot_components(forecast)
    img = io.BytesIO()
    plt.savefig(img, format="png")
    img.seek(0)
    plt.close(fig)
    return img


def generate_plotly_plot(forecast):
    fig = go.Figure()

    fig.add_trace(
        go.Scatter(
            x=forecast["ds"],
            y=forecast["yhat"],
            mode="lines",
            name="Forecast",
            line=dict(color="red"),
        )
    )
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
    fig.update_layout(
        title="Forecasted Values with Prophet",
        xaxis_title="Date",
        yaxis_title="Forecasted Value",
        legend_title="Legend",
    )

    return fig.to_html(full_html=False)


@old_routes.route("/dynamic_time_series/<target>")
def dynamic_time_series(target):
    model, historical_data = load_model_and_data(model_pickle_file(target))
    start_date_str = request.args.get("start_date", "2024-08-15")
    end_date_str = request.args.get("end_date", "2024-10-31")
    try:
        start_date = datetime.strptime(start_date_str, "%Y-%m-%d")
        end_date = datetime.strptime(end_date_str, "%Y-%m-%d")
    except ValueError:
        return "Invalid date format. Use YYYY-MM-DD.", 400
    plotly_plot = generate_plotly_plot(
        create_future_forecast(
            model, historical_data, get_regressors(target, models), start_date, end_date
        )
    )
    return render_template(
        "dynamic_time_series.html",
        plotly_plot=plotly_plot,
        target=target,
        start_date=start_date,
        end_date=end_date,
    )


@old_routes.route("/temp/plot.png")
def plot_png():
    target = request.args.get("target", None)
    if target is None:
        return "Target parameter is missing", 400
    model, historical_data = load_model_and_data(model_pickle_file(target))
    try:
        start_date = datetime.strptime(request.args.get("start_date", "2024-01-15"), "%Y-%m-%d")
        end_date = datetime.strptime(request.args.get("end_date", "2024-12-31"), "%Y-%m-%d")
    except ValueError:
        return "Invalid date format. Use YYYY-MM-DD.", 400

    img = generate_matplotlib_plot(
        model,
        create_future_forecast(
            model, historical_data, get_regressors(target, models), start_date, end_date
        ),
    )
    return send_file(img, mimetype="image/png")

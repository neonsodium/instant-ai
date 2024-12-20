import os

import pandas as pd
import plotly.graph_objects as go
import plotly.io as pio
from flask import Blueprint, jsonify, render_template, request

from app.filename_utils import filename_raw_data_csv
from app.ml_models.time_series import time_series_analysis
from app.os_utils import *

lazy_routes = Blueprint("lazy_routes", __name__)


@lazy_routes.route("/<project_id>/time-series/encode", methods=["GET", "POST"])
def initiate_feature_ranking(project_id):
    # request_data_json = request.get_json()
    # project_id = os.path.basename(request_data_json.get("project_id"))
    # user_added_vars_list = request_data_json.get("user_added_vars_list", [])
    # level = int(request_data_json.get("level"))
    # list_path = request_data_json.get("path")
    # target_var = request_data_json.get("target_var", None)

    project_id = "7a87a0d9-3a7e-4675-8269-660075998b29"
    level = 1
    list_path = [1]
    target_var = "amount_paid"
    user_added_vars_list = []

    directory_project = directory_project_path_full(project_id, [])
    # if not os.path.isdir(directory_project):
    #     return jsonify({"error": "Invalid Project ID"}), 400

    # if int(level) != len(list_path):
    #     return jsonify({"error": "Level and Path don't match"}), 400

    directory_project_cluster = directory_project_path_full(project_id, list_path)
    # if not os.path.exists(directory_project_cluster):
    #     return (jsonify({"error": "Cluster Does not exists.", "project_id": project_id}), 404)

    raw_data_file = os.path.join(directory_project, filename_raw_data_csv())
    # start_date_str = request_data_json.get("start_date")
    # end_date_str = request_data_json.get("end_date")
    start_date_str = "2024-09-17"
    end_date_str = "2025-09-30"
    # increase_factor = request_data_json.get("increase_factor")
    increase_factor = 4
    start_date = pd.to_datetime(start_date_str)
    end_date = pd.to_datetime(end_date_str)

    fig = time_series_analysis(
        directory_project_cluster,
        raw_data_file,
        user_added_vars_list,
        target_var,
        start_date,
        end_date,
        increase_factor,
        1,
    )

    fig_json = pio.to_json(fig)

    # Pass the JSON to the template
    return render_template("time_series.html", plotly_figure=fig_json)

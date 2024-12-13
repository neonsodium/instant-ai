import os

from flask import Blueprint, jsonify, request, render_template
from app.os_utils import *
from app.ml_models.time_series import time_series_analysis
from app.filename_utils import filename_raw_data_csv

import pandas as pd
import plotly.graph_objects as go
import plotly.io as pio

lazy_routes = Blueprint("lazy_routes", __name__)


@lazy_routes.route("/time-series", methods=["POST"])
def initiate_feature_ranking():
    request_data_json = request.get_json()
    # project_id = os.path.basename(request_data_json.get("project_id"))
    # user_added_vars_list = request_data_json.get("user_added_vars_list", [])
    # level = int(request_data_json.get("level"))
    # list_path = request_data_json.get("path")
    # target_var = request_data_json.get("target_var", None)

    project_id = "b1356c05-7195-497d-91f4-55549fc4ee04"
    level = 1
    list_path = [1]
    target_var = "Revenue"
    user_added_vars_list = []

    directory_project = directory_project_path_full(project_id, [])
    if not os.path.isdir(directory_project):
        return jsonify({"error": "Invalid Project ID"}), 400

    if int(level) != len(list_path):
        return jsonify({"error": "Level and Path don't match"}), 400

    directory_project_cluster = directory_project_path_full(project_id, list_path)
    if not os.path.exists(directory_project_cluster):
        return (jsonify({"error": "Cluster Does not exists.", "project_id": project_id}), 404)

    raw_data_file = os.path.join(directory_project, filename_raw_data_csv())
    # start_date_str = request_data_json.get("start_date")
    # end_date_str = request_data_json.get("end_date")
    start_date_str = "2024-09-17"
    end_date_str = "2025-09-30"
    increase_factor = request_data_json.get("increase_factor")
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
    return render_template("index.html", plotly_figure=fig_json)

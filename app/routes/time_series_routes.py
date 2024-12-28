import os

import pandas as pd
import plotly.graph_objects as go
import plotly.io as pio
from flask import Blueprint, jsonify, render_template, request

from app.filename_utils import filename_raw_data_csv
from app.ml_models.time_series import time_series_analysis
from app.os_utils import *

lazy_routes = Blueprint("lazy_routes", __name__)


@lazy_routes.route("/<project_id>/time-series/encode", methods=["POST"])
def initiate_feature_ranking(project_id):
    request_data_json = request.get_json()
    project_id = os.path.basename(request_data_json.get("project_id"))
    user_added_vars_list = request_data_json.get("user_added_vars_list", [])
    level = int(request_data_json.get("level"))
    list_path = request_data_json.get("path")
    kpi = request_data_json.get("kpi", None)
    no_of_months = request_data_json.get("no_of_months")
    date_column = request_data_json.get("date_column")
    increase_factor = request_data_json.get("increase_factor")
    zero_value_replacement = request_data_json.get("zero_value_replacement")

    directory_project = directory_project_path_full(project_id, [])
    if not os.path.isdir(directory_project):
        return jsonify({"error": "Invalid Project ID"}), 400

    if int(level) != len(list_path):
        return jsonify({"error": "Level and Path don't match"}), 400

    directory_project_cluster = directory_project_path_full(project_id, list_path)
    if not os.path.exists(directory_project_cluster):
        return (jsonify({"error": "Cluster Does not exists.", "project_id": project_id}), 404)

    if not os.path.isfile(os.path.join(directory_project_cluster, filename_raw_data_csv())):
        return jsonify({"message": "Data set not found"}), 400

    raw_data_file = os.path.join(directory_project, filename_raw_data_csv())

    fig = time_series_analysis(
        directory_project_cluster,
        raw_data_file,
        user_added_vars_list,
        kpi,
        no_of_months,
        date_column,
        increase_factor,
        zero_value_replacement,
    )

    fig_json = pio.to_json(fig)

    return render_template("time_series.html", plotly_figure=fig_json)

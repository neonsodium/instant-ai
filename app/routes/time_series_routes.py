import os
import pickle

import pandas as pd
import plotly.graph_objects as go
import plotly.io as pio
from flask import Blueprint, jsonify, request

from app.models.project_model import ProjectModel
from app.utils.filename_utils import (
    filename_categorical_columns_list_pkl,
    filename_raw_data_csv,
    filename_rev_one_hot_encoded_dict_pkl,
    filename_time_series_figure_pkl,
)
from app.utils.os_utils import *

time_series_routes = Blueprint("time_series", __name__)
project_model = ProjectModel()


# TODO More
def get_encoded_columns_for_column(column_name, encoder, categorical_columns):
    """
    Get the encoded column names for a specific column after OneHotEncoding.

    Parameters:
        column_name (str): The name of the original column to find encoded columns for.
        encoder (OneHotEncoder): The fitted OneHotEncoder object.
        categorical_columns (list): List of categorical column names passed to the encoder.

    Returns:
        list: The encoded column names corresponding to the input column.
    """

    all_encoded_columns = encoder.get_feature_names_out(categorical_columns)

    encoded_columns = [col for col in all_encoded_columns if col.startswith(f"{column_name}_")]

    return encoded_columns


@time_series_routes.route("/<project_id>/time-series/figure", methods=["POST", "GET"])
def get_time_series_figure(project_id):
    request_data_json = request.get_json()
    project_id = os.path.basename(request_data_json.get("project_id"))
    list_path = request_data_json.get("path")
    kpi = request_data_json.get("kpi", None)

    project = project_model.collection.find_one({"_id": project_id})
    if not project:
        return jsonify({"error": "Invalid Project ID"}), 400

    directory_project_base = directory_project_path_full(project_id, [])
    if not os.path.isdir(directory_project_base):
        return jsonify({"error": "Invalid Project ID"}), 400

    directory_project_cluster = directory_project_path_full(project_id, list_path)
    if not os.path.exists(directory_project_cluster):
        return (jsonify({"error": "Cluster Does not exists.", "project_id": project_id}), 404)

    if not os.path.isfile(os.path.join(directory_project_cluster, filename_raw_data_csv())):
        return jsonify({"message": "Data set not found"}), 400

    try:
        with open(
            os.path.join(directory_project_cluster, filename_time_series_figure_pkl(kpi)), "rb"
        ) as file:
            fig = pickle.load(file)
    except FileNotFoundError:
        return jsonify({"error": "Figure file not found"}), 404
    except pickle.UnpicklingError:
        return jsonify({"error": "Failed to unpickle the figure file"}), 500

    return jsonify({"plotly_figure": pio.to_json(fig)})


@time_series_routes.route("/<project_id>/time-series/encoded-columns", methods=["POST"])
def get_one_hot_encoded_columns(project_id):
    request_data_json = request.get_json()
    list_path = request_data_json.get("path", [])
    column_name = request_data_json.get("column_name")

    project = project_model.collection.find_one({"_id": project_id})
    if not project:
        return jsonify({"error": "Invalid Project ID"}), 400

    directory_project_base = directory_project_path_full(project_id, [])
    if not os.path.isdir(directory_project_base):
        return jsonify({"error": "Invalid Project ID"}), 404

    directory_project_cluster = directory_project_path_full(project_id, list_path)
    if not os.path.exists(directory_project_cluster):
        return (jsonify({"error": "Cluster Does not exists.", "project_id": project_id}), 404)

    directory_project_cluster = directory_project_path_full(project_id, list_path)
    cluster_filename_one_hot_encoded_labels_path = os.path.join(
        directory_project_cluster, filename_rev_one_hot_encoded_dict_pkl()
    )
    cluster_filename_categorical_columns_path = os.path.join(
        directory_project_cluster, filename_categorical_columns_list_pkl()
    )
    with open(cluster_filename_categorical_columns_path, "rb") as file:
        categorical_columns = pickle.load(file)

    with open(cluster_filename_one_hot_encoded_labels_path, "rb") as file:
        encoder = pickle.load(file)

    if column_name not in categorical_columns:
        return jsonify({"error": f"{column_name} is not a categorical column"}), 400

    encoded_columns = get_encoded_columns_for_column(column_name, encoder, categorical_columns)

    return jsonify({"categorical_column": encoded_columns}), 200


@time_series_routes.route("/<project_id>/time-series/categorical-columns", methods=["POST"])
def list_categorical_columns(project_id):
    """
    Lists the categorical columns for the given project ID.

    Parameters:
        project_id (str): The unique identifier for the project.

    Returns:
        JSON response containing the list of categorical columns or an error message.
    """
    try:
        request_data_json = request.get_json()
        list_path = request_data_json.get("path", [])

        project = project_model.collection.find_one({"_id": project_id})
        if not project:
            return jsonify({"error": "Invalid Project ID"}), 400

        directory_project_base = directory_project_path_full(project_id, [])
        if not os.path.isdir(directory_project_base):
            return jsonify({"error": "Invalid Project ID"}), 404

        directory_project_cluster = directory_project_path_full(project_id, list_path)
        if not os.path.exists(directory_project_cluster):
            return jsonify({"error": "Cluster Does not exist.", "project_id": project_id}), 404

        cluster_filename_categorical_columns_path = os.path.join(
            directory_project_cluster, filename_categorical_columns_list_pkl()
        )
        with open(cluster_filename_categorical_columns_path, "rb") as file:
            categorical_columns = pickle.load(file)

        return jsonify({"categorical_columns": categorical_columns}), 200

    except Exception as e:
        return jsonify({"error": "An error occurred", "details": str(e)}), 500

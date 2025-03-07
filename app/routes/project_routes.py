import os

import pandas as pd
from flask import Blueprint, jsonify, request, send_file

from app.data_preparation_ulits.preprocessing_engine import validate_df
from app.decorator import project_validation_decorator
from app.ml_models.idk_api import analyze_similarity_with_recent_data
from app.ml_models.summarising import summerise_cluster
from app.utils.filename_utils import (
    feature_descriptions_csv,
    feature_descriptions_json,
    filename_cluster_defs_dict_pkl,
    filename_feature_rank_score_df,
    filename_raw_data_csv,
)
from app.utils.model_utils import (
    create_project_and_directory,
    get_all_projects,
    get_project_columns,
    get_project_info,
)
from app.utils.os_utils import directory_project_path_full, list_sub_directories, load_from_pickle

main_routes = Blueprint("main_routes", __name__)


@main_routes.route("/", methods=["GET"])
def get_projects():
    """
    Retrieve all projects from the database.

    Returns:
        Response: A JSON response containing a list of projects or an error message.
    """
    try:
        projects = get_all_projects()

        if not projects:
            return jsonify({"message": "No projects found"}), 200

        return jsonify({"projects": projects}), 200
    except Exception as e:
        return (jsonify({"error": f"An error occurred while fetching projects: {str(e)}"}), 500)


@main_routes.route("/", methods=["POST"])
def create_project():
    """
    Create a new project, store it in the database, and create the associated directory structure.
    """
    request_data_json = request.get_json()
    project_name = request_data_json.get("name", "").strip()
    project_description = request_data_json.get("description", "").strip()

    if not project_name:
        return jsonify({"error": "Project name is required"}), 400
    if len(project_name) > 100:
        return jsonify({"error": "Project name must not exceed 100 characters"}), 400
    if not project_description:
        return jsonify({"error": "Project description is required"}), 400
    if len(project_description) > 500:
        return jsonify({"error": "Project description must not exceed 500 characters"}), 400

    status_code, response_data = create_project_and_directory(project_name, project_description)
    return jsonify(response_data), status_code


@main_routes.route("/<project_id>/clusters", methods=["POST"])
@project_validation_decorator
def get_cluster_info(project_id):

    request_data_json = request.get_json()
    list_path = request_data_json.get("path")

    directory_project_cluster = directory_project_path_full(project_id, list_path)
    if not os.path.exists(directory_project_cluster):
        return (jsonify({"error": "Cluster Does not exists.", "project_id": project_id}), 404)

    clusters = list_sub_directories(directory_project_cluster)

    return jsonify(
        {"Cluster Path": directory_project_cluster, "project_id": project_id, "clusters": clusters}
    )


@main_routes.route("/<project_id>/files/analyze_similarity", methods=["POST"])
@project_validation_decorator
def analyze_similarity_files(project_id):

    if "historical_file" not in request.files or "new_file" not in request.files:
        return jsonify({"error": "Both historical_file and new_file are required"}), 400

    historical_file = request.files["historical_file"]
    new_file = request.files["new_file"]

    directory_project_base = directory_project_path_full(project_id, [])

    historical_path = os.path.join(directory_project_base, historical_file.filename)
    new_path = os.path.join(directory_project_base, new_file.filename)

    historical_file.save(historical_path)
    new_file.save(new_path)

    kpi_column = request.form.get("kpi_column")
    date_column = request.form.get("date_column")

    if not kpi_column or not date_column:
        return jsonify({"error": "Both kpi_column and date_column parameters are required"}), 400

    result = analyze_similarity_with_recent_data(historical_path, new_path, kpi_column, date_column)

    return jsonify(result), 200


@main_routes.route("/<project_id>/clusters/download", methods=["POST"])
@project_validation_decorator
def download_cluster_data(project_id):

    request_data_json = request.get_json()
    list_path: list = request_data_json.get("path")

    directory_project_cluster = directory_project_path_full(project_id, list_path)
    if not os.path.exists(directory_project_cluster):
        return (jsonify({"error": "Cluster Does not exists.", "project_id": project_id}), 404)

    absolute_file_path = os.path.join(directory_project_cluster, filename_raw_data_csv())

    return send_file(absolute_file_path, as_attachment=True)


@main_routes.route("/<project_id>/features/weight/onehot", methods=["POST"])
@project_validation_decorator
def feature_ranking_weight_onehot(project_id):

    request_data_json = request.get_json()
    list_path: list = request_data_json.get("path")
    kpi = request_data_json.get("kpi")

    directory_project_cluster = directory_project_path_full(project_id, list_path)
    if not os.path.exists(directory_project_cluster):
        return (jsonify({"error": "Cluster Does not exists.", "project_id": project_id}), 404)

    if not os.path.isfile(
        os.path.join(directory_project_cluster, filename_feature_rank_score_df(kpi))
    ):
        return jsonify({"error": "Parameter weights not found"}), 400

    features = load_from_pickle(
        os.path.join(directory_project_cluster, filename_feature_rank_score_df(kpi))
    )

    return jsonify(features.to_dict(orient="records"))


@main_routes.route("/<project_id>/features/weight/label", methods=["POST"])
@project_validation_decorator
def feature_ranking_weight_label(project_id):

    request_data_json = request.get_json()
    list_path: list = request_data_json.get("path")
    kpi = request_data_json.get("kpi")

    directory_project_cluster = directory_project_path_full(project_id, list_path)
    if not os.path.exists(directory_project_cluster):
        return (jsonify({"error": "Cluster Does not exists.", "project_id": project_id}), 404)

    features = load_from_pickle(
        os.path.join(directory_project_cluster, filename_feature_rank_score_df(kpi))
    )

    return jsonify(features.to_dict(orient="records"))


@main_routes.route("/<project_id>/clusters/defination", methods=["POST"])
@project_validation_decorator
def cluster_def(project_id):

    request_data_json = request.get_json()
    list_path: list = request_data_json.get("path")
    kpi = request_data_json.get("kpi")
    cluster_label = request_data_json.get("cluster_no")

    directory_project_cluster = directory_project_path_full(project_id, list_path)
    if not os.path.exists(directory_project_cluster):
        return (jsonify({"error": "Cluster Does not exists.", "project_id": project_id}), 404)

    cluster_definitions = load_from_pickle(
        os.path.join(directory_project_cluster, filename_cluster_defs_dict_pkl())
    )
    if not os.path.isfile(
        os.path.join(directory_project_cluster, filename_cluster_defs_dict_pkl())
    ):
        return jsonify({"message": "Perform further subclustering"}), 400

    return jsonify(cluster_definitions.get(cluster_label, pd.DataFrame()).to_dict(orient="records"))


@main_routes.route("/<project_id>/clusters/summarize", methods=["POST"])
@project_validation_decorator
def summarize_cluster_info(project_id):
    request_data_json = request.get_json()
    list_path = request_data_json.get("path")

    directory_project_cluster = directory_project_path_full(project_id, list_path)
    all_clusters_summary = []

    for cluster in list_sub_directories(directory_project_cluster):
        data_raw = os.path.join(directory_project_cluster, cluster, filename_raw_data_csv())
        json_file = os.path.join(directory_project_cluster, cluster, feature_descriptions_json())
        csv_file = os.path.join(directory_project_cluster, cluster, feature_descriptions_csv())
        json_data = summerise_cluster(data_raw, csv_file, json_file)
        all_clusters_summary.append({cluster: json_data})

    return (jsonify(all_clusters_summary), 200)


@main_routes.route("/<project_id>/dataset/validate", methods=["GET", "POST"])
@project_validation_decorator
def validate_dataset(project_id):

    raw_data_file = os.path.join(
        directory_project_path_full(project_id, []), filename_raw_data_csv()
    )
    if not os.path.isfile(raw_data_file):
        return jsonify({"message": "Data set not uploaded"}), 400

    return jsonify({"message": validate_df(pd.read_csv(raw_data_file))}), 200


@main_routes.route("/<project_id>/dataset/columns", methods=["GET", "POST"])
@project_validation_decorator
def list_dataset_columns(project_id):

    raw_data_file = os.path.join(
        directory_project_path_full(project_id, []), filename_raw_data_csv()
    )
    if not os.path.isfile(raw_data_file):
        return jsonify({"message": "Data set not uploaded"}), 400

    try:
        columns = get_project_columns(project_id, raw_data_file)
        return jsonify({"columns": columns}), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 400


@main_routes.route("/<project_id>/status", methods=["GET"])
def get_project_status(project_id):
    try:

        project_data = get_project_info(project_id)

        if not project_data:
            return jsonify({"error": "Invalid Project ID"}), 400

        return jsonify(project_data), 200

    except Exception as e:

        return jsonify({"error": str(e)}), 500

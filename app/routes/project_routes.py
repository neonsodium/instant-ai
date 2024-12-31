import os
import pickle

import pandas as pd
from flask import Blueprint, jsonify, request, send_file

from app.data_preparation_ulits.preprocessing_engine import validate_df
from app.filename_utils import *
from app.ml_models.summarising import summerise_cluster
from app.os_utils import *

main_routes = Blueprint("main_routes", __name__)


@main_routes.route("/", methods=["GET"])
def get_projects():

    if not os.path.exists(all_project_dir_path()):
        return jsonify({"error": "Project directory not configured"}), 404

    try:
        projects: list = list_projects(all_project_dir_path())

    except OSError as e:
        return (
            jsonify({"error": f"An error occurred while accessing the directory: {str(e)}"}),
            500,
        )

    return jsonify({"projects": projects}), 200


@main_routes.route("/", methods=["POST"])
def create_project():
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

    new_project_id = create_project_uuid()
    result = create_directory(all_project_dir_path(), new_project_id)

    save_project_info(result["path"], filename_project_name_txt(), project_name)
    save_project_info(result["path"], filename_project_description_txt(), project_description)

    result.pop("path")
    return jsonify({"project_id": new_project_id, **result})


@main_routes.route("/<project_id>/clusters", methods=["POST"])
def get_cluster_info(project_id):

    request_data_json = request.get_json()
    level = int(request_data_json.get("level"))
    list_path = request_data_json.get("path")

    directory_project_base = directory_project_path_full(project_id, [])
    if not os.path.isdir(directory_project_base):
        return jsonify({"error": "Invalid Project ID"}), 404

    if int(level) != len(list_path):
        return jsonify({"error": "Level and Path don't match"}), 400

    directory_project_cluster = directory_project_path_full(project_id, list_path)
    if not os.path.exists(directory_project_cluster):
        return (jsonify({"error": "Cluster Does not exists.", "project_id": project_id}), 404)

    clusters = list_sub_directories(directory_project_cluster)

    return jsonify(
        {"Cluster Path": directory_project_cluster, "project_id": project_id, "clusters": clusters}
    )


@main_routes.route("/<project_id>/clusters/download", methods=["POST"])
def download_cluster_data(project_id):

    request_data_json = request.get_json()
    level = int(request_data_json.get("level"))
    list_path: list = request_data_json.get("path")

    directory_project_base = directory_project_path_full(project_id, [])
    if not os.path.isdir(directory_project_base):
        return jsonify({"error": "Invalid Project ID"}), 404

    if int(level) != len(list_path):
        return jsonify({"error": "Level and Path don't match"}), 400

    directory_project_cluster = directory_project_path_full(project_id, list_path)
    if not os.path.exists(directory_project_cluster):
        return (jsonify({"error": "Cluster Does not exists.", "project_id": project_id}), 404)

    absolute_file_path = os.path.join(directory_project_cluster, filename_raw_data_csv())

    return send_file(absolute_file_path, as_attachment=True)


@main_routes.route("/<project_id>/clusters/summarize", methods=["POST"])
def summarize_cluster_info(project_id):
    request_data_json = request.get_json()
    level = int(request_data_json.get("level"))
    list_path = request_data_json.get("path")

    if int(level) != len(list_path):
        return jsonify({"error": "Level and Path don't match"}), 400

    directory_project_cluster = directory_project_path_full(project_id, list_path)
    if not os.path.exists(directory_project_cluster):
        return (jsonify({"error": "Cluster Does not exists.", "project_id": project_id}), 404)

    clusters = list_sub_directories(directory_project_cluster)
    all_clusters_summary = []

    for cluster in clusters:
        data_raw = os.path.join(directory_project_cluster, cluster, filename_raw_data_csv())
        json_file = os.path.join(directory_project_cluster, cluster, feature_descriptions_json())
        csv_file = os.path.join(directory_project_cluster, cluster, feature_descriptions_csv())
        json_data = summerise_cluster(data_raw, csv_file, json_file)
        all_clusters_summary.append({cluster: json_data})

    return (jsonify(all_clusters_summary), 200)


@main_routes.route("/<project_id>/dataset/validate", methods=["GET", "POST"])
def validate_dataset(project_id):
    directory_project = directory_project_path_full(project_id, [])
    if not os.path.isdir(directory_project):
        return jsonify({"error": "Invalid Project ID"}), 400

    raw_data_file = os.path.join(directory_project, filename_raw_data_csv())
    if not os.path.isfile(raw_data_file):
        return jsonify({"message": "Data set not uploaded"}), 400

    return jsonify({"message": validate_df(pd.read_csv(raw_data_file))}), 200


@main_routes.route("/<project_id>/dataset/columns", methods=["GET", "POST"])
def list_dataset_columns(project_id):

    directory_project = directory_project_path_full(project_id, [])

    if not os.path.isdir(directory_project):
        return jsonify({"error": "Invalid Project ID"}), 400

    raw_data_file = os.path.join(directory_project, filename_raw_data_csv())
    if not os.path.isfile(raw_data_file):
        return jsonify({"message": "Data set not uploaded"}), 400

    drop_column_file = os.path.join(directory_project, filename_dropeed_column_data_csv())
    if os.path.isfile(drop_column_file):
        df = pd.read_csv(drop_column_file)
    else:
        df = pd.read_csv(raw_data_file)

    return jsonify({"columns": list(df.columns)}), 200


@main_routes.route("/files", methods=["GET"])
def list_all_files_in_projects():
    """
    Lists all files in the root directory and its subdirectories.
    """
    directory_project = all_project_dir_path()
    file_list = []
    for root, _, files in os.walk(directory_project):
        for file in files:
            full_path = os.path.join(root, file)
            # Make paths relative to the root directory
            relative_path = os.path.relpath(full_path, directory_project)
            file_list.append(relative_path)
    return jsonify({"files": file_list})


@main_routes.route("/files/download", methods=["GET"])
def download_project_file():
    """
    Downloads a file if the path is provided and valid.
    """
    directory_project = all_project_dir_path()
    relative_path = request.args.get("path", None)
    if not relative_path:
        return jsonify({"error": "The 'path' query parameter is required."}), 400

    absolute_file_path = os.path.abspath(os.path.join(directory_project, relative_path))
    if not absolute_file_path.startswith(os.path.abspath(directory_project)):
        # return jsonify({"error": "Access to the file is forbidden."}), 403
        return jsonify({"error": "File not found."}), 404

    if not os.path.exists(absolute_file_path) or not os.path.isfile(absolute_file_path):
        return jsonify({"error": "File not found."}), 404

    return send_file(absolute_file_path, as_attachment=True)


@main_routes.route("/<project_id>/status", methods=["GET"])
def get_project_status(project_id):
    try:
        # TODO
        # Construct the full directory path
        directory_project = directory_project_path_full(project_id, [])

        # Check if the directory exists
        if not os.path.isdir(directory_project):
            return jsonify({"error": "Invalid Project ID"}), 400

        # Check if the raw data file exists
        raw_data_file = os.path.join(directory_project, filename_raw_data_csv())
        data_uploaded = os.path.isfile(raw_data_file)

        # Check if feature ranking file exists
        feature_ranking_completed = is_feature_ranking_file_present(directory_project)

        # Get the clusters directory and subdirectories
        directory_project_cluster = directory_project_path_full(project_id, [])
        clusters_tree = get_directory_tree(directory_project_cluster)
        clusters = list_sub_directories(directory_project_cluster)

        # Attempt to load the KPI list
        kpi_list_filepath = os.path.join(directory_project, filename_kpi_list_pkl())
        try:
            with open(kpi_list_filepath, "rb") as kpi_list_pkl_file:
                kpi = pickle.load(kpi_list_pkl_file)
        except FileNotFoundError:
            return jsonify({"error": "KPI list file not found"}), 404
        except pickle.UnpicklingError:
            return jsonify({"error": "Failed to unpickle the KPI list file"}), 500

        # Attempt to load the important features file
        important_features_filepath = os.path.join(
            directory_project, filename_important_features_list_pkl(kpi)
        )
        try:
            with open(important_features_filepath, "rb") as important_features_list_pkl_file:
                important_features = pickle.load(important_features_list_pkl_file)
        except FileNotFoundError:
            return jsonify({"error": "Important features file not found"}), 404
        except pickle.UnpicklingError:
            return jsonify({"error": "Failed to unpickle the important features file"}), 500

        # Attempt to load the all KPI list file
        all_kpi_list_filepath = os.path.join(directory_project, filename_all_kpi_list_pkl())
        try:
            with open(all_kpi_list_filepath, "rb") as all_kpi_list_pkl_file:
                kpi_list = pickle.load(all_kpi_list_pkl_file)
        except FileNotFoundError:
            return jsonify({"error": "All KPI list file not found"}), 404
        except pickle.UnpicklingError:
            return jsonify({"error": "Failed to unpickle the all KPI list file"}), 500

        # Check if clustering has started by checking if the directory is not empty
        clustering_started = False
        if os.path.isdir(directory_project_cluster) and any(os.listdir(directory_project_cluster)):
            clustering_started = True

        # Prepare the response data
        status = {
            "data_uploaded": data_uploaded,
            "feature_ranking_completed": feature_ranking_completed,
            "clustering_started": clustering_started,
            "clusters": clusters_tree,
            "important_features": important_features,
            "kpi": kpi,
            "kpi_list": kpi_list,
        }

        return jsonify(status)

    except Exception as e:
        # Catch any unexpected exceptions
        return jsonify({"error": str(e)}), 500


@main_routes.route("/<project_id>/clusters/status", methods=["POST"])
def get_cluster_status(project_id):
    task_name = "clustering"
    # TODO add target varibale
    request_data_json = request.get_json()
    list_path = request_data_json.get("path")
    level = int(request_data_json.get("level"))
    kpi = request_data_json.get("kpi")

    directory_project_base = directory_project_path_full(project_id, [])
    if not os.path.isdir(directory_project_base):
        return jsonify({"error": "Invalid Project ID"}), 400

    if not kpi:
        return jsonify({"error": "Missing 'kpi' in request"}), 400

    input_file_path_feature_rank_pkl = os.path.join(
        directory_project_base, filename_feature_rank_list_pkl(kpi)
    )
    if not os.path.exists(input_file_path_feature_rank_pkl):
        return (
            jsonify(
                {"error": f"Feature ranking file for {kpi} not found.", "project_id": project_id}
            ),
            404,
        )

    if int(level) != len(list_path):
        return jsonify({"error": "Level and Path don't match"}), 400

    directory_project_cluster = directory_project_path_full(project_id, list_path)
    if not os.path.exists(directory_project_cluster):
        return (jsonify({"status": False, "project_id": project_id}), 404)

    return (jsonify({"status": True, "project_id": project_id}), 200)


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

    # Get all feature names generated by the encoder
    all_encoded_columns = encoder.get_feature_names_out(categorical_columns)

    # Filter feature names to include only those for the specified column
    encoded_columns = [col for col in all_encoded_columns if col.startswith(f"{column_name}_")]

    return encoded_columns


@main_routes.route("/<project_id>/time-series/encoded-columns", methods=["POST"])
def get_one_hot_encoded_columns(project_id):
    request_data_json = request.get_json()
    level = int(request_data_json.get("level"))
    list_path = request_data_json.get("path", [])
    column_name = request_data_json.get("column_name")

    directory_project_base = directory_project_path_full(project_id, [])
    if not os.path.isdir(directory_project_base):
        return jsonify({"error": "Invalid Project ID"}), 404

    if int(level) != len(list_path):
        return jsonify({"error": "Level and Path don't match"}), 400

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

    print(categorical_columns)

    encoded_columns = get_encoded_columns_for_column(column_name, encoder, categorical_columns)

    return jsonify({"categorical_column": encoded_columns}), 200


@main_routes.route("/<project_id>/time-series/encoded-columns", methods=["POST"])
def get_one_hot_encoded_columns(project_id):
    request_data_json = request.get_json()
    level = int(request_data_json.get("level"))
    list_path = request_data_json.get("path", [])
    column_name = request_data_json.get("column_name")

    directory_project_base = directory_project_path_full(project_id, [])
    if not os.path.isdir(directory_project_base):
        return jsonify({"error": "Invalid Project ID"}), 404

    if int(level) != len(list_path):
        return jsonify({"error": "Level and Path don't match"}), 400

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


@main_routes.route("/<project_id>/time-series/categorical-columns", methods=["GET"])
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
        level = int(request_data_json.get("level"))
        list_path = request_data_json.get("path", [])

        directory_project_base = directory_project_path_full(project_id, [])
        if not os.path.isdir(directory_project_base):
            return jsonify({"error": "Invalid Project ID"}), 404

        if int(level) != len(list_path):
            return jsonify({"error": "Level and Path don't match"}), 400

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

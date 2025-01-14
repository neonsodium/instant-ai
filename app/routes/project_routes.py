import os

import pandas as pd
from flask import Blueprint, jsonify, request, send_file

from app.data_preparation_ulits.preprocessing_engine import validate_df
from app.ml_models.summarising import summerise_cluster
from app.models.project_model import ProjectModel
from app.utils.filename_utils import (create_project_uuid,
                                      feature_descriptions_csv,
                                      feature_descriptions_json,
                                      filename_feature_rank_list_pkl,
                                      filename_raw_data_csv)
from app.utils.os_utils import (all_project_dir_path, create_directory,
                                directory_project_path_full,
                                list_sub_directories)

project_model = ProjectModel()
main_routes = Blueprint("main_routes", __name__)


@main_routes.route("/", methods=["GET"])
def get_projects():
    """
    Retrieve all projects from the database.

    Returns:
        Response: A JSON response containing a list of projects or an error message.
    """
    try:
        # Fetch projects from the database using ProjectModel
        projects = project_model.get_all_projects()

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

    # Validate input
    if not project_name:
        return jsonify({"error": "Project name is required"}), 400
    if len(project_name) > 100:
        return jsonify({"error": "Project name must not exceed 100 characters"}), 400
    if not project_description:
        return jsonify({"error": "Project description is required"}), 400
    if len(project_description) > 500:
        return jsonify({"error": "Project description must not exceed 500 characters"}), 400

    # Generate a new project ID
    new_project_id = create_project_uuid()

    # Create the directory structure
    directory_result = create_directory(all_project_dir_path(), new_project_id)
    if directory_result["status"] != "success":
        return jsonify({"error": directory_result["message"]}), 500

    # Save the project to MongoDB
    try:
        project = project_model.create_project(new_project_id, project_name, project_description)
        return jsonify({"project": project, **directory_result}), 201
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": f"Failed to create project: {str(e)}"}), 500


@main_routes.route("/<project_id>/clusters", methods=["POST"])
def get_cluster_info(project_id):

    request_data_json = request.get_json()
    level = int(request_data_json.get("level"))
    list_path = request_data_json.get("path")

    project = project_model.collection.find_one({"_id": project_id})
    if not project:
        return jsonify({"error": "Invalid Project ID"}), 400

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
    list_path: list = request_data_json.get("path")

    directory_project_base = directory_project_path_full(project_id, [])
    if not os.path.isdir(directory_project_base):
        return jsonify({"error": "Invalid Project ID"}), 404

    project = project_model.collection.find_one({"_id": project_id})
    if not project:
        return jsonify({"error": "Invalid Project ID"}), 400

    directory_project_cluster = directory_project_path_full(project_id, list_path)
    if not os.path.exists(directory_project_cluster):
        return (jsonify({"error": "Cluster Does not exists.", "project_id": project_id}), 404)

    absolute_file_path = os.path.join(directory_project_cluster, filename_raw_data_csv())

    return send_file(absolute_file_path, as_attachment=True)


@main_routes.route("/<project_id>/clusters/summarize", methods=["POST"])
def summarize_cluster_info(project_id):
    request_data_json = request.get_json()
    list_path = request_data_json.get("path")

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

    project = project_model.collection.find_one({"_id": project_id})
    if not project:
        return jsonify({"error": "Invalid Project ID"}), 400

    raw_data_file = os.path.join(directory_project, filename_raw_data_csv())
    if not os.path.isfile(raw_data_file):
        return jsonify({"message": "Data set not uploaded"}), 400

    return jsonify({"message": validate_df(pd.read_csv(raw_data_file))}), 200


@main_routes.route("/<project_id>/dataset/columns", methods=["GET", "POST"])
def list_dataset_columns(project_id):
    directory_project = directory_project_path_full(project_id, [])

    project = project_model.collection.find_one({"_id": project_id})
    if not project:
        return jsonify({"error": "Invalid Project ID"}), 400

    raw_data_file = os.path.join(directory_project, filename_raw_data_csv())
    if not os.path.isfile(raw_data_file):
        return jsonify({"message": "Data set not uploaded"}), 400

    # TODO Make function
    columns = project.get("columns", [])
    if not columns:
        df = pd.read_csv(raw_data_file)
        columns = list(df.columns)

        project_model.collection.update_one({"_id": project_id}, {"$set": {"columns": columns}})

    return jsonify({"columns": columns}), 200


@main_routes.route("/<project_id>/status", methods=["GET"])
def get_project_status(project_id):
    try:

        project_data = project_model.collection.find_one({"_id": project_id})

        if not project_data:
            return jsonify({"error": "Invalid Project ID"}), 400

        # Convert the MongoDB object to JSON serializable format
        project_data["_id"] = str(project_data["_id"])

        return jsonify(project_data), 200

    except Exception as e:

        return jsonify({"error": str(e)}), 500


@main_routes.route("/<project_id>/clusters/status", methods=["POST"])
def get_cluster_status(project_id):
    # TODO add target varibale
    request_data_json = request.get_json()
    list_path = request_data_json.get("path")
    kpi = request_data_json.get("kpi")

    directory_project_base = directory_project_path_full(project_id, [])
    if not os.path.isdir(directory_project_base):
        return jsonify({"error": "Invalid Project ID"}), 400

    project = project_model.collection.find_one({"_id": project_id})
    if not project:
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

    directory_project_cluster = directory_project_path_full(project_id, list_path)
    if not os.path.exists(directory_project_cluster):
        return (jsonify({"status": False, "project_id": project_id}), 404)

    return (jsonify({"status": True, "project_id": project_id}), 200)

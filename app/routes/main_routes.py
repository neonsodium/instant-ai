import os

from flask import Blueprint, abort, jsonify, request, send_file
import pandas as pd
from app.filename_utils import *
from app.ml_models.summarising import summerise_cluster
from app.os_utils import *
from app.data_preparation_ulits.preprocessing_engine import validate_dataset

main_routes = Blueprint("main_routes", __name__)


@main_routes.route("/get-projects", methods=["GET", "POST"])
def list_tasks():

    if not os.path.exists(all_project_dir_path()):
        return jsonify({"error": "Project directory not configured"}), 404

    try:
        projects: list = list_sub_directories(all_project_dir_path())

    except OSError as e:
        return (
            jsonify(
                {"error": f"An error occurred while accessing the directory: {str(e)}"}
            ),
            500,
        )

    return jsonify({"projects": projects}), 200


@main_routes.route("/create-project", methods=["GET", "POST"])
def create_new_project():
    new_project_id = create_project_uuid()
    result = create_directory(all_project_dir_path(), new_project_id)
    return jsonify({"project_id": new_project_id, **result})


@main_routes.route("/cluster-info", methods=["POST"])
def display_cluster():
    """
    curl -X POST http://localhost:8080/get_clusters \
    -H "Content-Type: application/json" \
    -d '{
            "level": 3,
            "path": [1, 2, 1],
            "project_id": "ID"
        }'
    """

    request_data_json = request.get_json()
    level = int(request_data_json.get("level"))
    path = request_data_json.get("path")
    project_id = os.path.basename(request_data_json.get("project_id"))
    del request_data_json
    # total paths should be equal to level
    if int(level) != len(path):
        return jsonify({"error": "Level and Path don't match"}), 400

    directory_cluster = directory_project_path_full(project_id, path)
    clusters = list_sub_directories(directory_cluster)

    return jsonify(
        {
            "Cluster Path": directory_cluster,
            "project_id": project_id,
            "clusters": clusters,
        }
    )


@main_routes.route("/summerising", methods=["POST"])
def start_summerising():
    """
    curl -X POST http://127.0.0.1:8080/process/summerising -H "Content-Type: application/json" -d '{
    "level": 3,
    "path": [1, 2, 1]
    }'
    """
    request_data_json = request.get_json()
    level = int(request_data_json.get("level"))
    path = request_data_json.get("path")
    project_id = os.path.basename(request_data_json.get("project_id"))
    del request_data_json
    # total paths should be equal to level
    if int(level) != len(path):
        return jsonify({"error": "Level and Path don't match"}), 400

    directory_project = directory_project_path_full(project_id, path)
    clusters = list_sub_directories(directory_project)

    for cluster in clusters:
        data_raw = os.path.join(directory_project, cluster, filename_raw_data_csv())
        json_file = os.path.join(
            directory_project, cluster, feature_descriptions_json()
        )
        csv_file = os.path.join(directory_project, cluster, feature_descriptions_csv())
        summerise_cluster(data_raw, json_file, csv_file)

    return (
        jsonify(
            {
                "message": "File encoding has started",
                "Project_id": project_id,
                "project_dir": os.path.join(
                    directory_project, filename_label_encoded_data_csv()
                ),
            }
        ),
        202,
    )


@main_routes.route("/validator", methods=["POST"])
def validate_data():
    """
    curl -X POST http://127.0.0.1:8080/validator -H "Content-Type: application/json" -d '{
    "project_id": "ID"
    }'
    """
    request_data_json = request.get_json()
    project_id = os.path.basename(request_data_json.get("project_id"))
    directory_project = directory_project_path_full(project_id, [])

    if not os.path.isdir(directory_project):
        return jsonify({"error": "Invalid Project ID"}), 400

    raw_data_file = os.path.join(directory_project, filename_raw_data_csv())
    if not os.path.isfile(raw_data_file):
        return jsonify({"message": "Data set not uploaded"}), 400

    df = pd.read_csv(raw_data_file)
    result = validate_dataset(df)
    print(result)

    return jsonify({"message": result}), 200


@main_routes.route("/list-column", methods=["POST"])
def list_column():
    """
    curl -X POST http://127.0.0.1:8080/list-column -H "Content-Type: application/json" -d '{
    "project_id": "ID",
    }'
    """
    request_data_json = request.get_json()
    project_id = os.path.basename(request_data_json.get("project_id"))
    directory_project = directory_project_path_full(project_id, [])

    if not os.path.isdir(directory_project):
        return jsonify({"error": "Invalid Project ID"}), 400

    raw_data_file = os.path.join(directory_project, filename_raw_data_csv())
    if not os.path.isfile(raw_data_file):
        return jsonify({"message": "Data set not uploaded"}), 400

    drop_column_file = os.path.join(
        directory_project, filename_dropeed_column_data_csv()
    )
    if os.path.isfile(drop_column_file):
        df = pd.read_csv(drop_column_file)
    else:
        df = pd.read_csv(raw_data_file)

    return jsonify({"columns": list(df.columns)}), 200


@main_routes.route("/list-files", methods=["GET"])
def list_files():
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


@main_routes.route("/download", methods=["GET"])
def download_file():
    """
    Downloads a file if the path is provided and valid.
    """
    directory_project = all_project_dir_path()
    relative_path = request.args.get("path", None)
    if not relative_path:
        return abort(400, description="The 'path' query parameter is required.")

    # Ensure the path is within the ROOT_DIRECTORY
    absolute_path = os.path.abspath(os.path.join(directory_project, relative_path))
    if not absolute_path.startswith(os.path.abspath(directory_project)):
        return abort(403, description="Access to the file is forbidden.")

    if not os.path.exists(absolute_path) or not os.path.isfile(absolute_path):
        return abort(404, description="File not found.")

    return send_file(absolute_path, as_attachment=True)


@main_routes.route("/time-series", methods=["POST"])
def start_time_series():
    """
    curl -X POST http://127.0.0.1:8080/process/summerising -H "Content-Type: application/json" -d '{
    "level": 3,
    "path": [1, 2, 1]
    }'
    """
    request_data_json = request.get_json()
    level = int(request_data_json.get("level"))
    path = request_data_json.get("path")
    project_id = os.path.basename(request_data_json.get("project_id"))
    del request_data_json
    # total paths should be equal to level
    if int(level) != len(path):
        return jsonify({"error": "Level and Path don't match"}), 400

    directory_project = directory_project_path_full(project_id, path)
    clusters = list_sub_directories(directory_project)

    for cluster in clusters:
        data_raw = os.path.join(directory_project, cluster, filename_raw_data_csv())
        json_file = os.path.join(
            directory_project, cluster, feature_descriptions_json()
        )
        csv_file = os.path.join(directory_project, cluster, feature_descriptions_csv())
        summerise_cluster(data_raw, csv_file, json_file)

    return (
        jsonify(
            {
                "message": "File encoding has started",
                "Project_id": project_id,
                "project_dir": os.path.join(
                    directory_project, filename_label_encoded_data_csv()
                ),
            }
        ),
        202,
    )

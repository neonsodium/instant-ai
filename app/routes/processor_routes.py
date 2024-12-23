import os

from flask import Blueprint, jsonify, request

from app.filename_utils import *
from app.os_utils import *
from app.tasks import *

processor_routes = Blueprint("processor_routes", __name__)


@processor_routes.route("/tasks/<task_id>/status", methods=["GET", "POST"])
def get_task_status_by_id(task_id):
    result = celery.AsyncResult(task_id)
    return jsonify({"status": result.status})


@processor_routes.route("/<project_id>/files/upload", methods=["POST"])
def upload_project_file(project_id):

    directory_project_base = directory_project_path_full(project_id, [])
    if not os.path.isdir(directory_project_base):
        return jsonify({"error": "Invalid Project ID"}), 400

    if "file" not in request.files:
        return jsonify({"error": "No file part in the request"}), 400

    file = request.files["file"]
    if file:
        result = async_save_file.delay(directory_project_base, file.read())

        return (jsonify({"message": "File processing has started", "task_id": result.id}), 202)
    else:
        return jsonify({"error": "Invalid file type"}), 400


@processor_routes.route("/<project_id>/dataset/columns/drop", methods=["POST"])
def drop_columns_from_dataset(project_id):
    request_data_json = request.get_json()

    directory_project = directory_project_path_full(project_id, [])
    drop_column_list = request_data_json.get("column", [])

    if not os.path.isdir(directory_project):
        return jsonify({"error": "Invalid Project ID"}), 400

    raw_data_file = os.path.join(directory_project, filename_raw_data_csv())
    if not os.path.isfile(raw_data_file):
        return jsonify({"message": "Data set not uploaded"}), 400

    if not drop_column_list:
        return jsonify({"error": "Invaild column"}), 400

    result = async_drop_columns.delay(directory_project, drop_column_list)

    return (jsonify({"message": "Column droppping has started", "task_id": result.id}), 202)


@processor_routes.route("/<project_id>/dataset/preprocess", methods=["GET", "POST"])
def start_data_preprocessing(project_id):
    """
    curl -X POST http://127.0.0.1:8080/process/pre-process -H "Content-Type: application/json" -d '{
    "project_id": "ID"
    }'
    """
    directory_project = directory_project_path_full(project_id, [])

    if not os.path.isdir(directory_project):
        return jsonify({"error": "Invalid Project ID"}), 400

    if not os.path.isfile(os.path.join(directory_project, filename_raw_data_csv())):
        return jsonify({"message": "Data set not uploaded"}), 400

    result = async_data_processer.delay(directory_project)
    return (jsonify({"message": "File pre-processing has started", "task_id": result.id}), 202)


@processor_routes.route("/<project_id>/features/ranking", methods=["POST"])
def start_feature_ranking(project_id):
    request_data_json = request.get_json()
    kpi_list = request_data_json.get("kpi_list", [])  # i.e drops these columns
    important_features = request_data_json.get("important_features", [])
    kpi = request_data_json.get("kpi", None)

    directory_project = directory_project_path_full(project_id, [])
    if not os.path.isdir(directory_project):
        return jsonify({"error": "Invalid Project ID"}), 400

    if not kpi:
        return jsonify({"error": "Missing 'kpi' in request"}), 400

    result = async_optimised_feature_rank.delay(
        kpi, kpi_list, important_features, directory_project
    )
    return (
        jsonify(
            {
                "message": "Feature Ranking has started",
                "task_id": str(result.id),
                "Project_id": project_id,
            }
        ),
        202,
    )


@processor_routes.route("/<project_id>/clusters/subcluster", methods=["POST"])
def initiate_subclustering(project_id):
    """
    curl -X POST http://127.0.0.1:8080/process -H "Content-Type: application/json" -d '{
    "kpi": "amount_paid",
    "level": 3,
    "path": [1, 2, 1]
    }'
    """
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

    # directory_project_kpi = os_path_join_secure(directory_project_base, target_var)
    # os.makedirs(directory_project_kpi, exist_ok=True)

    directory_project_cluster = directory_project_path_full(project_id, list_path)
    if not os.path.exists(directory_project_cluster):
        return (jsonify({"error": "Cluster Does not exists.", "project_id": project_id}), 404)

    result = async_optimised_clustering.delay(
        directory_project_cluster, input_file_path_feature_rank_pkl
    )

    return (
        jsonify(
            {"message": "Clustering has started", "task_id": result.id, "Project_id": project_id}
        ),
        202,
    )

import os

from flask import Blueprint, jsonify, request

from app.filename_utils import *
from app.os_utils import *
from app.tasks import *

processor_routes = Blueprint("processor_routes", __name__)


@processor_routes.route("/check-task/<task_id>", methods=["GET"])
def check_task(task_id):
    result = celery.AsyncResult(task_id)
    return jsonify({"status": result.status})


@processor_routes.route("/upload", methods=["POST"])
def upload_file():
    """
    curl -X POST http://127.0.0.1:8080/process/upload -H "Content-Type: application/json" -d '{
    "project_id": "ID",
    }'
    """
    request_data_json = request.get_json()
    project_id = os.path.basename(request_data_json.get("project_id"))

    directory_project = directory_project_path_full(project_id, [])
    if not os.path.isdir(directory_project):
        return jsonify({"error": "Invalid Project ID"}), 400

    if "file" not in request.files:
        return jsonify({"error": "No file part in the request"}), 400

    file = request.files["file"]
    if file:
        result = async_save_file.delay(directory_project, file.read())

        return (jsonify({"message": "File processing has started", "task_id": result.id}), 202)
    else:
        return jsonify({"error": "Invalid file type"}), 400


@processor_routes.route("/drop-column", methods=["POST"])
def drop_column():
    """
    curl -X POST http://127.0.0.1:8080/process/drop-column -H "Content-Type: application/json" -d '{
    "project_id": "ID",
    "column": ["COL1", "COL2", "COL3"]
    }'
    """
    request_data_json = request.get_json()
    project_id = os.path.basename(request_data_json.get("project_id"))
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


@processor_routes.route("/pre-process", methods=["POST"])
def start_pre_processing():
    """
    curl -X POST http://127.0.0.1:8080/process/pre-process -H "Content-Type: application/json" -d '{
    "project_id": "ID"
    }'
    """
    request_data_json = request.get_json()
    project_id = os.path.basename(request_data_json.get("project_id"))
    directory_project = directory_project_path_full(project_id, [])

    if not os.path.isdir(directory_project):
        return jsonify({"error": "Invalid Project ID"}), 400

    if not os.path.isfile(os.path.join(directory_project, filename_raw_data_csv())):
        return jsonify({"message": "Data set not uploaded"}), 400

    result = async_data_processer.delay(directory_project)
    return (jsonify({"message": "File pre-processing has started", "task_id": result.id}), 202)


@processor_routes.route("/feature-ranking", methods=["POST"])
def start_feature_ranking():
    """
    curl -X POST http://127.0.0.1:8080/process/feature-ranking -H "Content-Type: application/json" -d '{
    "target_vars_list": ["reading_fee_paid", "Number_of_Months", "Coupon_Discount", "num_books", "magazine_fee_paid", "Renewal_Amount", "amount_paid"],
    "target_var": "amount_paid",
    }'
    """
    request_data_json = request.get_json()
    project_id = os.path.basename(request_data_json.get("project_id"))
    target_vars_list = request_data_json.get("target_vars_list", [])
    target_var = request_data_json.get("target_var", None)

    directory_project = directory_project_path_full(project_id, [])
    result = async_optimised_feature_rank.delay(target_var, target_vars_list, directory_project)
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


@processor_routes.route("/time-series", methods=["POST"])
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
    if int(level) != len(path):
        return jsonify({"error": "Level and Path don't match"}), 400

    directory_project = directory_project_path_full(project_id, path)
    clusters = list_sub_directories(directory_project)

    return (
        jsonify(
            {
                "message": "File encoding has started",
                "Project_id": project_id,
                "project_dir": os.path.join(directory_project, filename_label_encoded_data_csv()),
            }
        ),
        202,
    )


@processor_routes.route("/cluster", methods=["POST"])
def start_sub_clustering():
    """
    curl -X POST http://127.0.0.1:8080/process -H "Content-Type: application/json" -d '{
    "target_var": "amount_paid",
    "level": 3,
    "path": [1, 2, 1]
    }'
    """
    # TODO add target varibale
    request_data_json = request.get_json()
    project_id = os.path.basename(request_data_json.get("project_id"))
    list_path = request_data_json.get("path")
    level = int(request_data_json.get("level"))
    target_var = request_data_json.get("target_var")

    directory_project_base = directory_project_path_full(project_id, [])
    if not os.path.isdir(directory_project_base):
        return jsonify({"error": "Invalid Project ID"}), 400

    input_file_path_feature_rank_pkl = os.path.join(
        directory_project_base, filename_feature_rank_list_pkl(target_var)
    )
    if not os.path.exists(input_file_path_feature_rank_pkl):
        return (
            jsonify(
                {
                    "error": f"Feature ranking file for {target_var} not found.",
                    "project_id": project_id,
                }
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

import os

from flask import Blueprint, jsonify, request
import pandas as pd
from app.filename_utils import *
from app.os_utils import *
from app.tasks import *

processor_routes = Blueprint("processor_routes", __name__)


@processor_routes.route("/check-task/<task_id>", methods=["GET"])
def check_task(task_id):
    result = celery.AsyncResult(task_id)
    return jsonify({"status": result.status})


# TODO seperate the preprocessing
@processor_routes.route("/upload", methods=["POST"])
def upload_file():
    project_id = os.path.basename(request.form.get("project_id"))
    directory_project = directory_project_path_full(project_id, [])

    if not os.path.isdir(directory_project):
        return jsonify({"error": "Invalid Project ID"}), 400

    if "file" not in request.files:
        return jsonify({"error": "No file part in the request"}), 400

    file = request.files["file"]
    if file:
        result = async_save_file.delay(directory_project, file.read())

        return (
            jsonify({"message": "File processing has started", "task_id": result.id}),
            202,
        )
    else:
        return jsonify({"error": "Invalid file type"}), 400


@processor_routes.route("/drop-column", methods=["POST"])
def drop_column():
    """
    curl -X POST http://127.0.0.1:8080/process/pre-process -H "Content-Type: application/json" -d '{
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

    drop_column_file = os.path.join(
        directory_project, filename_dropeed_column_data_csv()
    )
    if os.path.isfile(drop_column_file):
        df = pd.read_csv(drop_column_file)
    else:
        df = pd.read_csv(raw_data_file)

    df.drop(
        drop_column_list,
        axis=1,
        inplace=True,
    )
    df.to_csv(drop_column_file, index=False)
    return jsonify({"message": "Column removal process successfully."}), 200


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

    if os.path.isfile(os.path.join(directory_project, filename_raw_data_csv())):
        result = async_data_processer.delay(directory_project)
        return (
            jsonify(
                {"message": "File pre-processing has started", "task_id": result.id}
            ),
            202,
        )
    else:
        return jsonify({"message": "Data set not uploaded"}), 400


@processor_routes.route("/feature-ranking", methods=["POST"])
def start_feature_ranking():
    """
    curl -X POST http://127.0.0.1:8080/process/feature-ranking -H "Content-Type: application/json" -d '{
    "target_vars_list": ["reading_fee_paid", "Number_of_Months", "Coupon_Discount", "num_books", "magazine_fee_paid", "Renewal_Amount", "amount_paid"],
    "target_var": "amount_paid",
    "level": 3,
    "path": [1, 2, 1]
    }'
    """
    request_data_json = request.get_json()
    project_id = os.path.basename(request_data_json.get("project_id"))
    list_path = request_data_json.get("path")
    target_vars_list = request_data_json.get("target_vars_list", [])
    target_var = request_data_json.get("target_var", None)

    # target_vars_list = [
    #     "reading_fee_paid",
    #     "Number_of_Months",
    #     "Coupon_Discount",
    #     "num_books",
    #     "magazine_fee_paid",
    #     "Renewal_Amount",
    #     "amount_paid",]
    # target_var = "amount_paid"

    directory_project = directory_project_path_full(project_id, list_path)
    result = async_optimised_feature_rank.delay(
        target_var, target_vars_list, directory_project
    )
    return (
        jsonify(
            {
                "message": "Feature Ranking has started",
                "task_id": str(result.id),
                "Project_id": project_id,
                "project_dir": os.path.join(
                    directory_project, filename_label_encoded_data_csv()
                ),
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
        # summerise_cluster(data_raw, csv_file, json_file)

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
    path = request_data_json.get("path")
    if int(level) != len(path):
        return jsonify({"error": "Level and Path don't match"}), 400

    directory_project_base = directory_project_path_full(project_id, [])
    directory_project_cluster = directory_project_path_full(project_id, list_path)
    input_file_path_feature_rank_pkl = os.path.join(
        directory_project_base, filename_feature_rank_list_pkl()
    )

    if not os.path.exists(input_file_path_feature_rank_pkl):
        return (
            jsonify(
                {"error": "Feature ranking file not found", "project_id": project_id}
            ),
            404,
        )

    result = async_optimised_clustering.delay(
        directory_project_cluster, input_file_path_feature_rank_pkl
    )

    return (
        jsonify(
            {
                "message": "Clustering has started",
                "task_id": result.id,
                "Project_id": project_id,
                "project_dir": directory_project_cluster,
            }
        ),
        202,
    )

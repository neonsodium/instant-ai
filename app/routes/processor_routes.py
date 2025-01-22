import json
import os
from datetime import datetime

from flask import Blueprint, jsonify, request
from redis import Redis
from werkzeug.utils import secure_filename

from app import celery
from app.decorator import task_manager_decorator
from app.models.project_model import ProjectModel
from app.tasks import (
    async_drop_columns,
    async_optimised_clustering,
    async_optimised_feature_rank,
    async_save_file,
    async_time_series_analysis,
    async_connector_table,
)
from app.utils.filename_utils import filename_raw_data_csv, filename_feature_rank_list_pkl
from app.utils.model_utils import get_project_columns
from app.utils.os_utils import directory_project_path_full
from config import Config

processor_routes = Blueprint("processor_routes", __name__)
redis_client = Redis(host=Config.REDIS_HOST, port=Config.REDIS_PORT)
project_model = ProjectModel()


@processor_routes.route("/tasks/<task_id>/status", methods=["GET", "POST"])
def get_task_status_by_id(task_id):
    result = celery.AsyncResult(task_id)
    return jsonify({"status": result.status})


@processor_routes.route("/tasks/running", methods=["GET"])
def list_running_tasks():
    running_tasks = redis_client.hgetall("running_tasks")

    tasks_list = []
    for task_id, task_info in running_tasks.items():
        task_info = json.loads(task_info)
        tasks_list.append(task_info)

    return jsonify({"running_tasks": tasks_list}), 200


# Cant add decorator coz no json in request
@processor_routes.route("/<project_id>/files/upload", methods=["POST"])
def upload_project_file(project_id):

    directory_project_base = directory_project_path_full(project_id, [])

    project = project_model.collection.find_one({"_id": project_id})
    if not project:
        return jsonify({"error": "Invalid Project ID"}), 400

    if not os.path.isdir(directory_project_base):
        return jsonify({"error": "Invalid Project ID"}), 400

    if "file" not in request.files:
        return jsonify({"error": "No file part in the request"}), 400

    file = request.files["file"]

    if file:
        filename = secure_filename(file.filename)
        file_path = os.path.join(directory_project_base, filename_raw_data_csv())

        project = project_model.collection.find_one({"_id": project_id})

        if not project:
            return jsonify({"error": "Project not found"}), 404

        file.seek(0, os.SEEK_END)
        file_size = file.tell()
        file.seek(0)

        file_metadata = {
            "filename": filename,
            "file_path": file_path,
            "size": file_size,
            "uploaded_at": datetime.now().isoformat(),
        }

        if (
            project_model.collection.update_one(
                {"_id": project_id}, {"$push": {"files": file_metadata}}
            ).modified_count
            == 0
        ):
            return jsonify({"error": "Failed to update project with file details"}), 500

        result = async_save_file.apply_async(
            args=[directory_project_base, file.read()], kwargs={"project_id": project_id}
        )

        return (
            jsonify(
                {
                    "message": "File processing has started",
                    "task_id": result.id,
                    "project_id": project_id,
                }
            ),
            202,
        )
    else:
        return jsonify({"error": "Invalid file type"}), 400


@processor_routes.route("/<project_id>/dataset/columns/drop", methods=["POST"])
@task_manager_decorator("drop_columns")
def drop_columns_from_dataset(project_id, task_key=None, task_params=None):
    request_data_json = request.get_json()

    directory_project = directory_project_path_full(project_id, [])
    drop_column_list = request_data_json.get("column", [])

    project = project_model.collection.find_one({"_id": project_id})
    if not project:
        return jsonify({"error": "Invalid Project ID"}), 400

    if not os.path.isdir(directory_project):
        return jsonify({"error": "Project directory not found"}), 400

    raw_data_file = os.path.join(directory_project, filename_raw_data_csv())
    if not os.path.isfile(raw_data_file):
        return jsonify({"message": "Data set not uploaded"}), 400

    if not drop_column_list:
        return jsonify({"error": "Invalid column list"}), 400

    try:
        current_columns = get_project_columns(project_id, raw_data_file)
    except ValueError as e:
        return jsonify({"error": str(e)}), 400

    if not any(col in current_columns for col in drop_column_list):
        return (
            jsonify({"error": "None of the specified columns to drop exist in the dataset."}),
            400,
        )

    updated_columns = [col for col in current_columns if col not in drop_column_list]

    result = async_drop_columns.apply_async(
        args=[directory_project, drop_column_list],
        kwargs={"project_id": project_id, "task_key": task_key},
    )

    column_drop_metadata = {
        "columns_dropped": drop_column_list,
        "dropped_at": datetime.now().isoformat(),
        "task_id": result.id,
    }

    # Update project metadata in MongoDB
    project_model.collection.update_one(
        {"_id": project_id},
        {"$push": {"column_drops": column_drop_metadata}, "$set": {"columns": updated_columns}},
    )

    return (
        jsonify(
            {
                "message": "Column dropping has started",
                "task_id": result.id,
                "project_id": project_id,
            }
        ),
        202,
    )


@processor_routes.route("/<project_id>/dataset/connector", methods=["POST"])
@task_manager_decorator("connector")
def db_copy_project_file(project_id, task_key=None, task_params=None):
    """
        {
    "db_config": {
        "host": "localhost",
        "user": "your_username",
        "password": "your_password",
        "database": "your_database"
    },
    "table": "your_table_name"
    }
    """
    request_data_json = request.get_json()
    db_config = request_data_json.get("db_config")
    db_table_name = request_data_json.get("table")

    directory_project_base = directory_project_path_full(project_id, [])

    project = project_model.collection.find_one({"_id": project_id})
    if not project:
        return jsonify({"error": "Invalid Project ID"}), 400

    if not os.path.isdir(directory_project_base):
        return jsonify({"error": "Project directory not found"}), 400

    result = async_connector_table.apply_async(
        args=[directory_project_base, db_config, db_table_name],
        kwargs={"project_id": project_id, "task_key": task_key},
    )

    file_path = os.path.join(directory_project_base, filename_raw_data_csv())
    db_coonector_metadata = {
        "db_name": db_config.get("database"),
        "db_table": db_table_name,
        "file_path": file_path,
        "uploaded_at": datetime.now().isoformat(),
    }

    if (
        project_model.collection.update_one(
            {"_id": project_id}, {"$push": {"files": db_coonector_metadata}}
        ).modified_count
        == 0
    ):
        return jsonify({"error": "Failed to update project with file details"}), 500

    return (
        jsonify(
            {
                "message": "File processing has started",
                "task_id": result.id,
                "project_id": project_id,
            }
        ),
        202,
    )


@processor_routes.route("/<project_id>/features/ranking", methods=["POST"])
@task_manager_decorator("feature_ranking")
def start_feature_ranking(project_id, task_key=None, task_params=None):
    request_data_json = request.get_json()
    kpi_list = request_data_json.get("kpi_list", [])
    important_features = request_data_json.get("important_features", [])
    kpi = request_data_json.get("kpi")

    # Validate the project and dataset
    project = project_model.collection.find_one({"_id": project_id})
    if not project or not os.path.isdir(directory_project_path_full(project_id, [])):
        return jsonify({"error": "Invalid Project ID"}), 400

    if not os.path.isfile(
        os.path.join(directory_project_path_full(project_id, []), filename_raw_data_csv())
    ):
        return jsonify({"message": "Data set not uploaded"}), 400

    if not kpi:
        return jsonify({"error": "Missing 'kpi' in request"}), 400

    # Start task
    result = async_optimised_feature_rank.apply_async(
        args=[kpi, kpi_list, important_features, directory_project_path_full(project_id, [])],
        kwargs={"project_id": project_id, "task_key": task_key},
    )

    return (
        jsonify(
            {
                "message": "Feature Ranking has started",
                "task_id": str(result.id),
                "project_id": project_id,
            }
        ),
        202,
    )


@processor_routes.route("/<project_id>/clusters/subcluster", methods=["POST"])
@task_manager_decorator("clustering")
def initiate_subclustering(project_id, task_key=None, task_params=None):
    request_data_json = request.get_json()
    list_path = request_data_json.get("path")
    kpi = request_data_json.get("kpi")

    # Validate project and file paths
    project = project_model.collection.find_one({"_id": project_id})
    directory_project_base = directory_project_path_full(project_id, [])
    if not project or not os.path.isdir(directory_project_base):
        return jsonify({"error": "Invalid Project ID"}), 400

    if not os.path.isfile(os.path.join(directory_project_base, filename_raw_data_csv())):
        return jsonify({"message": "Data set not uploaded"}), 400

    input_file_path_feature_rank_pkl = os.path.join(
        directory_project_base, filename_feature_rank_list_pkl(kpi)
    )
    if not os.path.exists(input_file_path_feature_rank_pkl):
        return jsonify({"error": f"Feature ranking file for {kpi} not found."}), 404

    # Start task
    result = async_optimised_clustering.apply_async(
        args=[directory_project_path_full(project_id, list_path), input_file_path_feature_rank_pkl],
        kwargs={"project_id": project_id, "task_key": task_key},
    )

    return (
        jsonify(
            {
                "message": "Clustering has started",
                "task_id": str(result.id),
                "project_id": project_id,
            }
        ),
        202,
    )


@processor_routes.route("/<project_id>/time-series/analysis", methods=["POST"])
@task_manager_decorator("time_series_analysis")
def initiate_time_series(project_id, task_key=None, task_params=None):
    request_data_json = request.get_json()
    user_added_vars_list = request_data_json.get("user_added_vars_list", [])
    list_path = request_data_json.get("path")
    kpi = request_data_json.get("kpi", None)
    no_of_months = request_data_json.get("no_of_months")
    date_column = request_data_json.get("date_column")
    increase_factor = request_data_json.get("increase_factor")
    zero_value_replacement = request_data_json.get("zero_value_replacement")

    project = project_model.collection.find_one({"_id": project_id})
    if not project:
        return jsonify({"error": "Invalid Project ID"}), 400

    directory_project = directory_project_path_full(project_id, [])
    if not os.path.isdir(directory_project):
        return jsonify({"error": "Invalid Project ID"}), 400

    directory_project_cluster = directory_project_path_full(project_id, list_path)
    if not os.path.exists(directory_project_cluster):
        return jsonify({"error": "Cluster Does not exist.", "project_id": project_id}), 404

    if not os.path.isfile(os.path.join(directory_project_cluster, filename_raw_data_csv())):
        return jsonify({"message": "Data set not found"}), 400

    raw_data_file = os.path.join(directory_project_cluster, filename_raw_data_csv())

    result = async_time_series_analysis.apply_async(
        args=[
            directory_project_cluster,
            raw_data_file,
            user_added_vars_list,
            kpi,
            no_of_months,
            date_column,
            increase_factor,
            zero_value_replacement,
        ],
        kwargs={"project_id": project_id, "task_key": task_key},
    )

    return (
        jsonify(
            {
                "message": "Time series analysis has started",
                "task_id": str(result.id),
                "project_id": project_id,
            }
        ),
        202,
    )

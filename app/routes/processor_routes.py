import json
import os
from datetime import datetime

from flask import Blueprint, jsonify, request
from werkzeug.utils import secure_filename

from app import celery
from app.decorator import project_validation_decorator, task_manager_decorator
from app.models.project_model import ProjectModel
from app.tasks import (
    async_connector_table,
    async_drop_columns,
    async_mapping_columns,
    async_optimised_clustering,
    async_optimised_feature_rank,
    async_optimised_feature_rank_one_hot_encoded,
    async_save_file,
    async_time_series_analysis,
)
from app.utils.filename_utils import filename_feature_rank_list_pkl, filename_raw_data_csv
from app.utils.model_utils import get_all_running_tasking, get_project_columns
from app.utils.os_utils import directory_project_path_full

processor_routes = Blueprint("processor_routes", __name__)

project_model = ProjectModel()


@processor_routes.route("/tasks/<task_id>/status", methods=["GET", "POST"])
def get_task_status_by_id(task_id):
    result = celery.AsyncResult(task_id)
    return jsonify({"status": result.status})


@processor_routes.route("/tasks/running", methods=["GET"])
def list_running_tasks():
    running_tasks = get_all_running_tasking()

    tasks_list = []
    for task_id, task_info in running_tasks.items():
        task_info = json.loads(task_info)
        tasks_list.append(task_info)

    return jsonify({"running_tasks": tasks_list}), 200


# ** Cant add decorator coz no json in request**
@processor_routes.route("/<project_id>/files/upload", methods=["POST"])
@project_validation_decorator
def upload_project_file(project_id):

    if "file" not in request.files:
        return jsonify({"error": "No file part in the request"}), 400

    file = request.files["file"]
    directory_project_base = directory_project_path_full(project_id, [])

    if file:
        filename = secure_filename(file.filename)
        file_path = os.path.join(directory_project_base, filename_raw_data_csv())

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
@project_validation_decorator
def drop_columns_from_dataset(project_id, task_key=None, task_params=None):
    request_data_json = request.get_json()

    drop_column_list = request_data_json.get("column", [])

    raw_data_file = os.path.join(
        directory_project_path_full(project_id, []), filename_raw_data_csv()
    )
    if not os.path.isfile(raw_data_file):
        return jsonify({"message": "Data set not uploaded"}), 400

    if not drop_column_list:
        return jsonify({"error": "Invalid column list"}), 400

    try:
        current_columns = get_project_columns(project_id, raw_data_file)
    except ValueError as e:
        return jsonify({"error": str(e)}), 400

    missing_columns = [col for col in drop_column_list if col not in current_columns]
    if missing_columns:
        return (
            jsonify(
                {"error": f"The following columns are missing in the dataset: {missing_columns}"}
            ),
            400,
        )

    if not any(col in current_columns for col in drop_column_list):
        return (
            jsonify({"error": "None of the specified columns to drop exist in the dataset."}),
            400,
        )

    updated_columns = [col for col in current_columns if col not in drop_column_list]

    result = async_drop_columns.apply_async(
        args=[raw_data_file, drop_column_list],
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


@processor_routes.route("/<project_id>/dataset/columns/mapping", methods=["POST"])
@task_manager_decorator("mapping_columns")
@project_validation_decorator
def mapping_columns_from_dataset(project_id, task_key=None, task_params=None):
    request_data_json = request.get_json()

    raw_data_file = os.path.join(
        directory_project_path_full(project_id, []), filename_raw_data_csv()
    )
    if not os.path.isfile(raw_data_file):
        return jsonify({"message": "Dataset not uploaded"}), 400

    column_name_mapping = request_data_json.get("column_mapping")
    if not column_name_mapping:
        return jsonify({"error": "Missing 'column_mapping' in request"}), 400

    if isinstance(column_name_mapping, str):
        try:
            column_name_mapping = json.loads(column_name_mapping)
        except json.JSONDecodeError as e:
            return jsonify({"error": f"Invalid JSON format: {str(e)}"}), 400
    elif not isinstance(column_name_mapping, dict):
        return jsonify({"error": "'column_mapping' must be a JSON object"}), 400

    # Check columns in dataset
    try:
        current_columns = get_project_columns(project_id, raw_data_file)
    except ValueError as e:
        return jsonify({"error": str(e)}), 400

    missing_columns = [col for col in column_name_mapping if col not in current_columns]
    if missing_columns:
        return (
            jsonify(
                {"error": f"The following columns do not exist in the dataset: {missing_columns}"}
            ),
            400,
        )

    result = async_mapping_columns.apply_async(
        args=[raw_data_file, column_name_mapping],
        kwargs={"project_id": project_id, "task_key": task_key},
    )

    # Prepare metadata for MongoDB update
    column_mapping_metadata = {
        "column_mapping": column_name_mapping,
        "updated_at": datetime.now().isoformat(),
        "task_id": result.id,
    }

    updated_columns = [column_name_mapping.get(col, col) for col in current_columns]
    project_model.collection.update_one({"_id": project_id}, {"$set": {"columns": updated_columns}})

    return (
        jsonify(
            {
                "message": "Column mapping has started",
                "task_id": result.id,
                "project_id": project_id,
            }
        ),
        202,
    )


@processor_routes.route("/<project_id>/dataset/connector", methods=["POST"])
@task_manager_decorator("connector")
@project_validation_decorator
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

    file_path = os.path.join(directory_project_path_full(project_id, []), filename_raw_data_csv())
    result = async_connector_table.apply_async(
        args=[file_path, db_config, db_table_name],
        kwargs={"project_id": project_id, "task_key": task_key},
    )

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
@project_validation_decorator
def start_feature_ranking(project_id, task_key=None, task_params=None):
    request_data_json = request.get_json()
    kpi_list = request_data_json.get("kpi_list", [])
    important_features = request_data_json.get("important_features", [])
    kpi = request_data_json.get("kpi")

    if not os.path.isfile(
        os.path.join(directory_project_path_full(project_id, []), filename_raw_data_csv())
    ):
        return jsonify({"message": "Data set not uploaded"}), 400

    if not kpi:
        return jsonify({"error": "Missing 'kpi' in request"}), 400

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


@processor_routes.route("/<project_id>/features/onehot", methods=["POST"])
@task_manager_decorator("feature_ranking_onehotencoded")
@project_validation_decorator
def start_feature_weight(project_id, task_key=None, task_params=None):
    request_data_json = request.get_json()
    list_path = request_data_json.get("path")
    kpi = request_data_json.get("kpi")

    if not os.path.isfile(
        os.path.join(directory_project_path_full(project_id, list_path), filename_raw_data_csv())
    ):
        return jsonify({"message": "Cluster not found"}), 400

    if not kpi:
        return jsonify({"error": "Missing 'kpi' in request"}), 400

    # Start task
    result = async_optimised_feature_rank_one_hot_encoded.apply_async(
        args=[kpi, directory_project_path_full(project_id, list_path)],
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


@processor_routes.route("/<project_id>/features/label", methods=["POST"])
@task_manager_decorator("feature_ranking_labelencoded")
@project_validation_decorator
def start_feature_weight(project_id, task_key=None, task_params=None):
    request_data_json = request.get_json()
    kpi_list = request_data_json.get("kpi_list", [])
    important_features = request_data_json.get("important_features", [])
    list_path = request_data_json.get("path")
    kpi = request_data_json.get("kpi")

    # Validate dataset

    if not os.path.isfile(
        os.path.join(directory_project_path_full(project_id, list_path), filename_raw_data_csv())
    ):
        return jsonify({"message": "Cluster not found"}), 400

    if not kpi:
        return jsonify({"error": "Missing 'kpi' in request"}), 400

    # Start task
    result = async_optimised_feature_rank.apply_async(
        args=[
            kpi,
            kpi_list,
            important_features,
            directory_project_path_full(project_id, list_path),
        ],
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
@project_validation_decorator
def initiate_subclustering(project_id, task_key=None, task_params=None):
    request_data_json = request.get_json()
    list_path = request_data_json.get("path")
    kpi = request_data_json.get("kpi")

    directory_project_base = directory_project_path_full(project_id, [])
    if not os.path.isfile(os.path.join(directory_project_base, filename_raw_data_csv())):
        return jsonify({"message": "Data set not uploaded"}), 400

    input_file_path_feature_rank_pkl = os.path.join(
        directory_project_base, filename_feature_rank_list_pkl(kpi)
    )
    if not os.path.exists(input_file_path_feature_rank_pkl):
        return jsonify({"error": f"Feature ranking file for {kpi} not found."}), 404

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
@project_validation_decorator
def initiate_time_series(project_id, task_key=None, task_params=None):
    request_data_json = request.get_json()
    list_path = request_data_json.get("path")
    kpi = request_data_json.get("kpi", None)
    no_of_months = request_data_json.get("no_of_months")
    date_column = request_data_json.get("date_column")
    adjustments = request_data_json.get("adjustments")

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
            kpi,
            no_of_months,
            date_column,
            adjustments,
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

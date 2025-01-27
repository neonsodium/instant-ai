import json
import os
from datetime import datetime
from functools import wraps
from hashlib import sha256

# connectors
import mysql.connector
import csv
import os

import pandas as pd
from redis import Redis

from app import celery
from app.data_preparation_ulits.drop_columns import drop_columns
from app.data_preparation_ulits.mapping_columns import mapping_columns
from app.ml_models.cluster import optimised_clustering
from app.ml_models.feature_rank import generate_optimized_feature_rankings
from app.ml_models.time_series import time_series_analysis
from app.models.project_model import ProjectModel
from app.utils.filename_utils import (
    filename_raw_data_csv,
    filename_dropeed_column_data_csv,
    filename_time_series_figure_pkl,
)
from app.utils.os_utils import save_to_pickle
from config import Config

redis_client = Redis(host=Config.REDIS_HOST, port=Config.REDIS_PORT)

project_model = ProjectModel()


def delete_task_key(task_key, request_id):
    if task_key:
        redis_client.delete(task_key)
    else:
        print(f"Warning: Task key not found for task_id {request_id}")


def update_task_status(collection, task_field):
    """
    A decorator to update task statuses in MongoDB and to remove task Id in Redis.

    Args:
        collection (pymongo.collection.Collection): The MongoDB collection instance.
        task_field (str): The field in MongoDB where the task metadata is stored (e.g., "tasks", "column_drops").

    Returns:
        function: The wrapped function with task status management.
    """

    def decorator(func):
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            task_id = self.request.id
            project_id = kwargs.get("project_id")
            if not project_id:
                raise ValueError("Project ID must be provided as a keyword argument.")

            # Mark task as pending
            task_status = {"status": "pending", "start_time": datetime.now().isoformat()}
            collection.update_one(
                {"_id": project_id, f"{task_field}.task_id": task_id},
                {"$set": {f"{task_field}.$.status": task_status}},
            )
            task_key = kwargs.get("task_key")
            try:
                result = func(self, *args, **kwargs)

                task_status = {"status": "completed", "completed_at": datetime.now().isoformat()}
                collection.update_one(
                    {"_id": project_id, f"{task_field}.task_id": task_id},
                    {"$set": {f"{task_field}.$.status": task_status}},
                )

                delete_task_key(task_key, self.request.id)

                return result

            except Exception as e:
                delete_task_key(task_key, self.request.id)

                task_status = {
                    "status": "failed",
                    "error": str(e),
                    "completed_at": datetime.now().isoformat(),
                }
                collection.update_one(
                    {"_id": project_id, f"{task_field}.task_id": task_id},
                    {"$set": {f"{task_field}.$.status": task_status}},
                )
                raise e

        return wrapper

    return decorator


@celery.task(bind=True)
@update_task_status(project_model.collection, "column_drops")
def async_drop_columns(
    self, directory_project: str, drop_column_list: list, project_id: str, task_key
):
    drop_columns(directory_project, drop_column_list)
    return {"status": "Column removal process successfully completed."}


@celery.task(bind=True)
@update_task_status(project_model.collection, "mapping_columns")
def async_mapping_columns(
    self, directory_project: str, column_name_mapping: list, project_id: str, task_key
):
    mapping_columns(directory_project, column_name_mapping)
    return {"status": "Column removal process successfully completed."}


@celery.task(bind=True)
@update_task_status(project_model.collection, "connector")
def async_connector_table(
    self, directory_project: str, db_config, db_table_name, project_id: str, task_key
):
    filepath_raw_data = os.path.join(directory_project, filename_raw_data_csv())

    try:
        # Connect to the database
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()

        # Fetch data from the table
        query = f"SELECT * FROM {db_table_name}"
        cursor.execute(query)
        rows = cursor.fetchall()

        # Get column names
        column_names = [desc[0] for desc in cursor.description]

        # Write data to CSV
        with open(filepath_raw_data, "w", newline="", encoding="utf-8") as file:
            writer = csv.writer(file)
            writer.writerow(column_names)  # Write headers
            writer.writerows(rows)  # Write data rows

        cursor.close()
        conn.close()

        return {"status": "File saved and processing completed successfully."}

    except mysql.connector.Error as err:
        return {"status": "Database error: " + str(err)}

    except Exception as e:
        return {"status": "Error: " + str(e)}


@celery.task(bind=True)
@update_task_status(project_model.collection, "tasks")
def async_save_file(self, directory_project: str, file_content, project_id: str):
    filepath_raw_data = os.path.join(directory_project, filename_raw_data_csv())
    with open(filepath_raw_data, "wb") as f:
        f.write(file_content)

    df = pd.read_csv(filepath_raw_data)
    columns = list(df.columns)

    project_model.collection.update_one({"_id": project_id}, {"$set": {"columns": columns}})
    return {"status": "File saved and processing completed successfully."}


@celery.task(bind=True)
@update_task_status(project_model.collection, "tasks")
def async_optimised_feature_rank(
    self, kpi, kpi_list, important_features, directory_project, project_id: str, task_key
):
    try:
        # TODO remove Pickle file
        drop_column_file = os.path.join(directory_project, filename_dropeed_column_data_csv())
        raw_data_file = os.path.join(directory_project, filename_raw_data_csv())
        generate_optimized_feature_rankings(
            kpi, kpi_list, important_features, directory_project, raw_data_file, drop_column_file
        )
        return {"status": "Feature ranking completed"}
    except Exception as e:
        raise e


@celery.task(bind=True)
@update_task_status(project_model.collection, "tasks")
def async_time_series_analysis(
    self,
    directory_project_cluster,
    raw_data_file,
    user_added_vars_list,
    kpi,
    no_of_months,
    date_column,
    increase_factor,
    zero_value_replacement,
    project_id: str,
    task_key,
):
    try:
        fig = time_series_analysis(
            directory_project_cluster,
            raw_data_file,
            user_added_vars_list,
            kpi,
            no_of_months,
            date_column,
            increase_factor,
            zero_value_replacement,
        )

        save_to_pickle(
            fig, os.path.join(directory_project_cluster, filename_time_series_figure_pkl(kpi))
        )

        return {"status": "Analysis completed"}
    except Exception as e:
        raise e


@celery.task(bind=True)
@update_task_status(project_model.collection, "tasks")
def async_optimised_clustering(
    self, directory_project, input_file_path_feature_rank_pkl, project_id: str, task_key
):
    try:
        drop_column_file = os.path.join(directory_project, filename_dropeed_column_data_csv())
        raw_data_file = os.path.join(directory_project, filename_raw_data_csv())
        optimised_clustering(
            directory_project, drop_column_file, raw_data_file, input_file_path_feature_rank_pkl
        )
        return {"status": "Clustering completed"}
    except Exception as e:
        raise e


def generate_task_key(**kwargs):
    """
    Generate a unique hash key based on arbitrary input parameters.

    Args:
        **kwargs: Key-value pairs representing task parameters.

    Returns:
        str: A SHA256 hash representing the task key.
    """
    sorted_data = json.dumps(kwargs, sort_keys=True)
    return sha256(sorted_data.encode()).hexdigest()

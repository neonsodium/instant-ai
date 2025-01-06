import json
import os
from hashlib import sha256

from redis import Redis

from app.data_preparation_ulits.drop_columns import drop_columns
from app.data_preparation_ulits.label_encode_data import label_encode_data
from app.data_preparation_ulits.one_hot_encode import one_hot_encode_data
from app.filename_utils import *
from app.ml_models.cluster import optimised_clustering
from app.ml_models.feature_rank import generate_optimized_feature_rankings
from app.ml_models.time_series import time_series_analysis
from app.os_utils import save_to_pickle
from config import Config

from . import celery

redis_client = Redis(host=Config.REDIS_HOST, port=Config.REDIS_PORT)


@celery.task
def async_drop_columns(directory_project: str, drop_column_list):
    drop_columns(directory_project, drop_column_list)
    return {"status": "Column removal process successfully."}


@celery.task
def async_save_file(project_dir, file_content):
    filepath_raw_data = os.path.join(project_dir, filename_raw_data_csv())
    with open(filepath_raw_data, "wb") as f:
        f.write(file_content)
    # async_data_processer(project_dir)
    return {"status": "File saved and processing started"}


@celery.task(bind=True)
def async_optimised_feature_rank(self, kpi, kpi_list, important_features, directory_project):
    task_key = redis_client.get(f"task:{self.request.id}")  # Retrieve the associated task key
    try:
        drop_column_file = os.path.join(directory_project, filename_dropeed_column_data_csv())
        raw_data_file = os.path.join(directory_project, filename_raw_data_csv())
        generate_optimized_feature_rankings(
            kpi, kpi_list, important_features, directory_project, raw_data_file, drop_column_file
        )
        return {"status": "Feature ranking completed"}
    finally:
        if task_key:
            redis_client.delete(task_key)
        else:
            print(f"Warning: Task key not found for task_id {self.request.id}")


@celery.task(bind=True)
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
):
    task_key = redis_client.get(f"task:{self.request.id}")  # Retrieve the associated task key
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
    finally:
        if task_key:
            redis_client.delete(task_key)
        else:
            print(f"Warning: Task key not found for task_id {self.request.id}")


@celery.task(bind=True)
def async_optimised_clustering(self, directory_project, input_file_path_feature_rank_pkl):
    task_key = redis_client.get(f"task:{self.request.id}")  # Retrieve the associated task key
    try:
        drop_column_file = os.path.join(directory_project, filename_dropeed_column_data_csv())
        raw_data_file = os.path.join(directory_project, filename_raw_data_csv())
        optimised_clustering(
            directory_project, drop_column_file, raw_data_file, input_file_path_feature_rank_pkl
        )
        return {"status": "Clustering completed"}
    finally:
        if task_key:
            redis_client.delete(task_key)
        else:
            print(f"Warning: Task key not found for task_id {self.request.id}")


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

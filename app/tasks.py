import json
import os
from hashlib import sha256

from redis import Redis
import pickle

from app.data_preparation_ulits.drop_columns import drop_columns
from app.data_preparation_ulits.label_encode_data import label_encode_data
from app.data_preparation_ulits.one_hot_encode import one_hot_encode_data
from app.filename_utils import *
from app.ml_models.cluster import optimised_clustering
from app.ml_models.feature_rank import generate_optimized_feature_rankings
from app.ml_models.time_series import time_series_analysis

from . import celery

redis_client = Redis()


# TODO add error handling for all the async calls F++ ;_;
@celery.task
def async_data_processer(directory_project: str):
    # TODO

    input_file_path_drop_column_csv = os.path.join(
        directory_project, filename_dropeed_column_data_csv()
    )
    input_file_path_raw_data_csv = os.path.join(directory_project, filename_raw_data_csv())
    if os.path.isfile(input_file_path_drop_column_csv):
        input_file_path_csv = input_file_path_drop_column_csv
    else:
        input_file_path_csv = input_file_path_raw_data_csv

    output_label_encoded_path = os.path.join(directory_project, filename_label_encoded_data_csv())
    output_one_hot = os.path.join(directory_project, filename_one_hot_encoded_data_csv())
    output_rev_label_mapping = os.path.join(directory_project, filename_label_mapping_data_csv())
    output_rev_one_hot_dict = os.path.join(
        directory_project, filename_rev_one_hot_encoded_dict_pkl()
    )
    output_rev_label_dict = os.path.join(directory_project, filename_rev_label_encoded_dict_pkl())

    label_encode_data(
        input_file_path_csv,
        output_label_encoded_path,
        output_rev_label_dict,
        output_rev_label_mapping,
    )
    # one_hot_encode_data(output_drop_tables, output_rev_one_hot_dict, output_one_hot)
    return {"status": "Label encoding completed"}


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


@celery.task
def async_label_encode_data(
    input_csv_file_path, output_label_encoded_path, output_rev_label_encoded_path
):
    label_encode_data(input_csv_file_path, output_label_encoded_path, output_rev_label_encoded_path)
    return {"status": "Label encoding completed"}


@celery.task
def async_one_hot_encode_data(input_csv_file_path, output_one_hot_encoded_path):
    one_hot_encode_data(input_csv_file_path, output_one_hot_encoded_path)
    return {"status": "One hot encoding completed"}


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
        with open(
            os.path.join(directory_project_cluster, filename_time_series_figure_pkl(kpi)), "wb"
        ) as file:
            pickle.dump(fig, file)

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
    # Sort the dictionary to ensure consistent hashing
    sorted_data = json.dumps(kwargs, sort_keys=True)
    return sha256(sorted_data.encode()).hexdigest()

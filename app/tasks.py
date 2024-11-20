import os

from app.data_preparation_ulits.drop_columns import drop_columns_df
from app.data_preparation_ulits.label_encode_data import label_encode_data
from app.data_preparation_ulits.one_hot_encode import one_hot_encode_data
from app.data_preparation_ulits.preprocess_test_label_encoded_data import (
    preprocess_label_encoded_data,
)
from app.data_preparation_ulits.preprocess_test_one_hot_encoded import (
    preprocess_one_hot_data,
)
from app.filename_utils import *
from app.ml_models.optimised_clustering import optimised_clustering
from app.ml_models.optimised_feature_rank import optimised_feature_rank

from . import celery

# TODO add error handling for all the async calls F++


@celery.task
def async_data_processer(directory_project: str):
    input_file = os.path.join(directory_project, filename_raw_data_csv())
    output_drop_tables = os.path.join(
        directory_project, filename_dropeed_column_data_csv()
    )
    output_pre_label = os.path.join(directory_project, filename_pre_label_data_csv())
    output_label_csv = os.path.join(
        directory_project, filename_label_encoded_data_csv()
    )
    output_pre_one_hot = os.path.join(
        directory_project, filename_pre_one_hot_encoded_data_csv()
    )
    output_one_hot = os.path.join(
        directory_project, filename_one_hot_encoded_data_csv()
    )
    output_rev_label_mapping = os.path.join(
        directory_project, filename_label_mapping_data_csv()
    )
    output_rev_one_hot_dict = os.path.join(
        directory_project, filename_rev_one_hot_encoded_dict_pkl()
    )
    output_rev_label_dict = os.path.join(
        directory_project, filename_rev_label_encoded_dict_pkl()
    )

    drop_columns_df(input_file, output_drop_tables)
    preprocess_label_encoded_data(output_drop_tables, output_pre_label)
    preprocess_one_hot_data(output_drop_tables, output_pre_one_hot)
    label_encode_data(
        output_pre_label,
        output_label_csv,
        output_rev_label_dict,
        output_rev_label_mapping,
    )
    one_hot_encode_data(output_pre_one_hot, output_rev_one_hot_dict, output_one_hot)
    return {"status": "Label encoding completed"}


@celery.task
def async_drop_columns(directory_project: str):
    pass


@celery.task
def async_save_and_process_file(project_dir, file_content):
    filepath_raw_data = os.path.join(project_dir, filename_raw_data_csv())
    with open(filepath_raw_data, "wb") as f:
        f.write(file_content)

    async_data_processer(project_dir)

    return {"status": "File saved and processing started"}


@celery.task
def async_label_encode_data(
    input_csv_file_path, output_label_encoded_path, output_rev_label_encoded_path
):
    label_encode_data(
        input_csv_file_path, output_label_encoded_path, output_rev_label_encoded_path
    )
    return {"status": "Label encoding completed"}


@celery.task
def async_one_hot_encode_data(input_csv_file_path, output_one_hot_encoded_path):
    one_hot_encode_data(input_csv_file_path, output_one_hot_encoded_path)
    return {"status": "One hot encoding completed"}


@celery.task
def async_optimised_feature_rank(target_var, target_vars_list, directory_project):
    file_path_label_encoded_csv = os.path.join(
        directory_project, filename_label_encoded_data_csv()
    )
    optimised_feature_rank(
        target_var, target_vars_list, file_path_label_encoded_csv, directory_project
    )
    return {"status": "Feature ranking completed"}


@celery.task
def async_optimised_clustering(directory_project, input_file_path_feature_rank_pkl):
    input_file_path_label_encoded_csv = os.path.join(
        directory_project, filename_label_encoded_data_csv()
    )
    optimised_clustering(
        directory_project,
        input_file_path_label_encoded_csv,
        input_file_path_feature_rank_pkl,
    )
    return {"status": "Clustering completed"}

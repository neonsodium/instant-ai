from celery import chain
from . import celery
from .data_preparation_ulits.label_encode_data import label_encode_data
from .data_preparation_ulits.one_hot_encode import one_hot_encode_data
from .ml_models.optimised_clustering import optimised_clustering
from .ml_models.optimised_feature_rank import optimised_feature_rank

# TODO add error handling for all the async calls F++

@celery.task
def async_label_encode_data(input_csv_file_path,output_label_encoded_path,output_rev_label_encoded_path):
    label_encode_data(input_csv_file_path,output_label_encoded_path,output_rev_label_encoded_path)
    return {"status": "Label encoding completed"}

@celery.task
def async_one_hot_encode_data(input_csv_file_path,output_one_hot_encoded_path):
    one_hot_encode_data(input_csv_file_path,output_one_hot_encoded_path)
    return {"status": "One hot encoding completed"}

@celery.task
def async_optimised_feature_rank(target_var,target_vars,directory_project):
    optimised_feature_rank(target_var,target_vars,directory_project)
    return {"status": "Feature ranking completed"}

@celery.task
def async_optimised_clustering(directory_project,*a):
    optimised_clustering(directory_project)
    return {"status": "Clustering completed"}

@celery.task
def run_feature_rank_and_clustering(target_var, target_vars, directory_project):
    workflow = chain(
        async_optimised_feature_rank.s(target_var, target_vars, directory_project),
        async_optimised_clustering.s(directory_project,"a")
    )
    
    result = workflow.apply_async()  # Execute the chain asynchronously
    return {"status": "Feature ranking and clustering started", "task_id": result.id}
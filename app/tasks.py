from . import celery
from .ml_models.label_encode_data import label_encode_data
from .ml_models.optimised_clustering import optimised_clustering
from .ml_models.optimised_feature_rank import optimised_feature_rank

# TODO add error handling for all the async calls F++

@celery.task
def async_label_encode_data(filepath_raw_data,filepath_label_encode):
    label_encode_data(filepath_raw_data,filepath_label_encode)
    return {"status": "Label encoding completed"}

@celery.task
def async_optimised_feature_rank(target_var,target_vars,directory_project):
    optimised_feature_rank(target_var,target_vars,directory_project)
    return {"status": "Feature ranking completed"}
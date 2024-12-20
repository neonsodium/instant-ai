import re
import uuid


def create_project_uuid() -> str:
    return str(uuid.uuid4())


def filename_dropeed_column_data_csv() -> str:
    return "data_dropped_column.csv"


def filename_raw_data_csv() -> str:
    return "data_raw.csv"


def filename_pre_label_data_csv() -> str:
    return "data_pre_label.csv"


def filename_label_encoded_data_csv() -> str:
    return "data_label_encode.csv"


def filename_one_hot_encoded_data_csv() -> str:
    return "data_one_hot_encode.csv"


def filename_pre_one_hot_encoded_data_csv() -> str:
    return "data_pre_one_hot_encode.csv"


def filename_main_data_csv():
    return "data_main_cleaned.csv"


def filename_label_mapping_data_csv() -> str:
    return "data_label_mapping.csv"


def filename_rev_label_encoded_dict_pkl() -> str:
    return "dict_rev_label_encode_data.pkl"


def filename_rev_one_hot_encoded_dict_pkl() -> str:
    return "dict_rev_one_hot_encode_data.pkl"


def directory_cluster_format(cluster_num: str | int) -> str:
    return f"cluster_{cluster_num}"


def filename_cluster_format_csv(cluster_num: str | int) -> str:
    return f"cluster_{cluster_num}.csv"


# summerising algo
def feature_descriptions_csv() -> str:
    return "feature_descriptions.csv"


def feature_descriptions_json() -> str:
    return "feature_descriptions.json"


# feature ranking algo
def filename_feature_rank_score_df(target_var: str) -> str:
    return f"df_feature_ranking_scores_{re.sub(r'[^A-Za-z0-9_]', '', target_var)}.pkl"


def filename_feature_rank_list_pkl(target_var: str) -> str:
    return f"list_feature_ranking_{re.sub(r'[^A-Za-z0-9_]', '', target_var)}.pkl"


def filename_feature_rank_result_txt(target_var: str):
    return f"results_{re.sub(r'[^A-Za-z0-9_]', '', target_var)}.txt"

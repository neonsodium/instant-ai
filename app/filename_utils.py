import uuid
import re

def create_project_uuid() -> str:
    return str(uuid.uuid4())

def filename_raw_data_csv() -> str:
    return "data_raw.csv"

def filename_label_encoded_data_csv() -> str:
    return "label_encode_data.csv"

def directory_cluster_format(cluster_num: str | int) -> str:
    return f"cluster_{cluster_num}"

def filename_cluster_format_csv(cluster_num: str | int) -> str:
    return f"cluster_{cluster_num}.csv"

# feature ranking algo
def filename_feature_rank_score_df() -> str:
    return "df_feature_ranking_scores.pkl"

def filename_feature_rank_list_pkl()  -> str:
    return "list_feature_ranking.pkl"

def filename_feature_rank_result_txt(target_var: str):
    return f"results_{re.sub(r'[^A-Za-z0-9_]', '', target_var)}.txt"
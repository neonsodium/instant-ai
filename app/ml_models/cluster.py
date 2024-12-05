import os
import pickle

import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import AgglomerativeClustering

from app.data_preparation_ulits.label_encode_data import (
    reverse_label_encoding,
    apply_label_encoding,
)
from app.filename_utils import (
    directory_cluster_format,
    filename_raw_data_csv,
)


def optimised_clustering(
    directory_project,
    input_file_path_drop_column_csv,
    input_file_path_raw_data_csv,
    input_file_path_feature_rank_pkl,
):
    if os.path.isfile(input_file_path_drop_column_csv):
        df = pd.read_csv(input_file_path_drop_column_csv)
    else:
        df = pd.read_csv(input_file_path_raw_data_csv)

    with open(input_file_path_feature_rank_pkl, "rb") as file:
        features = pickle.load(file)

    MAX_NUM_CLUSTERS = 4
    df, label_encoders = apply_label_encoding(df)
    df = hierarchical_clustering(df, features, MAX_NUM_CLUSTERS)
    df = reverse_label_encoding(df, label_encoders)
    hierarchical_clustering_to_csv(df, directory_project)


def hierarchical_clustering(df, features, n_clusters):
    """
    Perform hierarchical clustering on the data, add cluster labels,
    and save individual clusters as CSV files in the current directory.

    Parameters:
    - data (pd.DataFrame): The input data.
    - features (list): List of features to use for clustering.
    - n_clusters (int): Number of clusters.
    """
    scaler = StandardScaler()
    x = df[features]
    x_scaled = scaler.fit_transform(x)

    agg_clustering = AgglomerativeClustering(n_clusters=n_clusters, linkage="ward")
    df["hierarchical_cluster"] = agg_clustering.fit_predict(x_scaled)
    return df


def hierarchical_clustering_to_csv(data, directory_project):
    # Save each cluster to a separate CSV file
    # for cluster_id in range(n_clusters):
    #     cluster_data = data[data["hierarchical_cluster"] == cluster_id].drop(columns=["hierarchical_cluster"])
    #     cluster_file_name = f"cluster_{cluster_id}.csv"
    #     cluster_data.to_csv(cluster_file_name, index=False)
    #     print(f"Cluster {cluster_id} saved to {cluster_file_name}")

    for cluster in data["hierarchical_cluster"].unique():
        cluster_df = data[data["hierarchical_cluster"] == cluster].drop(
            columns=["hierarchical_cluster"]
        )
        cluster_directory = os.path.join(
            directory_project, directory_cluster_format(cluster)
        )
        os.makedirs(cluster_directory, exist_ok=True)
        cluster_filename_raw_data_path = os.path.join(
            cluster_directory, filename_raw_data_csv()
        )
        # cluster_filename_label_encoded_path = os.path.join(
        #     cluster_directory, filename_label_encoded_data_csv()
        # )
        cluster_df.to_csv(cluster_filename_raw_data_path, index=False)


# def hierarchical_clustering_to_csv(data, n_clusters):
#     # Save each cluster to a separate CSV file
#     for cluster_id in range(n_clusters):
#         cluster_data = data[data["hierarchical_cluster"] == cluster_id].drop(
#             columns=["hierarchical_cluster"]
#         )
#         cluster_file_name = f"cluster_{cluster_id}.csv"
#         cluster_data.to_csv(cluster_file_name, index=False)
#         print(f"Cluster {cluster_id} saved to {cluster_file_name}")


# data, labels = apply_label_encoding(data)
# data = hierarchical_clustering(data, features, 4)
# print(data.head())
# data = reverse_label_encoding(data, labels)
# hierarchical_clustering_to_csv(data, 4)
# summary_cluster("cluster_1.csv")

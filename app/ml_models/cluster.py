import os
import pickle

import numpy as np
import pandas as pd
from sklearn.metrics import silhouette_score
from sklearn.mixture import GaussianMixture
from sklearn.preprocessing import StandardScaler

from app.data_preparation_ulits.label_encode_data import (
    apply_label_encoding,
    reverse_label_encoding,
)
from app.data_preparation_ulits.one_hot_encode import one_hot_encode_data
from app.filename_utils import (
    directory_cluster_format,
    filename_categorical_columns_list_pkl,
    filename_one_hot_encoded_data_csv,
    filename_raw_data_csv,
    filename_rev_one_hot_encoded_dict_pkl,
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

    df, label_encoders = apply_label_encoding(df)
    df = gaussian_clustering(df, features)
    df = reverse_label_encoding(df, label_encoders)
    hierarchical_clustering_to_csv(df, directory_project)


def gaussian_clustering(df, features):
    scaler = StandardScaler()
    x = df[features]
    x_scaled = scaler.fit_transform(x)

    n_components = np.arange(2, 11)

    silhouette_scores = []
    for n in n_components[1:]:
        gmm = GaussianMixture(n, covariance_type="full", random_state=0)
        labels = gmm.fit_predict(x_scaled)
        score = silhouette_score(x_scaled, labels)
        silhouette_scores.append(score)

    optimal_silhouette_clusters = n_components[1:][np.argmax(silhouette_scores)]
    best_gmm = GaussianMixture(n_components=optimal_silhouette_clusters, random_state=0)
    df["hierarchical_cluster"] = best_gmm.fit_predict(x_scaled)
    return df


def hierarchical_clustering_to_csv(data, directory_project):

    for cluster in data["hierarchical_cluster"].unique():
        cluster_df = data[data["hierarchical_cluster"] == cluster].drop(
            columns=["hierarchical_cluster"]
        )
        cluster_directory = os.path.join(directory_project, directory_cluster_format(cluster))
        os.makedirs(cluster_directory, exist_ok=True)

        cluster_filename_raw_data_path = os.path.join(cluster_directory, filename_raw_data_csv())
        cluster_df.to_csv(cluster_filename_raw_data_path, index=False)

        cluster_filename_one_hot_encoded_path = os.path.join(
            cluster_directory, filename_one_hot_encoded_data_csv()
        )
        cluster_filename_one_hot_encoded_labels_path = os.path.join(
            cluster_directory, filename_rev_one_hot_encoded_dict_pkl()
        )
        cluster_filename_categorical_columns_path = os.path.join(
            cluster_directory, filename_categorical_columns_list_pkl()
        )
        one_hot_encode_data(
            cluster_filename_raw_data_path,
            cluster_filename_one_hot_encoded_labels_path,
            cluster_filename_one_hot_encoded_path,
        )

        categorical_columns = cluster_df.select_dtypes(include=["object"]).columns.tolist()
        with open(cluster_filename_categorical_columns_path, "wb") as file:
            pickle.dump(categorical_columns, file)

import os
import pickle

import numpy as np
import pandas as pd
from sklearn.metrics import silhouette_score
from sklearn.mixture import GaussianMixture
from sklearn.preprocessing import StandardScaler

from app.data_preparation_ulits.label_encode_data import reverse_label_encoding
from app.filename_utils import (
    directory_cluster_format,
    filename_label_encoded_data_csv,
    filename_raw_data_csv,
)


def optimised_clustering(
    directory_project,
    input_file_path_label_encoded_csv,
    input_file_path_feature_rank_pkl,
):
    cluster_range = range(2, 11)
    features = []
    with open(input_file_path_feature_rank_pkl, "rb") as file:
        features = pickle.load(file)
    df = pd.read_csv(input_file_path_label_encoded_csv)
    scaler = StandardScaler()
    x = df[features]
    x_scaled = scaler.fit_transform(x)

    # Initialize lists to store metrics
    silhouette_scores = []
    bic_scores = []
    aic_scores = []

    # Loop over the range of cluster numbers
    for n_clusters in cluster_range:
        gmm = GaussianMixture(n_components=n_clusters, random_state=0)
        cluster_labels = gmm.fit_predict(x_scaled)

        # Calculate metrics
        silhouette_avg = silhouette_score(x_scaled, cluster_labels)
        silhouette_scores.append(silhouette_avg)
        bic_scores.append(gmm.bic(x_scaled))
        aic_scores.append(gmm.aic(x_scaled))

    # Find optimal number of clusters based on minimum BIC and AIC
    optimal_clusters_bic = cluster_range[np.argmin(bic_scores)]
    optimal_clusters_aic = cluster_range[np.argmin(aic_scores)]

    # Select the optimal cluster count (you can choose BIC or AIC)
    best_cluster_count = optimal_clusters_bic  # Here we use BIC; change to optimal_clusters_aic if preferred

    # Refit the GMM model with the best cluster count
    best_gmm = GaussianMixture(n_components=best_cluster_count, random_state=0)
    df["cluster_label"] = best_gmm.fit_predict(x_scaled)

    # Save each cluster as a separate file
    for cluster in df["cluster_label"].unique():
        cluster_df = df[df["cluster_label"] == cluster]
        cluster_directory = os.path.join(
            directory_project, directory_cluster_format(cluster)
        )
        os.makedirs(cluster_directory, exist_ok=True)
        cluster_filename_raw_data_path = os.path.join(
            cluster_directory, filename_raw_data_csv()
        )
        cluster_filename_label_encoded_path = os.path.join(
            cluster_directory, filename_label_encoded_data_csv()
        )
        cluster_df.to_csv(cluster_filename_label_encoded_path, index=False)


# features = [
#     "Number_of_Months",
#     "amount_paid",
#     "magazine_fee_paid",
#     "Coupon_Discount",
#     "reading_fee_paid",
#     "security_deposit",
#     "Percentage_Share",
#     "Renewal_Amount",
#     "taxable_amount",
# ]

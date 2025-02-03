import os

import numpy as np
import pandas as pd
from sklearn.cluster import AgglomerativeClustering
from sklearn.metrics import silhouette_score
from sklearn.mixture import GaussianMixture
from sklearn.preprocessing import StandardScaler

from app.data_preparation_ulits.label_encode_data import (
    apply_label_encoding, reverse_label_encoding)
from app.data_preparation_ulits.one_hot_encode import one_hot_encode_data
from app.utils.filename_utils import (directory_cluster_format,
                                      filename_categorical_columns_list_pkl,
                                      filename_cluster_defs_dict_pkl,
                                      filename_one_hot_encoded_data_csv,
                                      filename_raw_data_csv,
                                      filename_rev_one_hot_encoded_dict_pkl)
from app.utils.os_utils import load_from_pickle, save_to_pickle


def optimised_clustering(
    directory_project,
    input_file_path_drop_column_csv,
    input_file_path_raw_data_csv,
    input_file_path_feature_rank_pkl,
):

    df = pd.read_csv(input_file_path_raw_data_csv)

    features = load_from_pickle(input_file_path_feature_rank_pkl)

    df, label_encoders = apply_label_encoding(df)
    df = gaussian_clustering(df, features)
    df = reverse_label_encoding(df, label_encoders)
    hierarchical_clustering_to_csv(df, directory_project)
    df_result, cluster_defs, target_summary = hierarchical_clustering_auto(
        df=df,
        feature_cols=features,
        cluster_target="Revenue",  # optional
        range_n_clusters=range(2, 11),
        random_state=42,
    )
    save_to_pickle(cluster_defs, os.path.join(directory_project, filename_cluster_defs_dict_pkl()))


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
        save_to_pickle(categorical_columns, cluster_filename_categorical_columns_path)


def hierarchical_clustering_auto(
    df: pd.DataFrame,
    feature_cols: list,
    cluster_target: str = None,
    range_n_clusters=range(2, 11),
    random_state=0,
):
    """
    1) Scans a range of cluster counts (e.g., 2..10) using GMM to compute BIC, AIC, and Silhouette.
       - Silhouette only for n >= 2.
    2) Automatically picks the cluster count that yields the highest Silhouette.
    3) Performs Hierarchical Clustering (Ward's linkage) with that cluster count.
    4) Adds 'hierarchical_cluster' to your DataFrame.
    5) Summarizes 'cluster_target' by cluster (if cluster_target is given).
    6) Extracts "cluster definitions" (z-scores) for each cluster.

    Returns:
       df_out: DataFrame copy with new column 'hierarchical_cluster'
       cluster_definitions: dict {cluster_label -> DataFrame of [feature, cluster_mean, overall_mean, z_score, abs_z_score]}
       target_summary: If 'cluster_target' is provided, sum of that target per cluster. Otherwise empty DataFrame.
    """

    # (A) Create a copy so we don't mutate
    df_out = df.copy()

    # (B) Scale the chosen features
    X_raw = df_out[feature_cols].values
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X_raw)

    # (C) Compute metrics for GMM across range_n_clusters
    bic_scores = []
    aic_scores = []
    silhouette_scores = []

    for n in range_n_clusters:
        gmm = GaussianMixture(n_components=n, covariance_type="full", random_state=random_state)
        gmm.fit(X_scaled)

        bic_scores.append(gmm.bic(X_scaled))
        aic_scores.append(gmm.aic(X_scaled))

        if n >= 2:
            labels = gmm.predict(X_scaled)
            sil_score = silhouette_score(X_scaled, labels)
            silhouette_scores.append(sil_score)
        else:
            silhouette_scores.append(np.nan)

    # (D) Find the best cluster count by Silhouette (you can change to BIC or AIC)
    # Convert range_n_clusters to a list or array
    n_components_list = np.array(list(range_n_clusters), dtype=int)

    # For Silhouette: skip n=1, so we consider indices for n>=2
    silhouette_array = np.array(silhouette_scores, dtype=float)
    best_idx = np.nanargmax(silhouette_array)  # index of max silhouette
    best_n_sil = n_components_list[best_idx]  # cluster count

    print(f"Auto-selected cluster count (by Silhouette) = {best_n_sil}")

    # (E) Hierarchical Clustering with best_n_sil
    hier_clustering = AgglomerativeClustering(n_clusters=best_n_sil, linkage="ward")
    cluster_labels = hier_clustering.fit_predict(X_scaled)

    df_out["hierarchical_cluster"] = cluster_labels

    # (F) Summarize the target variable by cluster
    if cluster_target and cluster_target in df_out.columns:
        target_summary = (
            df_out.groupby("hierarchical_cluster")[cluster_target]
            .sum()
            .reset_index()
            .rename(columns={cluster_target: "total_" + cluster_target})
        )
    else:
        target_summary = pd.DataFrame()

    # (G) Extract cluster definitions (feature z-scores)
    cluster_definitions = _extract_cluster_definitions_hierarchical(
        df_out=df_out, feature_cols=feature_cols, cluster_col="hierarchical_cluster"
    )

    return df_out, cluster_definitions, target_summary


def _extract_cluster_definitions_hierarchical(
    df_out, feature_cols, cluster_col="hierarchical_cluster"
):
    """
    Helper function:
      For each hierarchical cluster, compute:
      - cluster_mean for each feature
      - overall_mean for each feature
      - z_score = (cluster_mean - overall_mean) / overall_std
      - abs_z_score for sorting
    Returns dict {cluster_label -> DataFrame}.
    """

    overall_mean = df_out[feature_cols].mean()
    overall_std = df_out[feature_cols].std().replace(0, 1e-9)  # avoid /0

    definitions = {}
    for c_label in sorted(df_out[cluster_col].unique()):
        cluster_data = df_out[df_out[cluster_col] == c_label][feature_cols]
        cluster_mean = cluster_data.mean()

        z_scores = (cluster_mean - overall_mean) / overall_std

        df_def = pd.DataFrame(
            {
                "feature": feature_cols,
                "cluster_mean": cluster_mean.values,
                "overall_mean": overall_mean.values,
                "z_score": z_scores.values,
            }
        )
        df_def["abs_z_score"] = df_def["z_score"].abs()

        # Sort by largest absolute z-score
        df_def.sort_values("abs_z_score", ascending=False, inplace=True)
        df_def.reset_index(drop=True, inplace=True)

        definitions[c_label] = df_def

    return definitions


def get_cluster_weights(cluster_definitions, cluster_label):
    """
    Given the dictionary of cluster definitions and a cluster label,
    returns the DataFrame that describes that cluster's features.

    Usage:
        cluster_df = get_cluster_weights(cluster_definitions, cluster_label=2)
    """
    return cluster_definitions.get(cluster_label, pd.DataFrame())


# function definition

# feature_cols = [
#     "reading_fee_paid",
#     "Number_of_Months",
#     "Membership_expiry_date",
#     "transaction",
#     "member_branch_id",
#     "Coupon_Discount",
#     "magazine_fee_paid",
#     "branch_name",
#     "created_name",
#     "display_name",
#     "branch_type",
#     "Renewal_Amount",
#     "over_due_adjustment_amount",
#     "Member_Name",
#     "Percentage_Share",
#     "reversed",
#     "adjustment_amount",
#     "Message_Status",
# ]

# print(df[feature_cols].dtypes)

# df_result, cluster_defs, target_summary = hierarchical_clustering_auto(
#     df=df,
#     feature_cols=feature_cols,
#     cluster_target="Revenue",  # optional
#     range_n_clusters=range(2, 11),
#     random_state=42,
# )


# Calling a function


# print(target_summary)

# # Inspect definitions for cluster 0:
# cluster0_defs = get_cluster_weights(cluster_defs, 0)
# print(cluster0_defs)

# # Inspect definitions for cluster 1:
# cluster1_defs = get_cluster_weights(cluster_defs, 1)
# print(cluster1_defs)

# cluster1_defs = get_cluster_weights(cluster_defs, 2)
# print(cluster1_defs)

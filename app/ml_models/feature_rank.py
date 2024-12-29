import os
import pickle

import pandas as pd
from sklearn.linear_model import LinearRegression

from app.data_preparation_ulits.label_encode_data import apply_label_encoding
from app.filename_utils import filename_feature_rank_list_pkl, filename_feature_rank_score_df
from app.ml_models.feature_ranking_ulits.extra_trees import extra_trees
from app.ml_models.feature_ranking_ulits.f_test_anova import f_test_anova
from app.ml_models.feature_ranking_ulits.mutual_info import mutual_info
from app.ml_models.feature_ranking_ulits.permutation_importance_svr import (
    permutation_importance_svr,
)
from app.ml_models.feature_ranking_ulits.random_forest import random_forest
from app.ml_models.feature_ranking_ulits.seq_feature_selector import perform_feature_selection


def generate_optimized_feature_rankings(
    kpi,
    kpi_list: list,
    important_features: list,
    directory_project: str,
    input_file_path_raw_data_csv: str,
    input_file_path_drop_column_csv: str,
):

    if os.path.isfile(input_file_path_drop_column_csv):
        df = pd.read_csv(input_file_path_drop_column_csv)
    else:
        df = pd.read_csv(input_file_path_raw_data_csv)

    df, label_encoders = apply_label_encoding(df)
    del label_encoders
    top_features = compute_feature_rankings(df, kpi, kpi_list)

    final_output = pd.concat([top_features], ignore_index=True)
    save_results(final_output, directory_project, kpi, important_features)

    return final_output["Feature"].to_list()


def compute_feature_rankings(df, kpi, kpi_list):
    if kpi not in kpi_list:
        kpi_list.append(kpi)

    feature_vars = [col for col in df.columns if col not in kpi_list]
    X = df[feature_vars]
    Y = df[kpi]

    algorithms = [
        "f_test_anova",
        "mutual_info",
        "extra_trees",
        "seq_feature_selector",
        "random_forest",
    ]
    weights = {
        "f_test_anova": 1.5,
        "mutual_info": 1.5,
        "extra_trees": 1.5,
        "seq_feature_selector": 1.0,
        "random_forest": 1.0,
    }

    impact_data = run_all_ranking_algorithms(algorithms, X, Y, feature_vars, weights)
    impact_data = compute_impact_score(impact_data)

    impact_data = impact_data.sort_values("Impact_Score", ascending=False).reset_index(drop=True)

    TOTAL_NUMBER_FEATURES = 20
    top_features = impact_data.head(TOTAL_NUMBER_FEATURES)
    return top_features


def execute_feature_ranking_algorithm(algorithm, X, Y, feature_vars):
    k_features = len(feature_vars)
    if algorithm == "f_test_anova":
        # result = f_test_anova(X, Y, k_features)
        # result = result.rename(columns={"Score": "Importance"})
        # return result
        pass
    elif algorithm == "mutual_info":
        return mutual_info(X, Y, k_features).rename(columns={"Score": "Importance"})
    elif algorithm == "extra_trees":
        return extra_trees(X, Y).rename(columns={"Score": "Importance"})
    elif algorithm == "permutation_importance_svr":
        feature_names = X.columns
        return permutation_importance_svr(X, Y, k_features, feature_names).rename(
            columns={"Score": "Importance"}
        )
    elif algorithm == "seq_feature_selector":
        selected_features, X_scaled, selector = perform_feature_selection(X, Y, k_features)

        regressor = LinearRegression()
        X_selected = X_scaled[:, list(selector.k_feature_idx_)]
        regressor.fit(X_selected, Y)
        feature_importances = regressor.coef_

        feature_importances_filtered = [
            feature_importances[i]
            for i in range(len(feature_importances))
            if i in selector.k_feature_idx_
        ]
        selected_features_filtered = [
            selected_features[i]
            for i in range(len(selected_features))
            if i in selector.k_feature_idx_
        ]

        importance_df = pd.DataFrame(
            {"Feature": selected_features_filtered, "Importance": feature_importances_filtered}
        ).sort_values(by="Importance", ascending=False)

        return importance_df
    elif algorithm == "random_forest":
        k_features = len(feature_vars)
        selected_features, X_scaled, rf_regressor = random_forest(X, Y, k_features)

        importances = rf_regressor.feature_importances_
        selected_feature_indices = [
            i for i in range(len(feature_vars)) if feature_vars[i] in selected_features
        ]
        filtered_importances = [importances[i] for i in selected_feature_indices]

        print("Length of selected_features:", len(selected_features))
        print("Length of filtered_importances:", len(filtered_importances))

        importance_df = pd.DataFrame(
            {"Feature": selected_features, "Importance": filtered_importances}
        ).sort_values(by="Importance", ascending=False)

        return importance_df
    else:
        return None


def run_all_ranking_algorithms(algorithms, X, Y, feature_vars, weights):
    results = {}
    impact_data = pd.DataFrame(columns=["Feature"])

    for algorithm in algorithms:
        result = execute_feature_ranking_algorithm(algorithm, X, Y, feature_vars)

        if result is not None:
            results[algorithm] = result
            result = normalize_importance(result)
            result = compute_rank_score(result, algorithm, weights)
            impact_data = pd.merge(
                impact_data,
                result[["Feature", "Weighted_Rank_Score"]],
                on="Feature",
                how="outer",
                suffixes=("", f"_{algorithm}"),
            )

    return impact_data


def normalize_importance(result):
    result["Normalized_Importance"] = (result["Importance"] - result["Importance"].min()) / (
        result["Importance"].max() - result["Importance"].min()
    )
    return result


# Helper Function to compute rank and weighted rank score
def compute_rank_score(result, algorithm, weights):
    result["Rank"] = result["Normalized_Importance"].rank(ascending=False, method="dense")
    result["Weighted_Rank_Score"] = 1 / result["Rank"]
    result["Weighted_Rank_Score"] *= weights[algorithm]
    return result


# Helper Function to compute the final impact score
def compute_impact_score(impact_data):
    impact_data["Impact_Score"] = impact_data.filter(like="Weighted_Rank_Score").sum(axis=1)
    impact_data["Impact_Score"] = (
        impact_data["Impact_Score"] - impact_data["Impact_Score"].min()
    ) / (impact_data["Impact_Score"].max() - impact_data["Impact_Score"].min())
    return impact_data


# Helper Function to save the results
def save_results(final_output, directory_project, kpi, kpi_list):
    final_output[["Feature", "Impact_Score"]].to_pickle(
        os.path.join(directory_project, filename_feature_rank_score_df(kpi))
    )

    feature_list = final_output["Feature"].to_list()
    union_list = list(set(feature_list).union(kpi_list))

    with open(
        os.path.join(directory_project, filename_feature_rank_list_pkl(kpi)), "wb"
    ) as feature_list_pkl_file:
        pickle.dump(union_list, feature_list_pkl_file)


def extract_feature_variables(df, kpi_list):
    return [col for col in df.columns if col not in kpi_list]

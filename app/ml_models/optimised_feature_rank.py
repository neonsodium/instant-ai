import os
import pickle

import pandas as pd
from sklearn.linear_model import LinearRegression

from app.filename_utils import (
    filename_feature_rank_list_pkl,
    filename_feature_rank_result_txt,
    filename_feature_rank_score_df,
)
from app.ml_models.feature_ranking_ulits.extra_trees import extra_trees
from app.ml_models.feature_ranking_ulits.f_test_anova import f_test_anova
from app.ml_models.feature_ranking_ulits.mutual_info import mutual_info
from app.ml_models.feature_ranking_ulits.permutation_importance_svr import (
    permutation_importance_svr,
)
from app.ml_models.feature_ranking_ulits.random_forest import random_forest
from app.ml_models.feature_ranking_ulits.seq_feature_selector import perform_feature_selection


def run_algorithm(algorithm, X, Y, feature_vars):
    k_features = len(feature_vars)
    if algorithm == "f_test_anova":
        result = f_test_anova(X, Y, k_features)
        result = result.rename(columns={"Score": "Importance"})
        return result
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


def optimised_feature_rank(
    target_var, target_vars_list: list, file_path_label_encoded_csv: str, directory_project: str
):
    df = pd.read_csv(file_path_label_encoded_csv)
    # df = df.drop(columns=["# created_date"])
    feature_vars = [col for col in df.columns if col not in target_vars_list]
    print(feature_vars)
    X = df[feature_vars]
    Y = df[target_var]

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

    results = {}
    impact_data = pd.DataFrame(columns=["Feature"])

    with open(
        os.path.join(directory_project, filename_feature_rank_result_txt(target_var)), "w"
    ) as file:
        for algorithm in algorithms:
            file.write(f"Running {algorithm} on target variable '{target_var}'\n")
            result = run_algorithm(algorithm, X, Y, feature_vars)

            if result is not None:
                file.write(result.head(1000).to_string())
                file.write("\n\n")
                results[algorithm] = result

                # Normalize the importance scores between 0 and 1
                result["Normalized_Importance"] = (
                    result["Importance"] - result["Importance"].min()
                ) / (result["Importance"].max() - result["Importance"].min())

                # Convert ranks into weighted scores, with higher ranks having more weight
                result["Rank"] = result["Normalized_Importance"].rank(
                    ascending=False, method="dense"
                )
                result["Weighted_Rank_Score"] = 1 / result["Rank"]  # Inverse rank score
                result["Weighted_Rank_Score"] *= weights[algorithm]  # Apply algorithm weight

                # Merge the weighted rank score into the impact data
                impact_data = pd.merge(
                    impact_data,
                    result[["Feature", "Weighted_Rank_Score"]],
                    on="Feature",
                    how="outer",
                    suffixes=("", f"_{algorithm}"),
                )

        # Calculate the final impact score as the weighted average of the rank scores
        impact_data["Impact_Score"] = impact_data.filter(like="Weighted_Rank_Score").sum(axis=1)
        # Normalize the final impact score between 0 and 1
        impact_data["Impact_Score"] = (
            impact_data["Impact_Score"] - impact_data["Impact_Score"].min()
        ) / (impact_data["Impact_Score"].max() - impact_data["Impact_Score"].min())

        # Sort by Impact_Score
        impact_data = impact_data.sort_values("Impact_Score", ascending=False).reset_index(
            drop=True
        )

        # Get the top 10 and bottom 10 features
        TOTAL_NUMBER_FEATURES = 20
        top_features = impact_data.head(TOTAL_NUMBER_FEATURES)
        print(top_features)

        # Concatenate top and bottom features
        final_output = pd.concat([top_features], ignore_index=True)
        feature_list = final_output["Feature"].to_list()

        # final ranking data saved in the project dir
        # TODO improve logic
        final_output[["Feature", "Impact_Score"]].to_pickle(
            os.path.join(directory_project, filename_feature_rank_score_df(target_var))
        )
        # print(final_output[['Feature', 'Impact_Score']])
        feature_list = final_output["Feature"].to_list()
        with open(
            os.path.join(directory_project, filename_feature_rank_list_pkl(target_var)), "wb"
        ) as file:
            pickle.dump(feature_list, file)

# %%writefile random_forest.py
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import cross_val_score
from sklearn.preprocessing import StandardScaler


def random_forest(X, Y, k_features=10):

    scaler = StandardScaler().fit(X)
    X_scaled = scaler.transform(X)

    rf_regressor = RandomForestRegressor()

    rf_regressor.fit(X_scaled, Y)

    importances = rf_regressor.feature_importances_

    indices = importances.argsort()[-k_features:]
    selected_feature_names = X.columns[indices]

    return selected_feature_names, X_scaled, rf_regressor


# %%writefile main.py
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import StandardScaler

# from seq_feature_selector import perform_feature_selection
# from random_forest import random_forest
# from f_test_anova import f_test_anova
# from mutual_info import mutual_info
# from extra_trees import extra_trees
# from permutation_importance_svr import permutation_importance_svr

# df = pd.read_csv("/content/drive/My Drive/new_data3.csv")
df = pd.read_csv("encoded_file.csv")
df = df.drop(columns=["# created_date"])

target_vars = [
    "reading_fee_paid",
    "Number_of_Months",
    "Coupon_Discount",
    "num_books",
    "magazine_fee_paid",
    "Renewal_Amount",
    "amount_paid",
]
feature_vars = [col for col in df.columns if col not in target_vars]


def run_algorithm(algorithm, X, Y):
    if algorithm == "f_test_anova":
        result = f_test_anova(X, Y)
        result = result.rename(columns={"Score": "Importance"})
        return result
    elif algorithm == "mutual_info":
        return mutual_info(X, Y).rename(columns={"Score": "Importance"})
    elif algorithm == "extra_trees":
        return extra_trees(X, Y).rename(columns={"Score": "Importance"})
    elif algorithm == "permutation_importance_svr":
        feature_names = X.columns
        return permutation_importance_svr(X, Y, feature_names).rename(
            columns={"Score": "Importance"}
        )
    elif algorithm == "seq_feature_selector":
        k_features = 10
        selected_features, X_scaled, selector = perform_feature_selection(
            X, Y, k_features
        )

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
            {
                "Feature": selected_features_filtered,
                "Importance": feature_importances_filtered,
            }
        ).sort_values(by="Importance", ascending=False)

        return importance_df
    elif algorithm == "random_forest":
        k_features = 10
        selected_features, X_scaled, rf_regressor = random_forest(X, Y, k_features)

        importances = rf_regressor.feature_importances_
        selected_feature_indices = [
            i for i in range(len(feature_vars)) if feature_vars[i] in selected_features
        ]
        filtered_importances = [importances[i] for i in selected_feature_indices]

        importance_df = pd.DataFrame(
            {"Feature": selected_features, "Importance": filtered_importances}
        ).sort_values(by="Importance", ascending=False)

        return importance_df
    else:
        print("Algorithm not recognized.")
        return None


if __name__ == "__main__":
    target = input(f"Please enter a target variable from the list {target_vars}: ")

    if target not in target_vars:
        print(f"Invalid target variable. Please choose from {target_vars}.")
    else:
        X = df[feature_vars]
        Y = df[target]

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

        with open(f"results_{target}.txt", "w") as file:
            for algorithm in algorithms:
                print(f"Running {algorithm} on target variable '{target}'")
                file.write(f"Running {algorithm} on target variable '{target}'\n")
                result = run_algorithm(algorithm, X, Y)

                if result is not None:
                    print(result.head(10))
                    file.write(result.head(10).to_string())
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
                    result["Weighted_Rank_Score"] = (
                        1 / result["Rank"]
                    )  # Inverse rank score
                    result["Weighted_Rank_Score"] *= weights[
                        algorithm
                    ]  # Apply algorithm weight

                    # Merge the weighted rank score into the impact data
                    impact_data = pd.merge(
                        impact_data,
                        result[["Feature", "Weighted_Rank_Score"]],
                        on="Feature",
                        how="outer",
                        suffixes=("", f"_{algorithm}"),
                    )

            # Calculate the final impact score as the weighted average of the rank scores
            impact_data["Impact_Score"] = impact_data.filter(
                like="Weighted_Rank_Score"
            ).sum(axis=1)
            # Normalize the final impact score between 0 and 1
            impact_data["Impact_Score"] = (
                impact_data["Impact_Score"] - impact_data["Impact_Score"].min()
            ) / (impact_data["Impact_Score"].max() - impact_data["Impact_Score"].min())

            # Sort the DataFrame by Impact_Score
            impact_data = impact_data.sort_values(
                "Impact_Score", ascending=False
            ).reset_index(drop=True)

            # Get the top 10 and bottom 10 features
            top_10 = impact_data.head(20)

            # Concatenate top and bottom features
            final_output = pd.concat([top_10], ignore_index=True)

            # Print the final ranking with impact score
            print("\nFinal Ranking with Impact Score:\n")
            print(final_output[["Feature", "Impact_Score"]])

            # Write the final ranking to a file
            file.write("\nFinal Ranking with Impact Score:\n")
            file.write(final_output[["Feature", "Impact_Score"]].to_string())
            file.write("\n")


import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.metrics import silhouette_score
from sklearn.mixture import GaussianMixture
from sklearn.preprocessing import StandardScaler


def find_and_save_separate_clusters(df, features, cluster_range=range(2, 11)):
    # Standardizing features
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
        cluster_filename = f"cluster_{cluster}.csv"
        cluster_df.to_csv(cluster_filename, index=False)
        print(f"Cluster {cluster} data saved to {cluster_filename}")

    # Plotting results
    plt.figure(figsize=(10, 5))
    plt.plot(cluster_range, silhouette_scores, marker="o", label="Silhouette Score")
    plt.xlabel("Number of Clusters")
    plt.ylabel("Silhouette Score")
    plt.title("Silhouette Score for Different Numbers of Clusters")
    plt.legend()
    plt.show()

    plt.figure(figsize=(10, 5))
    plt.plot(cluster_range, bic_scores, marker="o", label="BIC")
    plt.plot(cluster_range, aic_scores, marker="x", label="AIC")
    plt.xlabel("Number of Clusters")
    plt.ylabel("Score")
    plt.title("BIC and AIC Scores for Different Numbers of Clusters")
    plt.legend()
    plt.show()

    print(f"Optimal number of clusters based on BIC: {optimal_clusters_bic}")
    print(f"Optimal number of clusters based on AIC: {optimal_clusters_aic}")


# Usage example
features = [
    "Number_of_Months",
    "amount_paid",
    "magazine_fee_paid",
    "Coupon_Discount",
    "reading_fee_paid",
    "security_deposit",
    "Percentage_Share",
    "Renewal_Amount",
    "taxable_amount",
]
df = pd.read_csv("encoded_file.csv")
find_and_save_separate_clusters(df, features)

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.preprocessing import StandardScaler
from sklearn.mixture import GaussianMixture
from sklearn.metrics import silhouette_score

def find_and_save_separate_clusters(df, features, cluster_range=range(2, 11)):
    # Standardizing features
    x_scaled = StandardScaler().fit_transform(df[features])

    # Initialize lists to store metrics
    silhouette_scores = []
    bic_scores = []
    aic_scores = []

    # Loop over the range of cluster numbers
    for n_clusters in cluster_range:
        gmm = GaussianMixture(n_components=n_clusters, random_state=0)
        # Calculate metrics
        silhouette_scores.append(silhouette_score(x_scaled, gmm.fit_predict(x_scaled)))
        bic_scores.append(gmm.bic(x_scaled))
        aic_scores.append(gmm.aic(x_scaled))

    # Find optimal number of clusters based on minimum BIC and AIC
    optimal_clusters_bic = cluster_range[np.argmin(bic_scores)]
    optimal_clusters_aic = cluster_range[np.argmin(aic_scores)]

    # Select the optimal cluster count (you can choose BIC or AIC)
    # TODO Here we use BIC; change to optimal_clusters_aic if preferred
    # optimal_clusters_bic  
    # TODO silhouette_scores peak numebr of cluster
    # will  be input for GaussianMixture n_components = peak numebr of cluster
    # if n is 1, then stop

    # Refit the GMM model with the best cluster count
    df['cluster_label'] = GaussianMixture(n_components=optimal_clusters_bic, random_state=0).fit_predict(x_scaled)

    # Save each cluster as a separate file
    for cluster in df['cluster_label'].unique():
        cluster_df = df[df['cluster_label'] == cluster]
        cluster_filename = f"cluster_{cluster}.csv"
        cluster_df.to_csv(cluster_filename, index=False)
        print(f"Cluster {cluster} data saved to {cluster_filename}")

    # plt.figure(figsize=(10, 5))
    # plt.plot(cluster_range, silhouette_scores, marker='o', label='Silhouette Score')
    # plt.xlabel('Number of Clusters')
    # plt.ylabel('Silhouette Score')
    # plt.title('Silhouette Score for Different Numbers of Clusters')
    # plt.legend()
    # plt.show()

    # plt.figure(figsize=(10, 5))
    # plt.plot(cluster_range, bic_scores, marker='o', label='BIC')
    # plt.plot(cluster_range, aic_scores, marker='x', label='AIC')
    # plt.xlabel('Number of Clusters')
    # plt.ylabel('Score')
    # plt.title('BIC and AIC Scores for Different Numbers of Clusters')
    # plt.legend()
    # plt.show()

    print(f"Optimal number of clusters based on BIC: {optimal_clusters_bic}")
    print(f"Optimal number of clusters based on AIC: {optimal_clusters_aic}")

#TODO from feature selection: final ranking
features = ['Number_of_Months', 'amount_paid', 'magazine_fee_paid', 'Coupon_Discount',
            'reading_fee_paid', 'security_deposit', 'Percentage_Share', 'Renewal_Amount', 'taxable_amount']

# 
# df = pd.read_csv("encoded_file.csv")
# find_and_save_separate_clusters(df, features)
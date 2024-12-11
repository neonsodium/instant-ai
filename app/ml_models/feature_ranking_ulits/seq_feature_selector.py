import pandas as pd
from mlxtend.feature_selection import SequentialFeatureSelector as SFS
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import StandardScaler


def perform_feature_selection(X, Y, k_features):

    scaler = StandardScaler().fit(X)
    X_scaled = scaler.transform(X)

    regressor = LinearRegression()

    selector = SFS(regressor, k_features=k_features, scoring="neg_mean_squared_error", cv=5)

    selector.fit(X_scaled, Y)

    selected_feature_indices = selector.k_feature_idx_
    selected_feature_names = X.columns[list(selected_feature_indices)]

    return selected_feature_names, X_scaled, selector

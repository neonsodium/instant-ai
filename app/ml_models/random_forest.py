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

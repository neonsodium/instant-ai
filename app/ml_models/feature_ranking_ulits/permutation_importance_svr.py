import matplotlib.pyplot as plt
import pandas as pd
from sklearn.inspection import permutation_importance
from sklearn.svm import SVR


def permutation_importance_svr(X, Y, k_features, feature_names):
    model = SVR(kernel="linear")
    model.fit(X, Y)
    perm_importance = permutation_importance(model, X, Y)

    feature_importances = pd.DataFrame(
        {"Feature": feature_names, "Importance": perm_importance.importances_mean}
    )

    sorted_importances = feature_importances.sort_values(by="Importance", ascending=False)

    # Return top-k features
    return sorted_importances.head(k_features)

import matplotlib.pyplot as plt
from sklearn.svm import SVR
from sklearn.inspection import permutation_importance

def permutation_importance_svr(X, Y, feature_names):
    model = SVR(kernel='linear')
    model.fit(X, Y)
    perm_importance = permutation_importance(model, X, Y)
    sorted_idx = perm_importance.importances_mean.argsort()

    plt.barh(feature_names[sorted_idx][-10:], perm_importance.importances_mean[sorted_idx][-10:])
    plt.xlabel("Permutation Importance")
    plt.title("Permutation Importance")
    plt.show()

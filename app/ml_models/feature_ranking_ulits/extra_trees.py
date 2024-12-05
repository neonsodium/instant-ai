import pandas as pd
from sklearn.ensemble import ExtraTreesRegressor


def extra_trees(X, Y):
    model = ExtraTreesRegressor()
    model.fit(X, Y)
    feature_importances = model.feature_importances_
    featureScores = pd.DataFrame({"Feature": X.columns, "Importance": feature_importances})
    return featureScores.sort_values(by="Importance", ascending=False)

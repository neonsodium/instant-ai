import pandas as pd
from sklearn.feature_selection import SelectKBest, mutual_info_regression


def mutual_info(X, Y, k_features):
    bestfeatures = SelectKBest(score_func=mutual_info_regression, k=k_features)
    fit = bestfeatures.fit(X, Y)
    featureScores = pd.DataFrame({"Feature": X.columns, "Score": fit.scores_})
    return featureScores.sort_values(by="Score", ascending=False)

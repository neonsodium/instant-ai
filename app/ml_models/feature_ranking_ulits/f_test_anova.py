import pandas as pd
from sklearn.feature_selection import SelectKBest, f_regression


def f_test_anova(X, Y, k_features):
    bestfeatures = SelectKBest(score_func=f_regression, k=k_features)
    fit = bestfeatures.fit(X, Y)
    featureScores = pd.DataFrame({"Feature": X.columns, "Score": fit.scores_})
    ranked_features = featureScores.sort_values(by="Score", ascending=False).reset_index(drop=True)
    return ranked_features

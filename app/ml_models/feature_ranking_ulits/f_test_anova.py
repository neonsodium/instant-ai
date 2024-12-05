import pandas as pd
from sklearn.feature_selection import SelectKBest, f_regression


def f_test_anova(X, Y):
    bestfeatures = SelectKBest(score_func=f_regression, k=10)
    fit = bestfeatures.fit(X, Y)
    featureScores = pd.DataFrame({"Feature": X.columns, "Score": fit.scores_})
    ranked_features = featureScores.sort_values(by="Score", ascending=False).reset_index(drop=True)
    return ranked_features

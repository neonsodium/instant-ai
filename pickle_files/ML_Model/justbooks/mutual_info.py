import pandas as pd
from sklearn.feature_selection import SelectKBest, mutual_info_regression

def mutual_info(X, Y):
    bestfeatures = SelectKBest(score_func=mutual_info_regression, k=10)
    fit = bestfeatures.fit(X, Y)
    featureScores = pd.DataFrame({'Feature': X.columns, 'Score': fit.scores_})
    return featureScores.sort_values(by='Score', ascending=False)
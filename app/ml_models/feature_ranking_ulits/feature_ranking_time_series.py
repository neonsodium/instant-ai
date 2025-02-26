import numpy as np
import pandas as pd
from lightgbm import LGBMClassifier, LGBMRegressor
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.linear_model import Lasso, LogisticRegression
from sklearn.model_selection import train_test_split
from xgboost import XGBClassifier, XGBRegressor


def ensemble_feature_importance_auto(
    df: pd.DataFrame,  # Clusted onehot encoedd dataset
    target_col: str,  # user selected KPI
    features: list = None,  # <--- You can pass a list of features here (all onehot encoded cluster columns)
    random_state: int = 42,
):

    df = df.loc[:, ~df.columns.duplicated()]
    if features is None:
        features = [c for c in df.columns if c != target_col]

    X = df[features].copy()
    y = df[target_col].copy()

    y_unique = y.nunique(dropna=False)
    if pd.api.types.is_numeric_dtype(y):
        if y_unique <= 10:
            task_type = "classification"
        else:
            task_type = "regression"
    else:
        task_type = "classification"

    print(f"Auto-detected task_type = {task_type} (unique target values = {y_unique})")

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=random_state
    )
    del X_test, y_test

    if task_type == "classification":
        model_rf = RandomForestClassifier(n_estimators=100, random_state=random_state)
        # model_lgb = LGBMClassifier(random_state=random_state)
        model_xgb = XGBClassifier(
            use_label_encoder=False, eval_metric="logloss", random_state=random_state
        )
        model_lin = LogisticRegression(
            penalty="l1", solver="saga", max_iter=1000, random_state=random_state
        )
    else:
        model_rf = RandomForestRegressor(n_estimators=100, random_state=random_state)
        # model_lgb = LGBMRegressor(random_state=random_state)
        model_xgb = XGBRegressor(random_state=random_state)
        model_lin = Lasso(alpha=0.01, max_iter=10000, random_state=random_state)

    model_rf.fit(X_train, y_train)
    # model_lgb.fit(X_train, y_train)
    model_xgb.fit(X_train, y_train)
    model_lin.fit(X_train, y_train)

    rf_imp = _extract_importance(model_rf, features)
    # lgb_imp = _extract_importance(model_lgb, features)
    xgb_imp = _extract_importance(model_xgb, features)
    lin_imp = _extract_importance(model_lin, features)

    rf_imp_norm = _normalize_importances(rf_imp)
    # lgb_imp_norm = _normalize_importances(lgb_imp)
    xgb_imp_norm = _normalize_importances(xgb_imp)
    lin_imp_norm = _normalize_importances(lin_imp)

    df_imp = pd.DataFrame(
        {
            "feature": features,
            "rf_importance": rf_imp_norm,
            # "lgbm_importance": lgb_imp_norm,
            "xgb_importance": xgb_imp_norm,
            "linear_importance": lin_imp_norm,
        }
    )

    df_imp["final_importance"] = df_imp[
        # ["rf_importance", "lgbm_importance", "xgb_importance", "linear_importance"]
        ["rf_importance", "lgbm_importance", "xgb_importance", "linear_importance"]
    ].mean(axis=1)

    df_imp.sort_values("final_importance", ascending=False, inplace=True)
    df_imp.reset_index(drop=True, inplace=True)

    return df_imp


def _extract_importance(model, feature_names):

    n_features = len(feature_names)

    if hasattr(model, "feature_importances_"):
        imp = model.feature_importances_
        if len(imp) == n_features:
            return imp
        else:
            return np.zeros(n_features)
    elif hasattr(model, "coef_"):
        coefs = model.coef_ if hasattr(model, "coef_") else None
        if coefs is not None:
            if len(coefs.shape) > 1:
                # e.g. multi-class => sum abs
                abs_coef = np.abs(coefs).sum(axis=0)
            else:
                abs_coef = np.abs(coefs).flatten()
            if len(abs_coef) == n_features:
                return abs_coef

        if hasattr(model, "coef_") and isinstance(model.coef_, np.ndarray):
            c = np.abs(model.coef_)
            if c.shape[0] == n_features:
                return c
        return np.zeros(n_features)
    else:
        return np.zeros(n_features)


def _normalize_importances(imp_array):

    s = imp_array.sum()
    if s == 0:
        return imp_array
    return imp_array / s

from sklearn.preprocessing import LabelEncoder
from sklearn.impute import SimpleImputer
import numpy as np
import pandas as pd

# Load data
df = pd.read_csv('sales_data.csv')
# df = pd.read_csv('jb_sales.csv')
df.drop(['branch_email','Message_Status','User_Name','transaction','Month_Last_Date','TAX_TYPE','GST_AMOUNT','SGST_AMOUNT','CGST_AMOUNT','IGST_AMOUNT','created_by','id','created_name','Member_Name','email','transaction_date','payable_amount'], axis=1, inplace=True)
# Select columns with 'object' data type for label encoding
object_columns = df.select_dtypes(include=['object']).columns

# Initialize LabelEncoder
le = LabelEncoder()

# Apply label encoding to each object column
for col in object_columns:
    df[col] = le.fit_transform(df[col].astype(str))

# Impute missing values with the mean
imputer = SimpleImputer(missing_values=np.nan, strategy='mean')
df_imputed = imputer.fit_transform(df)

# Convert the imputed data back to a DataFrame
df_imputed = pd.DataFrame(df_imputed, columns=df.columns)

# Save the encoded and imputed DataFrame to a new CSV file
encoded_file_path = 'encoded_file.csv'
df_imputed.to_csv(encoded_file_path, index=False)



import pandas as pd
from sklearn.feature_selection import SelectKBest, f_regression

def f_test_anova(X, Y):
    bestfeatures = SelectKBest(score_func=f_regression, k=10)
    fit = bestfeatures.fit(X, Y)
    featureScores = pd.DataFrame({'Feature': X.columns, 'Score': fit.scores_})
    ranked_features = featureScores.sort_values(by='Score', ascending=False).reset_index(drop=True)
    return ranked_features

#writefile mutual_info.py
import pandas as pd
from sklearn.feature_selection import SelectKBest, mutual_info_regression

def mutual_info(X, Y):
    bestfeatures = SelectKBest(score_func=mutual_info_regression, k=10)
    fit = bestfeatures.fit(X, Y)
    featureScores = pd.DataFrame({'Feature': X.columns, 'Score': fit.scores_})
    return featureScores.sort_values(by='Score', ascending=False)



# writefile extra_trees.py
import pandas as pd
from sklearn.ensemble import ExtraTreesRegressor

def extra_trees(X, Y):
    model = ExtraTreesRegressor()
    model.fit(X, Y)
    feature_importances = model.feature_importances_
    featureScores = pd.DataFrame({'Feature': X.columns, 'Importance': feature_importances})
    return featureScores.sort_values(by='Importance', ascending=False)


# %%writefile permutation_importance_svr.py
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


# %%writefile seq_feature_selector.py
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LinearRegression
from mlxtend.feature_selection import SequentialFeatureSelector as SFS
import pandas as pd

def perform_feature_selection(X, Y, k_features=10):

    scaler = StandardScaler().fit(X)
    X_scaled = scaler.transform(X)

    regressor = LinearRegression()

    selector = SFS(regressor,
                    k_features=k_features,
                    scoring='neg_mean_squared_error',
                    cv=5)


    selector.fit(X_scaled, Y)


    selected_feature_indices = selector.k_feature_idx_
    selected_feature_names = X.columns[list(selected_feature_indices)]

    return selected_feature_names, X_scaled, selector



# %%writefile random_forest.py
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import cross_val_score
import pandas as pd

def random_forest(X, Y, k_features=10):

    scaler = StandardScaler().fit(X)
    X_scaled = scaler.transform(X)


    rf_regressor = RandomForestRegressor()


    rf_regressor.fit(X_scaled, Y)


    importances = rf_regressor.feature_importances_


    indices = importances.argsort()[-k_features:]
    selected_feature_names = X.columns[indices]

    return selected_feature_names, X_scaled, rf_regressor


# %%writefile main.py
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LinearRegression
#from seq_feature_selector import perform_feature_selection
#from random_forest import random_forest
#from f_test_anova import f_test_anova
#from mutual_info import mutual_info
#from extra_trees import extra_trees
# from permutation_importance_svr import permutation_importance_svr

#df = pd.read_csv("/content/drive/My Drive/new_data3.csv")
df = pd.read_csv("encoded_file.csv")
df = df.drop(columns=['# created_date'])

target_vars = ['reading_fee_paid', 'Number_of_Months', 'Coupon_Discount',
               'num_books', 'magazine_fee_paid', 'Renewal_Amount','amount_paid']
feature_vars = [col for col in df.columns if col not in target_vars]


def run_algorithm(algorithm, X, Y):
    if algorithm == 'f_test_anova':
        result = f_test_anova(X, Y)
        result = result.rename(columns={'Score': 'Importance'})
        return result
    elif algorithm == 'mutual_info':
        return mutual_info(X, Y).rename(columns={'Score': 'Importance'})
    elif algorithm == 'extra_trees':
        return extra_trees(X, Y).rename(columns={'Score': 'Importance'})
    elif algorithm == 'permutation_importance_svr':
        feature_names = X.columns
        return permutation_importance_svr(X, Y, feature_names).rename(columns={'Score': 'Importance'})
    elif algorithm == 'seq_feature_selector':
        k_features = 10
        selected_features, X_scaled, selector = perform_feature_selection(X, Y, k_features)

        regressor = LinearRegression()
        X_selected = X_scaled[:, list(selector.k_feature_idx_)]
        regressor.fit(X_selected, Y)
        feature_importances = regressor.coef_

        feature_importances_filtered = [feature_importances[i] for i in range(len(feature_importances)) if i in selector.k_feature_idx_]
        selected_features_filtered = [selected_features[i] for i in range(len(selected_features)) if i in selector.k_feature_idx_]

        importance_df = pd.DataFrame({
            'Feature': selected_features_filtered,
            'Importance': feature_importances_filtered
        }).sort_values(by='Importance', ascending=False)

        return importance_df
    elif algorithm == 'random_forest':
        k_features = 10
        selected_features, X_scaled, rf_regressor = random_forest(X, Y, k_features)

        importances = rf_regressor.feature_importances_
        selected_feature_indices = [i for i in range(len(feature_vars)) if feature_vars[i] in selected_features]
        filtered_importances = [importances[i] for i in selected_feature_indices]

        importance_df = pd.DataFrame({
            'Feature': selected_features,
            'Importance': filtered_importances
        }).sort_values(by='Importance', ascending=False)

        return importance_df
    else:
        print("Algorithm not recognized.")
        return None

if __name__ == "__main__":
    target = input(f"Please enter a target variable from the list {target_vars}: ")

    if target not in target_vars:
        print(f"Invalid target variable. Please choose from {target_vars}.")
    else:
        X = df[feature_vars]
        Y = df[target]

        algorithms = ['f_test_anova', 'mutual_info', 'extra_trees', 'seq_feature_selector', 'random_forest']
        weights = {
            'f_test_anova': 1.5,
            'mutual_info': 1.5,
            'extra_trees': 1.5,
            'seq_feature_selector': 1.0,
            'random_forest': 1.0
        }

        results = {}
        impact_data = pd.DataFrame(columns=['Feature'])

        with open(f"results_{target}.txt", 'w') as file:
            for algorithm in algorithms:
                print(f"Running {algorithm} on target variable '{target}'")
                file.write(f"Running {algorithm} on target variable '{target}'\n")
                result = run_algorithm(algorithm, X, Y)

                if result is not None:
                    print(result.head(10))
                    file.write(result.head(10).to_string())
                    file.write("\n\n")
                    results[algorithm] = result

                    # Normalize the importance scores between 0 and 1
                    result['Normalized_Importance'] = (result['Importance'] - result['Importance'].min()) / (result['Importance'].max() - result['Importance'].min())

                    # Convert ranks into weighted scores, with higher ranks having more weight
                    result['Rank'] = result['Normalized_Importance'].rank(ascending=False, method='dense')
                    result['Weighted_Rank_Score'] = 1 / result['Rank']  # Inverse rank score
                    result['Weighted_Rank_Score'] *= weights[algorithm]  # Apply algorithm weight

                    # Merge the weighted rank score into the impact data
                    impact_data = pd.merge(impact_data, result[['Feature', 'Weighted_Rank_Score']], on='Feature', how='outer', suffixes=('', f'_{algorithm}'))

            # Calculate the final impact score as the weighted average of the rank scores
            impact_data['Impact_Score'] = impact_data.filter(like='Weighted_Rank_Score').sum(axis=1)
            # Normalize the final impact score between 0 and 1
            impact_data['Impact_Score'] = (impact_data['Impact_Score'] - impact_data['Impact_Score'].min()) / (impact_data['Impact_Score'].max() - impact_data['Impact_Score'].min())

            # Sort the DataFrame by Impact_Score
            impact_data = impact_data.sort_values('Impact_Score', ascending=False).reset_index(drop=True)

            # Get the top 10 and bottom 10 features
            top_10 = impact_data.head(20)


            # Concatenate top and bottom features
            final_output = pd.concat([top_10], ignore_index=True)

            # Print the final ranking with impact score
            print("\nFinal Ranking with Impact Score:\n")
            print(final_output[['Feature', 'Impact_Score']])

            # Write the final ranking to a file
            file.write("\nFinal Ranking with Impact Score:\n")
            file.write(final_output[['Feature', 'Impact_Score']].to_string())
            file.write("\n")



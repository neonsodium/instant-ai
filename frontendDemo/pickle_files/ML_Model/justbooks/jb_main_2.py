import pandas as pd
from sklearn.linear_model import LinearRegression
from seq_feature_selector import perform_feature_selection
from random_forest import random_forest
from f_test_anova import f_test_anova
from mutual_info import mutual_info
from extra_trees import extra_trees
from permutation_importance_svr import permutation_importance_svr

df = pd.read_csv("labelencodedjb.csv")

target_vars = ['reading_fee_paid', 'Number_of_Months', 'Coupon_Discount',
               'num_books', 'magazine_fee_paid', 'Renewal_Amount']

feature_vars = ['# created_date', 'id', 'created_by', 'transaction_branch_id',
                'transaction_type_id', 'amount_paid', 'Coupon_Discount',
                'magazine_fee_paid', 'payable_amount', 'reading_fee_paid',
                'reversed', 'over_due_adjustment_amount', 'last_card_number',
                'primus_amount', 'adjustment_amount', 'security_deposit',
                'Percentage_Share', 'subscription_id', 'member_branch_id',
                'transaction', 'Transaction_Month', 'Transaction_Year',
                'created_name', 'branch_name','branch_type', 'member_card',
                'Member_Name', 'email','Number_of_Months', 'display_name',
                'Renewal_Amount','Message_Status', 'Membership_expiry_date',
                'User_Name', 'applied_reward_points', 'over_due_adjustment_amount.1',
                'reading_fee_adjustment_amount', 'share_percentage',
                'membership_start_date', 'Member_status', 'no_of_deliveries',
                'num_books', 'num_magazine', 'referred_by', 'dailysales']

def run_algorithm(algorithm, X, Y):
    if algorithm == 'f_test_anova':
        return f_test_anova(X, Y)
    elif algorithm == 'mutual_info':
        return mutual_info(X, Y)
    elif algorithm == 'extra_trees':
        return extra_trees(X, Y)
    elif algorithm == 'permutation_importance_svr':
        feature_names = X.columns
        permutation_importance_svr(X, Y, feature_names)
        return None
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

        results = {}

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
                    print("\n")


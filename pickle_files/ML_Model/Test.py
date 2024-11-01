import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
from sklearn_extra.cluster import KMedoids
import pickle
import pandas as pd

# Display all columns
pd.set_option('display.max_columns', None)

# Display all rows
pd.set_option('display.max_rows', None)


def get_branch_rank(branch_id):
    branch_dict = {1: [218, 354, 356, 318, 346, 953, 121, 310, 9], 2: [10, 958, 328, 1038, 957, 811], 3: [92, 89, 48, 345], 4: [21, 339, 340, 802, 351], 5: [224, 135], 6: [60], 7: [956, 134], 8: [11, 1042], 9: [1007], 10: [326], 11: [86], 12: [124, 125], 13: [903], 14: [801], 15: [75, 952], 16: [99], 17: [85, 91], 18: [97], 19: [17], 20: [959], 21: [70], 22: [108], 23: [1001], 24: [33], 25: [5], 26: [101], 27: [132], 28: [128], 29: [902], 30: [348], 31: [51, 114], 32: [131], 33: [120], 34: [36], 35: [15, 68], 36: [102], 37: [109], 38: [90], 39: [103], 40: [20], 41: [59], 42: [130], 43: [78], 44: [117], 45: [58], 46: [904], 47: [96], 48: [119], 49: [113], 50: [123], 51: [126], 52: [53], 53: [7], 54: [77], 55: [39], 56: [84], 57: [35], 58: [1013], 59: [57], 60: [47], 61: [112], 62: [14], 63: [18], 64: [2], 65: [115], 66: [25], 67: [129], 68: [116], 69: [347], 70: [55], 71: [87], 72: [1], 73: [26], 74: [110], 75: [100], 76: [331], 77: [62], 78: [56], 79: [8], 80: [122], 81: [16], 82: [350], 83: [1015], 84: [31], 85: [962], 86: [118], 87: [111], 88: [106], 89: [88], 90: [52], 91: [3], 92: [42], 93: [105], 94: [1003], 95: [63], 96: [1008], 97: [40], 98: [76], 99: [46], 100: [83], 101: [43], 102: [34], 103: [79], 104: [810], 105: [72], 106: [61], 107: [32], 108: [37], 109: [45], 110: [4]}
    for rank,branches in branch_dict.items():
        if(branch_id in branches):
            return rank

def get_optimal_cluster(category):
    grouped_data = filtered.groupby('cluster')
    cat_positions = pd.DataFrame(columns=['cat_rank','top_branch'],index=[0,1,2,3,4,5,6])
    for i,df in grouped_data:
        x = list(df['consolidated_category'].value_counts().sort_values(ascending=False).index).index(category)
        top_branch = list(df['issue_branch_id'].value_counts().sort_values(ascending=False).index)[0]
        cat_positions.at[i,'cat_rank'] = x
        cat_positions.at[i,'top_branch'] = get_branch_rank(top_branch)
    
    cat_positions.sort_values(by=['cat_rank','top_branch'],ascending=[True,False],inplace=True)
    return list(cat_positions.index)

def get_user_cluster(category,filtered):
    optimal_cluster = get_optimal_cluster(category)[0]
    return filtered[filtered['cluster']==optimal_cluster]

filtered=pd.read_csv("clustered_og_data.csv")

filtered["consolidated_category"].unique()

filtered.drop(columns=["Unnamed: 0"],inplace=True)

catagories = ['Non Fiction', 'Teens', 'Self Help', 'Fiction', 'Kids', 'GK','Languages', 'Entertainment']
for cat in catagories:
    x = get_user_cluster(cat,filtered)
    with open(f'cluster_model_{cat}.pkl', 'wb') as file:
        pickle.dump(x, file)
print(x.head(1))

# array(['Non Fiction', 'Teens', 'Self Help', 'Fiction', 'Kids', 'GK','Languages', 'Entertainment'], dtype=object)
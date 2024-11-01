import pandas as pd
import pickle

def read_rank_data(target):
    # Define the file name based on the target variable
    pickle_file_name = f"rank_data_{target}.pkl"
    
    # Open the pickle file and load the DataFrame
    with open(pickle_file_name, 'rb') as pickle_file:
        rank_data = pickle.load(pickle_file)
    
    # Return the DataFrame
    return rank_data

if __name__ == "__main__":
    target = input(f"Please enter the target variable to load the rank data: ")
    
    # Load and display the rank data
    try:
        rank_data = read_rank_data(target)
        print("\nLoaded Rank Data:")
        print(rank_data)
    except FileNotFoundError:
        print(f"Pickle file for target variable '{target}' not found.")

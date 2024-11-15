import pandas as pd
import pickle

# TODO not in use, remove
def reverse_label_encode_data(input_label_encoded_file_path: str, input_rev_label_encoded_path: str,output_label_encoded_mapping_path: str):
    df = pd.read_csv(input_label_encoded_file_path)
    with open(input_rev_label_encoded_path, "rb") as file:
        label_encoders = pickle.load(file)

    for col, mapping in label_encoders.items():
        # Reverse the mapping to get the original labels back
        reverse_mapping = {v: k for k, v in mapping.items()}
        df[col] = df[col].map(reverse_mapping)  # Map encoded values to original labels
        
    label_encoded_mapping = pd.DataFrame.from_dict(label_encoders, orient='index').T
    label_encoded_mapping = label_encoded_mapping.reset_index().rename(columns={'index': 'Original'})

    label_encoded_mapping.to_csv(output_label_encoded_mapping_path, index=False)
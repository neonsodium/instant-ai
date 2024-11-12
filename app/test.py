import time
from data_preparation_ulits.drop_columns import drop_columns_df
from data_preparation_ulits.label_encode_data import label_encode_data
from data_preparation_ulits.one_hot_encode import one_hot_encode_data
from data_preparation_ulits.preprocess_test_label_encoded_data import preprocess_label_encoded_data
from data_preparation_ulits.preprocess_test_one_hot_encoded import preprocess_one_hot_data
from data_preparation_ulits.reverse_label_encode import reverse_label_encode_data

# Define input and output file paths
input_file = "test_data/jb_sales.csv"
output_drop_tables = "test_data/drop_tables.csv"
output_pre_label = "test_data/pre_label.csv"
output_label = "test_data/label.csv"
output_pre_one_hot = "test_data/pre_one_hot.csv"
output_one_hot = "test_data/one_hot.csv"
output_rev_label = "test_data/rev_label.csv"
output_labeled_data = "test_data/labels.pkl"

res_list = []

# Measure execution time for each process
start_time = time.time()
drop_columns_df(input_file, output_drop_tables)
end_time = time.time()
res_list.append(f"drop_columns_df execution time: {end_time - start_time:.4f} seconds")

start_time = time.time()
preprocess_label_encoded_data(output_drop_tables, output_pre_label)
end_time = time.time()
res_list.append(f"preprocess_label_encoded_data execution time: {end_time - start_time:.4f} seconds")

start_time = time.time()
preprocess_one_hot_data(output_drop_tables, output_pre_one_hot)
end_time = time.time()
res_list.append(f"preprocess_one_hot_data execution time: {end_time - start_time:.4f} seconds")

start_time = time.time()
label_encode_data(output_pre_label, output_label, output_labeled_data)
end_time = time.time()
res_list.append(f"label_encode_data execution time: {end_time - start_time:.4f} seconds")

start_time = time.time()
one_hot_encode_data(output_pre_one_hot, output_one_hot)
end_time = time.time()
res_list.append(f"one_hot_encode_data execution time: {end_time - start_time:.4f} seconds")

start_time = time.time()
reverse_label_encode_data(output_label, output_rev_label, output_labeled_data)
end_time = time.time()
res_list.append(f"reverse_label_encode_data execution time: {end_time - start_time:.4f} seconds")

for i in res_list:
    print(i)

# drop_columns_df execution time: 0.2238 seconds
# preprocess_label_encoded_data execution time: 0.1700 seconds
# preprocess_one_hot_data execution time: 0.1786 seconds
# label_encode_data execution time: 0.2168 seconds
# one_hot_encode_data execution time: 109.0654 seconds
# reverse_label_encode_data execution time: 0.0344 seconds
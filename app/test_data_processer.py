from data_preparation_ulits.drop_columns import drop_columns_df
from data_preparation_ulits.label_encode_data import label_encode_data
from data_preparation_ulits.one_hot_encode import one_hot_encode_data
from data_preparation_ulits.preprocess_test_label_encoded_data import (
    preprocess_label_encoded_data,
)
from data_preparation_ulits.preprocess_test_one_hot_encoded import (
    preprocess_one_hot_data,
)
from data_preparation_ulits.reverse_label_encode import reverse_label_encode_data

input_file = "test_data/jb_sales.csv"
output_drop_tables = "test_data/drop_tables.csv"
output_pre_label = "test_data/pre_label.csv"
output_label = "test_data/label.csv"
output_pre_one_hot = "test_data/pre_one_hot.csv"
output_one_hot = "test_data/one_hot.csv"
output_rev_label_mapping = "test_data/rev_label_mapping.csv"
output_labeled_data = "test_data/labels.csv"

drop_columns_df(input_file, output_drop_tables)
preprocess_label_encoded_data(output_drop_tables, output_pre_label)
preprocess_one_hot_data(output_drop_tables, output_pre_one_hot)
label_encode_data(output_pre_label, output_labeled_data, output_rev_label_mapping)
one_hot_encode_data(output_pre_one_hot, output_one_hot)


# drop_columns_df execution time: 0.2238 seconds
# preprocess_label_encoded_data execution time: 0.1700 seconds
# preprocess_one_hot_data execution time: 0.1786 seconds
# label_encode_data execution time: 0.2168 seconds
# one_hot_encode_data execution time: 109.0654 seconds
# reverse_label_encode_data execution time: 0.0344 seconds

import os

import pandas as pd

from app.utils.filename_utils import filename_raw_data_csv


# TODO Get file name from Mongo
def mapping_columns(file_path: str, column_mapping: dict):
    pd.read_csv(file_path).rename(columns=column_mapping).to_csv(file_path, index=False)

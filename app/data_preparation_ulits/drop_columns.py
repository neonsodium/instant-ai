import os

import pandas as pd

from app.utils.filename_utils import filename_raw_data_csv


# TODO Get file name from Mongo
def drop_columns(file_path: str, drop_column_list: list):
    pd.read_csv(file_path).drop(drop_column_list, axis=1).to_csv(file_path, index=False)

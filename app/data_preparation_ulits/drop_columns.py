import os

import pandas as pd

from app.filename_utils import filename_dropeed_column_data_csv, filename_raw_data_csv


def drop_columns(directory_project: str, drop_column_list):
    drop_column_file = os.path.join(directory_project, filename_dropeed_column_data_csv())
    raw_data_file = os.path.join(directory_project, filename_raw_data_csv())
    if os.path.isfile(drop_column_file):
        df = pd.read_csv(drop_column_file)
    else:
        df = pd.read_csv(raw_data_file)

    df.drop(drop_column_list, axis=1, inplace=True)
    df.to_csv(drop_column_file, index=False)

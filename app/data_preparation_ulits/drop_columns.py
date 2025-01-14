import os

import pandas as pd

from app.utils.filename_utils import filename_raw_data_csv


# TODO Get file name from Mongo
def drop_columns(directory_project: str, drop_column_list):
    pd.read_csv(os.path.join(directory_project, filename_raw_data_csv())).drop(
        drop_column_list, axis=1
    ).to_csv(os.path.join(directory_project, filename_raw_data_csv()), index=False)

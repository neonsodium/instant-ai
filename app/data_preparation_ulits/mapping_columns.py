import os

import pandas as pd

from app.utils.filename_utils import filename_raw_data_csv


# TODO Get file name from Mongo
def mapping_columns(directory_project: str, column_mapping: dict):
    pd.read_csv(os.path.join(directory_project, filename_raw_data_csv())).rename(
        columns=column_mapping
    ).to_csv(os.path.join(directory_project, filename_raw_data_csv()), index=False)

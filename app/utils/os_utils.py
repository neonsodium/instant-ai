import os
import pickle
import re
from datetime import datetime

from flask import current_app

from app.utils.filename_utils import (
    directory_cluster_format,
    filename_project_description_txt,
    filename_project_name_txt,
)
from config import Config


def os_path_join_secure(base_dir: str, *sub_dirs: str) -> str:
    full_path = os.path.abspath(os.path.join(base_dir, *sub_dirs))
    if not full_path.startswith(os.path.abspath(base_dir)):
        raise ValueError("Unsafe path detected.")

    return full_path


def get_directory_tree(path):
    try:
        tree = {"name": os.path.basename(path) or path, "subcluster": []}

        entries = os.listdir(path)

        for entry in entries:
            full_path = os.path.join(path, entry)
            if os.path.isdir(full_path):
                tree["subcluster"].append(get_directory_tree(full_path))

        return tree
    except Exception as e:
        return {"error": str(e)}


def directory_project_path_full(project_id: str, path: list) -> str:
    sub_dirs = [directory_cluster_format(cluster_num) for cluster_num in path]
    a = os_path_join_secure(all_project_dir_path(), project_id)
    return os_path_join_secure(a, *sub_dirs)


def create_directory(base_dir: str, *sub_dirs: str) -> dict:
    """
    Creates a nested directory structure under the specified base directory.

    Args:
        base_dir (str): Base directory under which subdirectories will be created.
        sub_dirs (str): Variable number of subdirectories to nest within the base directory.

    Returns:
        dict: A response indicating 'success' or 'error' with a message and directory path.
    """
    directory_path = os_path_join_secure(base_dir, *sub_dirs)

    try:
        os.makedirs(directory_path, exist_ok=True)
        return {
            "status": "success",
            "message": "Directory created successfully.",
            "path": directory_path,
        }
    except OSError as e:
        return {
            "status": "error",
            "message": f"Failed to create directory: {str(e)}",
            "path": directory_path,
        }


def all_project_dir_path() -> str:
    return current_app.config[Config.PROJECTS_DIR_VAR_NAME]


def list_sub_directories(base_dir: str) -> list:
    list_sub_dir = []

    for project_id in os.listdir(base_dir):
        project_dir = os.path.join(base_dir, project_id)
        if os.path.isdir(project_dir):
            list_sub_dir.append(project_id)
    return list_sub_dir


def is_feature_ranking_file_present(directory_project: str) -> bool:
    """
    Checks if any file in the directory matches the pattern
    list_feature_ranking_<sanitized_target_var>.pkl
    """
    pattern = r"^list_feature_ranking_[A-Za-z0-9_]+\.pkl$"

    for file_name in os.listdir(directory_project):
        if re.match(pattern, file_name):
            return True

    return False


def save_to_pickle(data, file_path):
    """
    Saves the given data to a file using pickle.

    Args:
        data: The object to be pickled and saved.
        file_path (str): The file path where the pickled object should be stored.

    Returns:
        bool: True if the operation was successful, False otherwise.
    """
    try:
        with open(file_path, "wb") as file:
            pickle.dump(data, file)
        return True
    except (pickle.PickleError, IOError) as e:
        print(f"Error saving to pickle file: {e}")
        return False


def load_from_pickle(file_path):
    """
    Loads and returns data from a pickle file.

    Args:
        file_path (str): The file path of the pickle file to load.

    Returns:
        object: The deserialized object from the pickle file.
        None: If the operation fails.
    """
    try:
        with open(file_path, "rb") as file:
            data = pickle.load(file)
        return data
    except (pickle.UnpicklingError, IOError) as e:
        print(f"Error loading from pickle file: {e}")
        return None

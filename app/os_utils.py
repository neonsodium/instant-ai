import json
import os

from flask import current_app

from app.filename_utils import directory_cluster_format
from config import Config


def os_path_join_secure(base_dir: str, *sub_dirs: str) -> str:
    full_path = os.path.abspath(os.path.join(base_dir, *sub_dirs))
    if not full_path.startswith(os.path.abspath(base_dir)):
        raise ValueError("Unsafe path detected.")

    return full_path


def directory_project_path_full(project_id: str, path: list) -> str:
    # Create the list of formatted subdirectories
    sub_dirs = [directory_cluster_format(cluster_num) for cluster_num in path]
    return os_path_join_secure(
        os_path_join_secure(all_project_dir_path(), project_id), *sub_dirs
    )


def create_directory(base_dir: str, *sub_dirs: str) -> dict:
    """
    Creates a nested directory structure under the specified base directory.

    Usage:
        create_project_directory(current_app.config[Config.PROJECTS_DIR_VAR_NAME], 'dir1', 'dir11', 'task123')
        create_project_directory( project_dir_path(), 'dir1', 'dir11', 'task123')

    Args:
        base_dir (str): base directory under which subdirectories will be created.
        sub_dirs (str): Variable number of subdirectories to nest within the base directory.

    Returns:
        dict: A response indicating 'success' or 'error' with a message.
    """
    directory_path = os_path_join_secure(base_dir, *sub_dirs)

    try:
        os.makedirs(directory_path, exist_ok=True)
        return {
            "status": "success",
            "message": f"Directory created at {directory_path}",
        }
    except OSError as e:
        return {"status": "error", "message": f"Failed to create directory: {e}"}


def load_processed_data(json_file_path: str):
    with open(json_file_path, "r") as json_file:
        return json.load(json_file)


def load_project_name(project_dir: str) -> str:
    project_name_path = os.path.join(project_dir, "project_name.txt")
    if os.path.exists(project_name_path):
        with open(project_name_path, "r") as f:
            return f.read().strip()  # Remove any surrounding whitespace
    return None


def all_project_dir_path() -> str:
    return current_app.config[Config.PROJECTS_DIR_VAR_NAME]


def list_sub_directories(base_dir: str) -> list:
    list_sub_dir = []

    for project_id in os.listdir(base_dir):
        project_dir = os.path.join(base_dir, project_id)
        if os.path.isdir(project_dir):
            list_sub_dir.append(project_id)
            # TODO project_name = load_project_name(project_dir)
            # TODO tasks.append({"project_id": project_id, "project_name": project_name})
    return list_sub_dir
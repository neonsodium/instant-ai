import json
import os
import re
from datetime import datetime

from flask import current_app

from app.filename_utils import (
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


def load_project_info(project_dir: str, file_name: str) -> str:
    """Load the project name or description from a file inside the project directory."""
    project_info_file = os.path.join(project_dir, file_name)
    if os.path.isfile(project_info_file):
        with open(project_info_file, "r") as f:
            return f.read().strip()
    return "Unknown"


def save_project_info(project_dir: str, file_name: str, info: str):
    """Save the project name or description to a file inside the project directory."""
    project_info_file = os.path.join(project_dir, file_name)
    with open(project_info_file, "w") as f:
        f.write(info)
    return f"Information saved to {project_info_file}"


def directory_project_path_full(project_id: str, path: list) -> str:
    sub_dirs = [directory_cluster_format(cluster_num) for cluster_num in path]
    a = os_path_join_secure(all_project_dir_path(), project_id)
    return os_path_join_secure(a, *sub_dirs)


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
        return {"status": "success", "message": f"Directory created", "path": directory_path}
    except OSError as e:
        return {"status": "error", "message": f"Failed to create directory: {e}"}


def all_project_dir_path() -> str:
    return current_app.config[Config.PROJECTS_DIR_VAR_NAME]


def list_sub_directories(base_dir: str) -> list:
    list_sub_dir = []

    for project_id in os.listdir(base_dir):
        project_dir = os.path.join(base_dir, project_id)
        if os.path.isdir(project_dir):
            list_sub_dir.append(project_id)
    return list_sub_dir


def list_projects(base_dir: str) -> list:
    """List all projects with their IDs, names*, and creation dates."""
    projects = []

    for project_id in list_sub_directories(base_dir):
        project_dir = os.path.join(base_dir, project_id)
        project_name = load_project_info(project_dir, filename_project_name_txt())
        project_desc = load_project_info(project_dir, filename_project_description_txt())

        creation_time = os.stat(project_dir).st_ctime
        creation_date = datetime.fromtimestamp(creation_time).strftime("%Y-%m-%d")
        # creation_date = datetime.fromtimestamp(creation_time).strftime("%Y-%m-%d %H:%M:%S")
        if os.path.isdir(project_dir) and any(os.listdir(project_dir)):
            projects.append(
                {
                    "project_id": project_id,
                    "name": project_name,
                    "creation_date": creation_date,
                    "description": project_desc,
                }
            )

    return projects


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

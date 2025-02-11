import pandas as pd

from app.models.project_model import ProjectModel
from app.utils.filename_utils import create_project_uuid
from app.utils.os_utils import all_project_dir_path, create_directory

project_model = ProjectModel()
from redis import Redis

from config import Config

redis_client = Redis(host=Config.REDIS_HOST, port=Config.REDIS_PORT)


def get_project_columns(project_id, raw_data_file):
    """
    Retrieve the list of columns for the given project. If not already stored, load from the dataset.

    Args:
        project_id (str): The ID of the project.
        raw_data_file (str): Path to the raw data file.

    Returns:
        list: A list of column names.
    """
    project = project_model.collection.find_one({"_id": project_id})
    if not project:
        raise ValueError("Invalid Project ID")

    columns = project.get("columns", [])
    if not columns:
        df = pd.read_csv(raw_data_file)
        columns = list(df.columns)
        project_model.collection.update_one({"_id": project_id}, {"$set": {"columns": columns}})

    return columns


def get_project_info(project_id):
    """
    Fetches all projects from the project model.

    Returns:
        list: A list of all project objects.
    """
    return project_model.collection.find_one({"_id": project_id})


def get_all_running_tasking():
    return redis_client.hgetall("running_tasks")


def get_all_projects():
    """
    Fetches all projects from the project model.

    Returns:
        list: A list of all project objects.
    """
    return project_model.get_all_projects()


def create_project_and_directory(project_name, project_description):
    """
    Create a new project UUID, associated directory structure, and store the project in the database.

    Args:
        project_name (str): The name of the project.
        project_description (str): The description of the project.

    Returns:
        tuple: A tuple containing the HTTP status code and the response JSON.
    """
    try:

        new_project_id = create_project_uuid()

        directory_result = create_directory(all_project_dir_path(), new_project_id)
        if directory_result["status"] != "success":
            return 500, {"error": directory_result["message"]}

        project = project_model.create_project(new_project_id, project_name, project_description)

        return 201, {"project": project, **directory_result}

    except ValueError as e:

        return 400, {"error": str(e)}

    except Exception as e:

        return 500, {"error": f"Failed to create project: {str(e)}"}

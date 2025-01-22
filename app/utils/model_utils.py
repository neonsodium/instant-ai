import pandas as pd

from app.models.project_model import ProjectModel
from app.utils.filename_utils import create_project_uuid
from app.utils.os_utils import create_directory, all_project_dir_path

project_model = ProjectModel()


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
        # Generate unique project ID
        new_project_id = create_project_uuid()

        # Create directory structure for the project
        directory_result = create_directory(all_project_dir_path(), new_project_id)
        if directory_result["status"] != "success":
            return 500, {"error": directory_result["message"]}

        # Store project details in the database
        project = project_model.create_project(new_project_id, project_name, project_description)

        # Return success response
        return 201, {"project": project, **directory_result}

    except ValueError as e:
        # Handle validation errors
        return 400, {"error": str(e)}

    except Exception as e:
        # Handle unexpected errors
        return 500, {"error": f"Failed to create project: {str(e)}"}

from datetime import datetime, timezone

from pymongo.errors import DuplicateKeyError

from app.utils.mongo_utils import mongo_client


class ProjectModel:
    collection_name = "projects"

    def __init__(self):
        self.collection = mongo_client.get_collection(self.collection_name)

    def create_project(self, project_id: str, name: str, description: str) -> dict:
        """
        Create a new project in the MongoDB collection.

        Args:
            project_id (str): Unique identifier for the project.
            name (str): Name of the project.
            description (str): Description of the project.

        Returns:
            dict: The created project document.
        """
        project = {
            "_id": project_id,
            "name": name,
            "description": description,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "clusters": [],
        }
        try:
            self.collection.insert_one(project)
            return project
        except DuplicateKeyError:
            raise ValueError(f"Project with ID {project_id} already exists.")

    def get_all_projects(self) -> list:
        """
        Retrieve all projects from the MongoDB collection.

        Returns:
            list: A list of all project documents.
        """
        projects = self.collection.find(
            {}, {"_id": 1, "name": 1, "description": 1, "created_at": 1, "updated_at": 1}
        )

        return [
            {
                "id": str(proj["_id"]),  # Convert ObjectId to string
                "name": proj["name"],
                "description": proj["description"],
                "created_at": (
                    datetime.fromisoformat(proj["created_at"]).isoformat()
                    if isinstance(proj["created_at"], str)
                    else proj["created_at"].isoformat() if proj["created_at"] else None
                ),
                "updated_at": (
                    datetime.fromisoformat(proj["updated_at"]).isoformat()
                    if isinstance(proj["updated_at"], str)
                    else proj["updated_at"].isoformat() if proj["updated_at"] else None
                ),
            }
            for proj in projects
        ]

    def get_project_by_id(self, project_id: str) -> dict:
        """
        Retrieve a project by its ID.

        Args:
            project_id (str): Unique identifier for the project.

        Returns:
            dict: The project document or None if not found.
        """
        project = self.collection.find_one({"_id": project_id})
        if project:
            project["_id"] = str(project["_id"])
        return project

    def update_project(self, project_id: str, updates: dict) -> bool:
        """
        Update a project's details.

        Args:
            project_id (str): Unique identifier for the project.
            updates (dict): The fields to update.

        Returns:
            bool: True if the update was successful, False otherwise.
        """
        updates["updated_at"] = datetime.now().isoformat()
        result = self.collection.update_one({"_id": project_id}, {"$set": updates})
        return result.modified_count > 0

    def delete_project(self, project_id: str) -> bool:
        """
        Delete a project by its ID.

        Args:
            project_id (str): Unique identifier for the project.

        Returns:
            bool: True if the deletion was successful, False otherwise.
        """
        result = self.collection.delete_one({"_id": project_id})
        return result.deleted_count > 0

    def add_task_metadata(self, project_id, task_id, task_info):
        """
        Adds task metadata to the project document in MongoDB.

        Args:
            project_id (str): The ID of the project.
            task_id (str): The task ID.
            task_info (dict): The metadata related to the task.
        """
        task_metadata = {
            "task_id": task_id,
            "status": task_info["status"],
            "start_time": task_info["start_time"],
            "params": task_info["params"],
            "kpi": task_info.get("kpi"),
            "level": task_info["params"].get("level"),
            "path": task_info["params"].get("path"),
        }

        self.collection.update_one(
            {"_id": project_id},
            {
                "$push": {"tasks": task_metadata}
            },  # Assuming the "tasks" field exists as an array in the project document
        )

import json
from datetime import datetime
from functools import wraps

import redis
from flask import current_app, jsonify, request

from app.tasks import generate_task_key

# Assuming redis_client is already initialized somewhere globally
redis_client = redis.StrictRedis(host="localhost", port=6379, db=0)
from app.models.project_model import ProjectModel

project_model = ProjectModel()


redis_client = redis.StrictRedis(host="localhost", port=6379, db=0)


def task_manager_decorator(task_name):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            project_id = kwargs.get("project_id")
            request_data_json = request.get_json()
            task_params = {"project_id": project_id, "task_name": task_name}

            # Merge additional task-specific params if required
            task_params.update(request_data_json)

            task_key = generate_task_key(**task_params)

            # Check for existing task
            existing_task_id = redis_client.get(task_key)
            if existing_task_id:
                return (
                    jsonify(
                        {
                            "message": "Task is already running",
                            "task_id": existing_task_id.decode(),
                            "project_id": project_id,
                        }
                    ),
                    200,
                )

            # Call the original function
            response = func(*args, **kwargs, task_key=task_key, task_params=task_params)

            # Handle response from the original function
            # Handle response as a tuple
            if isinstance(response, tuple):
                response_body, status_code = response
            else:
                response_body, status_code = response, 200

            if status_code == 202:
                task_id = json.loads(response_body.response[0].decode("utf-8")).get("task_id")
                task_info = {
                    "task_id": task_id,
                    "status": "pending",
                    "project_id": project_id,
                    "start_time": datetime.now().isoformat(),
                    "params": task_params,
                }
                redis_client.hset(f"running_{task_name}_tasks", task_id, json.dumps(task_info))
                redis_client.setex(
                    task_key, current_app.config.get("REDIS_TIMEOUT_TASK_ID"), f"task:{task_id}"
                )
                project_model.add_task_metadata(project_id, task_id, task_info)

            return response

        return wrapper

    return decorator

get_task_status_by_id_swagger = {
    "responses": {
        "200": {
            "description": "Returns the status of a task by its ID",
            "schema": {
                "type": "object",
                "properties": {
                    "status": {
                        "type": "string",
                        "description": 'The current status of the task (e.g., "PENDING", "SUCCESS", "FAILURE")',
                    }
                },
            },
        }
    }
}

list_running_tasks_swagger = {
    "responses": {
        "200": {
            "description": "Returns a list of all currently running tasks",
            "schema": {
                "type": "object",
                "properties": {
                    "running_tasks": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "task_id": {
                                    "type": "string",
                                    "description": "ID of the running task",
                                },
                                "status": {"type": "string", "description": "Status of the task"},
                                "start_time": {
                                    "type": "string",
                                    "description": "Start time of the task",
                                },
                            },
                        },
                    }
                },
            },
        }
    }
}

upload_project_file_swagger = {
    "responses": {
        "202": {
            "description": "File upload has started and task is processing",
            "schema": {
                "type": "object",
                "properties": {
                    "message": {"type": "string", "description": "Status message"},
                    "task_id": {
                        "type": "string",
                        "description": "Task ID of the background process",
                    },
                },
            },
        },
        "400": {
            "description": "Invalid request due to missing file or invalid Project ID",
            "schema": {
                "type": "object",
                "properties": {"error": {"type": "string", "description": "Error message"}},
            },
        },
    }
}

drop_columns_from_dataset_swagger = {
    "summary": "Drop columns from the dataset",
    "description": "This endpoint allows users to drop specified columns from the dataset of a given project.",
    "parameters": [
        {
            "name": "project_id",
            "in": "path",
            "required": True,
            "description": "ID of the project.",
            "schema": {"type": "string", "example": "123e4567-e89b-12d3-a456-426614174000"},
        }
    ],
    "requestBody": {
        "required": True,
        "content": {
            "application/json": {
                "schema": {
                    "type": "object",
                    "properties": {
                        "column": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "List of column names to drop from the dataset.",
                            "example": ["col1", "col2"],
                        }
                    },
                    "required": ["column"],
                }
            }
        },
    },
    "responses": {
        "202": {
            "description": "Column dropping task has started",
            "content": {
                "application/json": {
                    "schema": {
                        "type": "object",
                        "properties": {
                            "message": {
                                "type": "string",
                                "description": "Status message",
                                "example": "Column drop task has been initiated.",
                            },
                            "task_id": {
                                "type": "string",
                                "description": "Task ID of the background process.",
                                "example": "abc12345-def6-7890-ghij-klmn123456op",
                            },
                        },
                    }
                }
            },
        },
        "400": {
            "description": "Invalid request due to missing columns or invalid Project ID",
            "content": {
                "application/json": {
                    "schema": {
                        "type": "object",
                        "properties": {
                            "error": {
                                "type": "string",
                                "description": "Error message",
                                "example": "Invalid Project ID or column list is missing.",
                            }
                        },
                    }
                }
            },
        },
    },
}


start_feature_ranking_swagger = {
    "responses": {
        "202": {
            "description": "Feature ranking task has started",
            "schema": {
                "type": "object",
                "properties": {
                    "message": {"type": "string", "description": "Status message"},
                    "task_id": {
                        "type": "string",
                        "description": "Task ID of the background process",
                    },
                    "Project_id": {"type": "string", "description": "Project ID"},
                },
            },
        },
        "400": {
            "description": "Invalid request due to missing KPI or invalid Project ID",
            "schema": {
                "type": "object",
                "properties": {"error": {"type": "string", "description": "Error message"}},
            },
        },
    }
}

initiate_subclustering_swagger = {
    "responses": {
        "202": {
            "description": "Clustering task has started",
            "schema": {
                "type": "object",
                "properties": {
                    "message": {"type": "string", "description": "Status message"},
                    "task_id": {
                        "type": "string",
                        "description": "Task ID of the background process",
                    },
                    "project_id": {"type": "string", "description": "Project ID"},
                },
            },
        },
        "400": {
            "description": "Invalid request due to missing dataset, level/path mismatch, or invalid Project ID",
            "schema": {
                "type": "object",
                "properties": {"error": {"type": "string", "description": "Error message"}},
            },
        },
    }
}

initiate_time_series_swagger = {
    "responses": {
        "202": {
            "description": "Time series analysis task has started",
            "schema": {
                "type": "object",
                "properties": {
                    "message": {"type": "string", "description": "Status message"},
                    "task_id": {
                        "type": "string",
                        "description": "Task ID of the background process",
                    },
                    "project_id": {"type": "string", "description": "Project ID"},
                },
            },
        },
        "400": {
            "description": "Invalid request due to missing dataset, level/path mismatch, or invalid Project ID",
            "schema": {
                "type": "object",
                "properties": {"error": {"type": "string", "description": "Error message"}},
            },
        },
    }
}

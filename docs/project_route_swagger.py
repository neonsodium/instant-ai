get_projects_swagger = {
    "summary": "Get all projects",
    "description": "This endpoint retrieves the list of all available projects.",
    "responses": {
        "200": {
            "description": "A list of projects.",
            "schema": {
                "type": "object",
                "properties": {"projects": {"type": "array", "items": {"type": "string"}}},
            },
        },
        "404": {
            "description": "Project directory not configured",
            "schema": {"type": "object", "properties": {"error": {"type": "string"}}},
        },
    },
}

create_project_swagger = {
    "summary": "Create a new project",
    "description": "This endpoint allows users to create a new project by providing a name and description.",
    "parameters": [
        {
            "name": "name",
            "in": "body",
            "type": "string",
            "description": "Name of the new project",
            "required": True,
        },
        {
            "name": "description",
            "in": "body",
            "type": "string",
            "description": "Description of the new project",
            "required": True,
        },
    ],
    "responses": {
        "200": {
            "description": "Project created successfully",
            "schema": {
                "type": "object",
                "properties": {"project_id": {"type": "string"}, "path": {"type": "string"}},
            },
        },
        "400": {
            "description": "Bad Request, missing or invalid parameters",
            "schema": {"type": "object", "properties": {"error": {"type": "string"}}},
        },
    },
}

get_cluster_info_swagger = {
    "parameters": [
        {
            "name": "project_id",
            "in": "path",
            "type": "string",
            "description": "Project ID",
            "required": True,
        },
        {
            "name": "level",
            "in": "body",
            "type": "integer",
            "description": "Cluster level",
            "required": True,
        },
        {
            "name": "path",
            "in": "body",
            "type": "array",
            "items": {"type": "string"},
            "description": "Cluster path",
            "required": True,
        },
    ],
    "responses": {
        "200": {
            "description": "Clusters retrieved successfully",
            "schema": {
                "type": "object",
                "properties": {
                    "Cluster Path": {"type": "string"},
                    "project_id": {"type": "string"},
                    "clusters": {"type": "array", "items": {"type": "string"}},
                },
            },
        },
        "400": {
            "description": "Bad Request",
            "schema": {"type": "object", "properties": {"error": {"type": "string"}}},
        },
        "404": {
            "description": "Cluster does not exist",
            "schema": {
                "type": "object",
                "properties": {"error": {"type": "string"}, "project_id": {"type": "string"}},
            },
        },
    },
}

download_cluster_data_swagger = {
    "parameters": [
        {
            "name": "project_id",
            "in": "path",
            "type": "string",
            "description": "Project ID",
            "required": True,
        },
        {
            "name": "level",
            "in": "body",
            "type": "integer",
            "description": "Cluster level",
            "required": True,
        },
        {
            "name": "path",
            "in": "body",
            "type": "array",
            "items": {"type": "string"},
            "description": "Cluster path",
            "required": True,
        },
    ],
    "responses": {
        "200": {
            "description": "File downloaded successfully",
            "schema": {"type": "string", "format": "binary"},
        },
        "400": {
            "description": "Bad Request",
            "schema": {"type": "object", "properties": {"error": {"type": "string"}}},
        },
        "404": {
            "description": "Cluster or file does not exist",
            "schema": {
                "type": "object",
                "properties": {"error": {"type": "string"}, "project_id": {"type": "string"}},
            },
        },
    },
}

# swagger_schemas.py
validate_dataset_swagger = {
    "parameters": [
        {
            "name": "project_id",
            "in": "path",
            "type": "string",
            "description": "Project ID",
            "required": True,
        }
    ],
    "responses": {
        "200": {
            "description": "Dataset validation result",
            "schema": {"type": "object", "properties": {"message": {"type": "string"}}},
        },
        "400": {
            "description": "Invalid Project ID or Dataset not uploaded",
            "schema": {"type": "object", "properties": {"error": {"type": "string"}}},
        },
    },
}

list_dataset_columns_swagger = {
    "parameters": [
        {
            "name": "project_id",
            "in": "path",
            "type": "string",
            "description": "Project ID",
            "required": True,
        }
    ],
    "responses": {
        "200": {
            "description": "List of dataset columns",
            "schema": {
                "type": "object",
                "properties": {"columns": {"type": "array", "items": {"type": "string"}}},
            },
        },
        "400": {
            "description": "Invalid Project ID or Dataset not uploaded",
            "schema": {"type": "object", "properties": {"error": {"type": "string"}}},
        },
    },
}

# swagger_schemas.py
summarize_cluster_swagger = {
    "parameters": [
        {
            "name": "project_id",
            "in": "path",
            "type": "string",
            "description": "Project ID",
            "required": True,
        },
        {
            "name": "level",
            "in": "body",
            "description": "Level of the clustering",
            "required": True,
            "schema": {"type": "integer"},
        },
        {
            "name": "path",
            "in": "body",
            "description": "Path list for clustering",
            "required": True,
            "schema": {"type": "array", "items": {"type": "string"}},
        },
    ],
    "responses": {
        "200": {
            "description": "Cluster summary result",
            "schema": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "Feature": {"type": "string"},
                        "Type": {"type": "string"},
                        "Statistic": {"type": "string"},
                        "Value": {"type": "string"},
                        "Count": {"type": "integer"},
                        "Mean": {"type": "number"},
                        "Sum": {"type": "number"},
                    },
                },
            },
        },
        "400": {
            "description": "Invalid request (level and path mismatch)",
            "schema": {"type": "object", "properties": {"error": {"type": "string"}}},
        },
        "404": {
            "description": "Cluster does not exist or project is invalid",
            "schema": {"type": "object", "properties": {"error": {"type": "string"}}},
        },
    },
}

# swagger_schemas.py
download_project_file_swagger = {
    "parameters": [
        {
            "name": "path",
            "in": "query",
            "type": "string",
            "description": "Relative path to the file to be downloaded",
            "required": True,
        }
    ],
    "responses": {
        "200": {
            "description": "File download successful",
            "schema": {"type": "string", "format": "binary"},
        },
        "400": {
            "description": "Missing path query parameter",
            "schema": {"type": "object", "properties": {"error": {"type": "string"}}},
        },
        "404": {
            "description": "File not found",
            "schema": {"type": "object", "properties": {"error": {"type": "string"}}},
        },
    },
}

get_project_status_swagger = {
    "parameters": [
        {
            "name": "project_id",
            "in": "path",
            "type": "string",
            "description": "Project ID",
            "required": True,
        }
    ],
    "responses": {
        "200": {
            "description": "Project status retrieved successfully",
            "schema": {
                "type": "object",
                "properties": {
                    "data_uploaded": {"type": "boolean"},
                    "feature_ranking_completed": {"type": "boolean"},
                    "clustering_started": {"type": "boolean"},
                    "clusters": {
                        "type": "object",
                        "properties": {
                            "name": {"type": "string"},
                            "subdirectories": {"type": "array", "items": {"type": "string"}},
                        },
                    },
                    "important_features": {"type": "array", "items": {"type": "string"}},
                    "drop_columns_list": {"type": "array", "items": {"type": "string"}},
                    "kpi": {"type": "string"},
                    "kpi_list": {"type": "array", "items": {"type": "string"}},
                },
            },
        },
        "400": {
            "description": "Invalid Project ID",
            "schema": {"type": "object", "properties": {"error": {"type": "string"}}},
        },
        "404": {
            "description": "KPI list file not found",
            "schema": {"type": "object", "properties": {"error": {"type": "string"}}},
        },
    },
}

get_cluster_status_swagger = {
    "parameters": [
        {
            "name": "project_id",
            "in": "path",
            "type": "string",
            "description": "Project ID",
            "required": True,
        },
        {
            "name": "path",
            "in": "body",
            "description": "List of paths to the clusters",
            "required": True,
            "schema": {"type": "array", "items": {"type": "string"}},
        },
        {
            "name": "level",
            "in": "body",
            "description": "Level of the cluster",
            "required": True,
            "schema": {"type": "integer"},
        },
        {
            "name": "kpi",
            "in": "body",
            "description": "Key Performance Indicator for the clustering",
            "required": True,
            "schema": {"type": "string"},
        },
    ],
    "responses": {
        "200": {
            "description": "Cluster status retrieved successfully",
            "schema": {
                "type": "object",
                "properties": {"status": {"type": "boolean"}, "project_id": {"type": "string"}},
            },
        },
        "400": {
            "description": "Invalid Project ID or Missing Parameters",
            "schema": {"type": "object", "properties": {"error": {"type": "string"}}},
        },
        "404": {
            "description": "Feature ranking file or cluster directory not found",
            "schema": {
                "type": "object",
                "properties": {"error": {"type": "string"}, "project_id": {"type": "string"}},
            },
        },
    },
}

# swagger_schemas.py
list_all_files_in_projects_swagger = {
    "responses": {
        "200": {
            "description": "Successfully retrieved list of files",
            "schema": {
                "type": "object",
                "properties": {
                    "files": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "List of relative file paths",
                    }
                },
            },
        }
    }
}

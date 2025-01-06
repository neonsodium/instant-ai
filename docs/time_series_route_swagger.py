# swagger_swagger.py

time_series_figure_swagger = {
    "tags": ["Time Series"],
    "description": "Retrieve a time series plotly figure for the specified project.",
    "parameters": [
        {
            "name": "project_id",
            "in": "path",
            "description": "Project ID",
            "required": True,
            "type": "string",
        },
        {
            "name": "request_data_json",
            "in": "body",
            "description": "Request body with necessary data",
            "required": True,
            "schema": {
                "type": "object",
                "properties": {
                    "project_id": {"type": "string"},
                    "level": {"type": "integer"},
                    "path": {"type": "array", "items": {"type": "string"}},
                    "kpi": {"type": "string"},
                },
            },
        },
    ],
    "responses": {
        "200": {
            "description": "Time series figure successfully retrieved.",
            "schema": {"type": "object", "properties": {"plotly_figure": {"type": "string"}}},
        },
        "400": {"description": "Invalid Project ID or other error"},
        "404": {"description": "Cluster or data set not found"},
    },
}

encoded_columns_swagger = {
    "tags": ["Time Series"],
    "description": "Retrieve OneHotEncoded column names for a specific categorical column.",
    "parameters": [
        {
            "name": "project_id",
            "in": "path",
            "description": "Project ID",
            "required": True,
            "type": "string",
        },
        {
            "name": "request_data_json",
            "in": "body",
            "description": "Request body with necessary data",
            "required": True,
            "schema": {
                "type": "object",
                "properties": {
                    "level": {"type": "integer"},
                    "path": {"type": "array", "items": {"type": "string"}},
                    "column_name": {"type": "string"},
                },
            },
        },
    ],
    "responses": {
        "200": {
            "description": "Encoded columns successfully retrieved.",
            "schema": {
                "type": "object",
                "properties": {
                    "categorical_column": {"type": "array", "items": {"type": "string"}}
                },
            },
        },
        "404": {"description": "Invalid Project ID or path"},
        "400": {"description": "Level and path mismatch or invalid categorical column"},
    },
}

categorical_columns_swagger = {
    "tags": ["Time Series"],
    "description": "List all categorical columns for a specified project.",
    "parameters": [
        {
            "name": "project_id",
            "in": "path",
            "description": "Project ID",
            "required": True,
            "type": "string",
        },
        {
            "name": "request_data_json",
            "in": "body",
            "description": "Request body with necessary data",
            "required": True,
            "schema": {
                "type": "object",
                "properties": {
                    "level": {"type": "integer"},
                    "path": {"type": "array", "items": {"type": "string"}},
                },
            },
        },
    ],
    "responses": {
        "200": {
            "description": "List of categorical columns successfully retrieved.",
            "schema": {
                "type": "object",
                "properties": {
                    "categorical_columns": {"type": "array", "items": {"type": "string"}}
                },
            },
        },
        "404": {"description": "Invalid Project ID or path"},
        "400": {"description": "Level and path mismatch"},
    },
}

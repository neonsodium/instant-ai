# swagger_docs.py

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

# Repeat the above for other routes...1~

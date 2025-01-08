import os

from flasgger import Swagger
from flask import Flask
from flask_compress import Compress
from flask_cors import CORS

from app.celery_utils import make_celery
from config import Config, DevelopmentConfig, ProductionConfig, TestingConfig

app = Flask(__name__)
CORS(app)
Compress(app)

app.config["SWAGGER"] = {"title": "My API", "uiversion": 3}

if Config.ENV == "development":
    app.config.from_object(DevelopmentConfig)
elif Config.ENV == "production":
    app.config.from_object(ProductionConfig)
elif Config.ENV == "testing":
    app.config.from_object(TestingConfig)

# projects folder exists
try:
    app.config[Config.PROJECTS_DIR_VAR_NAME] = Config.PROJECTS_DIR
    os.makedirs(os.path.join(os.getcwd(), app.config[Config.PROJECTS_DIR_VAR_NAME]), exist_ok=True)
except OSError:
    print(OSError)


# Configure JSON sorting for Demo API only ig? IDK, Ask the frontend guy lol <- sexist
app.config["JSON_SORT_KEYS"] = False
app.json.sort_keys = False
celery = make_celery(app)


from app.routes.processor_routes import processor_routes
from app.routes.project_routes import main_routes
from app.routes.time_series_routes import time_series_routes

template = {
    "swagger": "3.0",
    "info": {"title": "Instant-AI", "description": "Docs", "version": "0.6.5"},
}
app.config["SWAGGER"] = {
    "title": "Instant-Ai",
    "uiversion": 3,
    "template": "./resources/flasgger/swagger_ui.html",
}
Swagger(app, template=template)

app.register_blueprint(time_series_routes, url_prefix="/projects")
app.register_blueprint(main_routes, url_prefix="/projects")
app.register_blueprint(processor_routes, url_prefix="/projects")

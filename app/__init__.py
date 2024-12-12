import os

from flask import Flask
from flask_cors import CORS

from app.celery_utils import make_celery
from config import Config, DevelopmentConfig, ProductionConfig, TestingConfig

app = Flask(__name__)
CORS(app)


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


# Configure JSON sorting for Demo API only ig? IDK, Ask the frontend guy lol
app.config["JSON_SORT_KEYS"] = False
app.json.sort_keys = False
celery = make_celery(app)


from app.routes.processor_routes import processor_routes
from app.routes.project_routes import project_routes

app.register_blueprint(project_routes, url_prefix="/projects")
app.register_blueprint(processor_routes, url_prefix="/process")

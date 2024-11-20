import os

from flask import Flask
from flask_cors import CORS

from app.celery_utils import make_celery
from config import Config, DevelopmentConfig, ProductionConfig, TestingConfig

app = Flask(__name__)
CORS(app)


if Config.ENV == "development":
    from app.routes.demo_api_routes import demo_api_routes
    from app.routes.old_routes import old_routes
    from app.routes.user_routes import user_routes

    app.register_blueprint(user_routes, url_prefix="/user")
    app.register_blueprint(old_routes, url_prefix="/old")
    app.register_blueprint(demo_api_routes, url_prefix="/api/demo")
    app.config.from_object(DevelopmentConfig)
elif Config.ENV == "production":
    from app.routes.demo_api_routes import demo_api_routes
    from app.routes.old_routes import old_routes

    # from app.routes.user_routes import test_route
    # app.register_blueprint(test_route, url_prefix="/test")
    app.register_blueprint(old_routes, url_prefix="/old")
    app.register_blueprint(demo_api_routes, url_prefix="/api/demo")
    app.config.from_object(ProductionConfig)
elif Config.ENV == "testing":
    app.config.from_object(TestingConfig)

# projects folder exists
try:
    app.config[Config.PROJECTS_DIR_VAR_NAME] = Config.PROJECTS_DIR
    os.makedirs(
        os.path.join(os.getcwd(), app.config[Config.PROJECTS_DIR_VAR_NAME]),
        exist_ok=True,
    )
except OSError:
    print(OSError)


# Configure JSON sorting
app.config["JSON_SORT_KEYS"] = False
app.json.sort_keys = False

# first import config and then call make_celery
celery = make_celery(app)
# TODO move it
from app import app_routes

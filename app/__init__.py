import os
from flask import Flask
from flask_cors import CORS
from .celery_utils import make_celery
# TODO spilt the routes 
from config import Config, DevelopmentConfig, ProductionConfig, TestingConfig

# Initialize the app and set up CORS
app = Flask(__name__)
CORS(app)


# Load the configuration based on the environment
if Config.ENV == 'development':
    app.config.from_object(DevelopmentConfig)
elif Config.ENV == 'production':
    # TODO remove old routes
    # TODO add main route
    # TODO Refactor this file
    from .routes.old_routes import old_routes
    from .routes.user_routes import user_routes
    from .routes.demo_api_routes import demo_api_routes
    app.register_blueprint(user_routes, url_prefix='/user')
    app.register_blueprint(old_routes, url_prefix='/old')
    app.register_blueprint(demo_api_routes, url_prefix='/demo-api')
    app.config.from_object(ProductionConfig)
elif Config.ENV == 'testing':
    app.config.from_object(TestingConfig)

#projects folder exists
app.config[Config.PROJECTS_DIR_VAR_NAME] = Config.PROJECTS_DIR
try:
    # os.path.join(os.getcwd(), app.config[Config.PROJECTS_DIR_VAR_NAME])
    os.makedirs(os.path.join(os.getcwd(), app.config[Config.PROJECTS_DIR_VAR_NAME]),exist_ok=True)
except OSError:
    print(OSError)
    
# TODO spilt the routes 

# Configure JSON sorting
app.config['JSON_SORT_KEYS'] = False
app.json.sort_keys = False

# first import config and then call make_celery
celery = make_celery(app)
from app import app_routes
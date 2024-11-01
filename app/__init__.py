import os
from flask import Flask
from config import Config, DevelopmentConfig, ProductionConfig, TestingConfig
from flask_cors import CORS

# Initialize the app and set up CORS
app = Flask(__name__)
CORS(app)

# Ensure projects folder exists
app.config[Config.PROJECTS_DIR_VAR] = Config.PROJECTS_DIR
try:
    os.makedirs(app.config[Config.PROJECTS_DIR_VAR],exist_ok=True)
except OSError:
    print(OSError)

# Configure JSON sorting
app.config['JSON_SORT_KEYS'] = False
app.json.sort_keys = False

# Load the configuration based on the environment
if Config.ENV == 'development':
    app.config.from_object(DevelopmentConfig)
elif Config.ENV == 'production':
    from app import old_routes
    app.config.from_object(ProductionConfig)
elif Config.ENV == 'testing':
    app.config.from_object(TestingConfig)

# Import routes
from app import routes
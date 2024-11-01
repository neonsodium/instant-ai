from flask import Flask
from config import Config, DevelopmentConfig, ProductionConfig, TestingConfig
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Load the configuration from Config class
if Config.ENV == 'development':
    app.config.from_object(DevelopmentConfig)
elif Config.ENV == 'production':
    app.config.from_object(ProductionConfig)
elif Config.ENV == 'testing':
    app.config.from_object(TestingConfig)

from app import routes

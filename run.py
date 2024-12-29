from os import getenv

from app import app
from app.logger_config import configure_logging

LOG_LEVEL = getenv("LOG_LEVEL", "INFO")
LOG_FILE = getenv("LOG_FILE", "flask_app.log")
configure_logging(LOG_LEVEL, LOG_FILE)


if __name__ == "__main__":
    app.logger.info("Starting Flask application.")
    app.run(host=app.config.get("HOST"), port=app.config.get("PORT"), debug=app.config.get("DEBUG"))

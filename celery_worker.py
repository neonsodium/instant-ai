import logging
from os import getenv

from app import celery
from app.logger_config import configure_logging

# LOG_LEVEL = getenv("LOG_LEVEL", "INFO")
# LOG_FILE = getenv("LOG_FILE", "celery_app.log")
# configure_logging(LOG_LEVEL, LOG_FILE)

if __name__ == "__main__":
    logging.info("Starting Celery worker...")
    celery.start()

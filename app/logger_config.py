import logging
import os
from logging.handlers import RotatingFileHandler


def configure_logging(log_level: str = "INFO", log_file: str = None):
    """
    Configures logging for the application and Celery.
    """
    log_level = log_level.upper()
    formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")

    # Create the root logger
    logger = logging.getLogger()
    logger.setLevel(log_level)

    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # Optional: Add a file handler if log_file is provided
    if log_file:
        file_handler = RotatingFileHandler(
            log_file, maxBytes=10 * 1024 * 1024, backupCount=5  # 10MB per file, keep 5 backups
        )
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    logging.getLogger("werkzeug").setLevel(logging.ERROR)
    logging.getLogger("celery").setLevel(log_level)

    logging.info("Logging is configured.")

import os
import platform


class Config:
    SECRET_KEY = (
        os.environ.get("SECRET_KEY")
        or "you-will-never-guess:6d667eac81ee0897e67cecbaf10a801ee789f06a2e9849e46cd28728"
    )
    DEBUG = False
    HOST = "127.0.0.1"
    PROJECTS_DIR = "projects"
    PROJECTS_DIR_VAR_NAME = "PROJECTS_DIR"

    CELERY_BROKER_URL = "redis://localhost:6379/0"
    CELERY_RESULT_BACKEND = "redis://localhost:6379/0"
    REDIS_TIMEOUT_TASK_ID = 60 * 30000

    if platform.system() == "Darwin" or platform.system() == "Windows":  # MacOS coz i work on
        ENV = "development"
    elif platform.system() == "Linux":
        ENV = "production"
    else:
        ENV = "testing"

    ENV = "production"


class DevelopmentConfig(Config):
    DEBUG = True
    PORT = 8080
    LOGIN_REQUIRED = True
    PASSWORD = "p"
    USERNAME = "p"


class ProductionConfig(Config):
    DEBUG = False
    LOGIN_REQUIRED = True
    PORT = 8009  # 8009 to 80 on the internet on prod
    USERNAME = "girish_pvl"
    PASSWORD = "HelloML"


class TestingConfig(Config):
    DEBUG = True
    LOGIN_REQUIRED = False
    PORT = 8080
    USERNAME = "p"
    PASSWORD = "p"

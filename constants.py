import os

from dotenv import load_dotenv

load_dotenv()

DJANGO_SECRET_KEY = os.environ.get("DJANGO_SECRET_KEY")
JWT_SECRET = os.environ.get("JWT_SECRET")
DEBUG = os.environ.get("DEBUG") == "True"
ALLOWED_HOST = os.environ.get("ALLOWED_HOST", "127.0.0.1")
BASE_URL = os.environ.get("BASE_URL", "")  # default to empty string
STATIC_ROOT = os.environ.get("STATIC_ROOT")
VUE_ROOT = os.environ.get("VUE_ROOT")


class DBConfigError(ValueError):
    pass


# Get database configuration from the environment
# Precondition: Environment variables must be loaded.
def get_database_configuration(BASE_DIR: str) -> dict:
    # valid engines below - note MariaDB maps to mysql as per Django docs
    valid_engines = ["sqlite3", "postgresql", "mysql", "oracle"]

    # Get engine, defaulting to sqlite3
    engine = os.environ.get("SLUGGO_DB_ENGINE")
    if engine is None:
        engine = "sqlite3"  # default to sqlite
    elif engine not in valid_engines:
        raise DBConfigError("Invalid engine selected!")

    # Create dictionary for database configuration with engine (which must
    # exist)
    db_dict = {"ENGINE": f"django.db.backends.{engine}"}

    # Configure NAME, defaulting for sqlite3 if not provided.
    DB_NAME = os.environ.get("SLUGGO_DB_NAME")
    if DB_NAME is None and engine == "sqlite3":
        DB_NAME = os.path.join(BASE_DIR, "db.sqlite3")

    # Get potential fields
    DB_USER = os.environ.get("SLUGGO_DB_USER")
    DB_PASS = os.environ.get("SLUGGO_DB_PASS")
    DB_HOST = os.environ.get("SLUGGO_DB_HOST")
    DB_PORT = os.environ.get("SLUGGO_DB_PORT")

    # Add any of these values to their appropriate key if they exist
    if DB_NAME is not None:
        db_dict["NAME"] = DB_NAME
    if DB_USER is not None:
        db_dict["USER"] = DB_USER
    if DB_PASS is not None:
        db_dict["PASS"] = DB_PASS
    if DB_HOST is not None:
        db_dict["HOST"] = DB_HOST
    if DB_PORT is not None:
        db_dict["PORT"] = DB_PORT

    return {"default": db_dict}

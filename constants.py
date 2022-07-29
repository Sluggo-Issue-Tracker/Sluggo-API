import os

from dotenv import load_dotenv

load_dotenv()

DJANGO_SECRET_KEY = os.environ.get("DJANGO_SECRET_KEY")
JWT_SECRET = os.environ.get("JWT_SECRET")
DEBUG = os.environ.get("DEBUG") == "True"
ALLOWED_HOST = os.environ.get("ALLOWED_HOST")
BASE_URL = os.environ.get("BASE_URL", "")  # default to empty string
STATIC_ROOT = os.environ.get("STATIC_ROOT")

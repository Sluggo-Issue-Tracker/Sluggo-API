import os

from dotenv import load_dotenv

load_dotenv()

DJANGO_SECRET_KEY = os.environ.get("DJANGO_SECRET_KEY")
JWT_SECRET = os.environ.get("JWT_SECRET")

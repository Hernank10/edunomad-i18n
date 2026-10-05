from .base import *
import os

DEBUG = False
SECRET_KEY = os.environ.get("DJANGO_SECRET_KEY")
ALLOWED_HOSTS = ["localhost", "127.0.0.1"]


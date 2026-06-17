# config.py
# Centralized place for reading configuration/secrets from environment variables.
# Every other file that needs DB credentials imports them from here, instead of
# reading the .env file itself.

import os
from dotenv import load_dotenv

# Reads the .env file and loads its key=value pairs into the environment
load_dotenv()

DB_HOST = os.getenv("DB_HOST")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_NAME = os.getenv("DB_NAME")
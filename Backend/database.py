# database.py
# Centralized database connection logic. Every route that needs the database
# calls get_connection() instead of writing its own mysql.connector.connect() call.

import mysql.connector
from config import DB_HOST, DB_USER, DB_PASSWORD, DB_NAME

def get_connection():
    """Opens and returns a fresh connection to the MySQL database."""
    return mysql.connector.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME
    )
"""
db_connection.py
----------------
MySQL connection factory for the Flight Booking System.
Reads credentials from the .env file (never from source code).
"""

import os
import mysql.connector
from mysql.connector import Error
from dotenv import load_dotenv

# Load environment variables from .env in the project root
load_dotenv()


def get_connection():
    """
    Create and return a new MySQL connection using .env credentials.

    Returns:
        mysql.connector.connection.MySQLConnection

    Raises:
        RuntimeError: if connection cannot be established.
    """
    try:
        conn = mysql.connector.connect(
            host=os.getenv("DB_HOST", "localhost"),
            port=int(os.getenv("DB_PORT", 3306)),
            user=os.getenv("DB_USER", "root"),
            password=os.getenv("DB_PASSWORD", ""),
            database=os.getenv("DB_NAME", "flight_booking_db"),
            autocommit=False,
            connection_timeout=10,
        )
        return conn
    except Error as e:
        raise RuntimeError(
            f"Database connection failed: {e}\n"
            "Check that MySQL is running and your .env credentials are correct."
        ) from e


def test_connection():
    """
    Test the database connection.

    Returns:
        (bool, str): (success, message)
    """
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT DATABASE()")
        db_name = cursor.fetchone()[0]
        cursor.close()
        conn.close()
        return True, f"Connected to database: {db_name}"
    except (RuntimeError, Error) as e:
        return False, str(e)


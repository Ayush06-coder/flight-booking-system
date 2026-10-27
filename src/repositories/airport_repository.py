"""
airport_repository.py
---------------------
Data access layer for the 'airports' table.
"""

from src.db_connection import get_connection


def get_all_airports():
    """Return all airports ordered by city."""
    conn = get_connection()
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM airports ORDER BY city")
        return cursor.fetchall()
    finally:
        cursor.close()
        conn.close()


def get_airport_by_id(airport_id: int):
    """Return a single airport record or None."""
    conn = get_connection()
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM airports WHERE airport_id = %s", (airport_id,))
        return cursor.fetchone()
    finally:
        cursor.close()
        conn.close()


def get_airport_by_code(code: str):
    """Return airport matching IATA code or None."""
    conn = get_connection()
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute(
            "SELECT * FROM airports WHERE airport_code = %s",
            (code.strip().upper(),),
        )
        return cursor.fetchone()
    finally:
        cursor.close()
        conn.close()


def add_airport(code: str, name: str, city: str, country: str = "India") -> int:
    """Insert a new airport. Returns the new airport_id."""
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO airports (airport_code, airport_name, city, country) "
            "VALUES (%s, %s, %s, %s)",
            (code.strip().upper(), name.strip(), city.strip(), country.strip()),
        )
        conn.commit()
        return cursor.lastrowid
    except Exception:
        conn.rollback()
        raise
    finally:
        cursor.close()
        conn.close()


def update_airport(airport_id: int, code: str, name: str, city: str, country: str):
    """Update an existing airport record."""
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE airports SET airport_code=%s, airport_name=%s, city=%s, country=%s "
            "WHERE airport_id=%s",
            (code.strip().upper(), name.strip(), city.strip(), country.strip(), airport_id),
        )
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        cursor.close()
        conn.close()


def delete_airport(airport_id: int):
    """Delete an airport (FK RESTRICT prevents deletion if flights reference it)."""
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM airports WHERE airport_id = %s", (airport_id,))
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        cursor.close()
        conn.close()


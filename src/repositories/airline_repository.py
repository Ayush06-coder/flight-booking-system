"""
airline_repository.py
---------------------
Data access layer for the 'airlines' table.
"""

from src.db_connection import get_connection


def get_all_airlines():
    """Return all airlines ordered by name."""
    conn = get_connection()
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM airlines ORDER BY airline_name")
        return cursor.fetchall()
    finally:
        cursor.close()
        conn.close()


def get_airline_by_id(airline_id: int):
    """Return a single airline record or None."""
    conn = get_connection()
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM airlines WHERE airline_id = %s", (airline_id,))
        return cursor.fetchone()
    finally:
        cursor.close()
        conn.close()


def add_airline(name: str, code: str, email: str, phone: str) -> int:
    """Insert a new airline. Returns the new airline_id."""
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO airlines (airline_name, airline_code, contact_email, contact_phone) "
            "VALUES (%s, %s, %s, %s)",
            (name.strip(), code.strip().upper(), email.strip(), phone.strip()),
        )
        conn.commit()
        return cursor.lastrowid
    except Exception:
        conn.rollback()
        raise
    finally:
        cursor.close()
        conn.close()


def update_airline(airline_id: int, name: str, code: str, email: str, phone: str):
    """Update an existing airline record."""
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE airlines SET airline_name=%s, airline_code=%s, "
            "contact_email=%s, contact_phone=%s WHERE airline_id=%s",
            (name.strip(), code.strip().upper(), email.strip(), phone.strip(), airline_id),
        )
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        cursor.close()
        conn.close()


def delete_airline(airline_id: int):
    """
    Delete an airline. Raises an error if aircraft or flights reference it
    (enforced by FK RESTRICT).
    """
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM airlines WHERE airline_id = %s", (airline_id,))
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        cursor.close()
        conn.close()


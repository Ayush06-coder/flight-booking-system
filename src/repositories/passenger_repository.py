"""
passenger_repository.py
-----------------------
Data access layer for the 'passengers' table.
"""

from src.db_connection import get_connection


def get_all_passengers():
    """Return all passengers ordered by full_name."""
    conn = get_connection()
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM passengers ORDER BY full_name")
        return cursor.fetchall()
    finally:
        cursor.close()
        conn.close()


def get_passenger_by_id(passenger_id: int):
    """Return a single passenger record or None."""
    conn = get_connection()
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM passengers WHERE passenger_id=%s", (passenger_id,))
        return cursor.fetchone()
    finally:
        cursor.close()
        conn.close()


def search_passengers(term: str):
    """
    Search passengers by name, email, or phone (case-insensitive partial match).
    """
    conn = get_connection()
    try:
        cursor = conn.cursor(dictionary=True)
        like = f"%{term.strip()}%"
        cursor.execute(
            "SELECT * FROM passengers "
            "WHERE full_name LIKE %s OR email LIKE %s OR phone LIKE %s "
            "ORDER BY full_name",
            (like, like, like),
        )
        return cursor.fetchall()
    finally:
        cursor.close()
        conn.close()


def add_passenger(full_name: str, email: str, phone: str, dob: str = None) -> int:
    """
    Insert a new passenger. Returns the new passenger_id.
    dob should be 'YYYY-MM-DD' or None.
    """
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO passengers (full_name, email, phone, date_of_birth) "
            "VALUES (%s, %s, %s, %s)",
            (full_name.strip(), email.strip(), phone.strip(), dob or None),
        )
        conn.commit()
        return cursor.lastrowid
    except Exception:
        conn.rollback()
        raise
    finally:
        cursor.close()
        conn.close()


def update_passenger(passenger_id: int, full_name: str, email: str,
                     phone: str, dob: str = None):
    """Update an existing passenger record."""
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE passengers SET full_name=%s, email=%s, phone=%s, date_of_birth=%s "
            "WHERE passenger_id=%s",
            (full_name.strip(), email.strip(), phone.strip(), dob or None, passenger_id),
        )
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        cursor.close()
        conn.close()


def delete_passenger(passenger_id: int):
    """
    Delete a passenger. Raises IntegrityError (FK RESTRICT) if bookings
    or tickets reference this passenger.
    """
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM passengers WHERE passenger_id=%s", (passenger_id,))
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        cursor.close()
        conn.close()


def get_passenger_booking_history(passenger_id: int):
    """Return all bookings and ticket details for a passenger."""
    conn = get_connection()
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute(
            """
            SELECT
                b.booking_reference,
                b.booking_datetime,
                b.booking_status,
                b.total_amount,
                fs.flight_number,
                al.airline_name,
                orig.city       AS origin,
                dest.city       AS destination,
                fs.departure_datetime,
                t.seat_number,
                t.travel_class,
                t.ticket_fare,
                t.ticket_status,
                py.payment_status,
                py.transaction_reference
            FROM bookings b
            JOIN tickets          t    ON t.booking_id              = b.booking_id
            JOIN flight_schedules fs   ON t.flight_id               = fs.flight_id
            JOIN airlines         al   ON fs.airline_id             = al.airline_id
            JOIN airports         orig ON fs.origin_airport_id      = orig.airport_id
            JOIN airports         dest ON fs.destination_airport_id = dest.airport_id
            LEFT JOIN payments    py   ON py.booking_id             = b.booking_id
            WHERE b.passenger_id = %s
            ORDER BY b.booking_datetime DESC
            """,
            (passenger_id,),
        )
        return cursor.fetchall()
    finally:
        cursor.close()
        conn.close()


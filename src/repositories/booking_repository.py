"""
booking_repository.py
---------------------
Data access layer for bookings, tickets, and booking_status_history.
All booking creation and cancellation use explicit transactions.
"""

import mysql.connector
from src.db_connection import get_connection
from src.validators import generate_booking_reference


# ============================================================
# Read operations
# ============================================================

def get_all_bookings():
    """Return all bookings with passenger and basic flight info."""
    conn = get_connection()
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute(
            """
            SELECT
                b.booking_id,
                b.booking_reference,
                p.full_name         AS passenger_name,
                p.email,
                b.booking_datetime,
                b.total_amount,
                b.booking_status,
                COUNT(t.ticket_id)  AS ticket_count
            FROM bookings b
            JOIN passengers p ON b.passenger_id = p.passenger_id
            LEFT JOIN tickets t ON t.booking_id = b.booking_id
            GROUP BY b.booking_id, b.booking_reference, p.full_name, p.email,
                     b.booking_datetime, b.total_amount, b.booking_status
            ORDER BY b.booking_datetime DESC
            """
        )
        return cursor.fetchall()
    finally:
        cursor.close()
        conn.close()


def get_booking_by_reference(ref: str):
    """Return full booking detail by booking reference."""
    conn = get_connection()
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute(
            """
            SELECT
                b.*,
                p.full_name, p.email, p.phone
            FROM bookings b
            JOIN passengers p ON b.passenger_id = p.passenger_id
            WHERE b.booking_reference = %s
            """,
            (ref.strip().upper(),),
        )
        return cursor.fetchone()
    finally:
        cursor.close()
        conn.close()


def get_tickets_for_booking(booking_id: int):
    """Return all tickets linked to a booking with flight details."""
    conn = get_connection()
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute(
            """
            SELECT
                t.*,
                fs.flight_number,
                al.airline_name,
                orig.city       AS origin_city,
                dest.city       AS destination_city,
                fs.departure_datetime,
                fs.arrival_datetime
            FROM tickets t
            JOIN flight_schedules fs   ON t.flight_id               = fs.flight_id
            JOIN airlines         al   ON fs.airline_id             = al.airline_id
            JOIN airports         orig ON fs.origin_airport_id      = orig.airport_id
            JOIN airports         dest ON fs.destination_airport_id = dest.airport_id
            WHERE t.booking_id = %s
            ORDER BY t.ticket_id
            """,
            (booking_id,),
        )
        return cursor.fetchall()
    finally:
        cursor.close()
        conn.close()


def get_booking_status_history(booking_id: int):
    """Return status history for a booking."""
    conn = get_connection()
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute(
            "SELECT * FROM booking_status_history WHERE booking_id=%s ORDER BY changed_at",
            (booking_id,),
        )
        return cursor.fetchall()
    finally:
        cursor.close()
        conn.close()


# ============================================================
# Create booking (transactional)
# ============================================================

def create_booking(passenger_id: int, flight_id: int, seat_number: str,
                   travel_class: str, ticket_fare: float) -> dict:
    """
    Create a booking with one ticket in a single database transaction.

    Steps:
      1. Generate a unique booking reference (retrying if duplicate).
      2. Verify flight is not Cancelled.
      3. Check seat is not already taken (DB constraint will also catch this).
      4. Check class capacity.
      5. INSERT booking.
      6. INSERT ticket.
      7. COMMIT.

    Returns a dict with booking_id, booking_reference, ticket_id.
    Raises RuntimeError on any failure; transaction is rolled back.
    """
    conn = get_connection()
    try:
        conn.start_transaction()
        cursor = conn.cursor(dictionary=True)

        # Step 1: Generate unique booking reference
        ref = _generate_unique_ref(cursor)

        # Step 2: Check flight status
        cursor.execute(
            "SELECT flight_status FROM flight_schedules WHERE flight_id=%s FOR UPDATE",
            (flight_id,),
        )
        row = cursor.fetchone()
        if not row:
            raise RuntimeError("Flight not found.")
        if row["flight_status"] == "Cancelled":
            raise RuntimeError("Cannot book a cancelled flight.")

        # Step 3: Check seat availability (class capacity)
        class_col = "economy_seats" if travel_class == "Economy" else "business_seats"
        cursor.execute(
            f"SELECT ac.{class_col} AS cap FROM aircraft ac "
            "JOIN flight_schedules fs ON fs.aircraft_id=ac.aircraft_id "
            "WHERE fs.flight_id=%s",
            (flight_id,),
        )
        cap_row = cursor.fetchone()
        capacity = cap_row["cap"] if cap_row else 0

        cursor.execute(
            "SELECT COUNT(*) AS booked FROM tickets "
            "WHERE flight_id=%s AND travel_class=%s AND ticket_status='Active'",
            (flight_id, travel_class),
        )
        booked = cursor.fetchone()["booked"]

        if booked >= capacity:
            raise RuntimeError(f"No {travel_class} seats available on this flight.")

        # Step 4: INSERT booking
        cursor.execute(
            "INSERT INTO bookings (booking_reference, passenger_id, total_amount, booking_status) "
            "VALUES (%s, %s, %s, 'Confirmed')",
            (ref, passenger_id, ticket_fare),
        )
        booking_id = cursor.lastrowid

        # Step 5: INSERT ticket (UNIQUE constraint on flight_id+seat_number catches duplicates)
        cursor.execute(
            "INSERT INTO tickets (booking_id, passenger_id, flight_id, seat_number, "
            "travel_class, ticket_fare, ticket_status) "
            "VALUES (%s, %s, %s, %s, %s, %s, 'Active')",
            (booking_id, passenger_id, flight_id,
             seat_number.strip().upper(), travel_class, ticket_fare),
        )
        ticket_id = cursor.lastrowid

        conn.commit()
        return {"booking_id": booking_id, "booking_reference": ref, "ticket_id": ticket_id}

    except mysql.connector.IntegrityError as e:
        conn.rollback()
        if "uq_flight_seat" in str(e) or "Duplicate entry" in str(e):
            raise RuntimeError(
                f"Seat {seat_number} is already booked on this flight. "
                "Please choose a different seat."
            ) from e
        raise RuntimeError(f"Database integrity error: {e}") from e
    except Exception:
        conn.rollback()
        raise
    finally:
        cursor.close()
        conn.close()


# ============================================================
# Cancel booking
# ============================================================

def cancel_booking(booking_id: int, remarks: str = "Cancelled by passenger") -> bool:
    """
    Cancel a booking:
      1. Set booking_status → 'Cancelled'.
      2. Set all associated tickets → 'Cancelled'.
      3. Mark associated payment as 'Refunded' (simulated).
    Booking_status_history is updated via trigger.
    """
    conn = get_connection()
    try:
        conn.start_transaction()
        cursor = conn.cursor()

        # Verify booking exists and is cancellable
        cursor.execute(
            "SELECT booking_status FROM bookings WHERE booking_id=%s FOR UPDATE",
            (booking_id,),
        )
        row = cursor.fetchone()
        if not row:
            raise RuntimeError("Booking not found.")
        if row[0] == "Cancelled":
            raise RuntimeError("Booking is already cancelled.")
        if row[0] == "Completed":
            raise RuntimeError("Completed bookings cannot be cancelled.")

        # Cancel tickets
        cursor.execute(
            "UPDATE tickets SET ticket_status='Cancelled' WHERE booking_id=%s",
            (booking_id,),
        )

        # Update booking status (trigger will log history)
        cursor.execute(
            "UPDATE bookings SET booking_status='Cancelled' WHERE booking_id=%s",
            (booking_id,),
        )

        # Mark payment as Refunded (simulated)
        cursor.execute(
            "UPDATE payments SET payment_status='Refunded' "
            "WHERE booking_id=%s AND payment_status='Completed'",
            (booking_id,),
        )

        conn.commit()
        return True
    except Exception:
        conn.rollback()
        raise
    finally:
        cursor.close()
        conn.close()


# ============================================================
# Reports
# ============================================================

def get_bookings_by_date_range(start_date: str, end_date: str):
    """Return bookings within a date range."""
    conn = get_connection()
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute(
            """
            SELECT
                b.booking_reference,
                p.full_name,
                b.booking_datetime,
                b.total_amount,
                b.booking_status,
                py.payment_status
            FROM bookings b
            JOIN passengers p ON b.passenger_id = p.passenger_id
            LEFT JOIN payments py ON py.booking_id = b.booking_id
            WHERE DATE(b.booking_datetime) BETWEEN %s AND %s
            ORDER BY b.booking_datetime DESC
            """,
            (start_date, end_date),
        )
        return cursor.fetchall()
    finally:
        cursor.close()
        conn.close()


def get_booking_status_summary():
    """Return count of bookings per status."""
    conn = get_connection()
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute(
            "SELECT booking_status, COUNT(*) AS total FROM bookings GROUP BY booking_status"
        )
        return cursor.fetchall()
    finally:
        cursor.close()
        conn.close()


# ============================================================
# Internal helpers
# ============================================================

def _generate_unique_ref(cursor) -> str:
    """Generate a booking reference not already in the database."""
    for _ in range(10):
        ref = generate_booking_reference()
        cursor.execute(
            "SELECT 1 FROM bookings WHERE booking_reference=%s", (ref,)
        )
        if not cursor.fetchone():
            return ref
    raise RuntimeError("Could not generate a unique booking reference. Please try again.")


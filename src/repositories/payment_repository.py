"""
payment_repository.py
---------------------
Data access layer for the 'payments' table.
All payments in this system are simulated academic demonstrations.
"""

import uuid
from src.db_connection import get_connection


VALID_METHODS = ("Credit Card", "Debit Card", "UPI", "Net Banking", "Wallet")


def get_all_payments():
    """Return all payment records with booking references."""
    conn = get_connection()
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute(
            """
            SELECT
                py.*,
                b.booking_reference,
                p.full_name AS passenger_name
            FROM payments py
            JOIN bookings   b ON py.booking_id  = b.booking_id
            JOIN passengers p ON b.passenger_id = p.passenger_id
            ORDER BY py.payment_datetime DESC
            """
        )
        return cursor.fetchall()
    finally:
        cursor.close()
        conn.close()


def get_payments_for_booking(booking_id: int):
    """Return all payment records for a specific booking."""
    conn = get_connection()
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute(
            "SELECT * FROM payments WHERE booking_id=%s ORDER BY payment_datetime",
            (booking_id,),
        )
        return cursor.fetchall()
    finally:
        cursor.close()
        conn.close()


def record_payment(booking_id: int, amount: float, method: str) -> dict:
    """
    Record a SIMULATED payment for a booking.
    NOTE: No real financial transaction is performed.

    Returns a dict with payment_id and transaction_reference.
    """
    if method not in VALID_METHODS:
        raise ValueError(f"Invalid payment method. Choose from: {', '.join(VALID_METHODS)}")
    if amount < 0:
        raise ValueError("Payment amount cannot be negative.")

    # Generate a clearly labelled simulated transaction reference
    txn_ref = f"TXN-SIM-{uuid.uuid4().hex[:12].upper()}"

    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO payments (booking_id, amount, payment_method, payment_status, "
            "transaction_reference) VALUES (%s, %s, %s, 'Completed', %s)",
            (booking_id, amount, method, txn_ref),
        )
        payment_id = cursor.lastrowid
        conn.commit()
        return {"payment_id": payment_id, "transaction_reference": txn_ref}
    except Exception:
        conn.rollback()
        raise
    finally:
        cursor.close()
        conn.close()


def get_revenue_by_airline():
    """Return revenue aggregated by airline."""
    conn = get_connection()
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute(
            """
            SELECT
                al.airline_name,
                COUNT(DISTINCT b.booking_id) AS total_bookings,
                SUM(py.amount)               AS total_revenue,
                AVG(py.amount)               AS avg_revenue
            FROM payments py
            JOIN bookings           b  ON py.booking_id  = b.booking_id
            JOIN tickets            t  ON t.booking_id   = b.booking_id
            JOIN flight_schedules   fs ON t.flight_id    = fs.flight_id
            JOIN airlines           al ON fs.airline_id  = al.airline_id
            WHERE py.payment_status = 'Completed'
            GROUP BY al.airline_name
            ORDER BY total_revenue DESC
            """
        )
        return cursor.fetchall()
    finally:
        cursor.close()
        conn.close()


def get_revenue_by_route():
    """Return revenue aggregated by route (origin city → destination city)."""
    conn = get_connection()
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute(
            """
            SELECT
                orig.city   AS origin,
                dest.city   AS destination,
                COUNT(DISTINCT b.booking_id) AS bookings,
                SUM(py.amount)               AS route_revenue
            FROM payments py
            JOIN bookings           b  ON py.booking_id              = b.booking_id
            JOIN tickets            t  ON t.booking_id               = b.booking_id
            JOIN flight_schedules   fs ON t.flight_id                = fs.flight_id
            JOIN airports           orig ON fs.origin_airport_id     = orig.airport_id
            JOIN airports           dest ON fs.destination_airport_id= dest.airport_id
            WHERE py.payment_status = 'Completed'
            GROUP BY orig.city, dest.city
            ORDER BY route_revenue DESC
            """
        )
        return cursor.fetchall()
    finally:
        cursor.close()
        conn.close()


def get_payment_status_summary():
    """Return count and total per payment status."""
    conn = get_connection()
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute(
            "SELECT payment_status, COUNT(*) AS count, COALESCE(SUM(amount),0) AS total "
            "FROM payments GROUP BY payment_status"
        )
        return cursor.fetchall()
    finally:
        cursor.close()
        conn.close()


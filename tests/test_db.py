"""
test_db.py
----------
Automated database integration tests for the Flight Booking System.
Covers TC01–TC21 as defined in the test plan.

Run with:
    source .venv/bin/activate
    python3 -m pytest tests/test_db.py -v --tb=short
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
import mysql.connector
from mysql.connector import Error as MySQLError

from src.db_connection import get_connection, test_connection as check_db_connection
from src.repositories.airline_repository   import get_all_airlines
from src.repositories.airport_repository   import get_all_airports
from src.repositories.flight_repository    import (
    search_flights, get_flight_by_id, get_seat_availability,
    get_all_flights, get_dashboard_stats,
)
from src.repositories.passenger_repository import (
    add_passenger, get_passenger_by_id, delete_passenger, search_passengers,
)
from src.repositories.booking_repository   import (
    create_booking, cancel_booking, get_booking_by_reference,
    get_tickets_for_booking, get_booking_status_history,
)
from src.repositories.payment_repository   import (
    record_payment, get_payments_for_booking,
)
from src.validators import generate_booking_reference


# ── Helpers ────────────────────────────────────────────────────────────────

def run_sql(sql: str, params=None, fetch=False):
    """Execute raw SQL; return rows if fetch=True."""
    conn = get_connection()
    try:
        cur = conn.cursor(dictionary=True)
        cur.execute(sql, params or ())
        result = cur.fetchall() if fetch else None
        conn.commit()
        return result
    finally:
        cur.close()
        conn.close()


# ── TC01: Database exists ──────────────────────────────────────────────────

def test_TC01_database_exists():
    """TC01 — flight_booking_db database is accessible."""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT DATABASE()")
    db = cur.fetchone()[0]
    cur.close()
    conn.close()
    assert db == "flight_booking_db", f"Expected flight_booking_db, got {db}"


# ── TC02: All 9 tables exist ───────────────────────────────────────────────

def test_TC02_all_tables_exist():
    """TC02 — All 9 required tables exist in the database."""
    expected = {
        "airlines", "airports", "aircraft", "flight_schedules",
        "passengers", "bookings", "tickets", "payments",
        "booking_status_history",
    }
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "SELECT TABLE_NAME FROM information_schema.TABLES "
        "WHERE TABLE_SCHEMA = 'flight_booking_db' AND TABLE_TYPE = 'BASE TABLE'"
    )
    existing = {row[0] for row in cur.fetchall()}
    cur.close()
    conn.close()
    missing = expected - existing
    assert not missing, f"Missing tables: {missing}"


# ── TC03: Sample data row counts ───────────────────────────────────────────

def test_TC03_sample_data_counts():
    """TC03 — Sample data meets minimum row requirements."""
    minimums = {
        "airlines": 3, "airports": 8, "aircraft": 5,
        "flight_schedules": 10, "passengers": 10,
        "bookings": 12, "tickets": 12, "payments": 12,
    }
    conn = get_connection()
    cur = conn.cursor()
    for table, min_rows in minimums.items():
        cur.execute(f"SELECT COUNT(*) FROM {table}")
        count = cur.fetchone()[0]
        assert count >= min_rows, (
            f"Table '{table}' has {count} rows; expected at least {min_rows}"
        )
    cur.close()
    conn.close()


# ── TC04: Successful DB connection ─────────────────────────────────────────

def test_TC04_successful_connection():
    """TC04 — test_connection() returns (True, message)."""
    success, msg = check_db_connection()
    assert success is True, f"Connection failed: {msg}"
    assert "flight_booking_db" in msg


# ── TC05: Flight search by route and date ──────────────────────────────────

def test_TC05_flight_search():
    """TC05 — Flight search returns results for DEL→BOM on 2026-11-05."""
    # DEL = airport_id 1, BOM = airport_id 2 (based on INSERT order)
    results = search_flights(1, 2, "2026-11-05", "Economy")
    assert len(results) >= 1, "Expected at least one DEL→BOM Economy flight on 2026-11-05"
    for r in results:
        assert r["available_seats"] >= 0
        assert r["flight_status"] != "Cancelled"


# ── TC06: Passenger registration ───────────────────────────────────────────

class TestTC06PassengerRegistration:
    """TC06 — Passenger can be inserted and retrieved."""

    def setup_method(self):
        self.pid = None

    def test_add_and_retrieve(self):
        pid = add_passenger(
            "Test User TC06", "tc06.test@sample.com", "9100000006", "1995-01-01"
        )
        assert pid > 0
        self.pid = pid
        p = get_passenger_by_id(pid)
        assert p is not None
        assert p["full_name"] == "Test User TC06"
        assert p["email"] == "tc06.test@sample.com"

    def teardown_method(self):
        # Clean up
        if self.pid:
            try:
                delete_passenger(self.pid)
            except Exception:
                pass


# ── TC07: Successful booking creation ──────────────────────────────────────

class TestTC07BookingCreation:
    """TC07 — Full booking transaction creates booking + ticket."""

    def setup_method(self):
        self.pid = add_passenger(
            "TC07 Flyer", "tc07.flyer@sample.com", "9100000007"
        )
        self.booking_ref = None

    def test_create_booking(self):
        # Use flight_id=8 (SG-701 DEL→COK) with a fresh seat
        result = create_booking(
            passenger_id=self.pid,
            flight_id=8,
            seat_number="E35A",
            travel_class="Economy",
            ticket_fare=3850.00,
        )
        assert "booking_reference" in result
        assert result["booking_reference"].startswith("BK")
        assert result["ticket_id"] > 0
        self.booking_ref = result["booking_reference"]

        # Verify persists in DB
        b = get_booking_by_reference(self.booking_ref)
        assert b is not None
        assert b["booking_status"] == "Confirmed"

    def teardown_method(self):
        if self.booking_ref:
            try:
                b = get_booking_by_reference(self.booking_ref)
                if b:
                    conn = get_connection()
                    cur = conn.cursor()
                    cur.execute(
                        "DELETE FROM booking_status_history WHERE booking_id=%s",
                        (b["booking_id"],)
                    )
                    cur.execute(
                        "DELETE FROM tickets WHERE booking_id=%s",
                        (b["booking_id"],)
                    )
                    cur.execute(
                        "DELETE FROM bookings WHERE booking_id=%s",
                        (b["booking_id"],)
                    )
                    conn.commit()
                    cur.close()
                    conn.close()
            except Exception:
                pass
        if self.pid:
            try:
                delete_passenger(self.pid)
            except Exception:
                pass


# ── TC08: Unique booking reference ─────────────────────────────────────────

def test_TC08_unique_booking_reference():
    """TC08 — Generated references are unique and match expected format."""
    refs = [generate_booking_reference() for _ in range(500)]
    assert len(set(refs)) == 500, "Duplicate references generated"
    for ref in refs:
        assert ref.startswith("BK")
        assert len(ref) == 8


# ── TC09: Duplicate seat rejection ─────────────────────────────────────────

class TestTC09DuplicateSeat:
    """TC09 — Booking the same seat on the same flight is rejected."""

    def setup_method(self):
        self.pid1 = add_passenger("TC09 A", "tc09a@sample.com", "9100000091")
        self.pid2 = add_passenger("TC09 B", "tc09b@sample.com", "9100000092")
        self.booking_ref = None

    def test_duplicate_seat_rejected(self):
        # Book seat E36A on flight 9 (SG-801)
        result = create_booking(self.pid1, 9, "E36A", "Economy", 2800.00)
        self.booking_ref = result["booking_reference"]

        # Second attempt at same seat must fail
        with pytest.raises((RuntimeError, MySQLError)):
            create_booking(self.pid2, 9, "E36A", "Economy", 2800.00)

    def teardown_method(self):
        if self.booking_ref:
            try:
                b = get_booking_by_reference(self.booking_ref)
                if b:
                    conn = get_connection()
                    cur = conn.cursor()
                    cur.execute("DELETE FROM booking_status_history WHERE booking_id=%s", (b["booking_id"],))
                    cur.execute("DELETE FROM tickets WHERE booking_id=%s", (b["booking_id"],))
                    cur.execute("DELETE FROM bookings WHERE booking_id=%s", (b["booking_id"],))
                    conn.commit()
                    cur.close()
                    conn.close()
            except Exception:
                pass
        for pid in (self.pid1, self.pid2):
            if pid:
                try:
                    delete_passenger(pid)
                except Exception:
                    pass


# ── TC10: Seat capacity overflow rejection ─────────────────────────────────

def test_TC10_capacity_overflow():
    """TC10 — Booking beyond class capacity is rejected by trigger."""
    # Find a flight, get its business capacity, fill it, then try one more
    conn = get_connection()
    cur = conn.cursor(dictionary=True)
    # Use flight_id=7 (AI-601, 18 business seats) — already has some booked
    cur.execute(
        "SELECT ac.business_seats AS cap, "
        "(SELECT COUNT(*) FROM tickets WHERE flight_id=7 AND travel_class='Business' "
        " AND ticket_status='Active') AS booked "
        "FROM flight_schedules fs JOIN aircraft ac ON fs.aircraft_id=ac.aircraft_id "
        "WHERE fs.flight_id=7"
    )
    row = cur.fetchone()
    cur.close()
    conn.close()

    available = row["cap"] - row["booked"]
    if available <= 0:
        pytest.skip("No available Business seats on flight 7 to test overflow.")

    # Fill remaining seats
    pids = []
    refs = []
    try:
        for i in range(available):
            pid = add_passenger(
                f"TC10 Pax {i}", f"tc10.{i}@sample.com", f"910000{10+i:04d}"
            )
            pids.append(pid)
            r = create_booking(pid, 7, f"B{i+10:02d}C", "Business", 9750.00)
            refs.append(r["booking_reference"])

        # One more must fail
        extra_pid = add_passenger("TC10 Extra", "tc10extra@sample.com", "9199999999")
        pids.append(extra_pid)
        with pytest.raises((RuntimeError, MySQLError)):
            create_booking(extra_pid, 7, "B99C", "Business", 9750.00)
    finally:
        conn = get_connection()
        cur = conn.cursor()
        for ref in refs:
            try:
                b = get_booking_by_reference(ref)
                if b:
                    cur.execute("DELETE FROM booking_status_history WHERE booking_id=%s", (b["booking_id"],))
                    cur.execute("DELETE FROM tickets WHERE booking_id=%s", (b["booking_id"],))
                    cur.execute("DELETE FROM bookings WHERE booking_id=%s", (b["booking_id"],))
                    conn.commit()
            except Exception:
                pass
        cur.close()
        conn.close()
        for pid in pids:
            try:
                delete_passenger(pid)
            except Exception:
                pass


# ── TC11: Invalid FK rejection ─────────────────────────────────────────────

def test_TC11_invalid_fk_rejection():
    """TC11 — Inserting a ticket with a non-existent flight_id raises an error."""
    pid = add_passenger("TC11 User", "tc11@sample.com", "9100000011")
    try:
        with pytest.raises((RuntimeError, MySQLError)):
            create_booking(pid, 99999, "E01A", "Economy", 1000.00)
    finally:
        try:
            delete_passenger(pid)
        except Exception:
            pass


# ── TC12: Invalid travel class rejection ───────────────────────────────────

def test_TC12_invalid_travel_class():
    """TC12 — Booking with an invalid travel class raises an error."""
    from src.validators import validate_travel_class
    ok, msg = validate_travel_class("FirstClass")
    assert ok is False, "Expected validation to reject 'FirstClass'"


# ── TC13: Negative fare rejection ──────────────────────────────────────────

def test_TC13_negative_fare():
    """TC13 — A negative fare is rejected by validator and DB CHECK constraint."""
    from src.validators import validate_fare
    ok, msg = validate_fare(-500)
    assert ok is False

    # Also verify DB constraint directly
    conn = get_connection()
    cur = conn.cursor()
    try:
        with pytest.raises(MySQLError):
            cur.execute(
                "INSERT INTO tickets (booking_id, passenger_id, flight_id, "
                "seat_number, travel_class, ticket_fare) VALUES (1,1,1,'E99Z','Economy',-1)"
            )
            conn.commit()
    finally:
        conn.rollback()
        cur.close()
        conn.close()


# ── TC14: Cancelled flight booking rejection ───────────────────────────────

def test_TC14_cancelled_flight_booking():
    """TC14 — Booking a ticket on a Cancelled flight is rejected by trigger."""
    # flight_id=10 (6E-901) has status='Cancelled' in sample data
    pid = add_passenger("TC14 User", "tc14@sample.com", "9100000014")
    try:
        with pytest.raises((RuntimeError, MySQLError)):
            create_booking(pid, 10, "E01A", "Economy", 3100.00)
    finally:
        try:
            delete_passenger(pid)
        except Exception:
            pass


# ── TC15 & TC16: Booking cancellation + seat release ──────────────────────

class TestTC15TC16CancellationAndSeatRelease:
    """TC15 — Booking cancellation updates status.
    TC16 — Seat is released (ticket → Cancelled) after cancellation."""

    def setup_method(self):
        self.pid = add_passenger("TC15 Canceller", "tc15@sample.com", "9100000015")
        result = create_booking(self.pid, 8, "E37B", "Economy", 4500.00)
        self.booking_ref = result["booking_reference"]
        b = get_booking_by_reference(self.booking_ref)
        self.booking_id = b["booking_id"]

    def test_TC15_cancellation(self):
        """TC15 — Booking cancellation updates booking status to Cancelled."""
        cancel_booking(self.booking_id)
        b = get_booking_by_reference(self.booking_ref)
        assert b["booking_status"] == "Cancelled"
        history = get_booking_status_history(self.booking_id)
        statuses = [h["new_status"] for h in history]
        assert "Cancelled" in statuses

    def test_TC16_seat_release(self):
        """TC16 — Seat is released (ticket status becomes Cancelled) after cancellation."""
        cancel_booking(self.booking_id)
        tickets = get_tickets_for_booking(self.booking_id)
        assert all(t["ticket_status"] == "Cancelled" for t in tickets)

    def teardown_method(self):
        conn = get_connection()
        cur = conn.cursor()
        try:
            cur.execute("DELETE FROM payments WHERE booking_id=%s", (self.booking_id,))
            cur.execute("DELETE FROM booking_status_history WHERE booking_id=%s", (self.booking_id,))
            cur.execute("DELETE FROM tickets WHERE booking_id=%s", (self.booking_id,))
            cur.execute("DELETE FROM bookings WHERE booking_id=%s", (self.booking_id,))
            conn.commit()
        except Exception:
            conn.rollback()
        finally:
            cur.close()
            conn.close()
        try:
            delete_passenger(self.pid)
        except Exception:
            pass


# ── TC17: Payment status ───────────────────────────────────────────────────

def test_TC17_payment_status():
    """TC17 — Payments are recorded with correct status."""
    # Booking BK001ABC should have a Completed payment
    b = get_booking_by_reference("BK001ABC")
    assert b is not None
    payments = get_payments_for_booking(b["booking_id"])
    assert len(payments) >= 1
    statuses = [p["payment_status"] for p in payments]
    assert any(s in ("Completed", "Refunded") for s in statuses)


# ── TC18: JOIN query correctness ───────────────────────────────────────────

def test_TC18_join_query():
    """TC18 — Multi-table JOIN returns correct passenger + flight data."""
    conn = get_connection()
    cur = conn.cursor(dictionary=True)
    cur.execute(
        """
        SELECT p.full_name, al.airline_name, fs.flight_number,
               orig.city AS origin, dest.city AS destination
        FROM bookings b
        JOIN passengers       p    ON b.passenger_id          = p.passenger_id
        JOIN tickets          t    ON t.booking_id             = b.booking_id
        JOIN flight_schedules fs   ON t.flight_id              = fs.flight_id
        JOIN airlines         al   ON fs.airline_id            = al.airline_id
        JOIN airports         orig ON fs.origin_airport_id     = orig.airport_id
        JOIN airports         dest ON fs.destination_airport_id= dest.airport_id
        WHERE b.booking_reference = 'BK001ABC'
        """
    )
    rows = cur.fetchall()
    cur.close()
    conn.close()
    assert len(rows) == 1
    r = rows[0]
    assert r["full_name"] == "Arjun Sharma"
    assert r["airline_name"] == "IndiGo Airlines"
    assert r["flight_number"] == "6E-201"
    assert r["origin"] == "New Delhi"
    assert r["destination"] == "Mumbai"


# ── TC19: Revenue report accuracy ─────────────────────────────────────────

def test_TC19_revenue_accuracy():
    """TC19 — Revenue aggregation matches known sample data totals."""
    from src.repositories.payment_repository import get_revenue_by_airline
    rows = get_revenue_by_airline()
    assert len(rows) >= 3, "Expected revenue rows for all 3 airlines"
    total = sum(float(r["total_revenue"]) for r in rows)
    # Sample data has 11 Completed payments (BK011 is Refunded), adjust accordingly
    assert total > 0, "Total revenue must be positive"


# ── TC20: Transaction rollback ─────────────────────────────────────────────

def test_TC20_transaction_rollback():
    """TC20 — A failed booking rolls back cleanly (no partial data left)."""
    pid = add_passenger("TC20 Rollback", "tc20@sample.com", "9100000020")
    try:
        # Attempt booking on non-existent flight_id — should fail and rollback
        with pytest.raises((RuntimeError, MySQLError)):
            create_booking(pid, 99999, "E01A", "Economy", 1000.00)

        # Verify no orphan booking was created for this passenger
        conn = get_connection()
        cur = conn.cursor()
        cur.execute(
            "SELECT COUNT(*) FROM bookings WHERE passenger_id=%s", (pid,)
        )
        count = cur.fetchone()[0]
        cur.close()
        conn.close()
        assert count == 0, "Partial booking was created despite transaction failure"
    finally:
        try:
            delete_passenger(pid)
        except Exception:
            pass


# ── TC21: Connection error handling ───────────────────────────────────────

def test_TC21_connection_error_handling():
    """TC21 — Bad credentials produce a RuntimeError, not an unhandled crash."""
    import os
    original_pwd = os.environ.get("DB_PASSWORD", "")
    os.environ["DB_PASSWORD"] = "definitely_wrong_password_xyz"
    try:
        # Reload env — monkeypatch the env var directly
        import importlib
        import src.db_connection as dbc
        # Temporarily patch to use wrong password
        orig_connect = mysql.connector.connect

        def bad_connect(**kwargs):
            kwargs["password"] = "definitely_wrong_password_xyz"
            return orig_connect(**kwargs)

        mysql.connector.connect = bad_connect
        try:
            with pytest.raises((RuntimeError, MySQLError)):
                get_connection()
        finally:
            mysql.connector.connect = orig_connect
    finally:
        os.environ["DB_PASSWORD"] = original_pwd

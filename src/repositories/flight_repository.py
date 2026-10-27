"""
flight_repository.py
--------------------
Data access layer for flight_schedules and aircraft tables.
"""

from src.db_connection import get_connection


# ============================================================
# Aircraft
# ============================================================

def get_all_aircraft():
    """Return all aircraft with their airline name."""
    conn = get_connection()
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute(
            "SELECT ac.*, al.airline_name "
            "FROM aircraft ac JOIN airlines al ON ac.airline_id = al.airline_id "
            "ORDER BY al.airline_name, ac.aircraft_model"
        )
        return cursor.fetchall()
    finally:
        cursor.close()
        conn.close()


def add_aircraft(airline_id, model, reg_number, total, economy, business) -> int:
    """Insert a new aircraft. Returns new aircraft_id."""
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO aircraft "
            "(airline_id, aircraft_model, registration_number, total_seats, economy_seats, business_seats) "
            "VALUES (%s, %s, %s, %s, %s, %s)",
            (airline_id, model, reg_number, total, economy, business),
        )
        conn.commit()
        return cursor.lastrowid
    except Exception:
        conn.rollback()
        raise
    finally:
        cursor.close()
        conn.close()


# ============================================================
# Flight Schedules
# ============================================================

def search_flights(origin_id: int, destination_id: int, travel_date: str, travel_class: str):
    """
    Search for available (non-cancelled) flights on a given date.
    Returns available seat count for the requested class.
    """
    conn = get_connection()
    try:
        cursor = conn.cursor(dictionary=True)
        class_col = "ac.economy_seats" if travel_class == "Economy" else "ac.business_seats"
        booked_class_filter = f"t.travel_class = '{travel_class}'"

        sql = f"""
            SELECT
                fs.flight_id,
                al.airline_name,
                al.airline_code,
                fs.flight_number,
                orig.airport_code        AS origin_code,
                orig.city                AS origin_city,
                dest.airport_code        AS destination_code,
                dest.city                AS destination_city,
                fs.departure_datetime,
                fs.arrival_datetime,
                TIMESTAMPDIFF(MINUTE, fs.departure_datetime, fs.arrival_datetime)
                                         AS duration_minutes,
                fs.base_fare,
                CASE
                    WHEN %s = 'Business' THEN ROUND(fs.base_fare * 2.5, 2)
                    ELSE fs.base_fare
                END                      AS class_fare,
                fs.flight_status,
                {class_col}              AS class_capacity,
                COALESCE(
                    (SELECT COUNT(*) FROM tickets t2
                     WHERE t2.flight_id = fs.flight_id
                       AND t2.travel_class = %s
                       AND t2.ticket_status = 'Active'), 0
                )                        AS booked_seats,
                {class_col} - COALESCE(
                    (SELECT COUNT(*) FROM tickets t3
                     WHERE t3.flight_id = fs.flight_id
                       AND t3.travel_class = %s
                       AND t3.ticket_status = 'Active'), 0
                )                        AS available_seats
            FROM flight_schedules fs
            JOIN airlines  al   ON fs.airline_id            = al.airline_id
            JOIN airports  orig ON fs.origin_airport_id     = orig.airport_id
            JOIN airports  dest ON fs.destination_airport_id= dest.airport_id
            JOIN aircraft  ac   ON fs.aircraft_id           = ac.aircraft_id
            WHERE fs.origin_airport_id      = %s
              AND fs.destination_airport_id = %s
              AND DATE(fs.departure_datetime) = %s
              AND fs.flight_status <> 'Cancelled'
            ORDER BY fs.departure_datetime
        """
        cursor.execute(sql, (travel_class, travel_class, travel_class,
                             origin_id, destination_id, travel_date))
        return cursor.fetchall()
    finally:
        cursor.close()
        conn.close()


def get_all_flights():
    """Return all flight schedules with airline and airport names."""
    conn = get_connection()
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute(
            """
            SELECT
                fs.*,
                al.airline_name,
                orig.city   AS origin_city,
                orig.airport_code AS origin_code,
                dest.city   AS destination_city,
                dest.airport_code AS destination_code,
                ac.aircraft_model,
                ac.registration_number
            FROM flight_schedules fs
            JOIN airlines  al   ON fs.airline_id            = al.airline_id
            JOIN airports  orig ON fs.origin_airport_id     = orig.airport_id
            JOIN airports  dest ON fs.destination_airport_id= dest.airport_id
            JOIN aircraft  ac   ON fs.aircraft_id           = ac.aircraft_id
            ORDER BY fs.departure_datetime
            """
        )
        return cursor.fetchall()
    finally:
        cursor.close()
        conn.close()


def get_flight_by_id(flight_id: int):
    """Return a single flight schedule with full details."""
    conn = get_connection()
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute(
            """
            SELECT
                fs.*,
                al.airline_name,
                orig.city AS origin_city, orig.airport_code AS origin_code,
                dest.city AS destination_city, dest.airport_code AS destination_code,
                ac.aircraft_model, ac.total_seats, ac.economy_seats, ac.business_seats
            FROM flight_schedules fs
            JOIN airlines  al   ON fs.airline_id            = al.airline_id
            JOIN airports  orig ON fs.origin_airport_id     = orig.airport_id
            JOIN airports  dest ON fs.destination_airport_id= dest.airport_id
            JOIN aircraft  ac   ON fs.aircraft_id           = ac.aircraft_id
            WHERE fs.flight_id = %s
            """,
            (flight_id,),
        )
        return cursor.fetchone()
    finally:
        cursor.close()
        conn.close()


def add_flight(airline_id, aircraft_id, origin_id, destination_id,
               flight_number, departure, arrival, base_fare, status="Scheduled") -> int:
    """Insert a new flight schedule."""
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO flight_schedules
                (airline_id, aircraft_id, origin_airport_id, destination_airport_id,
                 flight_number, departure_datetime, arrival_datetime, base_fare, flight_status)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)
            """,
            (airline_id, aircraft_id, origin_id, destination_id,
             flight_number, departure, arrival, base_fare, status),
        )
        conn.commit()
        return cursor.lastrowid
    except Exception:
        conn.rollback()
        raise
    finally:
        cursor.close()
        conn.close()


def update_flight_status(flight_id: int, new_status: str):
    """Update the status of a flight schedule."""
    valid = ("Scheduled", "Boarding", "Departed", "Arrived", "Cancelled", "Delayed")
    if new_status not in valid:
        raise ValueError(f"Invalid flight status: {new_status}")
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE flight_schedules SET flight_status=%s WHERE flight_id=%s",
            (new_status, flight_id),
        )
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        cursor.close()
        conn.close()


def get_seat_availability(flight_id: int, travel_class: str) -> dict:
    """
    Return capacity and available seats for a class on a given flight.
    """
    conn = get_connection()
    try:
        cursor = conn.cursor(dictionary=True)
        class_col = "economy_seats" if travel_class == "Economy" else "business_seats"
        cursor.execute(
            f"SELECT {class_col} AS capacity FROM aircraft ac "
            "JOIN flight_schedules fs ON fs.aircraft_id = ac.aircraft_id "
            "WHERE fs.flight_id = %s",
            (flight_id,),
        )
        row = cursor.fetchone()
        capacity = row["capacity"] if row else 0

        cursor.execute(
            "SELECT COUNT(*) AS booked FROM tickets "
            "WHERE flight_id=%s AND travel_class=%s AND ticket_status='Active'",
            (flight_id, travel_class),
        )
        booked = cursor.fetchone()["booked"]
        return {"capacity": capacity, "booked": booked, "available": capacity - booked}
    finally:
        cursor.close()
        conn.close()


def get_booked_seats(flight_id: int) -> list:
    """Return list of already-booked seat numbers for a flight."""
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT seat_number FROM tickets "
            "WHERE flight_id=%s AND ticket_status='Active'",
            (flight_id,),
        )
        return [row[0] for row in cursor.fetchall()]
    finally:
        cursor.close()
        conn.close()


def get_dashboard_stats() -> dict:
    """Fetch summary statistics for the dashboard."""
    conn = get_connection()
    try:
        cursor = conn.cursor()

        cursor.execute("SELECT COUNT(*) FROM airlines")
        airlines = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM flight_schedules")
        flights = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM passengers")
        passengers = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM bookings")
        bookings = cursor.fetchone()[0]

        cursor.execute(
            "SELECT COUNT(*) FROM flight_schedules "
            "WHERE departure_datetime BETWEEN NOW() AND DATE_ADD(NOW(), INTERVAL 7 DAY) "
            "AND flight_status NOT IN ('Cancelled','Arrived')"
        )
        upcoming = cursor.fetchone()[0]

        cursor.execute(
            "SELECT COALESCE(SUM(amount),0) FROM payments WHERE payment_status='Completed'"
        )
        revenue = cursor.fetchone()[0]

        return {
            "airlines": airlines,
            "flights": flights,
            "passengers": passengers,
            "bookings": bookings,
            "upcoming": upcoming,
            "revenue": float(revenue),
        }
    finally:
        cursor.close()
        conn.close()


"""
validators.py
-------------
Input validation helpers for the Flight Booking System.
All user-facing inputs pass through these functions before
being used in SQL queries or business logic.
"""

import re
import random
import string
from datetime import datetime, date


# ---------------------------------------------------------------------------
# Email
# ---------------------------------------------------------------------------

def validate_email(email: str) -> tuple[bool, str]:
    """Return (True, '') if email is valid, else (False, error_message)."""
    if not email or not email.strip():
        return False, "Email address is required."
    pattern = r"^[\w.+\-]+@[\w\-]+(\.[a-zA-Z]{2,})+$"
    if re.match(pattern, email.strip()):
        return True, ""
    return False, f"'{email}' is not a valid email address."


# ---------------------------------------------------------------------------
# Phone
# ---------------------------------------------------------------------------

def validate_phone(phone: str) -> tuple[bool, str]:
    """Return (True, '') if phone is a 10-digit number, else (False, error)."""
    if not phone or not phone.strip():
        return False, "Phone number is required."
    digits = re.sub(r"\D", "", phone.strip())
    if len(digits) == 10:
        return True, ""
    return False, "Phone number must be exactly 10 digits."


# ---------------------------------------------------------------------------
# Date strings
# ---------------------------------------------------------------------------

def validate_date_string(date_str: str, field_name: str = "Date") -> tuple[bool, str]:
    """Validate a YYYY-MM-DD date string."""
    if not date_str or not date_str.strip():
        return False, f"{field_name} is required."
    try:
        datetime.strptime(date_str.strip(), "%Y-%m-%d")
        return True, ""
    except ValueError:
        return False, f"{field_name} must be in YYYY-MM-DD format."


def validate_future_date(date_str: str, field_name: str = "Date") -> tuple[bool, str]:
    """Validate that a YYYY-MM-DD date is today or in the future."""
    ok, msg = validate_date_string(date_str, field_name)
    if not ok:
        return False, msg
    chosen = datetime.strptime(date_str.strip(), "%Y-%m-%d").date()
    if chosen < date.today():
        return False, f"{field_name} cannot be in the past."
    return True, ""


# ---------------------------------------------------------------------------
# Travel class
# ---------------------------------------------------------------------------

VALID_TRAVEL_CLASSES = ("Economy", "Business")


def validate_travel_class(cls: str) -> tuple[bool, str]:
    """Return (True, '') if travel class is valid."""
    if cls in VALID_TRAVEL_CLASSES:
        return True, ""
    return False, f"Travel class must be one of: {', '.join(VALID_TRAVEL_CLASSES)}."


# ---------------------------------------------------------------------------
# Passenger count
# ---------------------------------------------------------------------------

def validate_passenger_count(count) -> tuple[bool, str]:
    """Validate passenger count is a positive integer."""
    try:
        n = int(count)
        if n < 1:
            return False, "Passenger count must be at least 1."
        if n > 9:
            return False, "Maximum 9 passengers per booking."
        return True, ""
    except (TypeError, ValueError):
        return False, "Passenger count must be a whole number."


# ---------------------------------------------------------------------------
# Fare / amount
# ---------------------------------------------------------------------------

def validate_fare(fare) -> tuple[bool, str]:
    """Validate that a fare value is non-negative."""
    try:
        f = float(fare)
        if f < 0:
            return False, "Fare cannot be negative."
        return True, ""
    except (TypeError, ValueError):
        return False, "Fare must be a numeric value."


# ---------------------------------------------------------------------------
# Name
# ---------------------------------------------------------------------------

def validate_name(name: str, field_name: str = "Name") -> tuple[bool, str]:
    """Validate a non-empty name containing only letters and spaces."""
    if not name or not name.strip():
        return False, f"{field_name} is required."
    if len(name.strip()) < 2:
        return False, f"{field_name} must be at least 2 characters."
    if not re.match(r"^[A-Za-z\s\-'\.]+$", name.strip()):
        return False, f"{field_name} may only contain letters, spaces, hyphens, and apostrophes."
    return True, ""


# ---------------------------------------------------------------------------
# Seat number
# ---------------------------------------------------------------------------

def validate_seat_number(seat: str) -> tuple[bool, str]:
    """
    Validate seat number format.
    Expected: 1 letter (class prefix) + 1-2 digits (row) + 1 letter (column).
    E.g. E12A, B01C
    """
    if not seat or not seat.strip():
        return False, "Seat number is required."
    pattern = r"^[EBeb]\d{1,2}[A-Fa-f]$"
    if re.match(pattern, seat.strip().upper()):
        return True, ""
    return False, ("Seat number must be in format: class prefix (E/B) + "
                   "row number (1-40) + column (A-F). Example: E12A, B01C")


# ---------------------------------------------------------------------------
# Booking reference generator
# ---------------------------------------------------------------------------

def generate_booking_reference(length: int = 8) -> str:
    """
    Generate a unique-looking alphanumeric booking reference.
    Format: BK + 6 uppercase alphanumeric characters. Example: BKAB12XY
    Note: Uniqueness must be verified against the database before use.
    """
    chars = string.ascii_uppercase + string.digits
    suffix = "".join(random.choices(chars, k=length - 2))
    return f"BK{suffix}"


# ---------------------------------------------------------------------------
# Origin ≠ destination
# ---------------------------------------------------------------------------

def validate_different_airports(origin_id, destination_id) -> tuple[bool, str]:
    """Ensure origin and destination airports are not the same."""
    if origin_id == destination_id:
        return False, "Origin and destination airports must be different."
    return True, ""


# ---------------------------------------------------------------------------
# Convenience: collect all errors
# ---------------------------------------------------------------------------

def collect_errors(*validation_results) -> list[str]:
    """
    Given multiple (bool, str) tuples, return a list of error messages
    for any that failed.
    """
    return [msg for ok, msg in validation_results if not ok and msg]


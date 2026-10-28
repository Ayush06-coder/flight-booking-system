"""
test_validators.py
------------------
Unit tests for src/validators.py — all validator functions.
Run with: python3 -m pytest tests/test_validators.py -v
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
from src.validators import (
    validate_email, validate_phone, validate_date_string,
    validate_future_date, validate_travel_class, validate_passenger_count,
    validate_fare, validate_name, validate_seat_number,
    generate_booking_reference, validate_different_airports, collect_errors,
)


# ── Email ──────────────────────────────────────────────────────────────────

class TestValidateEmail:
    def test_valid_email(self):
        ok, msg = validate_email("arjun.sharma@sample.com")
        assert ok is True and msg == ""

    def test_valid_email_with_plus(self):
        ok, _ = validate_email("user+tag@domain.co.in")
        assert ok is True

    def test_empty_email(self):
        ok, msg = validate_email("")
        assert ok is False and "required" in msg.lower()

    def test_missing_at(self):
        ok, _ = validate_email("invalidemail.com")
        assert ok is False

    def test_missing_domain(self):
        ok, _ = validate_email("user@")
        assert ok is False

    def test_whitespace_only(self):
        ok, _ = validate_email("   ")
        assert ok is False


# ── Phone ──────────────────────────────────────────────────────────────────

class TestValidatePhone:
    def test_valid_10_digit(self):
        ok, _ = validate_phone("9876543210")
        assert ok is True

    def test_valid_with_spaces(self):
        ok, _ = validate_phone("98765 43210")
        assert ok is True

    def test_9_digits(self):
        ok, _ = validate_phone("987654321")
        assert ok is False

    def test_11_digits(self):
        ok, _ = validate_phone("98765432100")
        assert ok is False

    def test_empty(self):
        ok, msg = validate_phone("")
        assert ok is False and "required" in msg.lower()

    def test_letters(self):
        ok, _ = validate_phone("ABCDEFGHIJ")
        assert ok is False


# ── Date string ────────────────────────────────────────────────────────────

class TestValidateDateString:
    def test_valid_date(self):
        ok, _ = validate_date_string("2026-11-05")
        assert ok is True

    def test_wrong_format(self):
        ok, _ = validate_date_string("05/11/2026")
        assert ok is False

    def test_empty(self):
        ok, _ = validate_date_string("")
        assert ok is False

    def test_invalid_month(self):
        ok, _ = validate_date_string("2026-13-01")
        assert ok is False

    def test_invalid_day(self):
        ok, _ = validate_date_string("2026-11-32")
        assert ok is False


# ── Travel class ───────────────────────────────────────────────────────────

class TestValidateTravelClass:
    def test_economy(self):
        ok, _ = validate_travel_class("Economy")
        assert ok is True

    def test_business(self):
        ok, _ = validate_travel_class("Business")
        assert ok is True

    def test_invalid_class(self):
        ok, _ = validate_travel_class("First")
        assert ok is False

    def test_case_sensitive(self):
        ok, _ = validate_travel_class("economy")
        assert ok is False


# ── Passenger count ────────────────────────────────────────────────────────

class TestValidatePassengerCount:
    def test_valid_one(self):
        ok, _ = validate_passenger_count(1)
        assert ok is True

    def test_valid_nine(self):
        ok, _ = validate_passenger_count(9)
        assert ok is True

    def test_zero(self):
        ok, _ = validate_passenger_count(0)
        assert ok is False

    def test_ten(self):
        ok, _ = validate_passenger_count(10)
        assert ok is False

    def test_string_number(self):
        ok, _ = validate_passenger_count("3")
        assert ok is True

    def test_non_numeric(self):
        ok, _ = validate_passenger_count("abc")
        assert ok is False


# ── Fare ───────────────────────────────────────────────────────────────────

class TestValidateFare:
    def test_zero_fare(self):
        ok, _ = validate_fare(0)
        assert ok is True

    def test_positive_fare(self):
        ok, _ = validate_fare(3500.00)
        assert ok is True

    def test_negative_fare(self):
        ok, _ = validate_fare(-100)
        assert ok is False

    def test_string_fare(self):
        ok, _ = validate_fare("3500")
        assert ok is True

    def test_invalid_string(self):
        ok, _ = validate_fare("abc")
        assert ok is False


# ── Name ───────────────────────────────────────────────────────────────────

class TestValidateName:
    def test_valid_name(self):
        ok, _ = validate_name("Arjun Sharma")
        assert ok is True

    def test_hyphenated_name(self):
        ok, _ = validate_name("Mary-Jane Watson")
        assert ok is True

    def test_single_char(self):
        ok, _ = validate_name("A")
        assert ok is False

    def test_empty(self):
        ok, _ = validate_name("")
        assert ok is False

    def test_digits_in_name(self):
        ok, _ = validate_name("User123")
        assert ok is False


# ── Seat number ────────────────────────────────────────────────────────────

class TestValidateSeatNumber:
    def test_valid_economy_seat(self):
        ok, _ = validate_seat_number("E12A")
        assert ok is True

    def test_valid_business_seat(self):
        ok, _ = validate_seat_number("B01C")
        assert ok is True

    def test_lowercase_accepted(self):
        ok, _ = validate_seat_number("e5f")
        assert ok is True

    def test_missing_prefix(self):
        ok, _ = validate_seat_number("12A")
        assert ok is False

    def test_invalid_prefix(self):
        ok, _ = validate_seat_number("F12A")
        assert ok is False

    def test_missing_column(self):
        ok, _ = validate_seat_number("E12")
        assert ok is False

    def test_empty_seat(self):
        ok, _ = validate_seat_number("")
        assert ok is False


# ── Booking reference generator ────────────────────────────────────────────

class TestGenerateBookingReference:
    def test_format(self):
        ref = generate_booking_reference()
        assert ref.startswith("BK")
        assert len(ref) == 8
        assert ref.isupper() or ref.isalnum()

    def test_uniqueness(self):
        refs = {generate_booking_reference() for _ in range(200)}
        # With 6 random alphanumeric chars (36^6 ≈ 2B combinations), 200 should all be unique
        assert len(refs) == 200


# ── Different airports ─────────────────────────────────────────────────────

class TestValidateDifferentAirports:
    def test_different(self):
        ok, _ = validate_different_airports(1, 2)
        assert ok is True

    def test_same(self):
        ok, msg = validate_different_airports(1, 1)
        assert ok is False and "different" in msg.lower()


# ── Collect errors ─────────────────────────────────────────────────────────

class TestCollectErrors:
    def test_no_errors(self):
        result = collect_errors((True, ""), (True, ""))
        assert result == []

    def test_one_error(self):
        result = collect_errors((True, ""), (False, "Invalid email"))
        assert result == ["Invalid email"]

    def test_multiple_errors(self):
        result = collect_errors((False, "Err1"), (False, "Err2"))
        assert len(result) == 2

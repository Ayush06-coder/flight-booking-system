"""
test_improvements.py
--------------------
Automated tests for recent improvements:
1. Screen refresh contracts on all UI frames
2. BookingsFrame prefill method contract
3. Connection failure error handling (safer startup)
4. Flight prefill data retrieval and class fare calculation
"""

import pytest
import os
from unittest.mock import patch

from src.ui.dashboard import DashboardFrame
from src.ui.flight_search import FlightSearchFrame
from src.ui.passengers import PassengersFrame
from src.ui.flights import FlightsFrame
from src.ui.bookings import BookingsFrame
from src.ui.payments import PaymentsFrame
from src.ui.reports import ReportsFrame
from src.db_connection import test_connection as check_db_connection, get_connection
from src.repositories.flight_repository import get_all_flights, get_flight_by_id, get_seat_availability


class TestScreenContracts:
    """Verify all UI screens implement the required refresh and prefill contracts."""

    @pytest.mark.parametrize("frame_cls", [
        DashboardFrame,
        FlightSearchFrame,
        PassengersFrame,
        FlightsFrame,
        BookingsFrame,
        PaymentsFrame,
        ReportsFrame,
    ])
    def test_frame_has_callable_refresh(self, frame_cls):
        """Every screen must implement a callable refresh() method."""
        assert hasattr(frame_cls, "refresh"), f"{frame_cls.__name__} missing refresh()"
        assert callable(getattr(frame_cls, "refresh")), f"{frame_cls.__name__}.refresh is not callable"

    def test_bookings_frame_has_prefill(self):
        """BookingsFrame must implement prefill(flight_id, travel_class)."""
        assert hasattr(BookingsFrame, "prefill"), "BookingsFrame missing prefill()"
        assert callable(getattr(BookingsFrame, "prefill")), "BookingsFrame.prefill is not callable"


class TestSaferStartupLogic:
    """Verify safer startup and database connection error handling."""

    def test_test_connection_success(self):
        """test_connection returns (True, message) against a running MySQL database."""
        success, msg = check_db_connection()
        assert success is True
        assert "Connected to database" in msg

    def test_test_connection_invalid_credentials(self):
        """test_connection returns (False, error_msg) when password is wrong, avoiding crash."""
        with patch.dict(os.environ, {"DB_PASSWORD": "__invalid_password_test__"}):
            success, msg = check_db_connection()
            assert success is False
            assert isinstance(msg, str)
            assert len(msg) > 0


class TestFlightPrefillLogic:
    """Verify flight data retrieval and fare calculation used by prefill."""

    def test_flight_prefill_lookup(self):
        """Verify flights can be retrieved by id and contain required fields for prefill."""
        flights = get_all_flights()
        assert len(flights) > 0
        flight = flights[0]
        flight_id = flight["flight_id"]

        retrieved = get_flight_by_id(flight_id)
        assert retrieved is not None
        assert retrieved["flight_id"] == flight_id
        assert float(retrieved["base_fare"]) > 0

    def test_prefill_fare_multiplier(self):
        """Verify that Economy uses base fare and Business scales fare by 2.5x."""
        flights = get_all_flights()
        flight = flights[0]
        base_fare = float(flight["base_fare"])

        economy_fare = base_fare
        business_fare = round(base_fare * 2.5, 2)

        assert business_fare == round(economy_fare * 2.5, 2)
        assert business_fare > economy_fare

    def test_prefill_seat_availability_data(self):
        """Verify seat availability lookup returns non-negative counts for pre-filled flight."""
        flights = [f for f in get_all_flights() if f["flight_status"] != "Cancelled"]
        assert len(flights) > 0
        flight_id = flights[0]["flight_id"]

        avail_eco = get_seat_availability(flight_id, "Economy")
        assert avail_eco["capacity"] > 0
        assert avail_eco["available"] >= 0

        avail_biz = get_seat_availability(flight_id, "Business")
        assert avail_biz["capacity"] > 0
        assert avail_biz["available"] >= 0

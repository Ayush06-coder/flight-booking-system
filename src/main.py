"""
main.py
-------
Entry point for the Flight Booking System desktop application.
Launches the Tkinter window with sidebar navigation.

Usage:
    source .venv/bin/activate
    python3 src/main.py
"""

import sys
import os

# Ensure the project root (parent of src/) is on the Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

import tkinter as tk
from tkinter import ttk, messagebox

from src.db_connection import test_connection
from src.ui.dashboard     import DashboardFrame
from src.ui.flight_search import FlightSearchFrame
from src.ui.passengers    import PassengersFrame
from src.ui.flights       import FlightsFrame
from src.ui.bookings      import BookingsFrame
from src.ui.payments      import PaymentsFrame
from src.ui.reports       import ReportsFrame


# ---------------------------------------------------------------------------
# Application window
# ---------------------------------------------------------------------------

class FlightBookingApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("✈  Flight Booking System")
        self.geometry("1200x760")
        self.minsize(900, 600)

        # Use the 'clam' theme — renders correctly on macOS (light & dark)
        style = ttk.Style(self)
        style.theme_use("clam")

        # Custom colours for sidebar
        style.configure("Sidebar.TFrame",  background="#1a2332")
        style.configure("SidebarBtn.TButton",
                        background="#1a2332", foreground="white",
                        font=("Helvetica", 11), relief="flat", anchor="w",
                        padding=(14, 10))
        style.map("SidebarBtn.TButton",
                  background=[("active", "#2c3e50"), ("pressed", "#3d5166")],
                  foreground=[("active", "white")])
        style.configure("Active.SidebarBtn.TButton",
                        background="#2980b9", foreground="white")

        self._frames: dict[str, ttk.Frame] = {}
        self._active_btn = None

        # Safer startup: test database connectivity BEFORE initializing UI frames
        if not self._check_db_or_exit():
            return

        self._build_ui()

    def _check_db_or_exit(self) -> bool:
        """
        Verify database connection before building the UI.
        If connection fails, display an error dialog with fix steps and exit cleanly.
        """
        success, msg = test_connection()
        if success:
            self.title(f"✈  Flight Booking System  —  {msg}")
            return True
        else:
            self.withdraw()  # Hide empty parent window before showing error dialog
            messagebox.showerror(
                "Database Connection Failed",
                f"{msg}\n\n"
                "Please check:\n"
                "1. MySQL is running: brew services start mysql\n"
                "2. Your .env file has the correct credentials\n"
                "3. The database exists: mysql -u root -p < database/schema.sql",
            )
            self.destroy()
            return False

    def _build_ui(self):
        # Sidebar
        sidebar = ttk.Frame(self, style="Sidebar.TFrame", width=190)
        sidebar.pack(side="left", fill="y")
        sidebar.pack_propagate(False)

        # Logo / title
        tk.Label(
            sidebar,
            text="✈\nFlight\nBooking\nSystem",
            bg="#1a2332", fg="white",
            font=("Helvetica", 13, "bold"),
            justify="center",
        ).pack(pady=(20, 14))

        ttk.Separator(sidebar).pack(fill="x", padx=10, pady=4)

        nav_items = [
            ("🏠  Dashboard",     "dashboard"),
            ("🔍  Flight Search", "search"),
            ("👤  Passengers",    "passengers"),
            ("✈   Flights/Admin", "flights"),
            ("📋  Bookings",      "bookings"),
            ("💳  Payments",      "payments"),
            ("📊  Reports",       "reports"),
        ]

        self._nav_buttons = {}
        for label, key in nav_items:
            btn = ttk.Button(
                sidebar, text=label, style="SidebarBtn.TButton",
                command=lambda k=key: self._show(k),
            )
            btn.pack(fill="x", padx=4, pady=1)
            self._nav_buttons[key] = btn

        # Footer
        tk.Label(
            sidebar,
            text="Flight Booking System\nDesktop Prototype",
            bg="#1a2332", fg="#7f8c8d",
            font=("Helvetica", 8), justify="center",
        ).pack(side="bottom", pady=10)

        # Content area
        self._content = ttk.Frame(self, padding=0)
        self._content.pack(side="left", fill="both", expand=True)

        # Pre-build all frames
        self._frames["dashboard"]  = DashboardFrame(self._content)
        self._frames["search"]     = FlightSearchFrame(self._content,
                                                       on_book_callback=self._on_book_flight)
        self._frames["passengers"] = PassengersFrame(self._content)
        self._frames["flights"]    = FlightsFrame(self._content)
        self._frames["bookings"]   = BookingsFrame(self._content)
        self._frames["payments"]   = PaymentsFrame(self._content)
        self._frames["reports"]    = ReportsFrame(self._content)

        for frame in self._frames.values():
            frame.place(relx=0, rely=0, relwidth=1, relheight=1)
            frame.lower()

        self._show("dashboard")

    def _show(self, key: str):
        frame = self._frames[key]
        frame.lift()

        # Update sidebar button styles
        if self._active_btn:
            self._active_btn.configure(style="SidebarBtn.TButton")
        btn = self._nav_buttons[key]
        btn.configure(style="Active.SidebarBtn.TButton")
        self._active_btn = btn

        # Automatically refresh target screen to ensure live data display
        if hasattr(frame, "refresh"):
            try:
                frame.refresh()
            except Exception as e:
                messagebox.showerror(
                    "Database Refresh Error",
                    f"Could not refresh data for '{key}':\n{e}\n\n"
                    "Please verify your MySQL connection."
                )

    def _on_book_flight(self, flight_id: int, flight_info=None, travel_class: str = "Economy"):
        """Called from FlightSearchFrame when user clicks 'Book Selected Flight'."""
        self._show("bookings")
        bookings_frame = self._frames.get("bookings")
        if bookings_frame and hasattr(bookings_frame, "prefill"):
            bookings_frame.prefill(flight_id=flight_id, travel_class=travel_class)


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    app = FlightBookingApp()
    try:
        if app.winfo_exists():
            app.mainloop()
    except tk.TclError:
        pass


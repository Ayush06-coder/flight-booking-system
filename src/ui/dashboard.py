"""
dashboard.py
------------
Dashboard UI module — shows live database-backed summary cards.
"""

import tkinter as tk
from tkinter import ttk
from src.repositories.flight_repository import get_dashboard_stats
from src.repositories.flight_repository import get_all_flights


class DashboardFrame(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent, padding=20)
        self._build()

    def _build(self):
        # Title
        ttk.Label(
            self, text="✈  Flight Booking System — Dashboard",
            font=("Helvetica", 18, "bold"),
        ).grid(row=0, column=0, columnspan=3, sticky="w", pady=(0, 20))

        ttk.Label(
            self,
            text="⚠  All flight schedules, fares, and passenger data shown are SIMULATED SAMPLE DATA "
                 "for academic demonstration purposes only.",
            foreground="#8B4513", font=("Helvetica", 9, "italic"), wraplength=700,
        ).grid(row=1, column=0, columnspan=3, sticky="w", pady=(0, 16))

        self._stats_frame = ttk.LabelFrame(self, text="Live Statistics", padding=14)
        self._stats_frame.grid(row=2, column=0, columnspan=3, sticky="nsew", pady=(0, 20))

        self._card_labels = {}
        self.refresh()

        # Upcoming flights table
        ttk.Label(
            self, text="Upcoming Flights (Next 7 Days)",
            font=("Helvetica", 13, "bold"),
        ).grid(row=3, column=0, columnspan=3, sticky="w", pady=(0, 6))

        cols = ("flight_number", "airline_name", "origin_city", "destination_city",
                "departure_datetime", "flight_status")
        self._tree = ttk.Treeview(self, columns=cols, show="headings", height=8)
        headers = ("Flight No", "Airline", "Origin", "Destination", "Departure", "Status")
        widths  = (90, 140, 110, 110, 160, 100)
        for c, h, w in zip(cols, headers, widths):
            self._tree.heading(c, text=h)
            self._tree.column(c, width=w, anchor="center")

        scrollbar = ttk.Scrollbar(self, orient="vertical", command=self._tree.yview)
        self._tree.configure(yscrollcommand=scrollbar.set)
        self._tree.grid(row=4, column=0, columnspan=2, sticky="nsew")
        scrollbar.grid(row=4, column=2, sticky="ns")

        ttk.Button(self, text="⟳  Refresh", command=self.refresh).grid(
            row=5, column=0, sticky="w", pady=(10, 0)
        )

        self.columnconfigure(0, weight=1)
        self.rowconfigure(4, weight=1)

        self._load_upcoming()

    def refresh(self):
        """Reload stats from the database and redraw cards."""
        try:
            stats = get_dashboard_stats()
        except Exception as e:
            stats = {k: "ERR" for k in
                     ("airlines", "flights", "passengers", "bookings", "upcoming", "revenue")}

        card_data = [
            ("✈  Airlines",    stats.get("airlines",   0)),
            ("🛫  Flights",    stats.get("flights",    0)),
            ("👤  Passengers", stats.get("passengers", 0)),
            ("📋  Bookings",   stats.get("bookings",   0)),
            ("🔜  Upcoming",   stats.get("upcoming",   0)),
            ("💰  Revenue",    f"₹ {stats.get('revenue', 0):,.2f}"),
        ]

        # Clear old widgets
        for w in self._stats_frame.winfo_children():
            w.destroy()

        for i, (label, value) in enumerate(card_data):
            row, col = divmod(i, 3)
            card = ttk.LabelFrame(self._stats_frame, text=label, padding=12)
            card.grid(row=row, column=col, padx=12, pady=8, sticky="nsew")
            ttk.Label(
                card, text=str(value),
                font=("Helvetica", 22, "bold"),
            ).pack()
            self._stats_frame.columnconfigure(col, weight=1)

        self._load_upcoming()

    def _load_upcoming(self):
        if not hasattr(self, "_tree"):
            return
        for row in self._tree.get_children():
            self._tree.delete(row)
        try:
            flights = get_all_flights()
            from datetime import datetime, timedelta
            now = datetime.now()
            cutoff = now + timedelta(days=7)
            for f in flights:
                dep = f["departure_datetime"]
                if isinstance(dep, str):
                    dep = datetime.strptime(dep, "%Y-%m-%d %H:%M:%S")
                if now <= dep <= cutoff and f["flight_status"] != "Cancelled":
                    self._tree.insert("", "end", values=(
                        f["flight_number"], f["airline_name"],
                        f["origin_city"], f["destination_city"],
                        str(dep), f["flight_status"],
                    ))
        except Exception:
            pass


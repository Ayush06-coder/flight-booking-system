"""
flight_search.py
----------------
Flight search UI module.
"""

import tkinter as tk
from tkinter import ttk, messagebox
from datetime import date

from src.repositories.airport_repository import get_all_airports
from src.repositories.flight_repository import search_flights


class FlightSearchFrame(ttk.Frame):
    def __init__(self, parent, on_book_callback=None):
        super().__init__(parent, padding=20)
        self._airports = []
        self._airport_map = {}      # "City (CODE)" → airport_id
        self._on_book = on_book_callback
        self._build()
        self._load_airports()

    def _build(self):
        ttk.Label(
            self, text="Flight Search",
            font=("Helvetica", 16, "bold"),
        ).grid(row=0, column=0, columnspan=4, sticky="w", pady=(0, 14))

        # Search form
        form = ttk.LabelFrame(self, text="Search Criteria", padding=12)
        form.grid(row=1, column=0, columnspan=4, sticky="ew", pady=(0, 14))

        ttk.Label(form, text="Origin:").grid(row=0, column=0, sticky="w", padx=6, pady=4)
        self._origin_var = tk.StringVar()
        self._origin_cb = ttk.Combobox(form, textvariable=self._origin_var, width=28, state="readonly")
        self._origin_cb.grid(row=0, column=1, sticky="ew", padx=6, pady=4)

        ttk.Label(form, text="Destination:").grid(row=0, column=2, sticky="w", padx=6, pady=4)
        self._dest_var = tk.StringVar()
        self._dest_cb = ttk.Combobox(form, textvariable=self._dest_var, width=28, state="readonly")
        self._dest_cb.grid(row=0, column=3, sticky="ew", padx=6, pady=4)

        ttk.Label(form, text="Travel Date (YYYY-MM-DD):").grid(row=1, column=0, sticky="w", padx=6, pady=4)
        self._date_var = tk.StringVar(value=str(date.today()))
        ttk.Entry(form, textvariable=self._date_var, width=18).grid(row=1, column=1, sticky="w", padx=6, pady=4)

        ttk.Label(form, text="Class:").grid(row=1, column=2, sticky="w", padx=6, pady=4)
        self._class_var = tk.StringVar(value="Economy")
        ttk.Combobox(
            form, textvariable=self._class_var,
            values=["Economy", "Business"], width=14, state="readonly",
        ).grid(row=1, column=3, sticky="w", padx=6, pady=4)

        ttk.Button(form, text="🔍  Search Flights", command=self._search).grid(
            row=2, column=0, columnspan=4, pady=10,
        )
        for i in range(4):
            form.columnconfigure(i, weight=1)

        # Results table
        ttk.Label(
            self, text="Search Results",
            font=("Helvetica", 13, "bold"),
        ).grid(row=2, column=0, columnspan=4, sticky="w", pady=(0, 6))

        self._status_lbl = ttk.Label(self, text="", foreground="gray")
        self._status_lbl.grid(row=3, column=0, columnspan=4, sticky="w")

        cols = ("flight_id", "airline", "flight_no", "origin", "destination",
                "departure", "arrival", "duration", "fare", "available", "status")
        self._tree = ttk.Treeview(self, columns=cols, show="headings", height=12)
        headers = ("ID", "Airline", "Flight No", "From", "To",
                   "Departure", "Arrival", "Duration", "Fare (₹)", "Seats", "Status")
        widths = (40, 130, 80, 90, 90, 140, 140, 80, 90, 60, 90)
        for c, h, w in zip(cols, headers, widths):
            self._tree.heading(c, text=h)
            self._tree.column(c, width=w, anchor="center")
        self._tree.column("flight_id", width=0, stretch=False)  # hide ID column visually

        vsb = ttk.Scrollbar(self, orient="vertical", command=self._tree.yview)
        hsb = ttk.Scrollbar(self, orient="horizontal", command=self._tree.xview)
        self._tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        self._tree.grid(row=4, column=0, columnspan=3, sticky="nsew")
        vsb.grid(row=4, column=3, sticky="ns")
        hsb.grid(row=5, column=0, columnspan=3, sticky="ew")

        btn_frame = ttk.Frame(self)
        btn_frame.grid(row=6, column=0, columnspan=4, sticky="w", pady=(10, 0))
        ttk.Button(btn_frame, text="📋  Book Selected Flight", command=self._book_selected).pack(side="left", padx=4)

        self.columnconfigure(0, weight=1)
        self.rowconfigure(4, weight=1)

    def _load_airports(self):
        try:
            self._airports = get_all_airports()
            labels = [f"{a['city']} ({a['airport_code']})" for a in self._airports]
            self._airport_map = {
                f"{a['city']} ({a['airport_code']})": a["airport_id"]
                for a in self._airports
            }
            curr_origin = self._origin_var.get()
            curr_dest   = self._dest_var.get()
            self._origin_cb["values"] = labels
            self._dest_cb["values"]   = labels
            if curr_origin in labels:
                self._origin_var.set(curr_origin)
            if curr_dest in labels:
                self._dest_var.set(curr_dest)
        except Exception as e:
            messagebox.showerror("DB Error", f"Could not load airports:\n{e}")

    def refresh(self):
        """Reload airport choices and refresh active search results if present."""
        self._load_airports()
        # If user has searched and has active criteria, refresh search results to update seat availability
        if (self._origin_var.get() and self._dest_var.get() and
                self._tree.get_children() and self._origin_var.get() != self._dest_var.get()):
            self._search()

    def _search(self):
        origin_label = self._origin_var.get()
        dest_label   = self._dest_var.get()
        travel_date  = self._date_var.get().strip()
        travel_class = self._class_var.get()

        if not origin_label or not dest_label:
            messagebox.showwarning("Input Error", "Please select both origin and destination.")
            return
        if origin_label == dest_label:
            messagebox.showwarning("Input Error", "Origin and destination cannot be the same.")
            return
        if not travel_date:
            messagebox.showwarning("Input Error", "Please enter a travel date.")
            return

        origin_id = self._airport_map[origin_label]
        dest_id   = self._airport_map[dest_label]

        for row in self._tree.get_children():
            self._tree.delete(row)

        try:
            results = search_flights(origin_id, dest_id, travel_date, travel_class)
        except Exception as e:
            messagebox.showerror("Search Error", str(e))
            return

        if not results:
            self._status_lbl.config(
                text=f"No {travel_class} flights found from {origin_label} to {dest_label} on {travel_date}.",
                foreground="gray",
            )
            return

        self._status_lbl.config(
            text=f"{len(results)} flight(s) found.", foreground="green"
        )

        for f in results:
            dur = f.get("duration_minutes", 0)
            hours, mins = divmod(dur, 60)
            self._tree.insert("", "end", values=(
                f["flight_id"],
                f["airline_name"],
                f["flight_number"],
                f"{f['origin_city']} ({f['origin_code']})",
                f"{f['destination_city']} ({f['destination_code']})",
                str(f["departure_datetime"]),
                str(f["arrival_datetime"]),
                f"{hours}h {mins}m",
                f"{float(f['class_fare']):,.2f}",
                f["available_seats"],
                f["flight_status"],
            ))

    def _book_selected(self):
        selected = self._tree.selection()
        if not selected:
            messagebox.showinfo("Select Flight", "Please select a flight from the results first.")
            return
        values = self._tree.item(selected[0], "values")
        flight_id = values[0]
        if self._on_book:
            self._on_book(
                flight_id=int(flight_id),
                flight_info=values,
                travel_class=self._class_var.get(),
            )
        else:
            messagebox.showinfo("Flight Selected",
                                f"Flight {values[2]} selected.\nGo to Bookings to complete.")


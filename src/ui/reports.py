"""
reports.py
----------
Reports UI — tabbed view of all analytical reports.
"""

import tkinter as tk
from tkinter import ttk, messagebox
import csv
import os

from src.repositories.payment_repository import (
    get_revenue_by_airline, get_revenue_by_route,
    get_payment_status_summary,
)
from src.repositories.booking_repository import (
    get_bookings_by_date_range, get_booking_status_summary,
)
from src.repositories.flight_repository import get_all_flights
from src.repositories.passenger_repository import get_all_passengers
from src.db_connection import get_connection


class ReportsFrame(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent, padding=20)
        self._build()

    def _build(self):
        ttk.Label(
            self, text="Reports & Analytics",
            font=("Helvetica", 16, "bold"),
        ).pack(anchor="w", pady=(0, 12))

        nb = ttk.Notebook(self)
        nb.pack(fill="both", expand=True)

        reports = [
            ("📅 Schedules",        self._build_schedules),
            ("👤 Passenger History", self._build_pax_history),
            ("📊 Revenue by Airline",self._build_rev_airline),
            ("🗺  Revenue by Route",  self._build_rev_route),
            ("💺 Occupancy",         self._build_occupancy),
            ("📋 Booking Status",    self._build_booking_status),
            ("💳 Payment Status",    self._build_payment_status),
            ("📆 Bookings by Date",  self._build_by_date),
        ]
        for title, builder in reports:
            frame = ttk.Frame(nb, padding=10)
            nb.add(frame, text=title)
            builder(frame)

    # ---------------------------------------------------------------
    # Helper: build a simple Treeview report tab
    # ---------------------------------------------------------------
    def _make_tree(self, parent, cols, headers, widths, loader_fn, height=14):
        btn_row = ttk.Frame(parent)
        btn_row.pack(fill="x", pady=(0, 6))
        ttk.Button(btn_row, text="⟳ Refresh", command=lambda: self._populate(tree, loader_fn)).pack(side="left")
        ttk.Button(btn_row, text="💾 Export CSV", command=lambda: self._export_csv(tree, cols)).pack(side="left", padx=6)

        tree = ttk.Treeview(parent, columns=cols, show="headings", height=height)
        for c, h, w in zip(cols, headers, widths):
            tree.heading(c, text=h)
            tree.column(c, width=w, anchor="center")

        vsb = ttk.Scrollbar(parent, orient="vertical", command=tree.yview)
        hsb = ttk.Scrollbar(parent, orient="horizontal", command=tree.xview)
        tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        tree.pack(side="left", fill="both", expand=True)
        vsb.pack(side="right", fill="y")

        self._populate(tree, loader_fn)
        return tree

    def _populate(self, tree, loader_fn):
        for r in tree.get_children(): tree.delete(r)
        try:
            for row in loader_fn():
                tree.insert("", "end", values=list(row.values()))
        except Exception as e:
            messagebox.showerror("Report Error", str(e))

    def _export_csv(self, tree, cols):
        path = os.path.expanduser("~/Desktop/report_export.csv")
        rows = [tree.item(r, "values") for r in tree.get_children()]
        try:
            with open(path, "w", newline="") as f:
                writer = csv.writer(f)
                writer.writerow(cols)
                writer.writerows(rows)
            messagebox.showinfo("Exported", f"Report saved to:\n{path}")
        except Exception as e:
            messagebox.showerror("Export Error", str(e))

    # ---------------------------------------------------------------
    # Report builders
    # ---------------------------------------------------------------
    def _build_schedules(self, parent):
        def loader():
            return [
                {
                    "flight_number":       f["flight_number"],
                    "airline_name":        f["airline_name"],
                    "origin_city":         f["origin_city"],
                    "destination_city":    f["destination_city"],
                    "departure_datetime":  str(f["departure_datetime"]),
                    "arrival_datetime":    str(f["arrival_datetime"]),
                    "base_fare":           f"{float(f['base_fare']):,.2f}",
                    "flight_status":       f["flight_status"],
                }
                for f in get_all_flights()
            ]
        self._make_tree(parent,
            cols=("flight_number","airline_name","origin_city","destination_city",
                  "departure_datetime","arrival_datetime","base_fare","flight_status"),
            headers=("Flight No","Airline","From","To","Departure","Arrival","Base Fare (₹)","Status"),
            widths=(80,130,100,100,150,150,110,100),
            loader_fn=loader,
        )

    def _build_pax_history(self, parent):
        def loader():
            conn = get_connection()
            try:
                cursor = conn.cursor(dictionary=True)
                cursor.execute("""
                    SELECT
                        p.full_name, b.booking_reference,
                        fs.flight_number, al.airline_name,
                        orig.city AS origin, dest.city AS destination,
                        fs.departure_datetime, t.travel_class,
                        t.seat_number, t.ticket_fare, b.booking_status
                    FROM passengers p
                    JOIN bookings b ON b.passenger_id = p.passenger_id
                    JOIN tickets t ON t.booking_id = b.booking_id
                    JOIN flight_schedules fs ON t.flight_id = fs.flight_id
                    JOIN airlines al ON fs.airline_id = al.airline_id
                    JOIN airports orig ON fs.origin_airport_id = orig.airport_id
                    JOIN airports dest ON fs.destination_airport_id = dest.airport_id
                    ORDER BY p.full_name, b.booking_datetime DESC
                """)
                rows = cursor.fetchall()
                for r in rows:
                    r["departure_datetime"] = str(r["departure_datetime"])
                    r["ticket_fare"] = f"{float(r['ticket_fare']):,.2f}"
                return rows
            finally:
                cursor.close(); conn.close()

        self._make_tree(parent,
            cols=("full_name","booking_reference","flight_number","airline_name",
                  "origin","destination","departure_datetime","travel_class",
                  "seat_number","ticket_fare","booking_status"),
            headers=("Passenger","Ref","Flight","Airline","From","To",
                     "Departure","Class","Seat","Fare (₹)","Status"),
            widths=(130,90,80,120,90,90,140,80,60,90,90),
            loader_fn=loader,
        )

    def _build_rev_airline(self, parent):
        def loader():
            rows = get_revenue_by_airline()
            for r in rows:
                r["total_revenue"] = f"{float(r['total_revenue']):,.2f}"
                r["avg_revenue"]   = f"{float(r['avg_revenue']):,.2f}"
            return rows
        self._make_tree(parent,
            cols=("airline_name","total_bookings","total_revenue","avg_revenue"),
            headers=("Airline","Total Bookings","Revenue (₹)","Avg per Booking (₹)"),
            widths=(180,120,140,160),
            loader_fn=loader,
        )

    def _build_rev_route(self, parent):
        def loader():
            rows = get_revenue_by_route()
            for r in rows:
                r["route_revenue"] = f"{float(r['route_revenue']):,.2f}"
            return rows
        self._make_tree(parent,
            cols=("origin","destination","bookings","route_revenue"),
            headers=("Origin","Destination","Bookings","Revenue (₹)"),
            widths=(130,130,90,140),
            loader_fn=loader,
        )

    def _build_occupancy(self, parent):
        def loader():
            conn = get_connection()
            try:
                cursor = conn.cursor(dictionary=True)
                cursor.execute("""
                    SELECT
                        fs.flight_number, al.airline_name,
                        orig.city AS origin, dest.city AS destination,
                        ac.total_seats,
                        COUNT(t.ticket_id) AS tickets_sold,
                        ROUND(COUNT(t.ticket_id)*100.0/ac.total_seats,2) AS occupancy_pct
                    FROM flight_schedules fs
                    JOIN airlines al ON fs.airline_id = al.airline_id
                    JOIN aircraft ac ON fs.aircraft_id = ac.aircraft_id
                    JOIN airports orig ON fs.origin_airport_id = orig.airport_id
                    JOIN airports dest ON fs.destination_airport_id = dest.airport_id
                    LEFT JOIN tickets t ON t.flight_id=fs.flight_id AND t.ticket_status='Active'
                    GROUP BY fs.flight_id, fs.flight_number, al.airline_name,
                             orig.city, dest.city, ac.total_seats
                    ORDER BY occupancy_pct DESC
                """)
                return cursor.fetchall()
            finally:
                cursor.close(); conn.close()

        self._make_tree(parent,
            cols=("flight_number","airline_name","origin","destination",
                  "total_seats","tickets_sold","occupancy_pct"),
            headers=("Flight No","Airline","From","To","Capacity","Sold","Occupancy %"),
            widths=(80,130,100,100,80,70,100),
            loader_fn=loader,
        )

    def _build_booking_status(self, parent):
        self._make_tree(parent,
            cols=("booking_status","total"),
            headers=("Booking Status","Count"),
            widths=(180,180),
            loader_fn=get_booking_status_summary,
            height=6,
        )

    def _build_payment_status(self, parent):
        def loader():
            rows = get_payment_status_summary()
            for r in rows:
                r["total"] = f"{float(r['total']):,.2f}"
            return rows
        self._make_tree(parent,
            cols=("payment_status","count","total"),
            headers=("Status","Count","Total Amount (₹)"),
            widths=(140,100,180),
            loader_fn=loader,
            height=6,
        )

    def _build_by_date(self, parent):
        ctrl = ttk.Frame(parent)
        ctrl.pack(fill="x", pady=(0, 8))
        ttk.Label(ctrl, text="From (YYYY-MM-DD):").pack(side="left")
        self._from_var = tk.StringVar(value="2026-10-01")
        ttk.Entry(ctrl, textvariable=self._from_var, width=14).pack(side="left", padx=4)
        ttk.Label(ctrl, text="To:").pack(side="left")
        self._to_var = tk.StringVar(value="2026-12-31")
        ttk.Entry(ctrl, textvariable=self._to_var, width=14).pack(side="left", padx=4)
        ttk.Button(ctrl, text="Apply", command=lambda: self._populate(
            self._date_tree,
            lambda: get_bookings_by_date_range(self._from_var.get(), self._to_var.get()),
        )).pack(side="left", padx=6)

        cols = ("booking_reference","full_name","booking_datetime",
                "total_amount","booking_status","payment_status")
        self._date_tree = ttk.Treeview(parent, columns=cols, show="headings", height=12)
        for c, h, w in zip(cols,
                            ("Reference","Passenger","Date","Amount (₹)","Status","Payment"),
                            (100,150,150,100,100,100)):
            self._date_tree.heading(c, text=h)
            self._date_tree.column(c, width=w, anchor="center")
        self._date_tree.pack(fill="both", expand=True)
        self._populate(self._date_tree,
                       lambda: get_bookings_by_date_range(self._from_var.get(), self._to_var.get()))


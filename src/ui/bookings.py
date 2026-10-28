"""
bookings.py
-----------
Booking management UI — search, create, view, and cancel bookings.
"""

import tkinter as tk
from tkinter import ttk, messagebox

from src.repositories.booking_repository import (
    get_all_bookings, get_booking_by_reference, get_tickets_for_booking,
    get_booking_status_history, create_booking, cancel_booking,
)
from src.repositories.passenger_repository import get_all_passengers, search_passengers
from src.repositories.flight_repository import (
    get_all_flights, get_seat_availability, get_booked_seats,
)
from src.validators import validate_seat_number


class BookingsFrame(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent, padding=20)
        self._build()
        self._load_bookings()

    def _build(self):
        ttk.Label(
            self, text="Booking Management",
            font=("Helvetica", 16, "bold"),
        ).grid(row=0, column=0, columnspan=2, sticky="w", pady=(0, 12))

        nb = ttk.Notebook(self)
        self._notebook = nb
        nb.grid(row=1, column=0, columnspan=2, sticky="nsew")

        self._list_tab   = ttk.Frame(nb, padding=12)
        self._create_tab = ttk.Frame(nb, padding=12)
        self._detail_tab = ttk.Frame(nb, padding=12)

        nb.add(self._list_tab,   text="📋  All Bookings")
        nb.add(self._create_tab, text="➕  New Booking")
        nb.add(self._detail_tab, text="🔍  Booking Detail")

        self._build_list_tab()
        self._build_create_tab()
        self._build_detail_tab()

        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)

    # ---------------------------------------------------------------
    # All Bookings tab
    # ---------------------------------------------------------------
    def _build_list_tab(self):
        p = self._list_tab

        sf = ttk.Frame(p)
        sf.pack(fill="x", pady=(0, 8))
        ttk.Label(sf, text="Search by reference:").pack(side="left")
        self._search_ref = tk.StringVar()
        ttk.Entry(sf, textvariable=self._search_ref, width=20).pack(side="left", padx=6)
        ttk.Button(sf, text="Search", command=self._search_by_ref).pack(side="left")
        ttk.Button(sf, text="Show All", command=self._load_bookings).pack(side="left", padx=4)

        cols = ("booking_id","booking_reference","passenger_name",
                "booking_datetime","total_amount","booking_status","ticket_count")
        self._tree = ttk.Treeview(p, columns=cols, show="headings", height=14)
        for c, h, w in zip(cols,
                            ("ID","Reference","Passenger","Date & Time","Amount (₹)","Status","Tickets"),
                            (40,100,160,150,100,100,60)):
            self._tree.heading(c, text=h)
            self._tree.column(c, width=w, anchor="center")
        self._tree.column("booking_id", width=0, stretch=False)

        vsb = ttk.Scrollbar(p, orient="vertical", command=self._tree.yview)
        self._tree.configure(yscrollcommand=vsb.set)
        self._tree.pack(side="left", fill="both", expand=True)
        vsb.pack(side="right", fill="y")

        bf = ttk.Frame(p)
        bf.pack(fill="x", pady=(8, 0))
        ttk.Button(bf, text="View Details", command=self._view_detail).pack(side="left", padx=4)
        ttk.Button(bf, text="❌  Cancel Booking", command=self._cancel_booking).pack(side="left", padx=4)
        ttk.Button(bf, text="⟳  Refresh", command=self._load_bookings).pack(side="left", padx=4)

    def _load_bookings(self):
        for r in self._tree.get_children():
            self._tree.delete(r)
        try:
            for b in get_all_bookings():
                tag = "cancelled" if b["booking_status"] == "Cancelled" else ""
                self._tree.insert("", "end", tags=(tag,), values=(
                    b["booking_id"], b["booking_reference"], b["passenger_name"],
                    str(b["booking_datetime"]),
                    f"{float(b['total_amount']):,.2f}",
                    b["booking_status"], b["ticket_count"],
                ))
            self._tree.tag_configure("cancelled", foreground="gray")
        except Exception as e:
            messagebox.showerror("DB Error", str(e))

    def _search_by_ref(self):
        ref = self._search_ref.get().strip()
        if not ref:
            self._load_bookings(); return
        booking = get_booking_by_reference(ref)
        for r in self._tree.get_children():
            self._tree.delete(r)
        if booking:
            self._tree.insert("", "end", values=(
                booking["booking_id"], booking["booking_reference"], booking["full_name"],
                str(booking["booking_datetime"]),
                f"{float(booking['total_amount']):,.2f}",
                booking["booking_status"], "",
            ))
        else:
            messagebox.showinfo("Not Found", f"No booking found for reference '{ref}'.")

    def _cancel_booking(self):
        sel = self._tree.selection()
        if not sel:
            messagebox.showwarning("Select", "Select a booking to cancel."); return
        vals = self._tree.item(sel[0], "values")
        booking_id = int(vals[0])
        ref        = vals[1]
        if not messagebox.askyesno("Confirm Cancellation",
                                    f"Cancel booking {ref}?\n"
                                    "Tickets will be released and payment marked as Refunded (simulated)."):
            return
        try:
            cancel_booking(booking_id)
            messagebox.showinfo("Cancelled", f"Booking {ref} has been cancelled.")
            self._load_bookings()
        except Exception as e:
            messagebox.showerror("Cancellation Failed", str(e))

    def _view_detail(self):
        sel = self._tree.selection()
        if not sel:
            messagebox.showwarning("Select", "Select a booking to view."); return
        vals = self._tree.item(sel[0], "values")
        booking_id = int(vals[0])
        self._populate_detail(booking_id)

    # ---------------------------------------------------------------
    # New Booking tab
    # ---------------------------------------------------------------
    def _build_create_tab(self):
        p = self._create_tab

        ttk.Label(p, text="Step 1: Select Flight", font=("Helvetica", 12, "bold")).pack(anchor="w")

        # Flight selector
        self._flight_map = {}
        self._flight_var = tk.StringVar()
        self._flight_cb = ttk.Combobox(p, textvariable=self._flight_var, width=70, state="readonly")
        self._flight_cb.pack(fill="x", pady=(4, 12))
        self._reload_flight_options()

        ttk.Label(p, text="Step 2: Select Passenger", font=("Helvetica", 12, "bold")).pack(anchor="w")

        # Passenger selector
        self._pax_map = {}
        self._pax_var = tk.StringVar()
        self._pax_cb = ttk.Combobox(p, textvariable=self._pax_var, width=50, state="readonly")
        self._pax_cb.pack(fill="x", pady=(4, 12))
        self._reload_passenger_options()

        ttk.Label(p, text="Step 3: Seat & Class", font=("Helvetica", 12, "bold")).pack(anchor="w")

        sf = ttk.Frame(p)
        sf.pack(fill="x", pady=(4, 0))

        self._class_var = tk.StringVar(value="Economy")
        ttk.Label(sf, text="Class:").pack(side="left")
        ttk.Combobox(sf, textvariable=self._class_var,
                     values=["Economy","Business"], width=12, state="readonly").pack(side="left", padx=6)
        self._class_var.trace_add("write", lambda *_: self._update_availability())

        ttk.Button(sf, text="Check Availability", command=self._update_availability).pack(side="left", padx=6)
        self._avail_lbl = ttk.Label(sf, text="", foreground="blue")
        self._avail_lbl.pack(side="left")

        sf2 = ttk.Frame(p)
        sf2.pack(fill="x", pady=(8, 0))
        ttk.Label(sf2, text="Seat Number (e.g. E12A, B01C):").pack(side="left")
        self._seat_var = tk.StringVar()
        ttk.Entry(sf2, textvariable=self._seat_var, width=12).pack(side="left", padx=6)

        self._booked_lbl = ttk.Label(p, text="", foreground="gray", wraplength=600)
        self._booked_lbl.pack(anchor="w", pady=(4, 0))

        # Fare display
        fare_frame = ttk.LabelFrame(p, text="Fare Estimate (SAMPLE DATA)", padding=10)
        fare_frame.pack(fill="x", pady=(12, 0))
        self._fare_lbl = ttk.Label(fare_frame, text="Select a flight to see fare.",
                                    font=("Helvetica", 14))
        self._fare_lbl.pack()

        ttk.Button(p, text="✅  Confirm Booking", command=self._confirm_booking,
                   ).pack(pady=14)

        self._flight_var.trace_add("write", lambda *_: self._update_availability())

    def _reload_flight_options(self):
        """Reload active flights into the combobox, preserving current selection if valid."""
        flights = get_all_flights()
        self._flight_map = {
            f"{f['flight_number']} | {f['origin_city']} → {f['destination_city']} | {str(f['departure_datetime'])}":
                f["flight_id"]
            for f in flights if f["flight_status"] != "Cancelled"
        }
        labels = list(self._flight_map.keys())
        if hasattr(self, "_flight_cb"):
            self._flight_cb["values"] = labels
        current = self._flight_var.get()
        if current and current not in self._flight_map:
            self._flight_var.set("")

    def _reload_passenger_options(self):
        """Reload passengers into the combobox, preserving current selection if valid."""
        pax = get_all_passengers()
        self._pax_map = {
            f"{pa['full_name']} ({pa['email']})": pa["passenger_id"]
            for pa in pax
        }
        labels = list(self._pax_map.keys())
        if hasattr(self, "_pax_cb"):
            self._pax_cb["values"] = labels
        current = self._pax_var.get()
        if current and current not in self._pax_map:
            self._pax_var.set("")

    def prefill(self, flight_id: int, travel_class: str = "Economy"):
        """
        Pre-fill the booking form with a selected flight and travel class.
        Switches to the 'New Booking' tab, reloads flights if necessary,
        sets the flight and class, clears the seat field, and updates availability/fare.
        """
        # Switch to New Booking tab (index 1)
        if hasattr(self, "_notebook"):
            self._notebook.select(1)

        # Look for flight in existing map; refresh if not found
        matching_key = next((k for k, fid in self._flight_map.items() if fid == flight_id), None)
        if not matching_key:
            self._reload_flight_options()
            matching_key = next((k for k, fid in self._flight_map.items() if fid == flight_id), None)

        if matching_key:
            self._flight_var.set(matching_key)

        if travel_class in ("Economy", "Business"):
            self._class_var.set(travel_class)

        # Clear seat so user picks a new seat, leaving passenger selection as is
        self._seat_var.set("")

        # Refresh availability & fare labels
        self._update_availability()

    def refresh(self):
        """
        Refresh booking list, dropdown options, and availability without wiping form input.
        """
        self._load_bookings()
        self._reload_flight_options()
        self._reload_passenger_options()
        if self._flight_var.get():
            self._update_availability()
        detail_ref = self._detail_ref.get().strip() if hasattr(self, "_detail_ref") else ""
        if detail_ref:
            booking = get_booking_by_reference(detail_ref)
            if booking:
                self._populate_detail(booking["booking_id"])

    def _update_availability(self):
        flight_label = self._flight_var.get()
        if not flight_label:
            return
        flight_id = self._flight_map[flight_label]
        cls = self._class_var.get()
        try:
            avail = get_seat_availability(flight_id, cls)
            booked = get_booked_seats(flight_id)
            self._avail_lbl.config(
                text=f"Available {cls} seats: {avail['available']} / {avail['capacity']}",
                foreground="green" if avail["available"] > 0 else "red",
            )
            self._booked_lbl.config(
                text=f"Already booked seats: {', '.join(booked) if booked else 'None'}"
            )
            # Update fare label
            from src.repositories.flight_repository import get_flight_by_id
            flight = get_flight_by_id(flight_id)
            if flight:
                fare = float(flight["base_fare"])
                if cls == "Business":
                    fare = round(fare * 2.5, 2)
                self._fare_lbl.config(
                    text=f"₹ {fare:,.2f}  ({cls} Class)  — SIMULATED SAMPLE FARE"
                )
        except Exception as e:
            self._avail_lbl.config(text=str(e), foreground="red")

    def _confirm_booking(self):
        flight_label = self._flight_var.get()
        pax_label    = self._pax_var.get()
        seat         = self._seat_var.get().strip().upper()
        cls          = self._class_var.get()

        if not flight_label:
            messagebox.showwarning("Input", "Please select a flight."); return
        if not pax_label:
            messagebox.showwarning("Input", "Please select a passenger."); return

        ok, msg = validate_seat_number(seat)
        if not ok:
            messagebox.showwarning("Seat Error", msg); return

        flight_id    = self._flight_map[flight_label]
        passenger_id = self._pax_map[pax_label]

        from src.repositories.flight_repository import get_flight_by_id
        flight = get_flight_by_id(flight_id)
        fare = float(flight["base_fare"])
        if cls == "Business":
            fare = round(fare * 2.5, 2)

        if not messagebox.askyesno("Confirm Booking",
                                    f"Book {cls} seat {seat} on {flight['flight_number']} "
                                    f"for ₹ {fare:,.2f}?\n\n"
                                    "⚠ This fare is SIMULATED SAMPLE DATA."):
            return
        try:
            result = create_booking(passenger_id, flight_id, seat, cls, fare)
            messagebox.showinfo(
                "Booking Confirmed! ✅",
                f"Booking Reference: {result['booking_reference']}\n"
                f"Ticket ID: {result['ticket_id']}\n"
                f"Seat: {seat} ({cls})\n"
                f"Fare: ₹ {fare:,.2f} (SIMULATED)\n\n"
                "Go to Bookings list to view full details.",
            )
            self._clear_create()
            self._load_bookings()
        except Exception as e:
            messagebox.showerror("Booking Failed", str(e))

    def _clear_create(self):
        self._flight_var.set("")
        self._pax_var.set("")
        self._seat_var.set("")
        self._class_var.set("Economy")
        self._avail_lbl.config(text="")
        self._booked_lbl.config(text="")
        self._fare_lbl.config(text="Select a flight to see fare.")

    # ---------------------------------------------------------------
    # Booking Detail tab
    # ---------------------------------------------------------------
    def _build_detail_tab(self):
        p = self._detail_tab

        sf = ttk.Frame(p)
        sf.pack(fill="x", pady=(0, 8))
        ttk.Label(sf, text="Booking Reference:").pack(side="left")
        self._detail_ref = tk.StringVar()
        ttk.Entry(sf, textvariable=self._detail_ref, width=18).pack(side="left", padx=6)
        ttk.Button(sf, text="Load", command=self._load_detail).pack(side="left")

        self._detail_info = ttk.LabelFrame(p, text="Booking Information", padding=10)
        self._detail_info.pack(fill="x", pady=(0, 12))
        self._detail_text = tk.Text(self._detail_info, height=5, state="disabled",
                                     relief="flat", bg="#f0f0f0", wrap="word")
        self._detail_text.pack(fill="x")

        ttk.Label(p, text="Ticket(s):", font=("Helvetica", 11, "bold")).pack(anchor="w")
        cols = ("ticket_id","flight_number","airline_name","origin_city","destination_city",
                "departure_datetime","seat_number","travel_class","ticket_fare","ticket_status")
        self._detail_tree = ttk.Treeview(p, columns=cols, show="headings", height=5)
        for c, h, w in zip(cols,("ID","Flight No","Airline","From","To","Departure",
                                  "Seat","Class","Fare (₹)","Status"),
                           (40,80,120,100,100,140,70,80,90,80)):
            self._detail_tree.heading(c, text=h)
            self._detail_tree.column(c, width=w, anchor="center")
        self._detail_tree.column("ticket_id", width=0, stretch=False)
        self._detail_tree.pack(fill="both", expand=True)

        ttk.Label(p, text="Status History:", font=("Helvetica", 11, "bold")).pack(anchor="w", pady=(10, 0))
        hcols = ("history_id","old_status","new_status","changed_at","remarks")
        self._hist_tree = ttk.Treeview(p, columns=hcols, show="headings", height=4)
        for c, h, w in zip(hcols,("ID","Old Status","New Status","Changed At","Remarks"),
                           (40,100,100,150,250)):
            self._hist_tree.heading(c, text=h)
            self._hist_tree.column(c, width=w, anchor="center")
        self._hist_tree.column("history_id", width=0, stretch=False)
        self._hist_tree.pack(fill="both", expand=True)

    def _populate_detail(self, booking_id: int):
        # Switch to detail tab (tab index 2)
        for child in self.winfo_children():
            if isinstance(child, ttk.Notebook):
                child.select(2)
                break

        booking = get_booking_by_reference.__doc__  # just a placeholder
        # Load booking info
        from src.repositories.booking_repository import get_all_bookings
        bookings = get_all_bookings()
        b = next((x for x in bookings if x["booking_id"] == booking_id), None)
        if b:
            info = (
                f"Reference:  {b['booking_reference']}\n"
                f"Passenger:  {b['passenger_name']}  |  {b['email']}\n"
                f"Booked On:  {b['booking_datetime']}\n"
                f"Total:      ₹ {float(b['total_amount']):,.2f}   |   Status: {b['booking_status']}"
            )
            self._detail_text.config(state="normal")
            self._detail_text.delete("1.0", "end")
            self._detail_text.insert("end", info)
            self._detail_text.config(state="disabled")
            self._detail_ref.set(b["booking_reference"])

        # Load tickets
        for r in self._detail_tree.get_children(): self._detail_tree.delete(r)
        for t in get_tickets_for_booking(booking_id):
            self._detail_tree.insert("", "end", values=(
                t["ticket_id"], t["flight_number"], t["airline_name"],
                t["origin_city"], t["destination_city"], str(t["departure_datetime"]),
                t["seat_number"], t["travel_class"],
                f"{float(t['ticket_fare']):,.2f}", t["ticket_status"],
            ))

        # Load history
        for r in self._hist_tree.get_children(): self._hist_tree.delete(r)
        for h in get_booking_status_history(booking_id):
            self._hist_tree.insert("", "end", values=(
                h["history_id"], h.get("old_status","—"),
                h["new_status"], str(h["changed_at"]), h.get("remarks",""),
            ))

    def _load_detail(self):
        ref = self._detail_ref.get().strip()
        if not ref:
            messagebox.showwarning("Input","Enter a booking reference."); return
        b = get_booking_by_reference(ref)
        if not b:
            messagebox.showinfo("Not Found", f"No booking for reference '{ref}'."); return
        self._populate_detail(b["booking_id"])


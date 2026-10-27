"""
flights.py
----------
Flight & Airline administration UI.
Tabs: Airlines | Airports | Aircraft | Flight Schedules
"""

import tkinter as tk
from tkinter import ttk, messagebox

from src.repositories.airline_repository  import get_all_airlines, add_airline, update_airline, delete_airline
from src.repositories.airport_repository  import get_all_airports, add_airport, update_airport, delete_airport
from src.repositories.flight_repository   import (
    get_all_aircraft, add_aircraft,
    get_all_flights, add_flight, update_flight_status,
)


class FlightsFrame(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent, padding=20)
        ttk.Label(
            self, text="Flight & Airline Administration",
            font=("Helvetica", 16, "bold"),
        ).pack(anchor="w", pady=(0, 12))

        nb = ttk.Notebook(self)
        nb.pack(fill="both", expand=True)

        self._airlines_tab  = _AirlinesTab(nb)
        self._airports_tab  = _AirportsTab(nb)
        self._aircraft_tab  = _AircraftTab(nb)
        self._schedules_tab = _SchedulesTab(nb)

        nb.add(self._airlines_tab,  text="✈  Airlines")
        nb.add(self._airports_tab,  text="🏢  Airports")
        nb.add(self._aircraft_tab,  text="🛩  Aircraft")
        nb.add(self._schedules_tab, text="📅  Schedules")


# ---------------------------------------------------------------------------
# Airlines sub-tab
# ---------------------------------------------------------------------------
class _AirlinesTab(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent, padding=14)
        self._sel_id = None
        self._build()
        self._load()

    def _build(self):
        form = ttk.LabelFrame(self, text="Airline Details", padding=10)
        form.pack(fill="x", pady=(0, 10))

        self._vars = {k: tk.StringVar() for k in ("name", "code", "email", "phone")}
        for i, (lbl, key) in enumerate([("Name *", "name"), ("Code *", "code"),
                                         ("Email *", "email"), ("Phone *", "phone")]):
            ttk.Label(form, text=lbl).grid(row=i//2, column=(i%2)*2, sticky="w", padx=6, pady=4)
            ttk.Entry(form, textvariable=self._vars[key], width=24).grid(
                row=i//2, column=(i%2)*2+1, sticky="ew", padx=6, pady=4)

        bf = ttk.Frame(form)
        bf.grid(row=2, column=0, columnspan=4, pady=8)
        ttk.Button(bf, text="Add",    command=self._add).pack(side="left", padx=4)
        ttk.Button(bf, text="Update", command=self._update).pack(side="left", padx=4)
        ttk.Button(bf, text="Delete", command=self._delete).pack(side="left", padx=4)
        ttk.Button(bf, text="Clear",  command=self._clear).pack(side="left", padx=4)

        cols = ("airline_id", "airline_name", "airline_code", "contact_email", "contact_phone")
        self._tree = ttk.Treeview(self, columns=cols, show="headings", height=10)
        for c, h, w in zip(cols, ("ID","Name","Code","Email","Phone"), (40,160,70,200,130)):
            self._tree.heading(c, text=h)
            self._tree.column(c, width=w, anchor="center")
        self._tree.column("airline_id", width=0, stretch=False)
        self._tree.pack(fill="both", expand=True)
        self._tree.bind("<<TreeviewSelect>>", self._on_select)

    def _load(self):
        for r in self._tree.get_children(): self._tree.delete(r)
        for a in get_all_airlines():
            self._tree.insert("", "end", values=(
                a["airline_id"], a["airline_name"], a["airline_code"],
                a["contact_email"], a["contact_phone"]))

    def _on_select(self, _):
        sel = self._tree.selection()
        if not sel: return
        v = self._tree.item(sel[0], "values")
        self._sel_id = int(v[0])
        for k, val in zip(("name","code","email","phone"), v[1:]):
            self._vars[k].set(val)

    def _add(self):
        try:
            add_airline(self._vars["name"].get(), self._vars["code"].get(),
                        self._vars["email"].get(), self._vars["phone"].get())
            self._clear(); self._load()
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def _update(self):
        if not self._sel_id:
            messagebox.showwarning("Select", "Select an airline first."); return
        try:
            update_airline(self._sel_id, self._vars["name"].get(), self._vars["code"].get(),
                           self._vars["email"].get(), self._vars["phone"].get())
            self._clear(); self._load()
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def _delete(self):
        if not self._sel_id:
            messagebox.showwarning("Select", "Select an airline first."); return
        if not messagebox.askyesno("Confirm", "Delete this airline?"): return
        try:
            delete_airline(self._sel_id); self._clear(); self._load()
        except Exception as e:
            messagebox.showerror("Cannot Delete", str(e))

    def _clear(self):
        for v in self._vars.values(): v.set("")
        self._sel_id = None


# ---------------------------------------------------------------------------
# Airports sub-tab
# ---------------------------------------------------------------------------
class _AirportsTab(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent, padding=14)
        self._sel_id = None
        self._build()
        self._load()

    def _build(self):
        form = ttk.LabelFrame(self, text="Airport Details", padding=10)
        form.pack(fill="x", pady=(0, 10))

        self._vars = {k: tk.StringVar() for k in ("code", "name", "city", "country")}
        self._vars["country"].set("India")
        for i, (lbl, key) in enumerate([("Code *","code"),("Name *","name"),
                                         ("City *","city"),("Country","country")]):
            ttk.Label(form, text=lbl).grid(row=i//2, column=(i%2)*2, sticky="w", padx=6, pady=4)
            ttk.Entry(form, textvariable=self._vars[key], width=24).grid(
                row=i//2, column=(i%2)*2+1, sticky="ew", padx=6, pady=4)

        bf = ttk.Frame(form)
        bf.grid(row=2, column=0, columnspan=4, pady=8)
        ttk.Button(bf, text="Add",    command=self._add).pack(side="left", padx=4)
        ttk.Button(bf, text="Update", command=self._update).pack(side="left", padx=4)
        ttk.Button(bf, text="Delete", command=self._delete).pack(side="left", padx=4)
        ttk.Button(bf, text="Clear",  command=self._clear).pack(side="left", padx=4)

        cols = ("airport_id","airport_code","airport_name","city","country")
        self._tree = ttk.Treeview(self, columns=cols, show="headings", height=10)
        for c, h, w in zip(cols,("ID","Code","Name","City","Country"),(40,70,200,120,100)):
            self._tree.heading(c, text=h); self._tree.column(c, width=w, anchor="center")
        self._tree.column("airport_id", width=0, stretch=False)
        self._tree.pack(fill="both", expand=True)
        self._tree.bind("<<TreeviewSelect>>", self._on_select)

    def _load(self):
        for r in self._tree.get_children(): self._tree.delete(r)
        for a in get_all_airports():
            self._tree.insert("", "end", values=(
                a["airport_id"],a["airport_code"],a["airport_name"],a["city"],a["country"]))

    def _on_select(self, _):
        sel = self._tree.selection()
        if not sel: return
        v = self._tree.item(sel[0], "values")
        self._sel_id = int(v[0])
        for k, val in zip(("code","name","city","country"), v[1:]):
            self._vars[k].set(val)

    def _add(self):
        try:
            add_airport(self._vars["code"].get(), self._vars["name"].get(),
                        self._vars["city"].get(), self._vars["country"].get() or "India")
            self._clear(); self._load()
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def _update(self):
        if not self._sel_id:
            messagebox.showwarning("Select","Select an airport first."); return
        try:
            update_airport(self._sel_id, self._vars["code"].get(), self._vars["name"].get(),
                           self._vars["city"].get(), self._vars["country"].get())
            self._clear(); self._load()
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def _delete(self):
        if not self._sel_id:
            messagebox.showwarning("Select","Select an airport first."); return
        if not messagebox.askyesno("Confirm","Delete this airport?"): return
        try:
            delete_airport(self._sel_id); self._clear(); self._load()
        except Exception as e:
            messagebox.showerror("Cannot Delete", str(e))

    def _clear(self):
        for v in self._vars.values(): v.set("")
        self._vars["country"].set("India")
        self._sel_id = None


# ---------------------------------------------------------------------------
# Aircraft sub-tab
# ---------------------------------------------------------------------------
class _AircraftTab(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent, padding=14)
        self._airline_map = {}
        self._build()
        self._load()

    def _build(self):
        form = ttk.LabelFrame(self, text="Aircraft Details", padding=10)
        form.pack(fill="x", pady=(0, 10))

        airlines = get_all_airlines()
        self._airline_map = {a["airline_name"]: a["airline_id"] for a in airlines}
        airline_names = list(self._airline_map.keys())

        self._vars = {k: tk.StringVar() for k in ("airline","model","reg","total","eco","biz")}

        fields = [("Airline *","airline"),("Model *","model"),("Reg. No *","reg"),
                  ("Total Seats *","total"),("Economy Seats *","eco"),("Business Seats *","biz")]
        for i, (lbl, key) in enumerate(fields):
            ttk.Label(form, text=lbl).grid(row=i//3, column=(i%3)*2, sticky="w", padx=6, pady=4)
            if key == "airline":
                cb = ttk.Combobox(form, textvariable=self._vars[key],
                                  values=airline_names, width=18, state="readonly")
                cb.grid(row=i//3, column=(i%3)*2+1, sticky="ew", padx=6, pady=4)
            else:
                ttk.Entry(form, textvariable=self._vars[key], width=18).grid(
                    row=i//3, column=(i%3)*2+1, sticky="ew", padx=6, pady=4)

        ttk.Button(form, text="Add Aircraft", command=self._add).grid(
            row=2, column=0, columnspan=6, pady=8)

        cols = ("aircraft_id","airline_name","aircraft_model","registration_number",
                "total_seats","economy_seats","business_seats")
        self._tree = ttk.Treeview(self, columns=cols, show="headings", height=10)
        for c, h, w in zip(cols,("ID","Airline","Model","Reg. No","Total","Economy","Business"),
                           (40,140,120,100,60,70,80)):
            self._tree.heading(c, text=h); self._tree.column(c, width=w, anchor="center")
        self._tree.column("aircraft_id", width=0, stretch=False)
        self._tree.pack(fill="both", expand=True)

    def _load(self):
        for r in self._tree.get_children(): self._tree.delete(r)
        for a in get_all_aircraft():
            self._tree.insert("", "end", values=(
                a["aircraft_id"], a["airline_name"], a["aircraft_model"],
                a["registration_number"], a["total_seats"],
                a["economy_seats"], a["business_seats"]))

    def _add(self):
        airline_name = self._vars["airline"].get()
        if not airline_name:
            messagebox.showwarning("Input","Select an airline."); return
        airline_id = self._airline_map[airline_name]
        try:
            total = int(self._vars["total"].get())
            eco   = int(self._vars["eco"].get())
            biz   = int(self._vars["biz"].get())
        except ValueError:
            messagebox.showwarning("Input","Seat counts must be integers."); return
        try:
            add_aircraft(airline_id, self._vars["model"].get(),
                         self._vars["reg"].get(), total, eco, biz)
            self._load()
        except Exception as e:
            messagebox.showerror("Error", str(e))


# ---------------------------------------------------------------------------
# Flight Schedules sub-tab
# ---------------------------------------------------------------------------
class _SchedulesTab(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent, padding=14)
        self._sel_id = None
        self._airline_map = {}
        self._airport_map = {}
        self._aircraft_map = {}
        self._build()
        self._load()

    def _build(self):
        form = ttk.LabelFrame(self, text="Schedule Details (SAMPLE DATA)", padding=10)
        form.pack(fill="x", pady=(0, 10))

        airlines = get_all_airlines()
        airports = get_all_airports()
        aircraft = get_all_aircraft()
        self._airline_map = {a["airline_name"]: a["airline_id"] for a in airlines}
        self._airport_map = {f"{a['city']} ({a['airport_code']})": a["airport_id"] for a in airports}
        self._aircraft_map = {f"{a['aircraft_model']} ({a['registration_number']})": a["aircraft_id"]
                              for a in aircraft}

        self._vars = {k: tk.StringVar() for k in
                      ("airline","aircraft","origin","dest","flight_no","dep","arr","fare","status")}
        self._vars["status"].set("Scheduled")

        widgets = [
            ("Airline *",   "airline",   list(self._airline_map.keys()),  "combo"),
            ("Aircraft *",  "aircraft",  list(self._aircraft_map.keys()), "combo"),
            ("Origin *",    "origin",    list(self._airport_map.keys()),  "combo"),
            ("Destination *","dest",     list(self._airport_map.keys()),  "combo"),
            ("Flight No *", "flight_no", None, "entry"),
            ("Departure *\n(YYYY-MM-DD HH:MM:SS)", "dep", None, "entry"),
            ("Arrival *\n(YYYY-MM-DD HH:MM:SS)", "arr", None, "entry"),
            ("Base Fare *", "fare",      None, "entry"),
            ("Status",      "status",    ["Scheduled","Boarding","Departed","Arrived","Cancelled","Delayed"], "combo"),
        ]
        for i, (lbl, key, values, wtype) in enumerate(widgets):
            ttk.Label(form, text=lbl, wraplength=140).grid(row=i//3, column=(i%3)*2, sticky="w", padx=4, pady=3)
            if wtype == "combo":
                w = ttk.Combobox(form, textvariable=self._vars[key], values=values, width=22, state="readonly")
            else:
                w = ttk.Entry(form, textvariable=self._vars[key], width=24)
            w.grid(row=i//3, column=(i%3)*2+1, sticky="ew", padx=4, pady=3)

        bf = ttk.Frame(form)
        bf.grid(row=4, column=0, columnspan=6, pady=8)
        ttk.Button(bf, text="Add Schedule", command=self._add).pack(side="left", padx=4)
        ttk.Button(bf, text="Update Status", command=self._update_status).pack(side="left", padx=4)
        ttk.Button(bf, text="Clear", command=self._clear).pack(side="left", padx=4)

        cols = ("flight_id","flight_number","airline_name","origin_city","destination_city",
                "departure_datetime","arrival_datetime","base_fare","flight_status")
        self._tree = ttk.Treeview(self, columns=cols, show="headings", height=10)
        for c, h, w in zip(cols,("ID","Flight No","Airline","From","To","Departure","Arrival","Fare","Status"),
                           (40,80,130,100,100,140,140,80,100)):
            self._tree.heading(c, text=h); self._tree.column(c, width=w, anchor="center")
        self._tree.column("flight_id", width=0, stretch=False)
        self._tree.pack(fill="both", expand=True)
        self._tree.bind("<<TreeviewSelect>>", self._on_select)

    def _load(self):
        for r in self._tree.get_children(): self._tree.delete(r)
        for f in get_all_flights():
            self._tree.insert("", "end", values=(
                f["flight_id"], f["flight_number"], f["airline_name"],
                f["origin_city"], f["destination_city"],
                str(f["departure_datetime"]), str(f["arrival_datetime"]),
                f["base_fare"], f["flight_status"]))

    def _on_select(self, _):
        sel = self._tree.selection()
        if not sel: return
        v = self._tree.item(sel[0], "values")
        self._sel_id = int(v[0])
        self._vars["status"].set(v[8])

    def _add(self):
        try:
            airline_id  = self._airline_map[self._vars["airline"].get()]
            aircraft_id = self._aircraft_map[self._vars["aircraft"].get()]
            origin_id   = self._airport_map[self._vars["origin"].get()]
            dest_id     = self._airport_map[self._vars["dest"].get()]
            if origin_id == dest_id:
                messagebox.showwarning("Input","Origin and destination must differ."); return
            add_flight(airline_id, aircraft_id, origin_id, dest_id,
                       self._vars["flight_no"].get(), self._vars["dep"].get(),
                       self._vars["arr"].get(), float(self._vars["fare"].get()),
                       self._vars["status"].get())
            self._clear(); self._load()
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def _update_status(self):
        if not self._sel_id:
            messagebox.showwarning("Select","Select a flight first."); return
        try:
            update_flight_status(self._sel_id, self._vars["status"].get())
            self._load()
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def _clear(self):
        for v in self._vars.values(): v.set("")
        self._vars["status"].set("Scheduled")
        self._sel_id = None


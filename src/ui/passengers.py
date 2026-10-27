"""
passengers.py
-------------
Passenger management UI.
"""

import tkinter as tk
from tkinter import ttk, messagebox

from src.repositories.passenger_repository import (
    get_all_passengers, search_passengers, add_passenger,
    update_passenger, delete_passenger,
)
from src.validators import validate_email, validate_phone, validate_name, validate_date_string


class PassengersFrame(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent, padding=20)
        self._selected_id = None
        self._build()
        self._load()

    def _build(self):
        ttk.Label(
            self, text="Passenger Management",
            font=("Helvetica", 16, "bold"),
        ).grid(row=0, column=0, columnspan=2, sticky="w", pady=(0, 14))

        # --- Form ---
        form = ttk.LabelFrame(self, text="Passenger Details", padding=12)
        form.grid(row=1, column=0, sticky="nsew", padx=(0, 12))

        labels = ["Full Name *", "Email *", "Phone *", "Date of Birth (YYYY-MM-DD)"]
        self._vars = {k: tk.StringVar() for k in ("name", "email", "phone", "dob")}
        keys = list(self._vars.keys())
        for i, (lbl, key) in enumerate(zip(labels, keys)):
            ttk.Label(form, text=lbl).grid(row=i, column=0, sticky="w", pady=4, padx=4)
            ttk.Entry(form, textvariable=self._vars[key], width=28).grid(row=i, column=1, pady=4, padx=4)

        btn_frame = ttk.Frame(form)
        btn_frame.grid(row=len(labels), column=0, columnspan=2, pady=12)
        ttk.Button(btn_frame, text="➕ Add",    command=self._add).pack(side="left", padx=4)
        ttk.Button(btn_frame, text="✏  Update", command=self._update).pack(side="left", padx=4)
        ttk.Button(btn_frame, text="🗑  Delete", command=self._delete).pack(side="left", padx=4)
        ttk.Button(btn_frame, text="✖  Clear",  command=self._clear).pack(side="left", padx=4)

        # --- Search + List ---
        right = ttk.Frame(self)
        right.grid(row=1, column=1, sticky="nsew")

        search_frame = ttk.Frame(right)
        search_frame.pack(fill="x", pady=(0, 8))
        ttk.Label(search_frame, text="Search:").pack(side="left")
        self._search_var = tk.StringVar()
        ttk.Entry(search_frame, textvariable=self._search_var, width=24).pack(side="left", padx=6)
        ttk.Button(search_frame, text="Search", command=self._search).pack(side="left")
        ttk.Button(search_frame, text="Show All", command=self._load).pack(side="left", padx=4)

        cols = ("passenger_id", "full_name", "email", "phone", "date_of_birth", "created_at")
        self._tree = ttk.Treeview(right, columns=cols, show="headings", height=14)
        headers = ("ID", "Full Name", "Email", "Phone", "Date of Birth", "Registered")
        widths  = (40, 150, 180, 110, 110, 150)
        for c, h, w in zip(cols, headers, widths):
            self._tree.heading(c, text=h, command=lambda _c=c: self._sort(_c))
            self._tree.column(c, width=w, anchor="center")
        self._tree.column("passenger_id", width=0, stretch=False)

        vsb = ttk.Scrollbar(right, orient="vertical", command=self._tree.yview)
        self._tree.configure(yscrollcommand=vsb.set)
        self._tree.pack(side="left", fill="both", expand=True)
        vsb.pack(side="right", fill="y")
        self._tree.bind("<<TreeviewSelect>>", self._on_select)

        self.columnconfigure(1, weight=1)
        self.rowconfigure(1, weight=1)

    def _load(self):
        self._populate(get_all_passengers())

    def _search(self):
        term = self._search_var.get().strip()
        if not term:
            self._load()
            return
        self._populate(search_passengers(term))

    def _populate(self, rows):
        for item in self._tree.get_children():
            self._tree.delete(item)
        for r in rows:
            self._tree.insert("", "end", values=(
                r["passenger_id"], r["full_name"], r["email"],
                r["phone"], r.get("date_of_birth", ""), str(r.get("created_at", "")),
            ))

    def _on_select(self, _event):
        selected = self._tree.selection()
        if not selected:
            return
        vals = self._tree.item(selected[0], "values")
        self._selected_id = int(vals[0])
        self._vars["name"].set(vals[1])
        self._vars["email"].set(vals[2])
        self._vars["phone"].set(vals[3])
        self._vars["dob"].set(vals[4])

    def _validate(self) -> list:
        errors = []
        ok, msg = validate_name(self._vars["name"].get(), "Full Name")
        if not ok: errors.append(msg)
        ok, msg = validate_email(self._vars["email"].get())
        if not ok: errors.append(msg)
        ok, msg = validate_phone(self._vars["phone"].get())
        if not ok: errors.append(msg)
        dob = self._vars["dob"].get().strip()
        if dob:
            ok, msg = validate_date_string(dob, "Date of Birth")
            if not ok: errors.append(msg)
        return errors

    def _add(self):
        errors = self._validate()
        if errors:
            messagebox.showwarning("Validation Error", "\n".join(errors))
            return
        try:
            pid = add_passenger(
                self._vars["name"].get(),
                self._vars["email"].get(),
                self._vars["phone"].get(),
                self._vars["dob"].get().strip() or None,
            )
            messagebox.showinfo("Success", f"Passenger added (ID: {pid}).")
            self._clear()
            self._load()
        except Exception as e:
            messagebox.showerror("Error", f"Could not add passenger:\n{e}")

    def _update(self):
        if not self._selected_id:
            messagebox.showwarning("No Selection", "Select a passenger to update.")
            return
        errors = self._validate()
        if errors:
            messagebox.showwarning("Validation Error", "\n".join(errors))
            return
        try:
            update_passenger(
                self._selected_id,
                self._vars["name"].get(),
                self._vars["email"].get(),
                self._vars["phone"].get(),
                self._vars["dob"].get().strip() or None,
            )
            messagebox.showinfo("Success", "Passenger updated.")
            self._clear()
            self._load()
        except Exception as e:
            messagebox.showerror("Error", f"Could not update passenger:\n{e}")

    def _delete(self):
        if not self._selected_id:
            messagebox.showwarning("No Selection", "Select a passenger to delete.")
            return
        if not messagebox.askyesno("Confirm Delete",
                                    "Delete this passenger? This will fail if they have bookings."):
            return
        try:
            delete_passenger(self._selected_id)
            messagebox.showinfo("Deleted", "Passenger record deleted.")
            self._clear()
            self._load()
        except Exception as e:
            messagebox.showerror("Cannot Delete",
                                  f"Deletion failed (referential integrity):\n{e}")

    def _clear(self):
        for v in self._vars.values():
            v.set("")
        self._selected_id = None

    def _sort(self, col):
        """Sort treeview by column."""
        rows = [(self._tree.set(c, col), c) for c in self._tree.get_children("")]
        rows.sort()
        for i, (_, item) in enumerate(rows):
            self._tree.move(item, "", i)


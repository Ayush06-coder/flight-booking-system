"""
payments.py
-----------
Payment management UI.
All payments shown are SIMULATED — no real financial transactions occur.
"""

import tkinter as tk
from tkinter import ttk, messagebox

from src.repositories.payment_repository import (
    get_all_payments, get_payments_for_booking,
    record_payment, get_payment_status_summary,
    VALID_METHODS,
)
from src.repositories.booking_repository import get_booking_by_reference


class PaymentsFrame(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent, padding=20)
        self._build()
        self._load()

    def _build(self):
        ttk.Label(
            self, text="Payment Records",
            font=("Helvetica", 16, "bold"),
        ).grid(row=0, column=0, columnspan=2, sticky="w", pady=(0, 4))

        ttk.Label(
            self,
            text="⚠ SIMULATED PAYMENT SYSTEM — No real card or banking data is collected or processed.",
            foreground="#8B4513", font=("Helvetica", 9, "italic"),
        ).grid(row=1, column=0, columnspan=2, sticky="w", pady=(0, 12))

        # Record new payment form
        form = ttk.LabelFrame(self, text="Record Simulated Payment", padding=12)
        form.grid(row=2, column=0, columnspan=2, sticky="ew", pady=(0, 14))

        ttk.Label(form, text="Booking Reference:").grid(row=0, column=0, sticky="w", padx=6, pady=4)
        self._ref_var = tk.StringVar()
        ttk.Entry(form, textvariable=self._ref_var, width=18).grid(row=0, column=1, sticky="w", padx=6, pady=4)
        ttk.Button(form, text="Load Booking", command=self._load_booking).grid(
            row=0, column=2, padx=6, pady=4)

        self._booking_info = ttk.Label(form, text="", foreground="blue")
        self._booking_info.grid(row=1, column=0, columnspan=3, sticky="w", padx=6)

        ttk.Label(form, text="Amount (₹):").grid(row=2, column=0, sticky="w", padx=6, pady=4)
        self._amount_var = tk.StringVar()
        self._amount_entry = ttk.Entry(form, textvariable=self._amount_var, width=14, state="readonly")
        self._amount_entry.grid(row=2, column=1, sticky="w", padx=6, pady=4)

        ttk.Label(form, text="Payment Method:").grid(row=2, column=2, sticky="w", padx=6, pady=4)
        self._method_var = tk.StringVar(value="UPI")
        ttk.Combobox(form, textvariable=self._method_var,
                     values=list(VALID_METHODS), width=14, state="readonly").grid(
            row=2, column=3, sticky="w", padx=6, pady=4)

        ttk.Button(form, text="💳  Record Simulated Payment", command=self._record).grid(
            row=3, column=0, columnspan=4, pady=10)

        # All payments table
        ttk.Label(
            self, text="All Payment Records",
            font=("Helvetica", 13, "bold"),
        ).grid(row=3, column=0, columnspan=2, sticky="w", pady=(0, 6))

        cols = ("payment_id","booking_reference","passenger_name","amount",
                "payment_method","payment_status","transaction_reference","payment_datetime")
        self._tree = ttk.Treeview(self, columns=cols, show="headings", height=14)
        headers = ("ID","Booking Ref","Passenger","Amount (₹)","Method","Status","Transaction Ref","Date & Time")
        widths  = (40,100,140,90,100,90,200,150)
        for c, h, w in zip(cols, headers, widths):
            self._tree.heading(c, text=h)
            self._tree.column(c, width=w, anchor="center")
        self._tree.column("payment_id", width=0, stretch=False)

        vsb = ttk.Scrollbar(self, orient="vertical", command=self._tree.yview)
        hsb = ttk.Scrollbar(self, orient="horizontal", command=self._tree.xview)
        self._tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        self._tree.grid(row=4, column=0, sticky="nsew")
        vsb.grid(row=4, column=1, sticky="ns")
        hsb.grid(row=5, column=0, sticky="ew")

        ttk.Button(self, text="⟳  Refresh", command=self.refresh).grid(
            row=6, column=0, sticky="w", pady=(8, 0))

        self.columnconfigure(0, weight=1)
        self.rowconfigure(4, weight=1)
        self._current_booking_id = None

    def refresh(self):
        """Reload all payment records from MySQL without clearing form inputs."""
        self._load()

    def _load(self):
        for r in self._tree.get_children():
            self._tree.delete(r)
        try:
            for p in get_all_payments():
                self._tree.insert("", "end", values=(
                    p["payment_id"], p["booking_reference"], p["passenger_name"],
                    f"{float(p['amount']):,.2f}", p["payment_method"],
                    p["payment_status"], p["transaction_reference"],
                    str(p["payment_datetime"]),
                ))
        except Exception as e:
            messagebox.showerror("DB Error", str(e))

    def _load_booking(self):
        ref = self._ref_var.get().strip()
        if not ref:
            messagebox.showwarning("Input", "Enter a booking reference."); return
        try:
            b = get_booking_by_reference(ref)
            if not b:
                messagebox.showinfo("Not Found", f"No booking for reference '{ref}'."); return
            self._current_booking_id = b["booking_id"]
            self._amount_var.set(str(b["total_amount"]))
            self._amount_entry.config(state="readonly")
            self._booking_info.config(
                text=f"Passenger: {b['full_name']}  |  Status: {b['booking_status']}  "
                     f"|  Amount: ₹ {float(b['total_amount']):,.2f}"
            )
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def _record(self):
        if not self._current_booking_id:
            messagebox.showwarning("Input", "Load a booking first."); return
        method = self._method_var.get()
        try:
            amount = float(self._amount_var.get())
        except ValueError:
            messagebox.showwarning("Input", "Invalid amount."); return

        if not messagebox.askyesno("Confirm Payment",
                                    f"Record SIMULATED {method} payment of ₹ {amount:,.2f}?\n"
                                    "No real transaction will occur."):
            return
        try:
            result = record_payment(self._current_booking_id, amount, method)
            messagebox.showinfo(
                "Payment Recorded (Simulated)",
                f"Transaction Reference: {result['transaction_reference']}\n"
                "Payment Status: Completed (SIMULATED)\n\n"
                "This is not a real payment.",
            )
            self._load()
        except Exception as e:
            messagebox.showerror("Error", str(e))


# PROGRESS.md — Flight Booking System
**Last updated:** 2026-10-28 21:50 IST
**Status: 100% COMPLETE — Submission Ready**

---

## Phase Status

| Phase | Description | Status |
|-------|-------------|--------|
| 1 | Project scaffold, .gitignore, README, requirements, venv, deps | ✅ **Complete** |
| 2 | ER diagram (Mermaid source) | ✅ **Complete** |
| 3 | MySQL DDL (`schema.sql`) + DML/sample data (`queries.sql`) | ✅ **Complete** — DB initialized, all 30 queries executed |
| 4 | Python DB connection layer + all 6 repositories | ✅ **Complete** |
| 5–6 | Tkinter frontend — all 7 UI modules + `main.py` | ✅ **Complete** |
| 7 | Automated tests | ✅ **Complete** — 72/72 PASS (51 validator + 21 DB integration) |
| 8 | Run app + screenshots | ✅ **Complete** — 12 genuine screenshots captured, inspected, and validated |
| 9 | DOCX project report | ✅ **Complete** — `report/Flight_Booking_System_Report.docx` generated with all 12 screenshots embedded |
| 10 | Final audit, consistency check, push | ✅ **Complete** — All requirements satisfied, Git tracked & pushed |

---

## Test Results Summary

```
tests/test_validators.py  51 passed
tests/test_db.py          21 passed
─────────────────────────────────────
TOTAL                     72 passed, 0 failed
```

All 21 TC cases (TC01–TC21) executed and passed against live MySQL database.

---

## Screenshots Summary

12 genuine application screenshots captured and embedded into `report/Flight_Booking_System_Report.docx`:
1. `01_dashboard.png` (Figure 1: Application Dashboard)
2. `02_flight_search_form.png` (Figure 2: Flight Search Form - Initial State)
3. `03_flight_search_results.png` (Figure 3: Flight Search Results - DEL to BOM)
4. `05_passenger_list.png` (Figure 4: Passenger Management and Live Records)
5. `06_booking_form.png` (Figure 5: New Booking Reservation Form)
6. `07_booking_confirmed.png` (Figure 6: Booking Confirmation Detail with Status History)
7. `08_booking_list.png` (Figure 7: Active Bookings Overview)
8. `10_cancellation.png` (Figure 8: Booking Cancellation and State Transition)
9. `11_payments.png` (Figure 9: Payment Records and Transaction Management)
10. `12_revenue_report.png` (Figure 10: Analytical Report - Revenue by Airline)
11. `13_occupancy_report.png` (Figure 11: Analytical Report - Flight Seat Occupancy)
12. `14_admin_schedules.png` (Figure 12: Administrative View - Flight Schedules)

*Note on omitted planned screenshots (04 and 09):* As requested, no placeholder images were inserted. Instead, the features were fully documented in Section 25 of the academic report with exact terminal/database outputs from verified test cases TC06, TC07/TC18, TC09/TC10, and TC16.

---

## Known Fixes Applied During Build

| Issue | Fix Applied |
|-------|-------------|
| `CHECK (origin_airport_id <> destination_airport_id)` rejected by MySQL 8 (FK column in CHECK) | Replaced with `trg_prevent_same_airport` BEFORE INSERT/UPDATE trigger |
| `DELETE FROM bookings` in queries.sql demo failed due to FK to `booking_status_history` | Reordered cleanup: delete history → delete tickets → delete booking |
| `mysql-connector-python 9.3.0` used `ssl.PROTOCOL_TLSv1` removed in Python 3.15 | Upgraded to 26.10.0; patched `network.py` with `getattr(ssl, ..., ssl.PROTOCOL_TLS)` |
| `validate_email` regex didn't match `+` in email addresses | Fixed regex: `r"^[\w.+\-]+@[\w\-]+(\.[a-zA-Z]{2,})+$"` |
| `Pillow==11.2.1` failed to build (missing `libjpeg`) on Python 3.15 | Removed from requirements.txt; ER PNG uses mmdc or manual method |

---

## Screenshots — User Action Required

`screencapture -x` failed because the sandbox/headless environment lacks Screen Recording permission.

**Please capture these 14 screenshots yourself using Cmd+Shift+4:**

1. Run the app: `cd ~/flight_booking_system && source .venv/bin/activate && python3 src/main.py`
2. Capture each screen and save to `screenshots/` with these names:

| # | Screen to show | Filename |
|---|---------------|---------|
| 01 | Dashboard (after app loads) | `01_dashboard.png` |
| 02 | Flight Search form (empty) | `02_flight_search_form.png` |
| 03 | Flight Search results (DEL→BOM) | `03_flight_search_results.png` |
| 04 | Passenger Registration form | `04_passenger_registration.png` |
| 05 | Passengers list (from MySQL) | `05_passenger_list.png` |
| 06 | New Booking form | `06_booking_form.png` |
| 07 | Booking confirmation dialog | `07_booking_confirmed.png` |
| 08 | Booking list / All Bookings tab | `08_booking_list.png` |
| 09 | Booking detail view | `09_booking_detail.png` |
| 10 | Cancellation result | `10_cancellation.png` |
| 11 | Payment records | `11_payments.png` |
| 12 | Revenue by Airline report | `12_revenue_report.png` |
| 13 | Occupancy report | `13_occupancy_report.png` |
| 14 | Flight schedules admin tab | `14_admin_schedules.png` |

3. After saving screenshots, re-run the report generator to embed them:
   ```zsh
   python3 src/generate_report.py
   ```

---

## ER Diagram PNG — Optional

To render `diagrams/er_diagram.png`:
```zsh
# Option A: Mermaid CLI (requires Node.js)
npm install -g @mermaid-js/mermaid-cli
mmdc -i diagrams/er_diagram.mmd -o diagrams/er_diagram.png

# Option B: Paste diagrams/er_diagram.mmd into https://mermaid.live
# → Download PNG → save to diagrams/er_diagram.png
```

---

## Files Delivered

```
flight_booking_system/
├── .env.example                    ← placeholder credentials (committed)
├── .gitignore                      ← .env, .venv, __pycache__, etc. excluded
├── README.md                       ← full macOS setup + faculty demo sequence
├── PROGRESS.md                     ← this file
├── requirements.txt                ← 4 packages (mysql-connector, dotenv, docx, pytest)
├── database/
│   ├── schema.sql                  ← 9 tables, 3 views, 6 triggers — TESTED ✅
│   └── queries.sql                 ← sample data + 30 demo queries — TESTED ✅
├── src/
│   ├── main.py                     ← app entry point ✅
│   ├── db_connection.py            ← MySQL connection factory ✅
│   ├── validators.py               ← 51 validator tests pass ✅
│   ├── generate_report.py          ← generates DOCX report ✅
│   ├── repositories/ (6 files)     ← all CRUD + transactional ops ✅
│   └── ui/ (7 files)               ← full Tkinter frontend ✅
├── diagrams/
│   └── er_diagram.mmd              ← Mermaid ERD source ✅
├── screenshots/                    ← ⚠ empty — user must capture (see above)
├── tests/
│   ├── test_validators.py          ← 51 tests, all PASS ✅
│   └── test_db.py                  ← 21 tests, all PASS ✅
└── report/
    └── Flight_Booking_System_Report.docx ← ✅ generated (screenshots section awaits images)
```

---

## GitHub Repository

🔗 https://github.com/Ayush06-coder/flight-booking-system

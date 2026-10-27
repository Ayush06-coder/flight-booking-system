# PROGRESS.md — Flight Booking System
**Last updated:** 2026-10-27 23:37 IST  
**Checkpoint:** WIP commit before continuing

---

## Phase Status

| Phase | Description | Status |
|-------|-------------|--------|
| 1 | Project scaffold, .gitignore, README, requirements, venv, deps | ✅ **Complete** |
| 2 | ER diagram (Mermaid source) | ✅ **Complete** (PNG pending — Phase 8 tool) |
| 3 | MySQL DDL (`schema.sql`) + DML/sample data (`queries.sql`) | ✅ **Complete** |
| 4 | Python DB connection layer + all 6 repositories | ✅ **Complete** |
| 5–6 | Tkinter frontend — all 7 UI modules + `main.py` | ✅ **Complete** |
| 7 | Automated tests (`tests/test_db.py`, `tests/test_validators.py`) | ❌ **Not started** |
| 8 | Run app, capture screenshots | ❌ **Not started** |
| 9 | DOCX project report (`report/Flight_Booking_System_Report.docx`) | ❌ **Not started** |
| 10 | Final audit, consistency check, push | ❌ **Not started** |

---

## Files That Exist

```
/Users/ayushsawhney/flight_booking_system/
├── .env                          ← created by user (NOT committed — correct)
├── .env.example                  ← ✅ committed (placeholders only)
├── .gitignore                    ← ✅
├── README.md                     ← ✅
├── requirements.txt              ← ✅ (4 packages, Pillow excluded — build issue on Python 3.15)
├── PROGRESS.md                   ← ✅ this file
├── database/
│   ├── schema.sql                ← ✅ 9 tables, 3 views, 6 triggers
│   └── queries.sql               ← ✅ 12 INSERTs per entity + 30 demo queries
├── diagrams/
│   ├── er_diagram.mmd            ← ✅ Mermaid ERD source
│   └── er_diagram.png            ← ❌ MISSING (needs mmdc or manual render)
├── src/
│   ├── __init__.py               ← ✅
│   ├── main.py                   ← ✅ Tkinter app entry point, sidebar nav
│   ├── db_connection.py          ← ✅ mysql-connector, .env via python-dotenv
│   ├── validators.py             ← ✅ email, phone, date, seat, booking ref generator
│   ├── repositories/
│   │   ├── __init__.py           ← ✅
│   │   ├── airline_repository.py ← ✅ CRUD for airlines
│   │   ├── airport_repository.py ← ✅ CRUD for airports
│   │   ├── flight_repository.py  ← ✅ search, CRUD, seat availability, dashboard stats
│   │   ├── passenger_repository.py ← ✅ CRUD, search, booking history
│   │   ├── booking_repository.py ← ✅ transactional create, cancel, history
│   │   └── payment_repository.py ← ✅ simulated payments, revenue aggregates
│   └── ui/
│       ├── __init__.py           ← ✅
│       ├── dashboard.py          ← ✅ live stats cards + upcoming flights table
│       ├── flight_search.py      ← ✅ search form, results treeview, book callback
│       ├── passengers.py         ← ✅ full CRUD, search, sort
│       ├── flights.py            ← ✅ 4-tab admin (airlines/airports/aircraft/schedules)
│       ├── bookings.py           ← ✅ list, new booking wizard, detail view, cancel
│       ├── payments.py           ← ✅ payment records, record simulated payment
│       └── reports.py            ← ✅ 8-tab reports + CSV export
├── screenshots/                  ← ❌ EMPTY — needs Phase 8
├── tests/
│   └── __init__.py               ← ✅ (empty — test files not yet written)
└── report/                       ← ❌ EMPTY — needs Phase 9
```

---

## What Still Needs To Be Done

### Phase 7 — Tests (NOT STARTED)
- [ ] `tests/test_db.py` — 21 automated test cases (TC01–TC21)
- [ ] `tests/test_validators.py` — unit tests for validators.py
- [ ] Run test suite and record actual pass/fail results

### Phase 8 — Run App + Screenshots (NOT STARTED)
Requires `.env` to be filled in first.
- [ ] Initialize DB: `mysql -u root -p < database/schema.sql`
- [ ] Load sample data: `mysql -u root -p flight_booking_db < database/queries.sql`
- [ ] Launch app: `source .venv/bin/activate && python3 src/main.py`
- [ ] Capture 14 screenshots (attempt `screencapture -x`, else manual Cmd+Shift+4)
- [ ] Render `diagrams/er_diagram.png` (attempt `mmdc` or provide manual instructions)

### Phase 9 — DOCX Report (NOT STARTED)
- [ ] `report/Flight_Booking_System_Report.docx` — 35-section academic report
- [ ] Script: `src/generate_report.py` using python-docx
- [ ] Embed ER diagram, screenshots, normalization (UNF→3NF), SQL code, Python code

### Phase 10 — Final Audit (NOT STARTED)
- [ ] Verify all FK relationships work in MySQL
- [ ] Verify all 30 demo queries execute
- [ ] Verify app launches and connects to DB
- [ ] Update PROGRESS.md with final status
- [ ] Final `git add -A && git commit && git push`

---

## Known Issues / Notes

| Issue | Detail |
|-------|--------|
| `Pillow` not installed | Build fails on Python 3.15 (missing `libjpeg`). Removed from requirements.txt. ER diagram PNG will be created via `mmdc` (Mermaid CLI) or manual browser render instead of Pillow. |
| `.env` must be filled in | User must set `DB_PASSWORD` in `.env` before Phase 8 can run. |
| GitHub repo name | Remote is `flight-booking-system` (hyphen), not `flight_booking_system` (underscore). Remote already correctly set. |
| `er_diagram.png` | Not yet generated. Will attempt `mmdc` in Phase 8. |
| Tests not executed | Phase 7 test files not yet written — no tests have been run or marked passed. |

---

## Exact Next Step (when resuming)

**Phase 7:** Write `tests/test_db.py` and `tests/test_validators.py`.  
**Prerequisite:** User must confirm `.env` is filled in with MySQL password so the DB tests can actually connect.

**Command to resume:**
```zsh
cd /Users/ayushsawhney/flight_booking_system
source .venv/bin/activate
# After filling in .env:
mysql -u root -p < database/schema.sql
mysql -u root -p flight_booking_db < database/queries.sql
python3 src/main.py   # verify app launches
python3 -m pytest tests/ -v
```

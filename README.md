# ✈️ Flight Booking System

> **Academic DBMS Project Based Learning (PBL)**
> B.Tech Computer Science — MySQL + Python Desktop Application

A complete, functional flight booking desktop application built with **MySQL 8**, **Python 3**, and **Tkinter**. Designed as a college PBL submission demonstrating relational database design, normalization (UNF → 3NF), SQL (DDL & DML), and Python–MySQL connectivity.

> **Disclaimer:** All flight schedules, prices, passenger data, and payment transactions in this project are **simulated sample data** created for academic demonstration purposes. This is not a real airline booking system.

---

## 📋 Features

- **Dashboard** — Live database-backed summary cards (airlines, flights, passengers, bookings, revenue)
- **Flight Search** — Search by origin, destination, date, travel class with real SQL queries
- **Passenger Management** — Register, search, update, and delete passenger profiles
- **Flight & Airline Admin** — Manage airlines, airports, aircraft, and flight schedules
- **Booking Management** — Full booking workflow with unique reference generation, seat allocation, and cancellation
- **Payment Management** — Simulated payment records with transaction references
- **Reports** — Revenue, occupancy, booking history, and status reports

---

## 🛠️ Technology Stack

| Component | Technology |
|-----------|-----------|
| Database | MySQL 8.x (via Homebrew) |
| Language | Python 3.15 |
| DB Connector | mysql-connector-python |
| Frontend | Tkinter with ttk widgets |
| Data Display | ttk.Treeview |
| ER Diagram | Mermaid ERD |
| Report | python-docx (DOCX) |
| Version Control | Git + GitHub |

---

## 🗄️ Database Architecture

**Database:** `flight_booking_db` | **Tables:** 9

```
airlines ──< aircraft ──< flight_schedules
airports >── flight_schedules (origin & destination)
passengers ──< bookings ──< tickets >── flight_schedules
bookings ──< payments
bookings ──< booking_status_history
```

| Table | Description |
|-------|-------------|
| `airlines` | Airline carrier information |
| `airports` | Airport codes and city/country |
| `aircraft` | Fleet linked to airlines |
| `flight_schedules` | Individual flight instances with full timestamps |
| `passengers` | Registered passenger profiles |
| `bookings` | Overall reservation with unique booking reference |
| `tickets` | Per-passenger seat/class/fare record |
| `payments` | Simulated payment records |
| `booking_status_history` | Audit trail for status changes |

---

## 📁 Folder Structure

```
flight_booking_system/
├── README.md
├── requirements.txt
├── .env.example            ← Copy to .env and fill in credentials
├── .gitignore
├── database/
│   ├── schema.sql          ← DDL: CREATE DATABASE, all tables, views, triggers
│   └── queries.sql         ← DML: sample data + 30+ demo queries
├── src/
│   ├── main.py             ← Application entry point
│   ├── db_connection.py    ← MySQL connection factory (reads .env)
│   ├── validators.py       ← Input validation helpers
│   ├── repositories/       ← Data access layer (one file per entity)
│   └── ui/                 ← Tkinter UI modules
├── diagrams/
│   ├── er_diagram.mmd      ← Mermaid ER diagram source
│   └── er_diagram.png      ← Rendered ER diagram
├── screenshots/            ← Application screenshots
├── tests/                  ← Automated test suite
└── report/
    └── Flight_Booking_System_Report.docx
```

---

## ⚙️ Setup Instructions (macOS)

### 1. Prerequisites

```zsh
# Verify MySQL is running
brew services list | grep mysql
# If not running:
brew services start mysql

# Verify Python and Tkinter
python3 --version
python3 -c "import tkinter; print('Tkinter OK')"
```

### 2. Clone / Open the Project

```zsh
cd /Users/ayushsawhney/flight_booking_system
```

### 3. Create Virtual Environment

```zsh
python3 -m venv .venv
source .venv/bin/activate
```

### 4. Install Dependencies

```zsh
pip install -r requirements.txt
```

### 5. Configure Database Credentials

```zsh
cp .env.example .env
# Open .env and set your actual MySQL password:
#   DB_HOST=localhost
#   DB_PORT=3306
#   DB_USER=root
#   DB_PASSWORD=<your MySQL root password>
#   DB_NAME=flight_booking_db
```

### 6. Initialize the Database

```zsh
# Create schema (tables, views, triggers)
mysql -u root -p < database/schema.sql

# Load sample data and demo queries
mysql -u root -p flight_booking_db < database/queries.sql
```

### 7. Run the Application

```zsh
source .venv/bin/activate
python3 src/main.py
```

---

## 🧪 Running Tests

```zsh
source .venv/bin/activate
python3 -m pytest tests/ -v --tb=short
```

---

## 📸 Screenshot Capture (macOS)

```zsh
# Automated (requires Screen Recording permission in System Settings):
screencapture -x screenshots/01_dashboard.png

# Manual: Use Cmd+Shift+4, drag to select, save into screenshots/
```

---

## 🔧 Troubleshooting

| Problem | Solution |
|---------|---------|
| `ModuleNotFoundError: No module named 'tkinter'` | `brew install python-tk` |
| MySQL connection refused | `brew services start mysql` |
| `Access denied for user 'root'` | Check your password in `.env` |
| `Unknown database 'flight_booking_db'` | Run `mysql -u root -p < database/schema.sql` first |
| Tkinter looks unstyled on macOS | The app uses `ttk` with `clam` theme — no extra setup needed |
| `pip install` fails | Ensure `.venv` is activated: `source .venv/bin/activate` |

---

## 🎓 Faculty Demonstration Sequence

1. Open Terminal → `cd /Users/ayushsawhney/flight_booking_system`
2. `source .venv/bin/activate && python3 src/main.py`
3. **Dashboard** — show live DB-backed counters
4. **Flight Search** → search DEL → BOM → click a result
5. **Booking** → fill passenger details → confirm booking → show unique reference
6. **Passengers** → show list fetched from MySQL
7. **Reports** → Revenue by Airline / Occupancy Summary
8. **Admin** → show flight schedule management
9. Exit app → run `mysql -u root -p flight_booking_db -e "SELECT * FROM bookings ORDER BY booking_id DESC LIMIT 5;"` to verify persistence
10. Run `python3 -m pytest tests/ -v` to show automated tests passing

---

## 🔗 Repository

**GitHub:** https://github.com/Ayush06-coder/flight-booking-system

---

## 📄 License

This project is created for academic purposes only.


# ✈️ Flight Booking System

A database-driven desktop application engineered with **MySQL 8.x** and **Python 3 (Tkinter / ttk)** for managing domestic flight schedules, seat inventories, customer reservations, and transaction records.

The application emphasizes clean relational architecture, strict transactional consistency, parameterized data access, and an intuitive desktop interface optimized for macOS.

> [!NOTE]
> **Prototype & Simulation Notice:**  
> All flight schedules, aircraft registrations, airport routes, ticket fares, passenger profiles, and payment transactions are **sample / simulated data** created for demonstration. The application does not interface with live airline Global Distribution Systems (GDS) or real banking networks.

---

## 🚀 Recent Improvements

- **Flight Search to Booking Pre-fill:** Clicking "Book Selected Flight" from Search automatically routes to the Booking form, selects the matching flight and travel class, clears previous seat selections, and dynamically calculates real-time seat availability and class fare.
- **Automatic Screen Refresh on Tab Switch:** Switching across any navigation tab (`Dashboard`, `Flight Search`, `Passengers`, `Flights/Admin`, `Bookings`, `Payments`, `Reports`) triggers an automatic database refresh so changes (new reservations, cancellations, passenger updates) immediately reflect without needing manual reloads or losing in-progress form inputs.
- **Safer Startup & Error Resilience:** Database connectivity is validated before initializing UI frames. If MySQL is unreachable, the application displays a structured error dialog with actionable remediation steps and exits cleanly rather than crashing with an unhandled traceback. Refresh operations similarly trap runtime errors gracefully.

---

## 📋 Features

- **Interactive Metric Dashboard:** Real-time KPI summary cards displaying live counts for registered airlines, scheduled flights, registered passengers, active bookings, and total collected revenue directly aggregated from MySQL.
- **Parametric Flight Search:** Search scheduled flights by origin airport, destination airport, travel date, and travel class (Economy / Business) using parameterized SQL queries. Displays carrier names, departure/arrival timestamps, aircraft models, base fares, and live seat counts.
- **Passenger Management:** Full directory supporting passenger registration, search, profile updates, and deletion with client-side validation for email syntax, 10-digit Indian mobile numbers, and date formats.
- **Transactional Flight Booking:** Create flight reservations with explicit ACID transaction boundaries (`conn.start_transaction()`, pessimistic row locking via `SELECT ... FOR UPDATE`, and `conn.commit()`). Generates unique 8-character alphanumeric booking references (e.g., `BK2MV3U0`) and inserts reservation and ticket records atomically.
- **Reservation Lifecycle & Cancellation:** View active bookings, search by reference, and process cancellations. Cancelling a booking marks tickets as `Cancelled`, updates payment status to `Refunded`, and records an audit log in `booking_status_history` via a database trigger.
- **Simulated Payment Management:** Record and inspect simulated payment transactions linked to bookings, supporting payment method selection (Credit Card, Debit Card, UPI, Net Banking) and tracking transaction states (`Completed`, `Pending`, `Refunded`).
- **Analytical Reporting:** Tabulated business reports including **Revenue by Airline**, **Flight Seat Occupancy**, **Revenue by Route**, **Booking Status Breakdown**, **Payment Status Summary**, and **Date-Range Filtering**.
- **Fleet & Schedule Administration:** Administrative view to inspect and manage airlines, domestic airports, aircraft fleet specifications, and operating flight schedules.

---

## 🛠️ Technology Stack

| Layer | Technology | Purpose |
|---|---|---|
| **Database** | MySQL 8.x | Relational database engine using InnoDB, foreign keys, triggers, views, and check constraints |
| **Language** | Python 3 (3.15+) | Core application logic, repositories, and UI framework |
| **Database Connector** | `mysql-connector-python` (26.10.0 / >=9.3.0) | Pure Python MySQL driver for connection pooling and parameterized query execution |
| **Desktop Frontend** | Tkinter & `ttk` | Native desktop GUI using the `clam` theme for macOS light/dark compatibility |
| **Data Presentation** | `ttk.Treeview` | Tabular data grids with column sorting and scrollable views |
| **Testing Framework** | `pytest` (8.3.5) | Automated test suite covering input validation, DB integration, and screen contracts |
| **Configuration** | `python-dotenv` (1.1.0) | Loads environment configuration securely from local `.env` |
| **Report Generation** | `python-docx` (1.1.2) | Generates comprehensive documentation reports (`.docx`) |
| **Version Control** | Git & GitHub | Distributed version control and source code hosting |

---

## 🗄️ Database Design

The relational schema is implemented in **MySQL 8.x** under the database name `flight_booking_db`. It consists of **9 normalized tables (3NF)**, **3 database views**, and **6 business logic triggers**.

### Tables & Relational Structure

| # | Table Name | Purpose | Key Constraints |
|---|---|---|---|
| 1 | `airlines` | Stores airline carrier names, unique codes, and contact details. | Primary Key (`airline_id`), UNIQUE (`airline_code`), CHECK email format |
| 2 | `airports` | Stores domestic airport details and standard 3-letter IATA codes. | Primary Key (`airport_id`), UNIQUE (`airport_code`) |
| 3 | `aircraft` | Manages aircraft fleet models, registration numbers, and seat split. | Primary Key (`aircraft_id`), UNIQUE (`registration_number`), Foreign Key (`airline_id` → `airlines`), CHECK (`economy_seats + business_seats = total_seats`) |
| 4 | `flight_schedules` | Defines flight instances, routes, timestamps, fares, and statuses. | Primary Key (`flight_id`), Foreign Keys (`airline_id`, `aircraft_id`, `origin_airport_id`, `destination_airport_id`), CHECK (`base_fare > 0`), Triggers prevent origin == destination |
| 5 | `passengers` | Stores registered passenger demographics and contact information. | Primary Key (`passenger_id`), CHECK email format, CHECK phone length |
| 6 | `bookings` | Master reservation header with timestamp, status, and total amount. | Primary Key (`booking_id`), UNIQUE (`booking_reference`), Foreign Key (`passenger_id` → `passengers`) |
| 7 | `tickets` | Per-seat passenger ticket linking a booking to a specific flight and seat. | Primary Key (`ticket_id`), Foreign Keys (`booking_id`, `passenger_id`, `flight_id`), UNIQUE (`flight_id`, `seat_number`), CHECK (`ticket_fare >= 0`) |
| 8 | `payments` | Records simulated financial transactions and payment states. | Primary Key (`payment_id`), UNIQUE (`payment_reference`), Foreign Key (`booking_id` → `bookings`) |
| 9 | `booking_status_history` | Audit trail logging state transitions (`Confirmed` → `Cancelled`). | Primary Key (`history_id`), Foreign Key (`booking_id` → `bookings`), Populated automatically via triggers |

### Database Views
- `v_active_flights`: Summarizes scheduled/active flights joined with carrier names and origin/destination airport cities.
- `v_booking_summary`: Comprehensive denormalized reservation report joining bookings, passengers, flight details, and ticket fares.
- `v_airline_revenue`: Financial aggregation view computing total bookings and total earned revenue grouped by airline.

### Triggers
- `trg_prevent_same_airport` / `trg_prevent_same_airport_update`: Enforces that `origin_airport_id <> destination_airport_id` on insert/update.
- `trg_booking_history_insert` / `trg_booking_history_update`: Automatically appends audit rows to `booking_status_history` upon reservation creation or status modification.
- `trg_aircraft_seats_check` / `trg_aircraft_seats_check_update`: Verifies seat capacity consistency before inserting or modifying aircraft records.

### Entity-Relationship (ER) Diagram
The Mermaid ER diagram source code is available in [`diagrams/er_diagram.mmd`](diagrams/er_diagram.mmd).

```
airlines (1) ────< aircraft (N) ────< flight_schedules (N)
airports (1) ────< flight_schedules [origin & destination]
passengers (1) ──< bookings (N) ────< tickets (N) >──── flight_schedules (1)
bookings (1) ────< payments (N)
bookings (1) ────< booking_status_history (N)
```

---

## 📁 Project Folder Structure

```
flight_booking_system/
├── .env.example                          # Template for database configuration (safe to commit)
├── .gitignore                            # Excludes .env, .venv/, __pycache__/, .DS_Store
├── PROGRESS.md                           # Development milestone and checkpoint log
├── README.md                             # Comprehensive project documentation
├── requirements.txt                      # Python library dependencies
├── database/
│   ├── queries.sql                       # Sample data inserts and 30 demonstration SQL queries
│   └── schema.sql                        # DDL: schema creation, 9 tables, 3 views, 6 triggers
├── diagrams/
│   └── er_diagram.mmd                    # Mermaid Entity-Relationship diagram source
├── report/
│   └── Flight_Booking_System_Report.docx # Detailed project documentation report with figures
├── screenshots/                          # Real application GUI captures from macOS
│   ├── 01_dashboard.png                  # Dashboard with live metric cards and flight schedule table
│   ├── 02_flight_search_form.png         # Flight search inquiry form
│   ├── 03_flight_search_results.png      # Query results for DEL -> BOM route
│   ├── 05_passenger_list.png             # Passenger registration form & live MySQL records
│   ├── 06_booking_form.png               # Booking reservation form with live fare calculation
│   ├── 07_booking_confirmed.png          # Booking detail view and audit trail for BK2MV3U0
│   ├── 08_booking_list.png               # Master booking records table
│   ├── 10_cancellation.png               # Cancelled reservation state and ticket release audit
│   ├── 11_payments.png                   # Simulated payment records table
│   ├── 12_revenue_report.png             # Revenue by Airline analytical report
│   ├── 13_occupancy_report.png           # Flight seat occupancy report
│   └── 14_admin_schedules.png            # Administrative flight schedules master view
├── src/
│   ├── __init__.py
│   ├── db_connection.py                  # Database connection factory & health check
│   ├── generate_report.py                # Python script to compile the DOCX academic report
│   ├── main.py                           # Application entry point (Tkinter GUI runner)
│   ├── validators.py                     # Business validation routines and reference generator
│   ├── repositories/                     # Data Access Layer (parameterized SQL operations)
│   │   ├── __init__.py
│   │   ├── airline_repository.py         # Airline entity queries
│   │   ├── airport_repository.py         # Airport entity queries
│   │   ├── booking_repository.py         # Transactional booking creation and cancellation
│   │   ├── flight_repository.py          # Flight search, schedule, and occupancy queries
│   │   ├── passenger_repository.py       # Passenger CRUD operations
│   │   └── payment_repository.py         # Payment creation and lookup operations
│   └── ui/                               # Modular Tkinter GUI frames
│       ├── __init__.py
│       ├── bookings.py                   # Booking creation, search, prefill, and cancellation UI
│       ├── dashboard.py                  # Metric cards and upcoming schedule UI
│       ├── flight_search.py              # Flight search and seat availability UI
│       ├── flights.py                    # Flight schedule admin UI
│       ├── passengers.py                 # Passenger registration and directory UI
│       ├── payments.py                   # Payment recording and history UI
│       └── reports.py                    # Analytical reporting UI
└── tests/                                # Automated test suite (85 tests)
    ├── __init__.py
    ├── test_db.py                        # 21 integration tests (TC01 - TC21) against live MySQL
    ├── test_improvements.py              # 13 tests for refresh/prefill contracts and error handling
    └── test_validators.py                # 51 unit tests for inputs and business validation logic
```

---

## ⚙️ Setup on macOS (zsh)

### Step 1: Install System Prerequisites
Install MySQL 8 and Python Tkinter support via Homebrew:
```zsh
brew install mysql python-tk
```

Start the MySQL service:
```zsh
brew services start mysql
```

Verify MySQL is running:
```zsh
brew services list | grep mysql
```

### Step 2: Set Up Virtual Environment
```zsh
cd ~/flight_booking_system
python3 -m venv .venv
source .venv/bin/activate
```

### Step 3: Install Dependencies
```zsh
pip install -r requirements.txt
```

### Step 4: Configure Database Credentials
Create your local `.env` configuration file:
```zsh
cp .env.example .env
```
Edit `.env` and set your local MySQL credentials:
```ini
DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=your_actual_mysql_password
DB_NAME=flight_booking_db
```
*(Note: `.env` is strictly excluded by `.gitignore` and never committed to version control).*

### Step 5: Initialize Schema & Sample Data
Import the DDL schema:
```zsh
mysql -u root -p < database/schema.sql
```

Load the sample data and demonstration queries:
```zsh
mysql -u root -p flight_booking_db < database/queries.sql
```

### Step 6: Verify Database Connectivity
Verify the Python MySQL connector connects properly:
```zsh
python3 -c "from src.db_connection import test_connection; print('Connected:', test_connection())"
```
*Expected output:* `Connected: (True, 'Connected to database: flight_booking_db')`

### Step 7: Launch the Application
```zsh
python3 src/main.py
```

---

## 🧪 Running the Automated Tests

The test suite validates data models, business rules, transactional rollback, UI contracts, and SQL integrity:

```zsh
source .venv/bin/activate
pytest tests/ -v
```

### Test Suite Summary
```
tests/test_db.py            21 passed (TC01 - TC21 database integration)
tests/test_improvements.py  13 passed (refresh/prefill contracts, safer startup)
tests/test_validators.py    51 passed (input sanitization & reference generator)
─────────────────────────────────────────────────────────────────────────────
TOTAL                       85 passed, 0 failed in 1.91s
```

---

## 📸 Application Screenshots

All screenshots below represent **genuine captures** of the running desktop application on macOS:

### Figure 1: Application Dashboard
![Dashboard](screenshots/01_dashboard.png)  
*Live metrics overview showing real-time statistics (3 Airlines, 10 Flights, 10 Passengers, 13 Bookings, ₹ 49,280.00 Revenue) and upcoming flight schedules.*

### Figure 2: Flight Search Form (Initial State)
![Flight Search Form](screenshots/02_flight_search_form.png)  
*Search interface with origin and destination airport selectors, travel date input, and travel class dropdown prior to query execution.*

### Figure 3: Flight Search Results
![Flight Search Results](screenshots/03_flight_search_results.png)  
*Flight search results for DEL → BOM on 2026-11-05 displaying flight 6E-201, departure/arrival times, aircraft model, fare (₹ 3,500.00), and remaining seats.*

### Figure 4: Passenger Management
![Passenger Management](screenshots/05_passenger_list.png)  
*Passenger registration form on the left with full validation rules, alongside the live MySQL passenger directory on the right.*

### Figure 5: Flight Reservation Form
![New Booking Form](screenshots/06_booking_form.png)  
*Booking creation screen showing passenger selection (Arjun Sharma), flight selection (6E-301), travel class (Business), seat input (E12A), and live fare calculation (₹ 10,500.00).*

### Figure 6: Booking Confirmation & Status History
![Booking Confirmation](screenshots/07_booking_confirmed.png)  
*Booking detail tab displaying confirmed reservation BK2MV3U0, ticket allocation, and the initial status audit history record.*

### Figure 7: Master Bookings List
![All Bookings List](screenshots/08_booking_list.png)  
*Master overview of all customer reservations recorded in MySQL showing booking references, passenger names, flight routes, total fares, and booking statuses.*

### Figure 8: Booking Cancellation & Audit History
![Booking Cancellation](screenshots/10_cancellation.png)  
*Reservation BK2MV3U0 following cancellation: booking status updated to Cancelled, ticket marked Cancelled, and audit history logging the transition event.*

### Figure 9: Payment Management
![Payment Records](screenshots/11_payments.png)  
*Simulated payment management module showing payment recording form and live transaction records with payment references and statuses.*

### Figure 10: Analytical Report — Revenue by Airline
![Revenue Report](screenshots/12_revenue_report.png)  
*Business report aggregating total bookings and revenue collected across airlines (IndiGo: ₹ 28,160.00, Air India: ₹ 14,190.00, SpiceJet: ₹ 6,930.00).*

### Figure 11: Analytical Report — Flight Seat Occupancy
![Occupancy Report](screenshots/13_occupancy_report.png)  
*Real-time flight seat occupancy report calculating total capacities, tickets sold, and capacity utilization percentages.*

### Figure 12: Administrative Flight Schedules
![Flight Schedules Admin](screenshots/14_admin_schedules.png)  
*Master flight schedule administration view showing flight routes, schedules, base fares, and flight statuses.*

---

## 🔒 Booking Logic & Double-Booking Prevention

The system implements transactional consistency to prevent invalid bookings and overbooking:

1. **Atomic Transaction Scope:** Booking creation in [`src/repositories/booking_repository.py`](src/repositories/booking_repository.py) runs inside an explicit transaction (`conn.start_transaction()`). If any validation or insert step fails, `conn.rollback()` restores the database state.
2. **Pessimistic Row Locking (`FOR UPDATE`):** When booking, the flight schedule row is locked with `SELECT flight_status FROM flight_schedules WHERE flight_id=%s FOR UPDATE` to prevent concurrent modifications while reading status.
3. **Capacity Threshold Verification:** The repository queries aircraft class capacity (`economy_seats` or `business_seats`) and counts active tickets (`SELECT COUNT(*) FROM tickets WHERE flight_id=%s AND travel_class=%s AND ticket_status='Active'`). If `booked >= capacity`, the transaction is aborted and rolled back.
4. **Relational Seat Uniqueness Constraint:** The `tickets` table enforces a composite unique constraint:
   ```sql
   CONSTRAINT uq_flight_seat UNIQUE (flight_id, seat_number)
   ```
   If a duplicate seat number is assigned to the same flight, MySQL throws error `1062 (Duplicate entry)`, immediately triggering a rollback.
5. **Technical Scope & Realism:** This design provides robust transactional consistency for a single-database desktop environment. It does not implement distributed locking, GDS PNR queuing, or multi-seat shopping carts. In this prototype, cancelling a booking marks the ticket as `Cancelled` and releases class capacity for the flight, while the row is retained in `tickets` for audit history.

---

## 🔧 Troubleshooting for macOS

| Issue | Root Cause | Solution |
|---|---|---|
| `ModuleNotFoundError: No module named 'tkinter'` | System Python on macOS omits Tkinter by default. | Run `brew install python-tk` and ensure your virtual environment uses the Homebrew Python binary. |
| `Can't connect to local MySQL server through socket` | MySQL background daemon is not running. | Run `brew services start mysql` and verify status with `brew services list`. |
| `Access denied for user 'root'@'localhost'` | Incorrect password specified in `.env`. | Open `.env` and verify `DB_PASSWORD` matches your local MySQL root password. |
| `Unknown database 'flight_booking_db'` | Database schema has not been imported yet. | Execute `mysql -u root -p < database/schema.sql` to initialize the database. |
| `AttributeError: module 'ssl' has no attribute 'PROTOCOL_TLSv1'` | Python 3.15 removed deprecated TLSv1 constants. | Use `mysql-connector-python>=9.3.0` (installed version `26.10.0`), which includes compatibility patches for Python 3.15. |
| Dark Mode visual contrast | macOS Dark Mode overriding standard native widgets. | The application enforces the `clam` theme with explicit hex colors to ensure full readability across all macOS display modes. |

---

## ⚠️ Known Limitations

- **Simulated Sample Data:** All flight schedules, aircraft registrations, airport codes, passenger profiles, and payment references are synthetic.
- **Single-Seat Booking Workflow:** The desktop UI is designed for single-passenger reservations per booking transaction. Multi-seat group reservations are supported by the database schema but require separate transactions in the frontend prototype.
- **Simulated Payment Gateway:** No live external banking or payment gateway is integrated; payments are handled as internal database records.
- **Screenshot Coverage Note:** Out of 14 planned screenshots, 12 genuine captures were taken and embedded. Two planned dialog screenshots (`04_passenger_registration.png` and `09_booking_detail.png`) were omitted to avoid artificial mockups; their functionality is comprehensively verified by automated test cases `TC06`, `TC07`, `TC09`, `TC10`, `TC16`, and `TC18`.

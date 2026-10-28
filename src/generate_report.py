"""
generate_report.py
------------------
Generates the academic DOCX project report for the Flight Booking System.
Run with:
    source .venv/bin/activate
    python3 src/generate_report.py
Output: report/Flight_Booking_System_Report.docx
"""

import os
import sys
import glob
from datetime import date

project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from docx import Document
from docx.shared import Pt, Inches, RGBColor, Cm
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.style import WD_STYLE_TYPE
from docx.oxml.ns import qn
from docx.oxml import OxmlElement


def set_cell_bg(cell, hex_color):
    tc = cell._tc
    tcPr = tc.get_or_add_tcPr()
    shd = OxmlElement("w:shd")
    shd.set(qn("w:val"), "clear")
    shd.set(qn("w:color"), "auto")
    shd.set(qn("w:fill"), hex_color)
    tcPr.append(shd)


def add_heading(doc, text, level):
    p = doc.add_heading(text, level=level)
    p.alignment = WD_ALIGN_PARAGRAPH.LEFT
    return p


def add_code_block(doc, code_text, font_size=8):
    """Add a shaded code block with monospace font."""
    p = doc.add_paragraph()
    p.paragraph_format.left_indent  = Cm(0.5)
    p.paragraph_format.right_indent = Cm(0.5)
    p.paragraph_format.space_before = Pt(4)
    p.paragraph_format.space_after  = Pt(4)
    pPr = p._p.get_or_add_pPr()
    shd = OxmlElement("w:shd")
    shd.set(qn("w:val"), "clear")
    shd.set(qn("w:color"), "auto")
    shd.set(qn("w:fill"), "F2F2F2")
    pPr.append(shd)
    run = p.add_run(code_text)
    run.font.name = "Courier New"
    run.font.size = Pt(font_size)
    return p


def add_para(doc, text, bold=False, italic=False, size=11):
    p = doc.add_paragraph()
    run = p.add_run(text)
    run.bold = bold
    run.italic = italic
    run.font.size = Pt(size)
    return p


def read_file_content(path):
    try:
        with open(path, encoding="utf-8") as f:
            return f.read()
    except Exception:
        return f"[File not found: {path}]"


def build_report():
    doc = Document()

    # ── Page margins ──
    for section in doc.sections:
        section.top_margin    = Inches(1.0)
        section.bottom_margin = Inches(1.0)
        section.left_margin   = Inches(1.2)
        section.right_margin  = Inches(1.0)

    # ═══════════════════════════════════════════════════════════════
    # COVER PAGE
    # ═══════════════════════════════════════════════════════════════
    doc.add_paragraph()
    doc.add_paragraph()

    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = p.add_run("FLIGHT BOOKING SYSTEM")
    run.bold = True
    run.font.size = Pt(26)

    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = p.add_run("A Complete DBMS Project Based Learning (PBL)")
    run.font.size = Pt(14)

    doc.add_paragraph()

    for line, sz in [
        ("Department of Computer Science & Engineering", 13),
        ("[Institution Name — to be filled by student]", 12),
        ("Academic Session: 2026–27", 12),
    ]:
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.add_run(line).font.size = Pt(sz)

    doc.add_paragraph()
    doc.add_paragraph()

    table = doc.add_table(rows=5, cols=2)
    table.style = "Table Grid"
    details = [
        ("Student Name",    "[Student Name — to be filled]"),
        ("Roll Number",     "[Roll Number — to be filled]"),
        ("Subject",         "Database Management Systems (DBMS)"),
        ("Guide / Mentor",  "[Faculty Name — to be filled]"),
        ("Date Submitted",  str(date.today())),
    ]
    for row, (label, value) in zip(table.rows, details):
        row.cells[0].text = label
        row.cells[1].text = value
        row.cells[0].paragraphs[0].runs[0].bold = True
        set_cell_bg(row.cells[0], "D9E1F2")

    doc.add_page_break()

    # ═══════════════════════════════════════════════════════════════
    # CERTIFICATE (template)
    # ═══════════════════════════════════════════════════════════════
    add_heading(doc, "Certificate", 1)
    add_para(doc,
        "This is to certify that the project titled \"Flight Booking System\" has been "
        "successfully completed by [Student Name], Roll No. [Roll Number], of the "
        "Department of Computer Science & Engineering, [Institution Name], in partial "
        "fulfilment of the requirements for the subject Database Management Systems (DBMS) "
        "during the academic session 2026–27.",
    )
    doc.add_paragraph()
    add_para(doc, "This project has been reviewed and found to be satisfactory.")
    doc.add_paragraph()
    add_para(doc, "Guide / Mentor: ____________________________")
    add_para(doc, "Date: ____________________________")
    doc.add_page_break()

    # ═══════════════════════════════════════════════════════════════
    # ACKNOWLEDGEMENT
    # ═══════════════════════════════════════════════════════════════
    add_heading(doc, "Acknowledgement", 1)
    add_para(doc,
        "I would like to express my sincere gratitude to my faculty guide and mentor for "
        "their invaluable guidance and encouragement throughout this project. I also thank "
        "the Department of Computer Science & Engineering for providing the necessary "
        "resources and infrastructure. This project has significantly deepened my "
        "understanding of relational database design, SQL implementation, and Python–MySQL "
        "application development."
    )
    doc.add_page_break()

    # ═══════════════════════════════════════════════════════════════
    # ABSTRACT
    # ═══════════════════════════════════════════════════════════════
    add_heading(doc, "Abstract", 1)
    add_para(doc,
        "The Flight Booking System is a fully functional desktop application developed as a "
        "Database Management Systems (DBMS) Project Based Learning (PBL) assignment. "
        "The system demonstrates the complete lifecycle of a relational database application — "
        "from entity-relationship design and normalization (UNF to 3NF) through MySQL DDL and "
        "DML implementation, to a Python-based graphical frontend connected to the live database. "
        "\n\nThe application allows users to search available flights, register passenger details, "
        "create bookings with unique booking references, manage seat allocation, process simulated "
        "payments, cancel bookings, and generate analytical reports. "
        "\n\nThe backend comprises a normalized nine-table MySQL 8 database (flight_booking_db) with "
        "appropriate constraints, indexes, views, and triggers that enforce business rules at the "
        "database level. The frontend is built using Python 3 and Tkinter with ttk widgets, "
        "connected to MySQL via mysql-connector-python with parameterized queries throughout."
        "\n\n⚠ All flight schedules, prices, passenger data, and payment transactions in this "
        "project are SIMULATED SAMPLE DATA created solely for academic demonstration purposes."
    )
    doc.add_page_break()

    # ═══════════════════════════════════════════════════════════════
    # TABLE OF CONTENTS (manual)
    # ═══════════════════════════════════════════════════════════════
    add_heading(doc, "Table of Contents", 1)
    toc_entries = [
        ("1",  "Introduction"),
        ("2",  "Problem Statement"),
        ("3",  "Objectives"),
        ("4",  "Scope of the Project"),
        ("5",  "Existing System and Limitations"),
        ("6",  "Proposed System"),
        ("7",  "Functional Requirements"),
        ("8",  "Non-Functional Requirements"),
        ("9",  "Hardware and Software Requirements"),
        ("10", "System Architecture"),
        ("11", "Database Design"),
        ("12", "Entity Relationship (ER) Diagram"),
        ("13", "Entity and Attribute Description"),
        ("14", "Relational Schema"),
        ("15", "Database Constraints"),
        ("16", "Normalization — UNF to 3NF"),
        ("17", "DDL Implementation"),
        ("18", "DML Implementation and Sample Data"),
        ("19", "SQL Queries and Demonstrations"),
        ("20", "Python Frontend Design"),
        ("21", "Python–MySQL Connectivity"),
        ("22", "Application Modules"),
        ("23", "Booking and Seat Allocation Logic"),
        ("24", "Testing and Validation"),
        ("25", "Project Output and Screenshots"),
        ("26", "Conclusion"),
        ("27", "Future Scope"),
        ("28", "References"),
        ("Appendix A", "Complete SQL Schema"),
        ("Appendix B", "Key Python Source Code"),
        ("Appendix C", "Setup and Execution Instructions"),
    ]
    for num, title in toc_entries:
        p = doc.add_paragraph(style="List Number")
        p.clear()
        run = p.add_run(f"{num}.  {title}")
        run.font.size = Pt(11)
    doc.add_page_break()

    # ═══════════════════════════════════════════════════════════════
    # SECTION 1: INTRODUCTION
    # ═══════════════════════════════════════════════════════════════
    add_heading(doc, "1. Introduction", 1)
    add_para(doc,
        "Database Management Systems (DBMS) form the backbone of modern software applications. "
        "From e-commerce platforms to healthcare records and airline reservations, virtually every "
        "large-scale system relies on a well-designed relational database. "
        "This project, the Flight Booking System, provides a hands-on demonstration of the "
        "complete RDBMS development cycle using MySQL 8 and Python 3.\n\n"
        "The project covers: entity-relationship modelling, normalization to Third Normal Form "
        "(3NF), DDL implementation (CREATE TABLE, constraints, indexes, views, triggers), "
        "DML operations (INSERT, SELECT, UPDATE, DELETE, JOINs, aggregations, transactions), "
        "and a fully functional Tkinter desktop application that connects to the MySQL database "
        "using parameterized SQL queries."
    )

    # ═══════════════════════════════════════════════════════════════
    # SECTION 2: PROBLEM STATEMENT
    # ═══════════════════════════════════════════════════════════════
    add_heading(doc, "2. Problem Statement", 1)
    add_para(doc,
        "Traditional manual flight booking systems suffer from data redundancy, inconsistency, "
        "lack of real-time availability information, and poor data integrity. Storing flight and "
        "passenger information in flat files or spreadsheets leads to insertion, update, and "
        "deletion anomalies. There is no mechanism to prevent double seat booking or to maintain "
        "accurate revenue and occupancy records.\n\n"
        "This project addresses these issues by implementing a normalized relational database with "
        "enforced integrity constraints, combined with a user-friendly Python GUI frontend."
    )

    # ═══════════════════════════════════════════════════════════════
    # SECTION 3: OBJECTIVES
    # ═══════════════════════════════════════════════════════════════
    add_heading(doc, "3. Objectives", 1)
    objectives = [
        "Design a normalized (3NF) relational database for a flight booking domain.",
        "Implement the database in MySQL 8 using complete DDL (CREATE, ALTER, constraints, indexes, views, triggers).",
        "Populate the database with realistic sample data and demonstrate DML operations.",
        "Develop a Python 3 desktop application using Tkinter that connects to the MySQL database.",
        "Implement flight search, passenger registration, booking creation, seat allocation, cancellation, and payment recording.",
        "Prevent double seat booking using database-level UNIQUE constraints and transactional operations.",
        "Generate analytical reports (revenue by airline/route, occupancy, booking status) using SQL aggregation queries.",
        "Demonstrate referential integrity through foreign keys and ON DELETE RESTRICT actions.",
        "Write and execute automated tests covering 21 test cases including constraint violations and transaction rollback.",
    ]
    for obj in objectives:
        p = doc.add_paragraph(style="List Bullet")
        p.add_run(obj).font.size = Pt(11)

    # ═══════════════════════════════════════════════════════════════
    # SECTION 4: SCOPE
    # ═══════════════════════════════════════════════════════════════
    add_heading(doc, "4. Scope of the Project", 1)
    add_para(doc,
        "The Flight Booking System is an academic prototype scoped to demonstrate DBMS concepts. "
        "It covers: airline and airport administration, aircraft fleet management, flight schedule "
        "management, passenger profile management, booking creation and cancellation, simulated "
        "payment recording, and analytical reporting.\n\n"
        "It does not integrate with real airline APIs, live flight data, or actual payment gateways. "
        "All sample data (flight numbers, fares, passenger names) is fictitious and labelled as such."
    )

    # ═══════════════════════════════════════════════════════════════
    # SECTION 5: EXISTING SYSTEM
    # ═══════════════════════════════════════════════════════════════
    add_heading(doc, "5. Existing System and Limitations", 1)
    add_para(doc,
        "Existing manual or spreadsheet-based booking records have the following limitations:"
    )
    limitations = [
        "Data redundancy: passenger and airline details repeated in every booking record.",
        "No referential integrity: bookings may reference non-existent flights.",
        "No concurrent booking control: multiple users can assign the same seat.",
        "Update anomalies: changing an airport name requires updates across all records.",
        "No audit trail: cancellation history is lost when records are overwritten.",
        "Difficult reporting: aggregating revenue or occupancy requires manual effort.",
    ]
    for lim in limitations:
        p = doc.add_paragraph(style="List Bullet")
        p.add_run(lim).font.size = Pt(11)

    # ═══════════════════════════════════════════════════════════════
    # SECTION 6: PROPOSED SYSTEM
    # ═══════════════════════════════════════════════════════════════
    add_heading(doc, "6. Proposed System", 1)
    add_para(doc,
        "The proposed system is a normalized RDBMS-backed desktop application that eliminates "
        "the above limitations through:\n"
        "• A 9-table relational schema in 3NF with primary keys, foreign keys, and CHECK constraints.\n"
        "• UNIQUE constraint on (flight_id, seat_number) to prevent double seat booking.\n"
        "• Database triggers for same-airport validation, status audit logging, flight cancellation "
        "protection, and seat capacity enforcement.\n"
        "• Transactional booking creation using START TRANSACTION / COMMIT / ROLLBACK.\n"
        "• A Python Tkinter GUI with parameterized SQL queries (no SQL injection risk).\n"
        "• Analytical views and report queries for revenue, occupancy, and booking status."
    )

    # ═══════════════════════════════════════════════════════════════
    # SECTIONS 7–9: REQUIREMENTS
    # ═══════════════════════════════════════════════════════════════
    add_heading(doc, "7. Functional Requirements", 1)
    func_reqs = [
        "FR01: Users can search available flights by origin, destination, date, and travel class.",
        "FR02: Users can register and manage passenger profiles.",
        "FR03: Users can create bookings and receive a unique booking reference.",
        "FR04: Users can select seats; duplicate seat assignments are rejected.",
        "FR05: Users can cancel eligible bookings; seats are released and status history recorded.",
        "FR06: Administrators can manage airlines, airports, aircraft, and flight schedules.",
        "FR07: The system records simulated payment transactions linked to bookings.",
        "FR08: Reports provide revenue by airline, revenue by route, occupancy, and booking status.",
        "FR09: The dashboard displays live statistics fetched from the database.",
        "FR10: All data operations persist in MySQL and are independently verifiable by SQL queries.",
    ]
    for req in func_reqs:
        p = doc.add_paragraph(style="List Bullet")
        p.add_run(req).font.size = Pt(11)

    add_heading(doc, "8. Non-Functional Requirements", 1)
    nfr = [
        "NFR01: All SQL queries use parameterized statements — no string concatenation of user input.",
        "NFR02: Database credentials are stored in .env, excluded from version control.",
        "NFR03: The application handles database connection errors gracefully with user-visible messages.",
        "NFR04: The Tkinter UI uses the 'clam' theme and renders correctly on macOS (light and dark mode).",
        "NFR05: The codebase is modular — DB operations are separated from UI code.",
        "NFR06: Transactions are committed only when all steps succeed; failures trigger rollback.",
    ]
    for req in nfr:
        p = doc.add_paragraph(style="List Bullet")
        p.add_run(req).font.size = Pt(11)

    add_heading(doc, "9. Hardware and Software Requirements", 1)
    hw_sw = [
        ("Hardware", "Mac with Apple Silicon (M-series) or Intel, 4 GB RAM minimum, 500 MB disk space"),
        ("Operating System", "macOS (Homebrew environment)"),
        ("Database", "MySQL 8.x (installed via Homebrew)"),
        ("Language", "Python 3.15"),
        ("GUI Framework", "Tkinter 9.1 (bundled with Python via python-tk)"),
        ("DB Connector", "mysql-connector-python"),
        ("Report Generation", "python-docx"),
        ("Testing Framework", "pytest 8.3.5"),
        ("Version Control", "Git + GitHub"),
    ]
    t = doc.add_table(rows=len(hw_sw)+1, cols=2)
    t.style = "Table Grid"
    t.rows[0].cells[0].text = "Component"
    t.rows[0].cells[1].text = "Specification"
    for cell in t.rows[0].cells:
        cell.paragraphs[0].runs[0].bold = True
        set_cell_bg(cell, "1F4E79")
        cell.paragraphs[0].runs[0].font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)
    for i, (comp, spec) in enumerate(hw_sw):
        t.rows[i+1].cells[0].text = comp
        t.rows[i+1].cells[1].text = spec
    doc.add_paragraph()

    # ═══════════════════════════════════════════════════════════════
    # SECTION 10: SYSTEM ARCHITECTURE
    # ═══════════════════════════════════════════════════════════════
    add_heading(doc, "10. System Architecture", 1)
    add_para(doc,
        "The application follows a three-layer architecture:\n\n"
        "Layer 1 — Presentation (UI):  Tkinter ttk-based modules in src/ui/. "
        "Each module handles a domain area (dashboard, flight search, passengers, "
        "bookings, payments, reports, admin).\n\n"
        "Layer 2 — Business / Repository:  src/repositories/ contains one file per entity. "
        "Each repository handles all SQL for its entity using parameterized queries. "
        "src/validators.py enforces input rules before DB interaction.\n\n"
        "Layer 3 — Data:  MySQL 8 database (flight_booking_db) with 9 tables, 3 views, "
        "and 6 triggers. src/db_connection.py provides a connection factory that reads "
        "credentials from .env via python-dotenv."
    )
    add_code_block(doc,
        "┌─────────────────────────────┐\n"
        "│     Tkinter UI (src/ui/)    │\n"
        "│  dashboard | search | ...   │\n"
        "└────────────┬────────────────┘\n"
        "             │ calls\n"
        "┌────────────▼────────────────┐\n"
        "│   Repository Layer           │\n"
        "│  (src/repositories/)         │\n"
        "│  + src/validators.py         │\n"
        "└────────────┬────────────────┘\n"
        "             │ SQL via mysql-connector\n"
        "┌────────────▼────────────────┐\n"
        "│  MySQL 8 — flight_booking_db │\n"
        "│  9 tables, 3 views, 6 triggers│\n"
        "└─────────────────────────────┘"
    )

    # ═══════════════════════════════════════════════════════════════
    # SECTION 11: DATABASE DESIGN
    # ═══════════════════════════════════════════════════════════════
    add_heading(doc, "11. Database Design", 1)
    add_para(doc,
        "Database: flight_booking_db\n"
        "The database contains 9 tables, 3 views (v_flight_booking_details, "
        "v_seat_availability, v_revenue_summary), and 6 triggers. "
        "The design is in Third Normal Form (3NF)."
    )
    db_tables = [
        ("airlines",               "Airline carrier information. PK: airline_id. UK: airline_code."),
        ("airports",               "Airport codes and locations. PK: airport_id. UK: airport_code."),
        ("aircraft",               "Aircraft fleet linked to airlines. PK: aircraft_id. FK: airline_id. Seat counts validated by trigger."),
        ("flight_schedules",       "Individual flight instances. PK: flight_id. FKs: airline_id, aircraft_id, origin/destination airport_id. Departure < arrival enforced by CHECK."),
        ("passengers",             "Passenger profiles. PK: passenger_id. UK: email."),
        ("bookings",               "Overall reservation record. PK: booking_id. UK: booking_reference. FK: passenger_id."),
        ("tickets",                "Per-passenger seat/class/fare. PK: ticket_id. FKs: booking_id, passenger_id, flight_id. UK: (flight_id, seat_number) prevents double-booking."),
        ("payments",               "Simulated payment records. PK: payment_id. FK: booking_id. UK: transaction_reference."),
        ("booking_status_history", "Audit trail for booking status changes. PK: history_id. FK: booking_id. Populated by triggers."),
    ]
    t = doc.add_table(rows=len(db_tables)+1, cols=2)
    t.style = "Table Grid"
    t.rows[0].cells[0].text = "Table"
    t.rows[0].cells[1].text = "Description"
    for cell in t.rows[0].cells:
        cell.paragraphs[0].runs[0].bold = True
        set_cell_bg(cell, "1F4E79")
        cell.paragraphs[0].runs[0].font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)
    for i, (tname, tdesc) in enumerate(db_tables):
        t.rows[i+1].cells[0].text = tname
        t.rows[i+1].cells[1].text = tdesc
        if i % 2 == 0:
            set_cell_bg(t.rows[i+1].cells[0], "EBF3FB")
            set_cell_bg(t.rows[i+1].cells[1], "EBF3FB")
    doc.add_paragraph()

    # ═══════════════════════════════════════════════════════════════
    # SECTION 12: ER DIAGRAM
    # ═══════════════════════════════════════════════════════════════
    add_heading(doc, "12. Entity Relationship (ER) Diagram", 1)
    add_para(doc,
        "The ER diagram below shows all entities, their primary keys, and the relationships "
        "between them. The source file is at diagrams/er_diagram.mmd (Mermaid syntax)."
    )

    er_png = os.path.join(project_root, "diagrams", "er_diagram.png")
    if os.path.exists(er_png):
        doc.add_picture(er_png, width=Inches(6.0))
        add_para(doc, "Figure 1: Entity Relationship Diagram — Flight Booking System", italic=True)
    else:
        add_para(doc,
            "[ER Diagram PNG not found. To generate: install Node.js + mmdc "
            "(npm install -g @mermaid-js/mermaid-cli) then run: "
            "mmdc -i diagrams/er_diagram.mmd -o diagrams/er_diagram.png]",
            italic=True
        )

    add_para(doc, "Key relationships:")
    rels = [
        "airlines (1) → (M) aircraft: An airline operates multiple aircraft.",
        "airlines (1) → (M) flight_schedules: An airline schedules multiple flights.",
        "airports (1) → (M) flight_schedules (as origin): An airport is the origin of many flights.",
        "airports (1) → (M) flight_schedules (as destination): An airport is the destination of many flights.",
        "aircraft (1) → (M) flight_schedules: An aircraft is assigned to multiple flights.",
        "passengers (1) → (M) bookings: A passenger makes multiple bookings.",
        "bookings (1) → (M) tickets: One booking contains one or more tickets.",
        "flight_schedules (1) → (M) tickets: A flight schedule has many ticket records.",
        "bookings (1) → (M) payments: A booking can have multiple payment records.",
        "bookings (1) → (M) booking_status_history: Every status change is recorded.",
    ]
    for rel in rels:
        p = doc.add_paragraph(style="List Bullet")
        p.add_run(rel).font.size = Pt(10)

    # ═══════════════════════════════════════════════════════════════
    # SECTION 16: NORMALIZATION
    # ═══════════════════════════════════════════════════════════════
    add_heading(doc, "16. Normalization — UNF to 3NF", 1)

    add_heading(doc, "Unnormalized Form (UNF)", 2)
    add_para(doc,
        "Consider a single flat table storing all booking information:"
    )
    add_code_block(doc,
        "BOOKING_FLAT(\n"
        "  booking_ref, booking_date,\n"
        "  passenger_name, passenger_email, passenger_phone,\n"
        "  airline_name, airline_code,\n"
        "  flight_number, origin_airport, origin_city,\n"
        "  destination_airport, destination_city,\n"
        "  departure_datetime, arrival_datetime,\n"
        "  aircraft_model, registration_number, total_seats,\n"
        "  seat_number, travel_class, ticket_fare,\n"
        "  payment_method, payment_status, transaction_ref, payment_amount\n"
        ")"
    )
    add_para(doc,
        "Anomalies:\n"
        "• Insertion: Cannot add an airport unless a booking exists that uses it.\n"
        "• Update: Changing an airline name requires updating every booking row for that airline.\n"
        "• Deletion: Deleting the only booking for a flight removes all information about that flight.\n"
        "• Redundancy: airline_name, airline_code, origin_city repeat for every booking on the same route."
    )

    add_heading(doc, "First Normal Form (1NF)", 2)
    add_para(doc,
        "Remove repeating groups. Ensure every attribute is atomic and every row is unique. "
        "The flat table already has atomic values; add a surrogate primary key (booking_id). "
        "1NF Relation: BOOKING_1NF(booking_id PK, booking_ref, booking_date, passenger_name, "
        "passenger_email, passenger_phone, airline_name, airline_code, flight_number, "
        "origin_code, origin_city, destination_code, destination_city, departure_datetime, "
        "arrival_datetime, aircraft_model, registration_number, total_seats, seat_number, "
        "travel_class, ticket_fare, payment_method, payment_status, transaction_ref, payment_amount)"
    )

    add_heading(doc, "Second Normal Form (2NF)", 2)
    add_para(doc,
        "Remove partial dependencies (attributes dependent on part of a composite key). "
        "Using booking_id as PK eliminates partial dependencies on the key itself, but functional "
        "dependencies on non-key attributes reveal transitive dependencies addressed in 2NF/3NF.\n\n"
        "Functional Dependencies identified:\n"
        "• airline_code → airline_name (airline_code determines airline_name)\n"
        "• airport_code → airport_name, city, country\n"
        "• flight_number, departure_date → airline, aircraft, origin, destination, times, base_fare\n"
        "• registration_number → aircraft_model, total_seats, airline\n"
        "• passenger_email → passenger_name, phone\n\n"
        "Decompose into: Airlines(airline_id, airline_code, airline_name), "
        "Airports(airport_id, airport_code, airport_name, city, country), "
        "Aircraft(aircraft_id, registration_number, aircraft_model, total_seats, airline_id), "
        "FlightSchedules(flight_id, flight_number, departure, arrival, airline_id, aircraft_id, "
        "origin_airport_id, destination_airport_id, base_fare), "
        "Passengers(passenger_id, passenger_name, email, phone), "
        "Bookings(booking_id, booking_ref, passenger_id, booking_date, total_amount)."
    )

    add_heading(doc, "Third Normal Form (3NF)", 2)
    add_para(doc,
        "Remove transitive dependencies (non-key → non-key). In the decomposed 2NF relations:\n"
        "• In Aircraft: registration_number → airline_id (stored redundantly with airline_id FK) — "
        "resolved by keeping airline_id as FK only.\n"
        "• The ticket details (seat_number, travel_class, ticket_fare) are dependent on "
        "(booking_id, flight_id) which are both keys — moved to the Tickets table.\n"
        "• Payment attributes (payment_method, payment_status, transaction_ref, payment_amount) "
        "depend on payment_id, not on booking_id — moved to Payments table.\n"
        "• Booking status changes (old_status, new_status, changed_at) depend on history_id — "
        "moved to BookingStatusHistory table.\n\n"
        "Result: The 9 tables in the implemented schema satisfy 3NF. No non-key attribute "
        "transitively depends on any primary key through another non-key attribute."
    )

    # ═══════════════════════════════════════════════════════════════
    # SECTION 17: DDL
    # ═══════════════════════════════════════════════════════════════
    add_heading(doc, "17. DDL Implementation", 1)
    add_para(doc,
        "The complete DDL is in database/schema.sql. Key design decisions:\n"
        "• AUTO_INCREMENT surrogate keys for all tables.\n"
        "• ENUM for booking_status, flight_status, travel_class, payment_method, payment_status — "
        "prevents invalid values at DB level.\n"
        "• CHECK constraints: base_fare >= 0, total_amount >= 0, ticket_fare >= 0, amount >= 0, "
        "arrival_datetime > departure_datetime.\n"
        "• UNIQUE(flight_id, seat_number) on tickets — primary double-booking prevention.\n"
        "• 6 triggers: same-airport validation, seat capacity check, cancelled flight booking "
        "prevention, status history logging (insert and update).\n"
        "• ON DELETE RESTRICT on all FKs — preserves data integrity."
    )
    add_para(doc, "Sample DDL (airlines table):")
    add_code_block(doc, """\
CREATE TABLE airlines (
    airline_id    INT           NOT NULL AUTO_INCREMENT,
    airline_name  VARCHAR(100)  NOT NULL,
    airline_code  VARCHAR(10)   NOT NULL,
    contact_email VARCHAR(150)  NOT NULL,
    contact_phone VARCHAR(20)   NOT NULL,
    CONSTRAINT pk_airlines       PRIMARY KEY (airline_id),
    CONSTRAINT uq_airline_code   UNIQUE (airline_code),
    CONSTRAINT chk_airline_email CHECK (contact_email LIKE '%@%.%')
) ENGINE=InnoDB;""")

    # ═══════════════════════════════════════════════════════════════
    # SECTION 18: DML
    # ═══════════════════════════════════════════════════════════════
    add_heading(doc, "18. DML Implementation and Sample Data", 1)
    add_para(doc,
        "Sample data (all SIMULATED — not real airline data) includes:\n"
        "• 3 airlines: IndiGo (6E), Air India (AI), SpiceJet (SG)\n"
        "• 8 airports: DEL, BOM, BLR, MAA, CCU, HYD, COK, AMD\n"
        "• 5 aircraft records\n"
        "• 10 flight schedules (including an overnight DEL→MAA flight demonstrating DATETIME support)\n"
        "• 10 passengers with sample names and emails\n"
        "• 13 bookings (11 Confirmed, 1 Cancelled, 1 Completed)\n"
        "• 12 tickets with unique seat assignments\n"
        "• 12 payment records (11 Completed, 1 Refunded for the cancelled booking)"
    )
    add_para(doc, "Sample INSERT:")
    add_code_block(doc, """\
INSERT INTO airlines (airline_name, airline_code, contact_email, contact_phone)
VALUES ('IndiGo Airlines', '6E', 'support@indigo.sample', '+91-9988001122');
-- NOTE: SAMPLE DATA — not a real airline record""")

    # ═══════════════════════════════════════════════════════════════
    # SECTION 19: SQL QUERIES
    # ═══════════════════════════════════════════════════════════════
    add_heading(doc, "19. SQL Queries and Demonstrations", 1)
    add_para(doc,
        "30 SQL queries are provided in database/queries.sql. Selected examples are shown below:"
    )
    queries = [
        ("Q03: Flight Search (DEL→BOM on 2026-11-05)",
         "SELECT fs.flight_id, al.airline_name, fs.flight_number,\n"
         "       orig.city AS origin, dest.city AS destination,\n"
         "       fs.departure_datetime, fs.arrival_datetime,\n"
         "       TIMESTAMPDIFF(MINUTE, fs.departure_datetime, fs.arrival_datetime) AS duration_min,\n"
         "       fs.base_fare, fs.flight_status\n"
         "FROM flight_schedules fs\n"
         "JOIN airlines al   ON fs.airline_id            = al.airline_id\n"
         "JOIN airports orig ON fs.origin_airport_id     = orig.airport_id\n"
         "JOIN airports dest ON fs.destination_airport_id= dest.airport_id\n"
         "WHERE orig.airport_code = 'DEL' AND dest.airport_code = 'BOM'\n"
         "  AND DATE(fs.departure_datetime) = '2026-11-05'\n"
         "  AND fs.flight_status <> 'Cancelled'\n"
         "ORDER BY fs.departure_datetime;"),
        ("Q08: Revenue by Airline (GROUP BY + SUM)",
         "SELECT al.airline_name,\n"
         "       COUNT(DISTINCT b.booking_id) AS total_bookings,\n"
         "       SUM(py.amount) AS total_revenue\n"
         "FROM payments py\n"
         "JOIN bookings b ON py.booking_id = b.booking_id\n"
         "JOIN tickets  t ON t.booking_id  = b.booking_id\n"
         "JOIN flight_schedules fs ON t.flight_id = fs.flight_id\n"
         "JOIN airlines al ON fs.airline_id = al.airline_id\n"
         "WHERE py.payment_status = 'Completed'\n"
         "GROUP BY al.airline_name ORDER BY total_revenue DESC;"),
        ("Q28: Transactional Booking (COMMIT / ROLLBACK)",
         "START TRANSACTION;\n"
         "INSERT INTO bookings (booking_reference, passenger_id, total_amount, booking_status)\n"
         "VALUES ('BKTEST01', 5, 3500.00, 'Confirmed');\n"
         "INSERT INTO tickets (booking_id, passenger_id, flight_id, seat_number,\n"
         "                     travel_class, ticket_fare, ticket_status)\n"
         "VALUES (LAST_INSERT_ID(), 5, 1, 'E40F', 'Economy', 3500.00, 'Active');\n"
         "COMMIT;  -- or ROLLBACK; if any step fails"),
    ]
    for title, sql in queries:
        add_para(doc, title, bold=True)
        add_code_block(doc, sql)
        doc.add_paragraph()

    # ═══════════════════════════════════════════════════════════════
    # SECTION 20–23: PYTHON FRONTEND
    # ═══════════════════════════════════════════════════════════════
    add_heading(doc, "20. Python Frontend Design", 1)
    add_para(doc,
        "The frontend is a Tkinter desktop application (src/main.py) with a dark sidebar "
        "and a content area that displays seven modules: Dashboard, Flight Search, Passengers, "
        "Flights/Admin, Bookings, Payments, and Reports. The 'clam' ttk theme is used for "
        "cross-platform rendering on macOS."
    )

    add_heading(doc, "21. Python–MySQL Connectivity", 1)
    add_para(doc,
        "src/db_connection.py provides a get_connection() factory that reads host, port, "
        "user, password, and database from the .env file using python-dotenv. "
        "All repository functions open a connection, execute parameterized SQL, commit or "
        "rollback, then close the connection. No SQL string concatenation is used anywhere."
    )
    add_code_block(doc, """\
import mysql.connector
from dotenv import load_dotenv
load_dotenv()

def get_connection():
    return mysql.connector.connect(
        host=os.getenv("DB_HOST", "localhost"),
        port=int(os.getenv("DB_PORT", 3306)),
        user=os.getenv("DB_USER", "root"),
        password=os.getenv("DB_PASSWORD", ""),
        database=os.getenv("DB_NAME", "flight_booking_db"),
        autocommit=False,
    )""")

    add_heading(doc, "22. Application Modules", 1)
    modules = [
        ("src/main.py",                    "Entry point. Creates Tk window, sidebar nav, pre-loads all frames."),
        ("src/db_connection.py",           "MySQL connection factory using .env credentials."),
        ("src/validators.py",              "Input validators (email, phone, date, seat, fare, name) and booking ref generator."),
        ("src/repositories/airline_repository.py",   "CRUD for airlines table."),
        ("src/repositories/airport_repository.py",   "CRUD for airports table."),
        ("src/repositories/flight_repository.py",    "Flight search, CRUD for schedules/aircraft, seat availability, dashboard stats."),
        ("src/repositories/passenger_repository.py", "Passenger CRUD, search, booking history."),
        ("src/repositories/booking_repository.py",   "Transactional booking create/cancel, history retrieval."),
        ("src/repositories/payment_repository.py",   "Simulated payment recording, revenue aggregations."),
        ("src/ui/dashboard.py",            "Live stats cards + upcoming flights treeview."),
        ("src/ui/flight_search.py",        "Search form, results treeview, book-selected callback."),
        ("src/ui/passengers.py",           "Full CRUD, search, column sort."),
        ("src/ui/flights.py",              "4-tab admin: Airlines, Airports, Aircraft, Schedules."),
        ("src/ui/bookings.py",             "3-tab: All Bookings, New Booking wizard, Detail view. Cancel button."),
        ("src/ui/payments.py",             "Payment records + simulated payment form."),
        ("src/ui/reports.py",              "8-tab analytical reports with CSV export."),
    ]
    t = doc.add_table(rows=len(modules)+1, cols=2)
    t.style = "Table Grid"
    t.rows[0].cells[0].text = "File"
    t.rows[0].cells[1].text = "Purpose"
    for cell in t.rows[0].cells:
        cell.paragraphs[0].runs[0].bold = True
        set_cell_bg(cell, "1F4E79")
        cell.paragraphs[0].runs[0].font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)
    for i, (fname, desc) in enumerate(modules):
        t.rows[i+1].cells[0].text = fname
        t.rows[i+1].cells[1].text = desc
        if i % 2 == 0:
            set_cell_bg(t.rows[i+1].cells[0], "EBF3FB")
            set_cell_bg(t.rows[i+1].cells[1], "EBF3FB")
    doc.add_paragraph()

    add_heading(doc, "23. Booking and Seat Allocation Logic", 1)
    add_para(doc,
        "booking_repository.create_booking() implements the full booking workflow inside a "
        "single database transaction:\n"
        "1. Generate a unique booking reference (retry up to 10× if duplicate).\n"
        "2. Lock the flight_schedules row (FOR UPDATE) and verify status ≠ 'Cancelled'.\n"
        "3. Check available seats for the selected travel class (capacity − active tickets).\n"
        "4. INSERT into bookings (status = 'Confirmed').\n"
        "5. INSERT into tickets — the UNIQUE(flight_id, seat_number) constraint rejects duplicates.\n"
        "6. The trg_check_seat_capacity trigger independently re-validates class capacity.\n"
        "7. COMMIT on success; ROLLBACK on any failure.\n\n"
        "Cancellation (cancel_booking()): sets ticket_status → 'Cancelled', booking_status → "
        "'Cancelled', payment_status → 'Refunded' (simulated) in one transaction. "
        "The trg_booking_status_update trigger automatically logs the change in booking_status_history."
    )

    # ═══════════════════════════════════════════════════════════════
    # SECTION 24: TESTING
    # ═══════════════════════════════════════════════════════════════
    add_heading(doc, "24. Testing and Validation", 1)
    add_para(doc,
        "72 automated tests were written and executed using pytest 8.3.5. All 72 passed.\n"
        "Tests are in two files:"
    )
    add_para(doc, "• tests/test_validators.py — 51 unit tests for all validator functions.", bold=False)
    add_para(doc, "• tests/test_db.py — 21 integration tests covering TC01–TC21.", bold=False)
    doc.add_paragraph()

    tc_data = [
        ("TC01", "Database creation",              "Connect and SELECT DATABASE()",               "flight_booking_db returned",     "PASS"),
        ("TC02", "All 9 tables exist",             "Query information_schema.TABLES",             "All 9 base tables found",        "PASS"),
        ("TC03", "Sample data row counts",         "COUNT(*) per table",                          "All tables meet minimum counts", "PASS"),
        ("TC04", "Successful DB connection",       "test_connection()",                           "(True, 'Connected to ...')",     "PASS"),
        ("TC05", "Flight search",                  "search_flights(DEL, BOM, 2026-11-05, Economy)","≥1 result, no Cancelled flights","PASS"),
        ("TC06", "Passenger registration",         "add_passenger() + get_passenger_by_id()",     "Record created and retrieved",   "PASS"),
        ("TC07", "Booking creation",               "create_booking() with valid data",            "booking_reference, ticket_id returned","PASS"),
        ("TC08", "Unique booking reference",       "generate_booking_reference() × 500",          "All 500 unique, BK prefix, len 8","PASS"),
        ("TC09", "Duplicate seat rejection",       "Same seat, same flight, 2nd booking",         "RuntimeError or IntegrityError", "PASS"),
        ("TC10", "Capacity overflow rejection",    "Fill all Business seats, then one more",      "RuntimeError raised",            "PASS"),
        ("TC11", "Invalid FK rejection",           "create_booking(flight_id=99999)",             "RuntimeError raised",            "PASS"),
        ("TC12", "Invalid travel class",           "validate_travel_class('FirstClass')",         "Returns (False, msg)",           "PASS"),
        ("TC13", "Negative fare rejection",        "validate_fare(-500); INSERT with -1 fare",    "Validator fails; MySQLError",    "PASS"),
        ("TC14", "Cancelled flight booking",       "create_booking on Cancelled flight_id=10",    "RuntimeError raised by trigger", "PASS"),
        ("TC15", "Booking cancellation",           "cancel_booking(booking_id)",                  "booking_status = 'Cancelled'",   "PASS"),
        ("TC16", "Seat release after cancel",      "Inspect tickets after cancellation",          "All tickets status = 'Cancelled'","PASS"),
        ("TC17", "Payment status",                 "get_payments_for_booking(BK001ABC)",          "Completed or Refunded status",   "PASS"),
        ("TC18", "JOIN query correctness",         "5-table JOIN on BK001ABC",                    "Arjun Sharma, 6E-201, DEL→BOM",  "PASS"),
        ("TC19", "Revenue report accuracy",        "get_revenue_by_airline()",                    "3 airlines, total > 0",          "PASS"),
        ("TC20", "Transaction rollback",           "create_booking(flight_id=99999)",             "No orphan booking in DB",        "PASS"),
        ("TC21", "Connection error handling",      "Inject wrong password via monkeypatch",       "RuntimeError or MySQLError",     "PASS"),
    ]
    t = doc.add_table(rows=len(tc_data)+1, cols=5)
    t.style = "Table Grid"
    for cell, hdr in zip(t.rows[0].cells, ["TC ID","Objective","Input","Expected","Result"]):
        cell.text = hdr
        cell.paragraphs[0].runs[0].bold = True
        set_cell_bg(cell, "1F4E79")
        cell.paragraphs[0].runs[0].font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)
    for i, row_data in enumerate(tc_data):
        for j, val in enumerate(row_data):
            t.rows[i+1].cells[j].text = val
            t.rows[i+1].cells[j].paragraphs[0].runs[0].font.size = Pt(9)
        if row_data[4] == "PASS":
            set_cell_bg(t.rows[i+1].cells[4], "C6EFCE")
    doc.add_paragraph()

    # ═══════════════════════════════════════════════════════════════
    # SECTION 25: SCREENSHOTS & OUTPUT
    # ═══════════════════════════════════════════════════════════════
    add_heading(doc, "25. Project Output and Screenshots", 1)
    add_para(doc,
        "This section presents genuine application screenshots captured from the live Tkinter frontend "
        "connected to the MySQL database (flight_booking_db). Each figure includes a descriptive caption "
        "explaining the user interface elements and the database records retrieved. "
        "For features where a dedicated separate screen was not captured, the functionality and "
        "underlying database operations are described directly using real automated test results and "
        "verified SQL query execution outputs."
    )

    # Detailed specifications for captured screenshots
    screenshot_catalog = [
        (
            "01_dashboard.png",
            "Application Dashboard with Live Database Statistics (3 Airlines, 10 Flights, 10 Passengers, 13 Bookings, and Total Revenue of ₹ 49,280.00) and Upcoming Flights Table",
        ),
        (
            "02_flight_search_form.png",
            "Flight Search Input Interface with Origin, Destination, Travel Date (2026-10-28), and Travel Class Selection Dropdown",
        ),
        (
            "03_flight_search_results.png",
            "Flight Search Query Results for New Delhi (DEL) to Mumbai (BOM) on 2026-11-05 Displaying Flight 6E-201, 2h 10m Duration, ₹ 3,500.00 Base Fare, and 166 Available Seats",
        ),
        (
            "05_passenger_list.png",
            "Passenger Management Screen Displaying Passenger Details Entry Form (Left) and Live Passenger Table Retrieved from MySQL (Right)",
        ),
        (
            "06_booking_form.png",
            "New Booking Wizard with Flight Selection (6E-301), Passenger Selection (Arjun Sharma), Seat Allocation (E12A), Business Class Availability Check (18 / 20 Seats), and Fare Calculation (₹ 10,500.00)",
        ),
        (
            "07_booking_confirmed.png",
            "Booking Detail View Displaying Confirmed Reservation (Booking Reference: BK2MV3U0), Active Ticket Record, and Initial Status History Audit Entry ('Booking created')",
        ),
        (
            "08_booking_list.png",
            "All Bookings List Displaying Live Reservation Records with Unique References (e.g., BK2MV3U0, BKTEST01, BK012HIJ), Passenger Names, Amounts, and Booking Statuses",
        ),
        (
            "10_cancellation.png",
            "Booking Cancellation Result for Reservation BK2MV3U0 Showing Booking Status Changed to Cancelled, Ticket Status Cancelled, and Audit History Logging Transition at 2026-10-28 21:40:30",
        ),
        (
            "11_payments.png",
            "Payment Records Module Showing Simulated Payment Form and Live Transactions Table Detailing Booking References, Methods (UPI, Credit Card, Debit Card, Net Banking, Wallet), and Completed/Refunded Statuses",
        ),
        (
            "12_revenue_report.png",
            "Revenue by Airline Analytical Report Generated via SQL Aggregation (IndiGo: 6 bookings / ₹ 28,160.00; Air India: 3 bookings / ₹ 14,190.00; SpiceJet: 2 bookings / ₹ 6,930.00)",
        ),
        (
            "13_occupancy_report.png",
            "Flight Occupancy Report Displaying Aircraft Capacity, Tickets Sold, and Occupancy Percentage Calculated by SQL Query Across Scheduled Routes",
        ),
        (
            "14_admin_schedules.png",
            "Flight Schedules Report under Reports Module Displaying Operating Routes, Flight Numbers, Departure/Arrival Timestamps, Base Fares, and Scheduled/Cancelled Statuses",
        ),
    ]

    screenshots_dir = os.path.join(project_root, "screenshots")
    fig_idx = 1
    # Check if ER diagram was embedded as Figure 1
    if os.path.exists(os.path.join(project_root, "diagrams", "er_diagram.png")):
        fig_idx = 2

    for filename, caption_text in screenshot_catalog:
        img_path = os.path.join(screenshots_dir, filename)
        if os.path.exists(img_path):
            try:
                doc.add_picture(img_path, width=Inches(5.8))
                add_para(doc, f"Figure {fig_idx}: {caption_text}", italic=True)
                doc.add_paragraph()
                fig_idx += 1
            except Exception as e:
                add_para(doc, f"[Image file {filename} could not be rendered: {e}]", italic=True)

    # ───────────────────────────────────────────────────────────────
    # Verification and Output for Uncaptured Standalone Screens
    # ───────────────────────────────────────────────────────────────
    add_heading(doc, "Verification of Features Without Standalone Screenshots", 2)
    add_para(doc,
        "The following planned screen captures were integrated into existing interface views or "
        "verified through genuine automated test executions and SQL query outputs rather than "
        "separate standalone images:"
    )

    add_para(doc, "1. Passenger Registration Workflow (Integrated in Passenger Management):", bold=True)
    add_para(doc,
        "In the desktop application architecture, the passenger registration form is positioned side-by-side "
        "with the live passenger table inside the Passenger Management interface (shown in Figure 4 above). "
        "Passenger creation was verified in automated test TC06 (test_TC06PassengerRegistration::test_add_and_retrieve). "
        "Execution result:\n"
        "• Function: add_passenger('Test User TC06', 'tc06.test@sample.com', '9100000006', '1995-01-01')\n"
        "• SQL executed: INSERT INTO passengers (full_name, email, phone, date_of_birth) VALUES (...)\n"
        "• Database Response: Returned auto-increment passenger_id > 0; record verified via SELECT * FROM passengers WHERE passenger_id = pid.\n"
        "• Status: PASSED (verified persistence and constraint integrity)."
    )

    add_para(doc, "2. Booking Detail and Ticket Lookup View:", bold=True)
    add_para(doc,
        "The Booking Detail tab was captured directly after booking confirmation (Figure 6) and following "
        "cancellation (Figure 8). The underlying query logic was also verified in automated test TC18 "
        "(test_TC18_join_query) which executes a multi-table INNER JOIN across bookings, passengers, tickets, "
        "flight_schedules, airlines, and airports for booking reference 'BK001ABC'. "
        "Execution result:\n"
        "• Passenger Name: Arjun Sharma\n"
        "• Airline & Flight: IndiGo Airlines (6E-201)\n"
        "• Route: New Delhi (DEL) → Mumbai (BOM)\n"
        "• Status: PASSED (verified multi-table relational join accuracy)."
    )

    add_para(doc, "3. Seat Availability & Double-Booking Prevention Validation:", bold=True)
    add_para(doc,
        "Double-booking prevention is enforced at the database level by the UNIQUE (flight_id, seat_number) "
        "constraint on the tickets table and the trg_check_seat_capacity trigger. This was rigorously "
        "verified in automated tests TC09 and TC10:\n"
        "• Test TC09 (test_TC09DuplicateSeat::test_duplicate_seat_rejected): Attempting to assign the same seat "
        "(E36A) to a second passenger on flight 9 resulted in an immediate IntegrityError / RuntimeError: "
        "'Duplicate entry for key uq_flight_seat'. Status: PASSED.\n"
        "• Test TC10 (test_TC10_capacity_overflow): Filling all Business seats on flight 7 and attempting one "
        "additional booking triggered trigger trg_check_seat_capacity, raising SQLSTATE 45000: "
        "'No seats available in the selected travel class'. Status: PASSED."
    )

    add_para(doc, "4. Flight and Booking Cancellation Seat Release:", bold=True)
    add_para(doc,
        "Seat release following booking cancellation was verified in automated test TC16 "
        "(TestTC15TC16CancellationAndSeatRelease::test_TC16_seat_release). When cancel_booking() was executed, "
        "all associated ticket rows had their ticket_status updated to 'Cancelled', making the seat immediately "
        "available again for subsequent flight searches. Status: PASSED."
    )

    # ═══════════════════════════════════════════════════════════════
    # CONCLUSION + FUTURE SCOPE + REFERENCES
    # ═══════════════════════════════════════════════════════════════
    add_heading(doc, "26. Conclusion", 1)
    add_para(doc,
        "The Flight Booking System successfully demonstrates all key concepts of Database "
        "Management Systems as required for the B.Tech DBMS PBL assignment. The project "
        "implements a 9-table normalized (3NF) relational database with 6 triggers, 3 views, "
        "parameterized SQL queries, and a fully functional Python Tkinter desktop application. "
        "72 automated tests confirm the correctness of constraint enforcement, transactional "
        "integrity, referential integrity, and business logic. The application connects to a "
        "live MySQL 8 database and all changes made through the GUI persist and are verifiable "
        "through independent SQL queries."
    )

    add_heading(doc, "27. Future Scope", 1)
    future = [
        "Web frontend using Flask or Django for multi-user access.",
        "Real-time seat map visualization.",
        "Integration with a real payment gateway API (Razorpay, Stripe) in a production environment.",
        "Role-based access control (admin vs. passenger vs. airline staff).",
        "Multi-city and connecting flight support.",
        "Email confirmation using SMTP.",
        "Price dynamic pricing engine based on demand and days to departure.",
    ]
    for item in future:
        p = doc.add_paragraph(style="List Bullet")
        p.add_run(item).font.size = Pt(11)

    add_heading(doc, "28. References", 1)
    refs = [
        "Ramakrishnan, R. & Gehrke, J. (2003). Database Management Systems, 3rd Edition. McGraw-Hill.",
        "Connolly, T. & Begg, C. (2015). Database Systems: A Practical Approach to Design, Implementation, and Management, 6th Edition. Pearson.",
        "MySQL 8.0 Reference Manual. https://dev.mysql.com/doc/refman/8.0/en/",
        "Python 3 Documentation. https://docs.python.org/3/",
        "mysql-connector-python Documentation. https://dev.mysql.com/doc/connector-python/en/",
        "Tkinter Documentation. https://docs.python.org/3/library/tkinter.html",
        "pytest Documentation. https://docs.pytest.org/",
    ]
    for ref in refs:
        p = doc.add_paragraph(style="List Number")
        p.add_run(ref).font.size = Pt(10)

    # ═══════════════════════════════════════════════════════════════
    # APPENDICES
    # ═══════════════════════════════════════════════════════════════
    doc.add_page_break()
    add_heading(doc, "Appendix A: Complete SQL Schema", 1)
    add_para(doc, "File: database/schema.sql")
    schema_content = read_file_content(os.path.join(project_root, "database", "schema.sql"))
    # Print in chunks to avoid extremely long code blocks
    lines = schema_content.split("\n")
    chunk_size = 60
    for i in range(0, len(lines), chunk_size):
        add_code_block(doc, "\n".join(lines[i:i+chunk_size]), font_size=7)

    doc.add_page_break()
    add_heading(doc, "Appendix B: Key Python Source Code", 1)

    key_files = [
        ("src/db_connection.py",                       "Database Connection Factory"),
        ("src/validators.py",                          "Input Validators"),
        ("src/repositories/booking_repository.py",     "Booking Repository (Transactional Logic)"),
    ]
    for fpath, title in key_files:
        add_heading(doc, title, 2)
        content = read_file_content(os.path.join(project_root, fpath))
        lines = content.split("\n")
        for i in range(0, len(lines), chunk_size):
            add_code_block(doc, "\n".join(lines[i:i+chunk_size]), font_size=7)
        doc.add_paragraph()

    doc.add_page_break()
    add_heading(doc, "Appendix C: Setup and Execution Instructions", 1)
    add_code_block(doc, """\
# 1. Verify MySQL is running
brew services list | grep mysql
# If not: brew services start mysql

# 2. Navigate to project directory
cd /Users/ayushsawhney/flight_booking_system

# 3. Create and activate virtual environment
python3 -m venv .venv
source .venv/bin/activate

# 4. Install dependencies
pip install -r requirements.txt

# 5. Configure credentials (.env must NOT be committed)
cp .env.example .env
# Edit .env: set DB_PASSWORD to your MySQL root password

# 6. Initialize the database
mysql -u root -p < database/schema.sql
mysql -u root -p flight_booking_db < database/queries.sql

# 7. Run the application
python3 src/main.py

# 8. Run automated tests
python3 -m pytest tests/ -v

# 9. Regenerate the report (after adding screenshots)
python3 src/generate_report.py""")

    # Save
    out_path = os.path.join(project_root, "report", "Flight_Booking_System_Report.docx")
    doc.save(out_path)
    print(f"Report saved: {out_path}")
    return out_path


if __name__ == "__main__":
    build_report()

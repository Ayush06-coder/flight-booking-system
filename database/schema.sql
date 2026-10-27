-- =============================================================================
-- FLIGHT BOOKING SYSTEM — DATABASE SCHEMA (DDL)
-- Database: flight_booking_db
-- MySQL 8.x
-- NOTE: All schedules, fares, and passenger data are SAMPLE/SIMULATED data
--       created for academic demonstration purposes only.
-- =============================================================================

-- Create and select the database
DROP DATABASE IF EXISTS flight_booking_db;
CREATE DATABASE flight_booking_db
    CHARACTER SET utf8mb4
    COLLATE utf8mb4_unicode_ci;

USE flight_booking_db;

-- =============================================================================
-- TABLE 1: airlines
-- Stores airline carrier information.
-- =============================================================================
CREATE TABLE airlines (
    airline_id      INT             NOT NULL AUTO_INCREMENT,
    airline_name    VARCHAR(100)    NOT NULL,
    airline_code    VARCHAR(10)     NOT NULL,
    contact_email   VARCHAR(150)    NOT NULL,
    contact_phone   VARCHAR(20)     NOT NULL,
    CONSTRAINT pk_airlines          PRIMARY KEY (airline_id),
    CONSTRAINT uq_airline_code      UNIQUE      (airline_code),
    CONSTRAINT chk_airline_email    CHECK       (contact_email LIKE '%@%.%')
) ENGINE=InnoDB;

-- =============================================================================
-- TABLE 2: airports
-- Stores airport information with IATA-style codes.
-- =============================================================================
CREATE TABLE airports (
    airport_id      INT             NOT NULL AUTO_INCREMENT,
    airport_code    VARCHAR(10)     NOT NULL,
    airport_name    VARCHAR(150)    NOT NULL,
    city            VARCHAR(100)    NOT NULL,
    country         VARCHAR(100)    NOT NULL DEFAULT 'India',
    CONSTRAINT pk_airports          PRIMARY KEY (airport_id),
    CONSTRAINT uq_airport_code      UNIQUE      (airport_code)
) ENGINE=InnoDB;

-- =============================================================================
-- TABLE 3: aircraft
-- Stores aircraft fleet records linked to an airline.
-- economy_seats + business_seats must equal total_seats (enforced by trigger).
-- =============================================================================
CREATE TABLE aircraft (
    aircraft_id             INT             NOT NULL AUTO_INCREMENT,
    airline_id              INT             NOT NULL,
    aircraft_model          VARCHAR(100)    NOT NULL,
    registration_number     VARCHAR(20)     NOT NULL,
    total_seats             INT             NOT NULL,
    economy_seats           INT             NOT NULL,
    business_seats          INT             NOT NULL,
    CONSTRAINT pk_aircraft              PRIMARY KEY (aircraft_id),
    CONSTRAINT uq_registration          UNIQUE      (registration_number),
    CONSTRAINT fk_aircraft_airline      FOREIGN KEY (airline_id)
        REFERENCES airlines(airline_id)   ON DELETE RESTRICT ON UPDATE CASCADE,
    CONSTRAINT chk_total_seats          CHECK (total_seats > 0),
    CONSTRAINT chk_economy_seats        CHECK (economy_seats >= 0),
    CONSTRAINT chk_business_seats       CHECK (business_seats >= 0),
    CONSTRAINT chk_seat_sum             CHECK (economy_seats + business_seats = total_seats)
) ENGINE=InnoDB;

-- =============================================================================
-- TABLE 4: flight_schedules
-- Stores individual flight instances with full departure/arrival timestamps.
-- Overnight and cross-day flights are supported via DATETIME columns.
-- =============================================================================
CREATE TABLE flight_schedules (
    flight_id               INT             NOT NULL AUTO_INCREMENT,
    airline_id              INT             NOT NULL,
    aircraft_id             INT             NOT NULL,
    origin_airport_id       INT             NOT NULL,
    destination_airport_id  INT             NOT NULL,
    flight_number           VARCHAR(20)     NOT NULL,
    departure_datetime      DATETIME        NOT NULL,
    arrival_datetime        DATETIME        NOT NULL,
    base_fare               DECIMAL(10,2)   NOT NULL DEFAULT 0.00,
    flight_status           ENUM(
                                'Scheduled',
                                'Boarding',
                                'Departed',
                                'Arrived',
                                'Cancelled',
                                'Delayed'
                            )               NOT NULL DEFAULT 'Scheduled',
    CONSTRAINT pk_flight_schedules          PRIMARY KEY (flight_id),
    CONSTRAINT fk_fs_airline                FOREIGN KEY (airline_id)
        REFERENCES airlines(airline_id)     ON DELETE RESTRICT ON UPDATE CASCADE,
    CONSTRAINT fk_fs_aircraft               FOREIGN KEY (aircraft_id)
        REFERENCES aircraft(aircraft_id)    ON DELETE RESTRICT ON UPDATE CASCADE,
    CONSTRAINT fk_fs_origin                 FOREIGN KEY (origin_airport_id)
        REFERENCES airports(airport_id)     ON DELETE RESTRICT ON UPDATE CASCADE,
    CONSTRAINT fk_fs_destination            FOREIGN KEY (destination_airport_id)
        REFERENCES airports(airport_id)     ON DELETE RESTRICT ON UPDATE CASCADE,
    CONSTRAINT chk_diff_airports            CHECK (origin_airport_id <> destination_airport_id),
    CONSTRAINT chk_arrival_after_departure  CHECK (arrival_datetime > departure_datetime),
    CONSTRAINT chk_base_fare                CHECK (base_fare >= 0)
) ENGINE=InnoDB;

-- Index for fast flight search by route and date
CREATE INDEX idx_fs_route_date
    ON flight_schedules (origin_airport_id, destination_airport_id, departure_datetime);

CREATE INDEX idx_fs_flight_number
    ON flight_schedules (flight_number);

-- =============================================================================
-- TABLE 5: passengers
-- Stores registered passenger profiles.
-- Only minimal personal data is collected (academic prototype).
-- =============================================================================
CREATE TABLE passengers (
    passenger_id    INT             NOT NULL AUTO_INCREMENT,
    full_name       VARCHAR(150)    NOT NULL,
    email           VARCHAR(150)    NOT NULL,
    phone           VARCHAR(20)     NOT NULL,
    date_of_birth   DATE                    ,
    created_at      DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT pk_passengers        PRIMARY KEY (passenger_id),
    CONSTRAINT uq_passenger_email   UNIQUE      (email),
    CONSTRAINT chk_passenger_email  CHECK       (email LIKE '%@%.%')
) ENGINE=InnoDB;

CREATE INDEX idx_passenger_name ON passengers (full_name);

-- =============================================================================
-- TABLE 6: bookings
-- Overall reservation record. One booking per transaction (may cover multiple
-- passengers via the tickets table).
-- =============================================================================
CREATE TABLE bookings (
    booking_id          INT             NOT NULL AUTO_INCREMENT,
    booking_reference   VARCHAR(20)     NOT NULL,
    passenger_id        INT             NOT NULL,
    booking_datetime    DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP,
    total_amount        DECIMAL(10,2)   NOT NULL DEFAULT 0.00,
    booking_status      ENUM(
                            'Pending',
                            'Confirmed',
                            'Cancelled',
                            'Completed'
                        )               NOT NULL DEFAULT 'Pending',
    CONSTRAINT pk_bookings              PRIMARY KEY (booking_id),
    CONSTRAINT uq_booking_reference     UNIQUE      (booking_reference),
    CONSTRAINT fk_booking_passenger     FOREIGN KEY (passenger_id)
        REFERENCES passengers(passenger_id) ON DELETE RESTRICT ON UPDATE CASCADE,
    CONSTRAINT chk_total_amount         CHECK (total_amount >= 0)
) ENGINE=InnoDB;

CREATE INDEX idx_booking_reference  ON bookings (booking_reference);
CREATE INDEX idx_booking_passenger  ON bookings (passenger_id);
CREATE INDEX idx_booking_status     ON bookings (booking_status);

-- =============================================================================
-- TABLE 7: tickets
-- Per-passenger ticket record. Links a booking to a specific flight, seat, and
-- fare class. The UNIQUE constraint on (flight_id, seat_number) prevents
-- double-seat assignment on the same flight.
-- =============================================================================
CREATE TABLE tickets (
    ticket_id       INT             NOT NULL AUTO_INCREMENT,
    booking_id      INT             NOT NULL,
    passenger_id    INT             NOT NULL,
    flight_id       INT             NOT NULL,
    seat_number     VARCHAR(10)     NOT NULL,
    travel_class    ENUM('Economy', 'Business') NOT NULL DEFAULT 'Economy',
    ticket_fare     DECIMAL(10,2)   NOT NULL DEFAULT 0.00,
    ticket_status   ENUM(
                        'Active',
                        'Cancelled',
                        'Used'
                    )               NOT NULL DEFAULT 'Active',
    CONSTRAINT pk_tickets               PRIMARY KEY (ticket_id),
    CONSTRAINT fk_ticket_booking        FOREIGN KEY (booking_id)
        REFERENCES bookings(booking_id) ON DELETE RESTRICT ON UPDATE CASCADE,
    CONSTRAINT fk_ticket_passenger      FOREIGN KEY (passenger_id)
        REFERENCES passengers(passenger_id) ON DELETE RESTRICT ON UPDATE CASCADE,
    CONSTRAINT fk_ticket_flight         FOREIGN KEY (flight_id)
        REFERENCES flight_schedules(flight_id) ON DELETE RESTRICT ON UPDATE CASCADE,
    -- Prevents two active tickets from sharing a seat on the same flight
    CONSTRAINT uq_flight_seat           UNIQUE (flight_id, seat_number),
    CONSTRAINT chk_ticket_fare          CHECK (ticket_fare >= 0)
) ENGINE=InnoDB;

CREATE INDEX idx_ticket_booking     ON tickets (booking_id);
CREATE INDEX idx_ticket_flight      ON tickets (flight_id);
CREATE INDEX idx_ticket_passenger   ON tickets (passenger_id);

-- =============================================================================
-- TABLE 8: payments
-- Simulated payment records linked to bookings.
-- NOTE: No real financial data is stored or processed.
-- =============================================================================
CREATE TABLE payments (
    payment_id              INT             NOT NULL AUTO_INCREMENT,
    booking_id              INT             NOT NULL,
    amount                  DECIMAL(10,2)   NOT NULL,
    payment_method          ENUM(
                                'Credit Card',
                                'Debit Card',
                                'UPI',
                                'Net Banking',
                                'Wallet'
                            )               NOT NULL,
    payment_status          ENUM(
                                'Pending',
                                'Completed',
                                'Failed',
                                'Refunded'
                            )               NOT NULL DEFAULT 'Pending',
    transaction_reference   VARCHAR(50)     NOT NULL,
    payment_datetime        DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT pk_payments              PRIMARY KEY (payment_id),
    CONSTRAINT uq_txn_reference         UNIQUE      (transaction_reference),
    CONSTRAINT fk_payment_booking       FOREIGN KEY (booking_id)
        REFERENCES bookings(booking_id) ON DELETE RESTRICT ON UPDATE CASCADE,
    CONSTRAINT chk_payment_amount       CHECK (amount >= 0)
) ENGINE=InnoDB;

CREATE INDEX idx_payment_booking    ON payments (booking_id);
CREATE INDEX idx_payment_status     ON payments (payment_status);

-- =============================================================================
-- TABLE 9: booking_status_history
-- Audit trail for every booking status change.
-- =============================================================================
CREATE TABLE booking_status_history (
    history_id      INT             NOT NULL AUTO_INCREMENT,
    booking_id      INT             NOT NULL,
    old_status      VARCHAR(20)             ,
    new_status      VARCHAR(20)     NOT NULL,
    changed_at      DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP,
    remarks         VARCHAR(255)            ,
    CONSTRAINT pk_history               PRIMARY KEY (history_id),
    CONSTRAINT fk_history_booking       FOREIGN KEY (booking_id)
        REFERENCES bookings(booking_id) ON DELETE RESTRICT ON UPDATE CASCADE
) ENGINE=InnoDB;

CREATE INDEX idx_history_booking    ON booking_status_history (booking_id);

-- =============================================================================
-- VIEWS
-- =============================================================================

-- View: v_flight_booking_details
-- Provides a denormalized view of ticket details for reporting.
CREATE OR REPLACE VIEW v_flight_booking_details AS
SELECT
    b.booking_id,
    b.booking_reference,
    p.full_name              AS passenger_name,
    p.email                  AS passenger_email,
    p.phone                  AS passenger_phone,
    al.airline_name,
    al.airline_code,
    fs.flight_number,
    orig.airport_code        AS origin_code,
    orig.city                AS origin_city,
    dest.airport_code        AS destination_code,
    dest.city                AS destination_city,
    fs.departure_datetime,
    fs.arrival_datetime,
    TIMESTAMPDIFF(MINUTE, fs.departure_datetime, fs.arrival_datetime)
                             AS duration_minutes,
    t.seat_number,
    t.travel_class,
    t.ticket_fare,
    t.ticket_status,
    b.booking_status,
    b.booking_datetime,
    b.total_amount,
    py.payment_status,
    py.payment_method,
    py.transaction_reference
FROM bookings b
JOIN passengers       p    ON b.passenger_id          = p.passenger_id
JOIN tickets          t    ON t.booking_id             = b.booking_id
JOIN flight_schedules fs   ON t.flight_id              = fs.flight_id
JOIN airlines         al   ON fs.airline_id            = al.airline_id
JOIN airports         orig ON fs.origin_airport_id     = orig.airport_id
JOIN airports         dest ON fs.destination_airport_id= dest.airport_id
LEFT JOIN payments    py   ON py.booking_id            = b.booking_id;

-- View: v_seat_availability
-- Shows remaining seats per flight and class.
CREATE OR REPLACE VIEW v_seat_availability AS
SELECT
    fs.flight_id,
    al.airline_name,
    fs.flight_number,
    orig.city                AS origin_city,
    dest.city                AS destination_city,
    fs.departure_datetime,
    fs.arrival_datetime,
    fs.flight_status,
    fs.base_fare,
    ac.economy_seats         AS total_economy,
    ac.business_seats        AS total_business,
    COALESCE(SUM(CASE WHEN t.travel_class = 'Economy'  AND t.ticket_status = 'Active' THEN 1 ELSE 0 END), 0)
                             AS booked_economy,
    COALESCE(SUM(CASE WHEN t.travel_class = 'Business' AND t.ticket_status = 'Active' THEN 1 ELSE 0 END), 0)
                             AS booked_business,
    ac.economy_seats  - COALESCE(SUM(CASE WHEN t.travel_class = 'Economy'  AND t.ticket_status = 'Active' THEN 1 ELSE 0 END), 0)
                             AS available_economy,
    ac.business_seats - COALESCE(SUM(CASE WHEN t.travel_class = 'Business' AND t.ticket_status = 'Active' THEN 1 ELSE 0 END), 0)
                             AS available_business
FROM flight_schedules fs
JOIN airlines         al   ON fs.airline_id            = al.airline_id
JOIN airports         orig ON fs.origin_airport_id     = orig.airport_id
JOIN airports         dest ON fs.destination_airport_id= dest.airport_id
JOIN aircraft         ac   ON fs.aircraft_id           = ac.aircraft_id
LEFT JOIN tickets     t    ON t.flight_id              = fs.flight_id
GROUP BY
    fs.flight_id, al.airline_name, fs.flight_number,
    orig.city, dest.city, fs.departure_datetime, fs.arrival_datetime,
    fs.flight_status, fs.base_fare, ac.economy_seats, ac.business_seats;

-- View: v_revenue_summary
-- Aggregates completed payment revenue by airline and route.
CREATE OR REPLACE VIEW v_revenue_summary AS
SELECT
    al.airline_name,
    orig.city                           AS origin_city,
    dest.city                           AS destination_city,
    COUNT(DISTINCT b.booking_id)        AS total_bookings,
    SUM(py.amount)                      AS total_revenue,
    AVG(py.amount)                      AS avg_revenue_per_booking
FROM payments py
JOIN bookings           b    ON py.booking_id           = b.booking_id
JOIN tickets            t    ON t.booking_id            = b.booking_id
JOIN flight_schedules   fs   ON t.flight_id             = fs.flight_id
JOIN airlines           al   ON fs.airline_id           = al.airline_id
JOIN airports           orig ON fs.origin_airport_id    = orig.airport_id
JOIN airports           dest ON fs.destination_airport_id = dest.airport_id
WHERE py.payment_status = 'Completed'
GROUP BY al.airline_name, orig.city, dest.city;

-- =============================================================================
-- TRIGGERS
-- =============================================================================

DELIMITER $$

-- Trigger: trg_booking_status_insert
-- Automatically records initial booking status in history on INSERT.
CREATE TRIGGER trg_booking_status_insert
AFTER INSERT ON bookings
FOR EACH ROW
BEGIN
    INSERT INTO booking_status_history (booking_id, old_status, new_status, remarks)
    VALUES (NEW.booking_id, NULL, NEW.booking_status, 'Booking created');
END$$

-- Trigger: trg_booking_status_update
-- Records status changes in booking_status_history on UPDATE.
CREATE TRIGGER trg_booking_status_update
AFTER UPDATE ON bookings
FOR EACH ROW
BEGIN
    IF OLD.booking_status <> NEW.booking_status THEN
        INSERT INTO booking_status_history (booking_id, old_status, new_status, remarks)
        VALUES (NEW.booking_id, OLD.booking_status, NEW.booking_status,
                CONCAT('Status changed from ', OLD.booking_status, ' to ', NEW.booking_status));
    END IF;
END$$

-- Trigger: trg_validate_aircraft_seats
-- Validates economy + business = total before aircraft INSERT.
CREATE TRIGGER trg_validate_aircraft_seats
BEFORE INSERT ON aircraft
FOR EACH ROW
BEGIN
    IF NEW.economy_seats + NEW.business_seats <> NEW.total_seats THEN
        SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'economy_seats + business_seats must equal total_seats';
    END IF;
END$$

-- Trigger: trg_validate_aircraft_seats_update
-- Validates economy + business = total before aircraft UPDATE.
CREATE TRIGGER trg_validate_aircraft_seats_update
BEFORE UPDATE ON aircraft
FOR EACH ROW
BEGIN
    IF NEW.economy_seats + NEW.business_seats <> NEW.total_seats THEN
        SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'economy_seats + business_seats must equal total_seats';
    END IF;
END$$

-- Trigger: trg_prevent_cancelled_flight_booking
-- Prevents inserting a ticket for a cancelled flight.
CREATE TRIGGER trg_prevent_cancelled_flight_booking
BEFORE INSERT ON tickets
FOR EACH ROW
BEGIN
    DECLARE v_status VARCHAR(20);
    SELECT flight_status INTO v_status
    FROM flight_schedules WHERE flight_id = NEW.flight_id;
    IF v_status = 'Cancelled' THEN
        SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'Cannot book a ticket on a cancelled flight';
    END IF;
END$$

-- Trigger: trg_check_seat_capacity
-- Prevents overbooking beyond aircraft capacity for each class.
CREATE TRIGGER trg_check_seat_capacity
BEFORE INSERT ON tickets
FOR EACH ROW
BEGIN
    DECLARE v_capacity   INT;
    DECLARE v_booked     INT;

    -- Get class capacity from aircraft
    IF NEW.travel_class = 'Economy' THEN
        SELECT ac.economy_seats INTO v_capacity
        FROM flight_schedules fs
        JOIN aircraft ac ON fs.aircraft_id = ac.aircraft_id
        WHERE fs.flight_id = NEW.flight_id;
    ELSE
        SELECT ac.business_seats INTO v_capacity
        FROM flight_schedules fs
        JOIN aircraft ac ON fs.aircraft_id = ac.aircraft_id
        WHERE fs.flight_id = NEW.flight_id;
    END IF;

    -- Count currently active tickets for this class
    SELECT COUNT(*) INTO v_booked
    FROM tickets
    WHERE flight_id = NEW.flight_id
      AND travel_class = NEW.travel_class
      AND ticket_status = 'Active';

    IF v_booked >= v_capacity THEN
        SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'No seats available in the selected travel class';
    END IF;
END$$

DELIMITER ;

-- =============================================================================
-- END OF SCHEMA
-- =============================================================================


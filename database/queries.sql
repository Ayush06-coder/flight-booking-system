-- =============================================================================
-- FLIGHT BOOKING SYSTEM — DML: SAMPLE DATA & DEMO QUERIES
-- Database: flight_booking_db
-- NOTE: ALL flight schedules, prices, passenger records, and payment
--       transactions in this file are SIMULATED SAMPLE DATA created for
--       academic demonstration purposes only.
-- =============================================================================

USE flight_booking_db;

-- =============================================================================
-- SECTION 1: SAMPLE DATA INSERTS
-- =============================================================================

-- --------------------------------------------------------------------
-- Airlines (3 records — SAMPLE DATA)
-- --------------------------------------------------------------------
INSERT INTO airlines (airline_name, airline_code, contact_email, contact_phone) VALUES
('IndiGo Airlines',  '6E', 'support@indigo.sample',   '+91-9988001122'),
('Air India',        'AI', 'support@airindia.sample',  '+91-9988002233'),
('SpiceJet',         'SG', 'support@spicejet.sample',  '+91-9988003344');

-- --------------------------------------------------------------------
-- Airports (8 records — SAMPLE DATA, realistic IATA codes)
-- --------------------------------------------------------------------
INSERT INTO airports (airport_code, airport_name, city, country) VALUES
('DEL', 'Indira Gandhi International Airport',   'New Delhi',  'India'),
('BOM', 'Chhatrapati Shivaji Maharaj Int. Airport', 'Mumbai',  'India'),
('BLR', 'Kempegowda International Airport',      'Bengaluru',  'India'),
('MAA', 'Chennai International Airport',          'Chennai',   'India'),
('CCU', 'Netaji Subhas Chandra Bose Int. Airport','Kolkata',   'India'),
('HYD', 'Rajiv Gandhi International Airport',     'Hyderabad', 'India'),
('COK', 'Cochin International Airport',           'Kochi',     'India'),
('AMD', 'Sardar Vallabhbhai Patel Int. Airport',  'Ahmedabad', 'India');

-- --------------------------------------------------------------------
-- Aircraft (5 records — SAMPLE DATA)
-- --------------------------------------------------------------------
INSERT INTO aircraft (airline_id, aircraft_model, registration_number, total_seats, economy_seats, business_seats) VALUES
(1, 'Airbus A320',    'VT-IGA',  180, 168, 12),
(1, 'Airbus A321neo', 'VT-IGB',  220, 200, 20),
(2, 'Boeing 787-8',   'VT-ANA',  256, 220, 36),
(2, 'Airbus A320',    'VT-ANB',  180, 162, 18),
(3, 'Boeing 737-800', 'VT-SGJ',  189, 177, 12);

-- --------------------------------------------------------------------
-- Flight Schedules (10 records — SAMPLE/SIMULATED DATA)
-- Prices and times are fictitious. Overnight flights are included.
-- --------------------------------------------------------------------
INSERT INTO flight_schedules
    (airline_id, aircraft_id, origin_airport_id, destination_airport_id,
     flight_number, departure_datetime, arrival_datetime, base_fare, flight_status)
VALUES
-- IndiGo
(1, 1, 1, 2, '6E-201',  '2026-11-05 06:00:00', '2026-11-05 08:10:00',  3500.00, 'Scheduled'),
(1, 1, 2, 1, '6E-202',  '2026-11-05 09:30:00', '2026-11-05 11:40:00',  3500.00, 'Scheduled'),
(1, 2, 1, 3, '6E-301',  '2026-11-06 07:15:00', '2026-11-06 09:45:00',  4200.00, 'Scheduled'),
(1, 2, 3, 5, '6E-401',  '2026-11-07 14:00:00', '2026-11-07 17:30:00',  5100.00, 'Scheduled'),
-- Air India
(2, 3, 1, 4, 'AI-501',  '2026-11-05 22:00:00', '2026-11-06 00:30:00',  4800.00, 'Scheduled'), -- overnight
(2, 3, 4, 1, 'AI-502',  '2026-11-06 05:00:00', '2026-11-06 07:45:00',  4800.00, 'Scheduled'),
(2, 4, 1, 6, 'AI-601',  '2026-11-08 10:30:00', '2026-11-08 12:30:00',  3900.00, 'Scheduled'),
-- SpiceJet
(3, 5, 1, 7, 'SG-701',  '2026-11-09 08:00:00', '2026-11-09 10:45:00',  4500.00, 'Scheduled'),
(3, 5, 2, 8, 'SG-801',  '2026-11-10 13:00:00', '2026-11-10 14:30:00',  2800.00, 'Scheduled'),
(1, 1, 6, 2, '6E-901',  '2026-11-10 16:00:00', '2026-11-10 17:30:00',  3100.00, 'Cancelled');

-- --------------------------------------------------------------------
-- Passengers (10 records — SAMPLE/FICTITIOUS DATA)
-- --------------------------------------------------------------------
INSERT INTO passengers (full_name, email, phone, date_of_birth) VALUES
('Arjun Sharma',       'arjun.sharma@sample.com',   '9876543210', '1995-04-12'),
('Priya Nair',         'priya.nair@sample.com',     '9876543211', '1992-08-25'),
('Rahul Verma',        'rahul.verma@sample.com',    '9876543212', '1988-01-30'),
('Sneha Patel',        'sneha.patel@sample.com',    '9876543213', '1997-11-05'),
('Karan Mehta',        'karan.mehta@sample.com',    '9876543214', '1990-03-17'),
('Divya Rao',          'divya.rao@sample.com',      '9876543215', '1994-07-22'),
('Amit Kumar',         'amit.kumar@sample.com',     '9876543216', '1985-12-10'),
('Pooja Singh',        'pooja.singh@sample.com',    '9876543217', '1999-05-01'),
('Vikram Joshi',       'vikram.joshi@sample.com',   '9876543218', '1993-09-14'),
('Ananya Das',         'ananya.das@sample.com',     '9876543219', '1996-02-28');

-- --------------------------------------------------------------------
-- Bookings (12 records — SAMPLE DATA)
-- --------------------------------------------------------------------
INSERT INTO bookings (booking_reference, passenger_id, booking_datetime, total_amount, booking_status) VALUES
('BK001ABC', 1,  '2026-10-20 10:00:00',  3850.00, 'Confirmed'),
('BK002DEF', 2,  '2026-10-20 11:00:00',  5280.00, 'Confirmed'),
('BK003GHI', 3,  '2026-10-21 09:30:00',  4620.00, 'Confirmed'),
('BK004JKL', 4,  '2026-10-21 14:00:00',  5280.00, 'Confirmed'),
('BK005MNO', 5,  '2026-10-22 08:15:00',  3850.00, 'Confirmed'),
('BK006PQR', 6,  '2026-10-22 16:45:00',  5610.00, 'Confirmed'),
('BK007STU', 7,  '2026-10-23 10:00:00',  4950.00, 'Confirmed'),
('BK008VWX', 8,  '2026-10-24 13:30:00',  3080.00, 'Confirmed'),
('BK009YZA', 9,  '2026-10-24 15:00:00',  4620.00, 'Confirmed'),
('BK010BCD', 10, '2026-10-25 09:00:00',  3850.00, 'Confirmed'),
('BK011EFG', 1,  '2026-10-25 17:00:00',  5280.00, 'Cancelled'),
('BK012HIJ', 3,  '2026-10-26 11:00:00',  4290.00, 'Confirmed');

-- --------------------------------------------------------------------
-- Tickets (12 records — SAMPLE DATA)
-- seat_number format: [class_initial][row][A-F]
-- Economy class has rows 1-40; Business class rows 1-6 (per aircraft model)
-- --------------------------------------------------------------------
INSERT INTO tickets (booking_id, passenger_id, flight_id, seat_number, travel_class, ticket_fare, ticket_status) VALUES
(1,  1,  1, 'E12A', 'Economy',  3850.00, 'Active'),
(2,  2,  3, 'B01A', 'Business', 5280.00, 'Active'),
(3,  3,  5, 'B02A', 'Business', 4620.00, 'Active'),
(4,  4,  3, 'B01B', 'Business', 5280.00, 'Active'),
(5,  5,  2, 'E15C', 'Economy',  3850.00, 'Active'),
(6,  6,  4, 'B02B', 'Business', 5610.00, 'Active'),
(7,  7,  6, 'E20D', 'Economy',  4950.00, 'Active'),
(8,  8,  9, 'E05B', 'Economy',  3080.00, 'Active'),
(9,  9,  7, 'E10A', 'Economy',  4620.00, 'Active'),
(10, 10, 8, 'E08F', 'Economy',  3850.00, 'Active'),
(11, 1,  3, 'E30A', 'Economy',  5280.00, 'Cancelled'),
(12, 3,  1, 'E14B', 'Economy',  4290.00, 'Active');

-- --------------------------------------------------------------------
-- Payments (12 records — SIMULATED TRANSACTIONS)
-- Transaction references are simulated and not real payment gateway IDs.
-- --------------------------------------------------------------------
INSERT INTO payments (booking_id, amount, payment_method, payment_status, transaction_reference, payment_datetime) VALUES
(1,   3850.00, 'UPI',         'Completed', 'TXN-SIM-20261020-0001', '2026-10-20 10:02:00'),
(2,   5280.00, 'Credit Card', 'Completed', 'TXN-SIM-20261020-0002', '2026-10-20 11:03:00'),
(3,   4620.00, 'Net Banking', 'Completed', 'TXN-SIM-20261021-0003', '2026-10-21 09:35:00'),
(4,   5280.00, 'Debit Card',  'Completed', 'TXN-SIM-20261021-0004', '2026-10-21 14:05:00'),
(5,   3850.00, 'UPI',         'Completed', 'TXN-SIM-20261022-0005', '2026-10-22 08:20:00'),
(6,   5610.00, 'Credit Card', 'Completed', 'TXN-SIM-20261022-0006', '2026-10-22 16:50:00'),
(7,   4950.00, 'Wallet',      'Completed', 'TXN-SIM-20261023-0007', '2026-10-23 10:05:00'),
(8,   3080.00, 'UPI',         'Completed', 'TXN-SIM-20261024-0008', '2026-10-24 13:35:00'),
(9,   4620.00, 'Net Banking', 'Completed', 'TXN-SIM-20261024-0009', '2026-10-24 15:05:00'),
(10,  3850.00, 'Credit Card', 'Completed', 'TXN-SIM-20261025-0010', '2026-10-25 09:05:00'),
(11,  5280.00, 'UPI',         'Refunded',  'TXN-SIM-20261025-0011', '2026-10-25 17:05:00'),
(12,  4290.00, 'Debit Card',  'Completed', 'TXN-SIM-20261026-0012', '2026-10-26 11:05:00');


-- =============================================================================
-- SECTION 2: DEMO SQL QUERIES
-- All queries below are executable against flight_booking_db.
-- =============================================================================

-- --------------------------------------------------------------------
-- Q01: SELECT all airlines
-- --------------------------------------------------------------------
SELECT * FROM airlines ORDER BY airline_name;

-- --------------------------------------------------------------------
-- Q02: SELECT all airports ordered by city
-- --------------------------------------------------------------------
SELECT airport_code, airport_name, city, country FROM airports ORDER BY city;

-- --------------------------------------------------------------------
-- Q03: Flight search — DEL to BOM on 2026-11-05
-- --------------------------------------------------------------------
SELECT
    fs.flight_id,
    al.airline_name,
    fs.flight_number,
    orig.city       AS origin,
    dest.city       AS destination,
    fs.departure_datetime,
    fs.arrival_datetime,
    TIMESTAMPDIFF(MINUTE, fs.departure_datetime, fs.arrival_datetime) AS duration_min,
    fs.base_fare,
    fs.flight_status
FROM flight_schedules fs
JOIN airlines  al   ON fs.airline_id            = al.airline_id
JOIN airports  orig ON fs.origin_airport_id     = orig.airport_id
JOIN airports  dest ON fs.destination_airport_id= dest.airport_id
WHERE orig.airport_code = 'DEL'
  AND dest.airport_code = 'BOM'
  AND DATE(fs.departure_datetime) = '2026-11-05'
  AND fs.flight_status <> 'Cancelled'
ORDER BY fs.departure_datetime;

-- --------------------------------------------------------------------
-- Q04: Seat availability for all scheduled flights
-- --------------------------------------------------------------------
SELECT
    flight_id,
    airline_name,
    flight_number,
    origin_city,
    destination_city,
    departure_datetime,
    available_economy,
    available_business,
    flight_status
FROM v_seat_availability
WHERE flight_status = 'Scheduled'
ORDER BY departure_datetime;

-- --------------------------------------------------------------------
-- Q05: All bookings with passenger and flight details (JOIN)
-- --------------------------------------------------------------------
SELECT
    b.booking_reference,
    p.full_name,
    al.airline_name,
    fs.flight_number,
    orig.city       AS from_city,
    dest.city       AS to_city,
    fs.departure_datetime,
    t.seat_number,
    t.travel_class,
    t.ticket_fare,
    b.booking_status
FROM bookings b
JOIN passengers       p    ON b.passenger_id          = p.passenger_id
JOIN tickets          t    ON t.booking_id             = b.booking_id
JOIN flight_schedules fs   ON t.flight_id              = fs.flight_id
JOIN airlines         al   ON fs.airline_id            = al.airline_id
JOIN airports         orig ON fs.origin_airport_id     = orig.airport_id
JOIN airports         dest ON fs.destination_airport_id= dest.airport_id
ORDER BY b.booking_id;

-- --------------------------------------------------------------------
-- Q06: Passenger booking history for passenger_id = 1
-- --------------------------------------------------------------------
SELECT
    b.booking_reference,
    fs.flight_number,
    orig.city       AS from_city,
    dest.city       AS to_city,
    fs.departure_datetime,
    t.travel_class,
    t.seat_number,
    t.ticket_fare,
    b.booking_status,
    py.payment_status
FROM bookings b
JOIN tickets          t    ON t.booking_id             = b.booking_id
JOIN flight_schedules fs   ON t.flight_id              = fs.flight_id
JOIN airports         orig ON fs.origin_airport_id     = orig.airport_id
JOIN airports         dest ON fs.destination_airport_id= dest.airport_id
LEFT JOIN payments    py   ON py.booking_id            = b.booking_id
WHERE b.passenger_id = 1
ORDER BY b.booking_datetime DESC;

-- --------------------------------------------------------------------
-- Q07: COUNT of bookings grouped by status
-- --------------------------------------------------------------------
SELECT booking_status, COUNT(*) AS total_bookings
FROM bookings
GROUP BY booking_status
ORDER BY total_bookings DESC;

-- --------------------------------------------------------------------
-- Q08: SUM of revenue by airline (Completed payments only)
-- --------------------------------------------------------------------
SELECT
    al.airline_name,
    COUNT(DISTINCT b.booking_id) AS total_bookings,
    SUM(py.amount)               AS total_revenue,
    AVG(py.amount)               AS avg_booking_value
FROM payments py
JOIN bookings           b  ON py.booking_id    = b.booking_id
JOIN tickets            t  ON t.booking_id     = b.booking_id
JOIN flight_schedules   fs ON t.flight_id      = fs.flight_id
JOIN airlines           al ON fs.airline_id    = al.airline_id
WHERE py.payment_status = 'Completed'
GROUP BY al.airline_name
ORDER BY total_revenue DESC;

-- --------------------------------------------------------------------
-- Q09: Revenue by route
-- --------------------------------------------------------------------
SELECT
    orig.city   AS origin,
    dest.city   AS destination,
    COUNT(DISTINCT b.booking_id) AS bookings,
    SUM(py.amount)               AS route_revenue
FROM payments py
JOIN bookings           b  ON py.booking_id    = b.booking_id
JOIN tickets            t  ON t.booking_id     = b.booking_id
JOIN flight_schedules   fs ON t.flight_id      = fs.flight_id
JOIN airports           orig ON fs.origin_airport_id     = orig.airport_id
JOIN airports           dest ON fs.destination_airport_id= dest.airport_id
WHERE py.payment_status = 'Completed'
GROUP BY orig.city, dest.city
ORDER BY route_revenue DESC;

-- --------------------------------------------------------------------
-- Q10: Flight occupancy summary
-- --------------------------------------------------------------------
SELECT
    fs.flight_number,
    al.airline_name,
    orig.city         AS origin,
    dest.city         AS destination,
    ac.total_seats,
    COUNT(t.ticket_id) AS tickets_sold,
    ROUND(COUNT(t.ticket_id) * 100.0 / ac.total_seats, 2) AS occupancy_pct
FROM flight_schedules fs
JOIN airlines   al   ON fs.airline_id           = al.airline_id
JOIN aircraft   ac   ON fs.aircraft_id          = ac.aircraft_id
JOIN airports   orig ON fs.origin_airport_id    = orig.airport_id
JOIN airports   dest ON fs.destination_airport_id = dest.airport_id
LEFT JOIN tickets t  ON t.flight_id = fs.flight_id AND t.ticket_status = 'Active'
GROUP BY fs.flight_id, fs.flight_number, al.airline_name, orig.city, dest.city, ac.total_seats
ORDER BY occupancy_pct DESC;

-- --------------------------------------------------------------------
-- Q11: Bookings in the last 7 days (date filtering)
-- --------------------------------------------------------------------
SELECT
    b.booking_reference,
    p.full_name,
    b.booking_datetime,
    b.total_amount,
    b.booking_status
FROM bookings b
JOIN passengers p ON b.passenger_id = p.passenger_id
WHERE b.booking_datetime >= DATE_SUB(NOW(), INTERVAL 7 DAY)
ORDER BY b.booking_datetime DESC;

-- --------------------------------------------------------------------
-- Q12: Passengers with more than one booking (HAVING)
-- --------------------------------------------------------------------
SELECT
    p.full_name,
    p.email,
    COUNT(b.booking_id) AS booking_count
FROM passengers p
JOIN bookings b ON b.passenger_id = p.passenger_id
GROUP BY p.passenger_id, p.full_name, p.email
HAVING COUNT(b.booking_id) > 1
ORDER BY booking_count DESC;

-- --------------------------------------------------------------------
-- Q13: Most-booked routes
-- --------------------------------------------------------------------
SELECT
    orig.city AS origin,
    dest.city AS destination,
    COUNT(t.ticket_id) AS tickets_sold
FROM tickets t
JOIN flight_schedules   fs  ON t.flight_id              = fs.flight_id
JOIN airports           orig ON fs.origin_airport_id    = orig.airport_id
JOIN airports           dest ON fs.destination_airport_id= dest.airport_id
WHERE t.ticket_status = 'Active'
GROUP BY orig.city, dest.city
ORDER BY tickets_sold DESC
LIMIT 5;

-- --------------------------------------------------------------------
-- Q14: Payment status report
-- --------------------------------------------------------------------
SELECT
    py.payment_status,
    COUNT(*)           AS payment_count,
    SUM(py.amount)     AS total_amount,
    MIN(py.amount)     AS min_amount,
    MAX(py.amount)     AS max_amount,
    AVG(py.amount)     AS avg_amount
FROM payments py
GROUP BY py.payment_status;

-- --------------------------------------------------------------------
-- Q15: Available seats report (from view)
-- --------------------------------------------------------------------
SELECT
    flight_number,
    airline_name,
    origin_city,
    destination_city,
    departure_datetime,
    available_economy,
    available_business
FROM v_seat_availability
ORDER BY departure_datetime;

-- --------------------------------------------------------------------
-- Q16: LEFT JOIN — flights with no bookings
-- --------------------------------------------------------------------
SELECT
    fs.flight_number,
    al.airline_name,
    orig.city  AS origin,
    dest.city  AS destination,
    fs.departure_datetime
FROM flight_schedules fs
LEFT JOIN tickets     t   ON t.flight_id = fs.flight_id AND t.ticket_status = 'Active'
JOIN airlines         al  ON fs.airline_id           = al.airline_id
JOIN airports         orig ON fs.origin_airport_id   = orig.airport_id
JOIN airports         dest ON fs.destination_airport_id = dest.airport_id
WHERE t.ticket_id IS NULL;

-- --------------------------------------------------------------------
-- Q17: Subquery — passengers who have made a booking
-- --------------------------------------------------------------------
SELECT full_name, email, phone
FROM passengers
WHERE passenger_id IN (
    SELECT DISTINCT passenger_id FROM bookings
)
ORDER BY full_name;

-- --------------------------------------------------------------------
-- Q18: UPDATE — update booking status
-- --------------------------------------------------------------------
UPDATE bookings
SET booking_status = 'Completed'
WHERE booking_reference = 'BK001ABC';

-- Verify the change
SELECT booking_reference, booking_status FROM bookings WHERE booking_reference = 'BK001ABC';

-- --------------------------------------------------------------------
-- Q19: UPDATE — cancel a ticket and update associated booking
-- (Normally handled via Python transaction; shown here for demo)
-- --------------------------------------------------------------------
UPDATE tickets SET ticket_status = 'Cancelled'
WHERE booking_id = 11 AND passenger_id = 1;

-- --------------------------------------------------------------------
-- Q20: DELETE demonstration — remove a passenger with no bookings
-- (Safe to delete test_passenger if they exist; skipped if not)
-- --------------------------------------------------------------------
-- INSERT a temporary passenger for deletion demo
INSERT INTO passengers (full_name, email, phone)
VALUES ('Test Delete User', 'delete.test@sample.com', '9000000000');

-- Delete them (safe: no bookings)
DELETE FROM passengers WHERE email = 'delete.test@sample.com';

-- Verify deletion
SELECT COUNT(*) AS deleted_user_count FROM passengers WHERE email = 'delete.test@sample.com';

-- --------------------------------------------------------------------
-- Q21: ORDER BY — flights ordered by departure time (soonest first)
-- --------------------------------------------------------------------
SELECT flight_number, departure_datetime, arrival_datetime, flight_status
FROM flight_schedules
ORDER BY departure_datetime ASC;

-- --------------------------------------------------------------------
-- Q22: MIN/MAX/AVG fare across all flights
-- --------------------------------------------------------------------
SELECT
    MIN(base_fare)  AS cheapest_fare,
    MAX(base_fare)  AS costliest_fare,
    AVG(base_fare)  AS average_fare
FROM flight_schedules
WHERE flight_status <> 'Cancelled';

-- --------------------------------------------------------------------
-- Q23: Booking status history audit log
-- --------------------------------------------------------------------
SELECT
    bsh.history_id,
    b.booking_reference,
    bsh.old_status,
    bsh.new_status,
    bsh.changed_at,
    bsh.remarks
FROM booking_status_history bsh
JOIN bookings b ON bsh.booking_id = b.booking_id
ORDER BY bsh.changed_at DESC;

-- --------------------------------------------------------------------
-- Q24: Aircraft utilization by airline
-- --------------------------------------------------------------------
SELECT
    al.airline_name,
    COUNT(ac.aircraft_id) AS fleet_size,
    SUM(ac.total_seats)   AS total_capacity,
    SUM(ac.economy_seats) AS economy_capacity,
    SUM(ac.business_seats) AS business_capacity
FROM airlines al
LEFT JOIN aircraft ac ON ac.airline_id = al.airline_id
GROUP BY al.airline_id, al.airline_name
ORDER BY fleet_size DESC;

-- --------------------------------------------------------------------
-- Q25: Full booking detail using view
-- --------------------------------------------------------------------
SELECT * FROM v_flight_booking_details ORDER BY booking_id;

-- --------------------------------------------------------------------
-- Q26: Revenue summary from view
-- --------------------------------------------------------------------
SELECT * FROM v_revenue_summary ORDER BY total_revenue DESC;

-- --------------------------------------------------------------------
-- Q27: Upcoming flights in the next 30 days
-- --------------------------------------------------------------------
SELECT
    fs.flight_number,
    al.airline_name,
    orig.city  AS origin,
    dest.city  AS destination,
    fs.departure_datetime,
    fs.flight_status
FROM flight_schedules fs
JOIN airlines   al   ON fs.airline_id           = al.airline_id
JOIN airports   orig ON fs.origin_airport_id    = orig.airport_id
JOIN airports   dest ON fs.destination_airport_id = dest.airport_id
WHERE fs.departure_datetime BETWEEN NOW() AND DATE_ADD(NOW(), INTERVAL 30 DAY)
  AND fs.flight_status <> 'Cancelled'
ORDER BY fs.departure_datetime;

-- --------------------------------------------------------------------
-- Q28: TRANSACTION demonstration — safe booking creation with ROLLBACK
-- This is a representative example. The Python layer performs this
-- transactionally for every real booking.
-- --------------------------------------------------------------------
START TRANSACTION;

-- Step 1: Insert booking
INSERT INTO bookings (booking_reference, passenger_id, total_amount, booking_status)
VALUES ('BKTEST01', 5, 3500.00, 'Confirmed');

-- Step 2: Insert ticket (seat E40F on flight 1 — assumed available)
INSERT INTO tickets (booking_id, passenger_id, flight_id, seat_number, travel_class, ticket_fare, ticket_status)
VALUES (LAST_INSERT_ID(), 5, 1, 'E40F', 'Economy', 3500.00, 'Active');

-- If both succeed, commit
COMMIT;

-- To demonstrate rollback: uncomment START TRANSACTION above, then:
-- ROLLBACK;  -- Would undo both inserts if an error occurred

-- Verify
SELECT b.booking_reference, t.seat_number, t.ticket_status
FROM bookings b
JOIN tickets t ON t.booking_id = b.booking_id
WHERE b.booking_reference = 'BKTEST01';

-- Clean up demo transaction record (history must be deleted first due to FK RESTRICT)
DELETE FROM booking_status_history
WHERE booking_id = (SELECT booking_id FROM (SELECT booking_id FROM bookings WHERE booking_reference = 'BKTEST01') AS t);
DELETE FROM tickets
WHERE booking_id = (SELECT booking_id FROM (SELECT booking_id FROM bookings WHERE booking_reference = 'BKTEST01') AS t);
DELETE FROM bookings WHERE booking_reference = 'BKTEST01';

-- --------------------------------------------------------------------
-- Q29: Count passengers registered per month
-- --------------------------------------------------------------------
SELECT
    DATE_FORMAT(created_at, '%Y-%m') AS month,
    COUNT(*)                         AS new_passengers
FROM passengers
GROUP BY month
ORDER BY month;

-- --------------------------------------------------------------------
-- Q30: Booking count per travel class
-- --------------------------------------------------------------------
SELECT
    travel_class,
    COUNT(*)           AS ticket_count,
    SUM(ticket_fare)   AS total_revenue,
    AVG(ticket_fare)   AS avg_fare
FROM tickets
WHERE ticket_status = 'Active'
GROUP BY travel_class;

-- =============================================================================
-- END OF QUERIES
-- =============================================================================


import sqlite3

# Connect to database
conn = sqlite3.connect("flight_ticketing.db")

# Create cursor
cursor = conn.cursor()

# =====================================
# FLIGHTS TABLE
# =====================================

cursor.execute("""
CREATE TABLE IF NOT EXISTS flights(
    flight_id INTEGER PRIMARY KEY AUTOINCREMENT,
    flight_number TEXT UNIQUE NOT NULL,
    airline_name TEXT NOT NULL,
    departure_city TEXT NOT NULL,
    destination_city TEXT NOT NULL,
    departure_date TEXT NOT NULL,
    departure_time TEXT NOT NULL,
    arrival_time TEXT NOT NULL,
    ticket_price REAL NOT NULL,
    total_seats INTEGER NOT NULL,
    available_seats INTEGER NOT NULL
)
""")

# =====================================
# PASSENGERS TABLE
# =====================================

cursor.execute("""
CREATE TABLE IF NOT EXISTS passengers(
    passenger_id INTEGER PRIMARY KEY AUTOINCREMENT,
    full_name TEXT NOT NULL,
    email TEXT NOT NULL,
    phone TEXT NOT NULL,
    identification_number TEXT NOT NULL
)
""")

# =====================================
# BOOKINGS TABLE
# =====================================

cursor.execute("""
CREATE TABLE IF NOT EXISTS bookings(
    booking_id INTEGER PRIMARY KEY AUTOINCREMENT,
    booking_reference TEXT UNIQUE NOT NULL,
    passenger_id INTEGER NOT NULL,
    flight_id INTEGER NOT NULL,
    number_of_passengers INTEGER NOT NULL,
    travel_class TEXT NOT NULL,
    total_cost REAL NOT NULL,
    booking_date TEXT NOT NULL,
    booking_status TEXT NOT NULL,

    FOREIGN KEY(passenger_id)
    REFERENCES passengers(passenger_id),

    FOREIGN KEY(flight_id)
    REFERENCES flights(flight_id)
)
""")

# =====================================
# ADMINISTRATORS TABLE
# =====================================

cursor.execute("""
CREATE TABLE IF NOT EXISTS administrators(
    admin_id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL
)
""")

# =====================================
# CONTACT MESSAGES TABLE
# =====================================

cursor.execute("""
CREATE TABLE IF NOT EXISTS contact_messages(
    message_id INTEGER PRIMARY KEY AUTOINCREMENT,
    customer_name TEXT NOT NULL,
    email TEXT NOT NULL,
    subject TEXT NOT NULL,
    message TEXT NOT NULL,
    submission_date TEXT NOT NULL
)
""")

# =====================================
# SAMPLE FLIGHTS
# =====================================

cursor.execute("""
INSERT OR IGNORE INTO flights(
    flight_number,
    airline_name,
    departure_city,
    destination_city,
    departure_date,
    departure_time,
    arrival_time,
    ticket_price,
    total_seats,
    available_seats
)
VALUES(
    'SL101',
    'SkyLink Airlines',
    'Nairobi',
    'Mombasa',
    '2026-11-15',
    '08:00',
    '09:15',
    8500,
    100,
    100
)
""")

cursor.execute("""
INSERT OR IGNORE INTO flights(
    flight_number,
    airline_name,
    departure_city,
    destination_city,
    departure_date,
    departure_time,
    arrival_time,
    ticket_price,
    total_seats,
    available_seats
)
VALUES(
    'SL205',
    'SkyLink Airlines',
    'Nairobi',
    'Kisumu',
    '2026-11-15',
    '10:30',
    '11:25',
    6500,
    90,
    90
)
""")

cursor.execute("""
INSERT OR IGNORE INTO flights(
    flight_number,
    airline_name,
    departure_city,
    destination_city,
    departure_date,
    departure_time,
    arrival_time,
    ticket_price,
    total_seats,
    available_seats
)
VALUES(
    'SL310',
    'SkyLink Airlines',
    'Mombasa',
    'Nairobi',
    '2026-11-15',
    '14:00',
    '15:15',
    9000,
    120,
    120
)
""")

cursor.execute("""
INSERT OR IGNORE INTO administrators(
    username,
    password_hash
)
VALUES(
    'admin',
    'admin123'
)
""")

# Save changes
conn.commit()

# Close database
conn.close()

print("Database created successfully.")
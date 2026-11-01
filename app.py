from flask import Flask, render_template, request, redirect, session, flash
from functools import wraps
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3
import random

app = Flask(__name__)
app.secret_key = "skylink-9f3k2m8x7q1w5z4p6r0t"

DB_NAME = "flight_ticketing.db"


# ---------------------------------------------------------
# DATABASE SETUP (creates the customers table if missing)
# ---------------------------------------------------------
def init_db():
    conn = sqlite3.connect(DB_NAME)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS customers (
            customer_id INTEGER PRIMARY KEY AUTOINCREMENT,
            full_name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()


init_db()


# ---------------------------------------------------------
# ADMIN PROTECTION
# Only admin pages use this. Customers never need to log in.
# ---------------------------------------------------------
def admin_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if not session.get("admin"):
            flash("Please log in as admin.")
            return redirect("/admin/login")
        return view(*args, **kwargs)
    return wrapped


# ---------------------------------------------------------
# HOME PAGE
# ---------------------------------------------------------
@app.route('/')
def home():
    return render_template('index.html')


# ---------------------------------------------------------
# CUSTOMER SIGN UP / LOGIN / LOGOUT  (all optional)
# ---------------------------------------------------------
@app.route('/signup', methods=['GET', 'POST'])
def signup():

    if request.method == 'POST':

        full_name = request.form['full_name'].strip()
        email = request.form['email'].strip().lower()
        password = request.form['password']

        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()

        try:
            cursor.execute("""
                INSERT INTO customers (full_name, email, password_hash)
                VALUES (?, ?, ?)
            """, (full_name, email, generate_password_hash(password)))
            conn.commit()
        except sqlite3.IntegrityError:
            flash("That email is already registered.")
            return redirect('/signup')
        finally:
            conn.close()

        flash("Account created. Please log in.")
        return redirect('/login')

    return render_template('signup.html')


@app.route('/login', methods=['GET', 'POST'])
def login():

    if request.method == 'POST':

        email = request.form['email'].strip().lower()
        password = request.form['password']

        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()

        cursor.execute("""
            SELECT customer_id, full_name, password_hash
            FROM customers
            WHERE email = ?
        """, (email,))

        user = cursor.fetchone()
        conn.close()

        if user and check_password_hash(user[2], password):
            session['customer_id'] = user[0]
            session['customer_name'] = user[1]
            session['customer_email'] = email
            return redirect('/')

        flash("Invalid email or password.")

    return render_template('login.html')


@app.route('/logout')
def logout():
    session.pop('customer_id', None)
    session.pop('customer_name', None)
    session.pop('customer_email', None)
    flash("You have been logged out.")
    return redirect('/')


# ---------------------------------------------------------
# SEARCH FLIGHTS (open to everyone)
# ---------------------------------------------------------
@app.route('/search', methods=['GET', 'POST'])
def search():

    flights = []

    if request.method == 'POST':

        departure = request.form['departure']
        destination = request.form['destination']

        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()

        cursor.execute("""
            SELECT *
            FROM flights
            WHERE departure_city = ?
            AND destination_city = ?
        """, (departure, destination))

        flights = cursor.fetchall()

        conn.close()

    return render_template(
        'search_flights.html',
        flights=flights
    )


# ---------------------------------------------------------
# BOOK FLIGHT (open to everyone, guests included)
# ---------------------------------------------------------
@app.route('/book/<int:flight_id>', methods=['GET', 'POST'])
def book(flight_id):

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT *
        FROM flights
        WHERE flight_id = ?
    """, (flight_id,))

    flight = cursor.fetchone()

    if flight is None:
        conn.close()
        return "Flight not found."

    if request.method == 'POST':

        full_name = request.form['full_name']
        email = request.form['email']
        phone = request.form['phone']
        id_number = request.form['id_number']

        passengers = int(request.form['passengers'])

        # Check available seats
        available_seats = flight[10]

        if passengers > available_seats:
            conn.close()
            return "Not enough seats available."

        # Save passenger
        cursor.execute("""
        INSERT INTO passengers(
            full_name,
            email,
            phone,
            identification_number
        )
        VALUES(?,?,?,?)
        """,
        (
            full_name,
            email,
            phone,
            id_number
        ))

        passenger_id = cursor.lastrowid

        conn.commit()

        # Calculate cost
        ticket_price = flight[8]

        total_cost = ticket_price * passengers

        # Generate booking reference
        booking_reference = "SKY" + str(
            random.randint(10000, 99999)
        )

        # Save booking
        cursor.execute("""
        INSERT INTO bookings(
            booking_reference,
            passenger_id,
            flight_id,
            number_of_passengers,
            travel_class,
            total_cost,
            booking_date,
            booking_status
        )
        VALUES(
            ?, ?, ?, ?, ?, ?, DATE('now'), ?
        )
        """,
        (
            booking_reference,
            passenger_id,
            flight_id,
            passengers,
            "Economy",
            total_cost,
            "Confirmed"
        ))

        # Reduce seats
        cursor.execute("""
        UPDATE flights
        SET available_seats =
        available_seats - ?
        WHERE flight_id = ?
        """,
        (
            passengers,
            flight_id
        ))

        conn.commit()

        conn.close()

        return render_template(
            "booking_confirmation.html",
            booking_reference=booking_reference,
            passenger=full_name,
            flight_number=flight[1],
            departure=flight[3],
            destination=flight[4],
            departure_date=flight[5],
            departure_time=flight[6],
            arrival_time=flight[7],
            passengers=passengers,
            total_cost=total_cost
        )

    conn.close()

    # Logged-in customers get their details pre-filled; guests get blank fields
    return render_template(
        "booking.html",
        flight=flight,
        prefill_name=session.get('customer_name', ''),
        prefill_email=session.get('customer_email', '')
    )


# ---------------------------------------------------------
# MY BOOKINGS (guests look up with reference + email)
# ---------------------------------------------------------
@app.route('/my_bookings', methods=['GET', 'POST'])
def my_bookings():

    booking = None
    booking_id = None

    if request.method == 'POST':

        booking_reference = request.form['booking_reference']
        email = request.form['email']

        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()

        cursor.execute("""
        SELECT
            bookings.booking_reference,
            passengers.full_name,
            passengers.email,
            flights.flight_number,
            bookings.booking_status,
            bookings.booking_id

        FROM bookings

        JOIN passengers
        ON bookings.passenger_id =
        passengers.passenger_id

        JOIN flights
        ON bookings.flight_id =
        flights.flight_id

        WHERE bookings.booking_reference = ?
        AND passengers.email = ?
        """,
        (
            booking_reference,
            email
        ))

        result = cursor.fetchone()

        conn.close()

        if result:
            booking = result[:5]
            booking_id = result[5]

    return render_template(
        "my_bookings.html",
        booking=booking,
        booking_id=booking_id
    )


# ---------------------------------------------------------
# CANCEL BOOKING
# ---------------------------------------------------------
@app.route('/cancel/<int:booking_id>')
def cancel_booking(booking_id):

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
    SELECT
        flight_id,
        number_of_passengers,
        booking_status
    FROM bookings
    WHERE booking_id = ?
    """,
    (booking_id,))

    booking = cursor.fetchone()

    if booking is None:
        conn.close()
        return "Booking not found."

    flight_id = booking[0]
    passengers = booking[1]
    status = booking[2]

    # Prevents seats being added back twice
    if status == 'Cancelled':
        conn.close()
        return "This booking is already cancelled."

    cursor.execute("""
    UPDATE bookings
    SET booking_status = 'Cancelled'
    WHERE booking_id = ?
    """,
    (booking_id,))

    cursor.execute("""
    UPDATE flights
    SET available_seats =
        available_seats + ?
    WHERE flight_id = ?
    """,
    (
        passengers,
        flight_id
    ))

    conn.commit()
    conn.close()

    return """
    Booking Cancelled Successfully.
    """


# ---------------------------------------------------------
# ADMIN LOGIN / DASHBOARD / LOGOUT
# ---------------------------------------------------------
@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():

    if request.method == 'POST':

        username = request.form['username']
        password = request.form['password']

        conn = sqlite3.connect(DB_NAME)

        cursor = conn.cursor()

        cursor.execute("""
        SELECT *
        FROM administrators
        WHERE username = ?
        AND password_hash = ?
        """,
        (
            username,
            password
        ))

        admin = cursor.fetchone()

        conn.close()

        if admin:
            session['admin'] = True
            return redirect('/admin/dashboard')

        return "Invalid Login"

    return render_template(
        'admin/login.html'
    )


@app.route('/admin/dashboard')
@admin_required
def admin_dashboard():
    return render_template(
        'admin/dashboard.html'
    )


@app.route('/admin/logout')
def admin_logout():
    session.pop('admin', None)
    flash("Admin logged out.")
    return redirect('/admin/login')


# ---------------------------------------------------------
# ADMIN: FLIGHTS
# ---------------------------------------------------------
@app.route('/admin/flights')
@admin_required
def admin_flights():

    conn = sqlite3.connect(DB_NAME)

    cursor = conn.cursor()

    cursor.execute("""
    SELECT *
    FROM flights
    """)

    flights = cursor.fetchall()

    conn.close()

    return render_template(
        'admin/flights.html',
        flights=flights
    )


@app.route(
    '/admin/add_flight',
    methods=['GET', 'POST']
)
@admin_required
def add_flight():

    if request.method == 'POST':

        flight_number = request.form[
            'flight_number'
        ]

        airline_name = request.form[
            'airline_name'
        ]

        departure_city = request.form[
            'departure_city'
        ]

        destination_city = request.form[
            'destination_city'
        ]

        ticket_price = request.form[
            'ticket_price'
        ]

        available_seats = request.form[
            'available_seats'
        ]

        departure_date = request.form[
            'departure_date'
        ]

        departure_time = request.form[
            'departure_time'
        ]

        arrival_time = request.form[
            'arrival_time'
        ]

        conn = sqlite3.connect(DB_NAME)

        cursor = conn.cursor()

        cursor.execute("""
        INSERT INTO flights(
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
            ?,?,?,?,?,?,?,?,?,?
        )
        """,
        (
            flight_number,
            airline_name,
            departure_city,
            destination_city,
            departure_date,
            departure_time,
            arrival_time,
            ticket_price,
            available_seats,
            available_seats
        ))

        conn.commit()
        conn.close()

        return "Flight Added"

    return render_template(
        'admin/add_flight.html'
    )


@app.route(
    '/admin/edit_flight/<int:flight_id>',
    methods=['GET', 'POST']
)
@admin_required
def edit_flight(flight_id):

    conn = sqlite3.connect(DB_NAME)

    cursor = conn.cursor()

    if request.method == 'POST':

        flight_number = request.form[
            'flight_number'
        ]

        airline_name = request.form[
            'airline_name'
        ]

        departure_city = request.form[
            'departure_city'
        ]

        destination_city = request.form[
            'destination_city'
        ]

        ticket_price = request.form[
            'ticket_price'
        ]

        available_seats = request.form[
            'available_seats'
        ]

        departure_date = request.form[
            'departure_date'
        ]

        departure_time = request.form[
            'departure_time'
        ]

        arrival_time = request.form[
            'arrival_time'
        ]

        cursor.execute("""
        UPDATE flights
        SET
            flight_number = ?,
            airline_name = ?,
            departure_city = ?,
            destination_city = ?,
            departure_date = ?,
            departure_time = ?,
            arrival_time = ?,
            ticket_price = ?,
            available_seats = ?
        WHERE flight_id = ?
        """,
        (
            flight_number,
            airline_name,
            departure_city,
            destination_city,
            departure_date,
            departure_time,
            arrival_time,
            ticket_price,
            available_seats,
            flight_id
        ))

        conn.commit()
        conn.close()

        return "Flight Updated Successfully"

    cursor.execute("""
    SELECT *
    FROM flights
    WHERE flight_id = ?
    """,
    (flight_id,))

    flight = cursor.fetchone()

    conn.close()

    return render_template(
        'admin/edit_flight.html',
        flight=flight
    )


@app.route('/admin/delete_flight/<int:flight_id>')
@admin_required
def delete_flight(flight_id):

    conn = sqlite3.connect(DB_NAME)

    cursor = conn.cursor()

    cursor.execute("""
    DELETE FROM flights
    WHERE flight_id = ?
    """,
    (flight_id,))

    conn.commit()
    conn.close()

    return "Flight Deleted Successfully"


@app.route('/admin/update_price/<int:flight_id>', methods=['POST'])
@admin_required
def update_price(flight_id):

    try:
        new_price = float(request.form['ticket_price'])
    except ValueError:
        flash("Please enter a valid price.")
        return redirect('/admin/flights')

    if new_price <= 0:
        flash("Price must be greater than zero.")
        return redirect('/admin/flights')

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
    UPDATE flights
    SET ticket_price = ?
    WHERE flight_id = ?
    """,
    (new_price, flight_id))

    conn.commit()
    conn.close()

    flash("Ticket price updated.")
    return redirect('/admin/flights')


# ---------------------------------------------------------
# ADMIN: BOOKINGS
# ---------------------------------------------------------
@app.route('/admin/bookings')
@admin_required
def admin_bookings():

    conn = sqlite3.connect(DB_NAME)

    cursor = conn.cursor()

    cursor.execute("""
    SELECT
        bookings.booking_reference,
        passengers.full_name,
        flights.flight_number,
        bookings.number_of_passengers,
        bookings.total_cost,
        bookings.booking_status

    FROM bookings

    JOIN passengers
    ON bookings.passenger_id =
    passengers.passenger_id

    JOIN flights
    ON bookings.flight_id =
    flights.flight_id
    """)

    bookings = cursor.fetchall()

    conn.close()

    return render_template(
        'admin/bookings.html',
        bookings=bookings
    )


# ---------------------------------------------------------
# CONTACT US (open to everyone)
# ---------------------------------------------------------
@app.route('/contact', methods=['GET', 'POST'])
def contact():

    if request.method == 'POST':

        customer_name = request.form['customer_name']
        email = request.form['email']
        subject = request.form['subject']
        message = request.form['message']

        conn = sqlite3.connect(DB_NAME)

        cursor = conn.cursor()

        cursor.execute("""
        INSERT INTO contact_messages(
            customer_name,
            email,
            subject,
            message,
            submission_date
        )
        VALUES(
            ?, ?, ?, ?, DATE('now')
        )
        """,
        (
            customer_name,
            email,
            subject,
            message
        ))

        conn.commit()
        conn.close()

        return "Message Sent Successfully"

    return render_template(
        'contact.html'
    )


if __name__ == '__main__':
    app.run(debug=True)
SkyLink Airlines Flight Ticketing System
Project Overview
SkyLink Airlines Flight Ticketing System is a web-based airline reservation application developed using Python, Flask, SQLite, HTML, and CSS.

The system allows registered users to search flights, make reservations, manage bookings, and communicate with customer support. Administrators can manage flights and monitor bookings through a secure administration portal.

Key Features
Customer Features
User Registration
User Login
User Authentication
Search Flights
Book Flight Tickets
Booking Confirmation
View Bookings
Cancel Bookings
Contact Customer Support
Administrator Features
Secure Admin Login
Manage Flights
Add Flights
Edit Flights
Delete Flights
View Customer Bookings
Monitor System Activity
Technologies Used
Python 3
Flask
SQLite
HTML5
CSS3
PyCharm
Project Structure
flight_ticketing_system/
│
├── app.py
├── database.py
├── flight_ticketing.db
├── README.md
│
├── static/
│   ├── css/
│   │   └── style.css
│   │
│   └── images/
│       ├── logo.png
│       ├── aircraft.jpg
│       ├── nairobi.jpg
│       ├── mombasa.jpg
│       └── kisumu.jpg
│
├── templates/
│   ├── admin/
│   ├── base.html
│   ├── index.html
│   ├── search_flights.html
│   ├── booking.html
│   ├── booking_confirmation.html
│   ├── my_bookings.html
│   ├── contact.html
│   ├── login.html
│   └── register.html
│
└── requirements.txt
Database Tables
Flights
Stores flight information, schedules, prices, and seat availability.

Passengers
Stores passenger details.

Bookings
Stores reservation information and booking references.

Users
Stores authenticated customer accounts.

Administrators
Stores administrator credentials.

Contact Messages
Stores customer inquiries submitted through the Contact Us page.

User Authentication
The system includes an authentication module that provides:

User Registration
User Login
Password Validation
Session Management
Protected Routes
Secure Access Control
Authenticated users can access customer-specific services while administrators access management functions through separate login credentials. Administrator credentials: username: admin, password: admin123

Installation Guide
Step 1: Install Dependencies
pip install flask
Step 2: Initialize Database
python database.py
Step 3: Run the Application
python app.py
Step 4: Open Web Application
http://127.0.0.1:5000
Modules
Home Page
Displays airline branding, destination information, and navigation links.

Flight Search
Allows users to search available flights.

Flight Booking
Allows customers to reserve seats on available flights.

Authentication
Supports user registration and login.

Booking Management
Allows users to view and cancel reservations.

Contact Us
Allows customers to submit inquiries.

Administration
Allows administrators to manage flights and bookings.

Future Enhancements
Online Payment Integration
Email Ticket Generation
PDF E-Ticket Downloads
SMS Notifications
Flight Tracking
Advanced Analytics Dashboard
Mobile Application Support

Author
Stephen W. Gichimu

SkyLink Airlines Flight Ticketing System

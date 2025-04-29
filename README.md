# SQL Injection Detection Web App

This project is a simple Flask web application designed to detect and log SQL injection attempts through a fake login form.

It stores detected attacks in a SQLite database and allows admin users to view and download logs through a protected dashboard.

**Live Demo:** https://sql-injection-detector.onrender.com

## Features

- Detects common SQL injection patterns in login inputs
- Logs attacks to a database
- Admin login system with session management
- Admin dashboard for viewing and downloading attack logs
- Dark mode toggle for user interface

## Technologies Used

- Python
- Flask
- Flask-Login
- Flask-SQLAlchemy
- HTML/CSS

## How to Run Locally

1. Clone the repository
2. Install dependencies: pip install -r requirements.txt
3. Run the application: python app.py
4. Visit `http://127.0.0.1:5000/` in your browser

## Deployment

This app is ready for deployment on platforms like Render.  
The `render.yaml` file is provided for easy configuration.









# SQL Injection Detection Web App

🔗 **Live Demo**: https://sql-injection-detector.onrender.com

This is a Flask web app that detects and logs SQL injection (SQLi) attempts through a fake login form. It uses both traditional regex pattern matching and an optional machine learning classifier to identify suspicious inputs.

All detected attacks are logged to a SQLite database. An admin dashboard allows reviewing, exporting, and analyzing attack activity.

---

## 🔒 Features

- ✅ Detects SQL injection via **regex** and optional **machine learning (Logistic Regression)**
- ✅ **Honeypot endpoints** to trap bots probing for vulnerable routes
- ✅ Logs all attacks with timestamp, IP address, and credentials
- ✅ Admin dashboard with login protection and session management
- ✅ Downloadable CSV logs for auditing
- ✅ Toggleable **dark mode** UI
- ✅ **Analytics dashboard** (Plotly) with interactive charts:
  - Attack volume over time
  - Top payloads
  - Honeypot vs. SQLi attack ratio

---

## 🛠 Technologies Used

- Python, Flask
- Flask-Login, Flask-SQLAlchemy
- Plotly (for dashboard analytics)
- Scikit-learn (for ML-based detection)
- HTML/CSS (Dark Mode UI)
- SQLite

---

## 🧠 Admin Login

- **Username**: `admin`
- **Password**: `secure123`

---

## 📦 Deployment

This project is deployed using [Render](https://render.com). The app can also be Dockerized or hosted on any platform that supports Flask.

---

## 📚 TODO / Future Improvements

- Filter logs by IP or time range
- Display detection source (ML vs Regex)
- Support IP blocking or throttling

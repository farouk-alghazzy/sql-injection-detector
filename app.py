from flask import Flask, request, render_template_string, redirect, url_for, send_file, Response
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, logout_user, login_required, UserMixin
from datetime import datetime
import csv
import io
import os
import re

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///attacks.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

class Admin(UserMixin):
    id = 1
    username = "admin"
    password = "secure123"

@login_manager.user_loader
def load_user(user_id):
    if user_id == "1":
        return Admin()
    return None

class Attack(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.String(100))
    ip_address = db.Column(db.String(100))
    username = db.Column(db.String(200))
    password = db.Column(db.String(200))

def is_sql_injection(text):
    patterns = [
        r"(\bor\b|\band\b).*(=)",
        r"(--|\#)",
        r"(\bselect\b|\binsert\b|\bdelete\b|\bdrop\b|\bupdate\b|\bexec\b|\bcreate\b|\bunion\b|\bsleep\b)",
        r"(\*/|/\*)",
        r"(;)",
        r"('|\"|\`)",
        r"(\bxp_cmdshell\b|\butl_http\b)"
    ]
    for pattern in patterns:
        if re.search(pattern, text, re.IGNORECASE):
            return True
    return False

@app.route('/', methods=['GET', 'POST'])
def main_login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if is_sql_injection(username) or is_sql_injection(password):
            new_attack = Attack(
                timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                ip_address=request.remote_addr,
                username=username,
                password=password
            )
            db.session.add(new_attack)
            db.session.commit()
            return redirect('/')

        return render_template_string('''
        <html>
        <head>
            <link rel="stylesheet" href="/static/style.css">
            <script>
                function toggleDarkMode() {
                    const body = document.body;
                    const dark = body.classList.toggle("dark-mode");
                    localStorage.setItem("darkMode", dark);
                }
                window.onload = () => {
                    if (localStorage.getItem("darkMode") === "true") {
                        document.body.classList.add("dark-mode");
                    }
                };
            </script>
        </head>
        <body>
            <div style="text-align:right; padding:10px;">
                <button onclick="toggleDarkMode()" class="toggle-btn">Toggle Dark Mode</button>
            </div>
            <div class="login-box">
                <h2>Login Successful</h2>
                <p style="text-align:center;">Welcome, your credentials have been received.</p>
                <div style="text-align:center; margin-top:20px;">
                    <a href="/" class="admin-link">Back to Login</a>
                </div>
            </div>
        </body>
        </html>
        ''')

    return render_template_string('''
    <html>
    <head>
        <link rel="stylesheet" href="/static/style.css">
        <script>
            function toggleDarkMode() {
                const body = document.body;
                const dark = body.classList.toggle("dark-mode");
                localStorage.setItem("darkMode", dark);
            }
            window.onload = () => {
                if (localStorage.getItem("darkMode") === "true") {
                    document.body.classList.add("dark-mode");
                }
            };
        </script>
    </head>
    <body>
        <div style="text-align:right; padding:10px;">
            <button onclick="toggleDarkMode()" class="toggle-btn">Toggle Dark Mode</button>
        </div>
        <div class="login-box">
            <h2>User Login</h2>
            <form method="POST">
                <input type="text" name="username" placeholder="Username">
                <input type="password" name="password" placeholder="Password">
                <input type="submit" value="Login">
            </form>
            <div style="text-align:center; margin-top:15px;">
                <a href="/login" class="admin-link">Admin Login</a>
            </div>
        </div>
    </body>
    </html>
    ''')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if username == Admin.username and password == Admin.password:
            login_user(Admin())
            return redirect(url_for('admin_dashboard'))
        else:
            return redirect(url_for('login'))

    return render_template_string('''
    <html>
    <head>
        <link rel="stylesheet" href="/static/style.css">
        <script>
            function toggleDarkMode() {
                const body = document.body;
                const dark = body.classList.toggle("dark-mode");
                localStorage.setItem("darkMode", dark);
            }
            window.onload = () => {
                if (localStorage.getItem("darkMode") === "true") {
                    document.body.classList.add("dark-mode");
                }
            };
        </script>
    </head>
    <body>
        <div style="text-align:right; padding:10px;">
            <button onclick="toggleDarkMode()" class="toggle-btn">Toggle Dark Mode</button>
        </div>
        <div class="login-box">
            <h2>Admin Login</h2>
            <form method="POST">
                <input type="text" name="username" placeholder="Username">
                <input type="password" name="password" placeholder="Password">
                <input type="submit" value="Login">
            </form>
            <div style="text-align:center; margin-top:15px;">
                <a href="/" class="admin-link">Back to Main Page</a>
            </div>
        </div>
    </body>
    </html>
    ''')

@app.route('/admin')
@login_required
def admin_dashboard():
    attacks = Attack.query.order_by(Attack.id.desc()).all()
    logs_html = ''.join([
        f'<div class="log-entry"><b>[{a.timestamp}]</b> Attack from {a.ip_address}<br><b>Username:</b> {a.username}<br><b>Password:</b> {a.password}</div>'
        for a in attacks
    ])
    return render_template_string(f'''
    <html>
    <head>
        <link rel="stylesheet" href="/static/style.css">
        <script>
            function toggleDarkMode() {{
                const body = document.body;
                const dark = body.classList.toggle("dark-mode");
                localStorage.setItem("darkMode", dark);
            }}
            window.onload = () => {{
                if (localStorage.getItem("darkMode") === "true") {{
                    document.body.classList.add("dark-mode");
                }}
            }};
        </script>
    </head>
    <body>
        <div style="text-align:right; padding:10px;">
            <button onclick="toggleDarkMode()" class="toggle-btn">Toggle Dark Mode</button>
        </div>
        <div class="admin-box">
            <h2>Admin Dashboard</h2>
            <div class="log-list">{logs_html}</div>
            <div class="actions">
                <a href="/download">Download Logs</a>
                <a href="/logout" style="background-color:red;">Logout</a>
            </div>
        </div>
    </body>
    </html>
    ''')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/download')
@login_required
def download_log():
    attacks = Attack.query.order_by(Attack.id.desc()).all()
    si = io.StringIO()
    cw = csv.writer(si)
    cw.writerow(['Timestamp', 'IP Address', 'Username', 'Password'])
    for a in attacks:
        cw.writerow([a.timestamp, a.ip_address, a.username, a.password])
    output = si.getvalue().encode('utf-8')
    return Response(output, mimetype="text/csv", headers={"Content-Disposition": "attachment;filename=attack_log.csv"})

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
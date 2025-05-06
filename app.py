from flask import Flask, request, render_template_string, redirect, url_for, send_file, Response
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, logout_user, login_required, UserMixin
from datetime import datetime
import csv
import io
import os
import re
import plotly.graph_objs as go
import plotly.offline as pyo
from collections import Counter
import pickle

with open('model.pkl', 'rb') as f:
    ml_model = pickle.load(f)
with open('vectorizer.pkl', 'rb') as f:
    ml_vectorizer = pickle.load(f)

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
    username = "admin" # <--- Admin Login 
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
        use_ml = request.form.get('use_ml') == 'on'

        sqli_flag = False
        if use_ml:
            u_vec = ml_vectorizer.transform([username])
            p_vec = ml_vectorizer.transform([password])
            u_pred = ml_model.predict(u_vec)[0]
            p_pred = ml_model.predict(p_vec)[0]
            sqli_flag = (u_pred == 1 or p_pred == 1)
        else:
            sqli_flag = is_sql_injection(username) or is_sql_injection(password)

        if sqli_flag:
            new_attack = Attack(
                timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                ip_address=request.remote_addr,
                username=username,
                password=password
            )
            db.session.add(new_attack)
            db.session.commit()
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
                    <h2>SQL Injection Detected</h2>
                    <p style="text-align:center;">Malicious input detected and logged.</p>
                    <div style="text-align:center; margin-top:20px;">
                        <a href="/" class="admin-link">Return to Login</a>
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
                <label><input type="checkbox" name="use_ml"> Use ML Detection</label>
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
    logs_html = ''
    for a in attacks:
        if 'honeypot endpoint' in a.username:
            logs_html += f'<div class="log-entry"><b>[{a.timestamp}]</b> Honeypot triggered at <b>{a.username}</b> from {a.ip_address}</div>'
        else:
            logs_html += f'<div class="log-entry"><b>[{a.timestamp}]</b> Attack from {a.ip_address}<br><b>Username:</b> {a.username}<br><b>Password:</b> {a.password}</div>'
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
                <a href="/analytics">View Analytics</a>
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

@app.route('/admin-panel')
def fake_admin_panel():
    log_fake_hit('admin-panel')
    return "403 Forbidden"

@app.route('/debug-console')
def fake_debug_console():
    log_fake_hit('debug-console')
    return "403 Forbidden"

def log_fake_hit(endpoint):
    new_attack = Attack(
        timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        ip_address=request.remote_addr,
        username=f'[honeypot endpoint: {endpoint}]',
        password='N/A'
    )
    db.session.add(new_attack)
    db.session.commit()

import plotly.graph_objs as go
import plotly.offline as pyo
from collections import Counter

@app.route('/analytics')
@login_required
def analytics():
    attacks = Attack.query.all()

    timestamps = [a.timestamp.split()[0] for a in attacks]
    usernames = [a.username for a in attacks]

    from collections import Counter
    import plotly.graph_objs as go
    import plotly.offline as pyo

    time_counts = Counter(timestamps)
    time_chart = go.Figure([go.Bar(x=list(time_counts.keys()), y=list(time_counts.values()))])
    time_div = pyo.plot(time_chart, output_type='div', include_plotlyjs=False)

    filtered_payloads = [u for u in usernames if 'honeypot' not in u and u not in ('', 'N/A')]
    top_payloads = Counter(filtered_payloads).most_common(5)
    labels, values = zip(*top_payloads) if top_payloads else ([], [])
    payload_chart = go.Figure([go.Bar(x=labels, y=values)])
    payload_div = pyo.plot(payload_chart, output_type='div', include_plotlyjs=False)

    honeypot_count = sum('honeypot' in u for u in usernames)
    injection_count = len(attacks) - honeypot_count
    type_chart = go.Figure([go.Pie(labels=['SQL Injection', 'Honeypot Trigger'], values=[injection_count, honeypot_count])])
    type_div = pyo.plot(type_chart, output_type='div', include_plotlyjs=False)

    total_attacks = len(attacks)
    total_honeypots = honeypot_count
    total_sqli = injection_count
    unique_ips = len(set([a.ip_address for a in attacks if a.ip_address]))
    most_common_payload = top_payloads[0][0] if top_payloads else 'N/A'

    return render_template_string(f'''
    <html>
    <head>
        <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
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
            <a href="/admin" class="toggle-btn">Back to Dashboard</a>
        </div>

        <div class="admin-box">
            <h2>Analytics</h2>
            <div class="summary-box" style="margin-bottom: 30px; padding: 15px; border-radius: 10px;">
                <h3>Summary</h3>
                <p><b>Total Attacks:</b> {total_attacks}</p>
                <p><b>SQL Injection Attempts:</b> {total_sqli}</p>
                <p><b>Honeypot Triggers:</b> {total_honeypots}</p>
                <p><b>Unique IP Addresses:</b> {unique_ips}</p>
                <p><b>Most Common Payload:</b> {most_common_payload}</p>
            </div>

            <div class="log-list">
                <h3>Attack Count Over Time</h3>
                {time_div}
                <h3>Top Payloads</h3>
                {payload_div}
                <h3>Honeypot vs Injection Attempts</h3>
                {type_div}
            </div>
        </div>
    </body>
    </html>
    ''')




if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)

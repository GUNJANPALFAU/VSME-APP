from flask import Flask, render_template, request, redirect, url_for, session, send_from_directory
import sqlite3
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = 'vsme_secret'
UPLOAD_FOLDER = 'uploads'
DATABASE = 'users.db'

# Ensure upload folder exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# === DB: Create users table if not exists ===
def init_db():
    with sqlite3.connect(DATABASE) as conn:
        c = conn.cursor()
        c.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                company_name TEXT,
                address_line1 TEXT,
                postal_code TEXT,
                city TEXT,
                country TEXT
            )
        ''')
        conn.commit()

# === DB: Add new user ===
def add_user(username, password, company_name, address_line1, postal_code, city, country):
    with sqlite3.connect(DATABASE) as conn:
        c = conn.cursor()
        try:
            c.execute('''INSERT INTO users (username, password, company_name, address_line1, postal_code, city, country)
                         VALUES (?, ?, ?, ?, ?, ?, ?)''',
                      (username, password, company_name, address_line1, postal_code, city, country))
            conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False

# === DB: Verify user login ===
def verify_user(username, password):
    with sqlite3.connect(DATABASE) as conn:
        c = conn.cursor()
        c.execute('SELECT * FROM users WHERE username = ? AND password = ?', (username, password))
        return c.fetchone() is not None

print("Looking for DB at:", os.path.abspath(DATABASE))

# === Routes ===

@app.route('/')
def home():
    return redirect(url_for('login'))

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        company_name = request.form.get("company_name")
        address_line1 = request.form.get("address_line1")
        postal_code = request.form.get("postal_code")
        city = request.form.get("city")
        country = request.form.get("country")
        registering_person = request.form.get("registering_person")
        designation = request.form.get("designation")
        establishment_year = request.form.get("establishment_year")
        company_email = request.form.get("company_email")
        username = request.form.get("username")
        password = request.form.get("password")

        if not all([company_name, address_line1, postal_code, city, country,
                    registering_person, designation, establishment_year,
                    company_email, username, password]):
            return "Missing field", 400

        if add_user(username, password, company_name, address_line1, postal_code, city, country):
            return redirect("/login")
        else:
            return "Username already exists", 409

    return render_template("register.html")

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()
        if verify_user(username, password):
            session['username'] = username
            return redirect(url_for('dashboard'))
        else:
            return "Invalid credentials", 401
    return render_template('login.html')

@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    if 'username' not in session:
        return redirect(url_for('login'))

    username = session['username']

    with sqlite3.connect(DATABASE) as conn:
        c = conn.cursor()
        c.execute('''
            SELECT company_name, address_line1, postal_code, city, country
            FROM users WHERE username = ?
        ''', (username,))
        row = c.fetchone()

    if row:
        company_name, address_line1, postal_code, city, country = row
    else:
        company_name = address_line1 = postal_code = city = country = "N/A"

    user_folder = os.path.join(UPLOAD_FOLDER, username)
    os.makedirs(user_folder, exist_ok=True)

    # === ✅ Handle file upload
    if request.method == 'POST':
        file = request.files.get('file')
        if file and file.filename.endswith('.xlsx'):
            filename = secure_filename(file.filename)
            filepath = os.path.join(user_folder, filename)
            file.save(filepath)
            return redirect(url_for('dashboard'))  # Refresh page after upload

    # List uploaded files
    files = os.listdir(user_folder)

    return render_template("dashboard.html",
        company_name=company_name,
        address_line1=address_line1,
        postal_code=postal_code,
        city=city,
        country=country,
        username=username,
        files=files
    )

@app.route('/download/<filename>')
def download_file(filename):
    if 'username' not in session:
        return redirect(url_for('login'))
    username = session['username']
    return send_from_directory(os.path.join(UPLOAD_FOLDER, username), filename, as_attachment=True)

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('login'))

# === Run ===
if __name__ == '__main__':
    init_db()
    app.run(debug=True)

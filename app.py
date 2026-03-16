from flask import Flask, render_template, request, redirect, session, send_file
import sqlite3
from datetime import date
import csv
import os

app = Flask(__name__)
app.secret_key = "secret123"

# --- DATABASE SETUP ---
def db():
    conn = sqlite3.connect("habits.db")
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Memastikan tabel database ada saat aplikasi dijalankan"""
    conn = db()
    # Tabel User
    conn.execute('''CREATE TABLE IF NOT EXISTS users 
                    (id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT UNIQUE, password TEXT)''')
    # Tabel Habits (ditambah user_id agar tiap orang punya habit masing-masing)
    conn.execute('''CREATE TABLE IF NOT EXISTS habits 
                    (id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER, name TEXT, 
                     reminder TEXT, streak INTEGER DEFAULT 0, status INTEGER DEFAULT 0)''')
    # Tabel History
    conn.execute('''CREATE TABLE IF NOT EXISTS history 
                    (id INTEGER PRIMARY KEY AUTOINCREMENT, habit_id INTEGER, date TEXT, status INTEGER)''')
    conn.commit()

# Jalankan inisialisasi saat script dijalankan
init_db()

# --- ROUTES ---

@app.route("/", methods=["GET","POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        conn = db()
        user = conn.execute("SELECT * FROM users WHERE username = ? AND password = ?", 
                            (username, password)).fetchone()
        
        if user:
            session["login"] = True
            session["user_id"] = user["id"]
            session["username"] = user["username"]
            return redirect("/dashboard")
        else:
            return "Username atau Password salah!" # Anda bisa mengganti ini dengan flash message

    return render_template("login.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        try:
            conn = db()
            conn.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
            conn.commit()
            return redirect("/")
        except sqlite3.IntegrityError:
            return "Username sudah terdaftar!"
            
    return render_template("register.html")

@app.route("/dashboard")
def dashboard():
    if "login" not in session:
        return redirect("/")

    user_id = session["user_id"]
    conn = db()

    # Hanya ambil habit milik user yang sedang login
    habits = conn.execute("SELECT * FROM habits WHERE user_id = ?", (user_id,)).fetchall()

    total = len(habits)
    done = len([h for h in habits if h["status"] == 1])
    progress = int((done/total)*100) if total > 0 else 0

    best = conn.execute("SELECT MAX(streak) as best FROM habits WHERE user_id = ?", (user_id,)).fetchone()
    best_streak = best["best"] if best["best"] else 0

    return render_template(
        "dashboard.html",
        habits=habits,
        progress=progress,
        best_streak=best_streak,
        username=session["username"]
    )

@app.route("/add", methods=["POST"])
def add():
    if "login" not in session: return redirect("/")
    
    name = request.form["habit"]
    reminder = request.form["reminder"]
    user_id = session["user_id"]

    conn = db()
    conn.execute(
        "INSERT INTO habits(user_id, name, reminder, streak, status) VALUES (?,?,?,0,0)",
        (user_id, name, reminder)
    )
    conn.commit()
    return redirect("/dashboard")

@app.route("/check/<int:id>")
def check(id):
    if "login" not in session: return redirect("/")
    
    conn = db()
    habit = conn.execute("SELECT streak FROM habits WHERE id=?", (id,)).fetchone()
    
    if habit:
        new_streak = habit["streak"] + 1
        conn.execute("UPDATE habits SET status=1, streak=? WHERE id=?", (new_streak, id))
        conn.execute("INSERT INTO history(habit_id, date, status) VALUES (?,?,?)", 
                     (id, date.today().isoformat(), 1))
        conn.commit()

    return redirect("/dashboard")

@app.route("/delete/<int:id>")
def delete(id):
    conn = db()
    conn.execute("DELETE FROM habits WHERE id=?", (id,))
    conn.commit()
    return redirect("/dashboard")

@app.route("/export")
def export():
    if "login" not in session: return redirect("/")
    
    conn = db()
    # Export data history berdasarkan habit milik user tersebut
    data = conn.execute('''SELECT h.name, hi.date, hi.status 
                           FROM history hi 
                           JOIN habits h ON hi.habit_id = h.id 
                           WHERE h.user_id = ?''', (session["user_id"],)).fetchall()

    file_path = "habit_data.csv"
    with open(file_path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["Habit Name", "Date", "Status"])
        for row in data:
            writer.writerow([row["name"], row["date"], "Done" if row["status"] == 1 else "Missed"])

    return send_file(file_path, as_attachment=True)

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

if __name__ == "__main__":
    app.run(debug=True)
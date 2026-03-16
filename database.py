import sqlite3

conn = sqlite3.connect("habits.db")

conn.execute("""
CREATE TABLE IF NOT EXISTS habits(
id INTEGER PRIMARY KEY AUTOINCREMENT,
name TEXT,
reminder TEXT,
streak INTEGER,
status INTEGER
)
""")

conn.execute("""
CREATE TABLE IF NOT EXISTS history(
id INTEGER PRIMARY KEY AUTOINCREMENT,
habit_id INTEGER,
date TEXT,
status INTEGER
)
""")

conn.commit()
conn.close()

print("Database created")
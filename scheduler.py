import sqlite3

conn = sqlite3.connect("habits.db")

conn.execute(
"UPDATE habits SET status=0"
)

conn.commit()
conn.close()
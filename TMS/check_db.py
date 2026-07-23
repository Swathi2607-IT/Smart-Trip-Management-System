import sqlite3
DATABASE = 'database/trip_management.db'
conn = sqlite3.connect(DATABASE)
cursor = conn.cursor()
cursor.execute("SELECT * FROM transports")
rows = cursor.fetchall()
for row in rows:
    print(row)
conn.close()

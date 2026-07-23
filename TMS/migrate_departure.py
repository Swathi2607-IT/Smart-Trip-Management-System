import sqlite3

try:
    conn = sqlite3.connect('database/trip_management.db')
    c = conn.cursor()
    c.execute("ALTER TABLE bookings ADD COLUMN departure_city TEXT DEFAULT ''")
    conn.commit()
    print("Added departure_city successfully.")
except sqlite3.OperationalError as e:
    print("Already exists or error:", e)
finally:
    conn.close()

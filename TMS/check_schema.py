import sqlite3

db = sqlite3.connect('database/trip_management.db')
cursor = db.cursor()

cursor.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name='hotels'")
hotels_schema = cursor.fetchone()
print("Hotels Schema:", hotels_schema[0] if hotels_schema else "No hotels table")

cursor.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name='destinations'")
dest_schema = cursor.fetchone()
print("Destinations Schema:", dest_schema[0] if dest_schema else "No destinations table")

db.close()

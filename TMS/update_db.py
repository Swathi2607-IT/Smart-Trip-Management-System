import sqlite3

db = sqlite3.connect('database/trip_management.db')
cursor = db.cursor()

try:
    cursor.execute("ALTER TABLE destinations ADD COLUMN category TEXT DEFAULT 'Location'")
except sqlite3.OperationalError:
    pass # Column might exist

try:
    cursor.execute("ALTER TABLE destinations ADD COLUMN location TEXT DEFAULT 'India'")
except sqlite3.OperationalError:
    pass # Column might exist

# Update categories
updates = [
    ("Goa", "Beach", "Goa, India"),
    ("Manali", "Mountain", "Himachal Pradesh, India"),
    ("Munnar", "Nature", "Kerala, India"),
    ("Jaipur", "Heritage", "Rajasthan, India"),
    ("Agra", "Heritage", "Uttar Pradesh, India"),
    ("Andaman", "Beach", "Andaman Islands, India"),
    ("Darjeeling", "Mountain", "West Bengal, India"),
    ("Kerala", "Nature", "Kerala, India")
]

for name, cat, loc in updates:
    cursor.execute("UPDATE destinations SET category = ?, location = ? WHERE name = ?", (cat, loc, name))

db.commit()
db.close()
print("Destinations table cleanly restructured and synced with category & location tags.")

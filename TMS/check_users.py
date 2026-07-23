import sqlite3
DATABASE = 'database/trip_management.db'
db = sqlite3.connect(DATABASE)
db.row_factory = sqlite3.Row
users = db.execute("SELECT * FROM users").fetchall()
print(f"Total Users: {len(users)}")
for u in users:
    print(f"User: {u['name']} | Email: {u['email']} | Role: {u['role']} | PassHash: {u['password'][:30]}...")
db.close()

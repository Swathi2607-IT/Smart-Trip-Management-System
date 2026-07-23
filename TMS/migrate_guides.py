import sqlite3
import random

db_path = 'database/trip_management.db'

def migrate():
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    
    # 1. Update guides
    try:
        c.execute("ALTER TABLE guides ADD COLUMN destination_id INTEGER")
        c.execute("ALTER TABLE guides ADD COLUMN rating REAL DEFAULT 4.5")
        c.execute("ALTER TABLE guides ADD COLUMN experience INTEGER DEFAULT 2")
    except sqlite3.OperationalError:
        pass # Already exists
        
    # 2. Update bookings
    try:
        c.execute("ALTER TABLE bookings ADD COLUMN guide_status TEXT DEFAULT 'Not Requested'")
        c.execute("ALTER TABLE bookings ADD COLUMN rejected_guides TEXT DEFAULT ''")
    except sqlite3.OperationalError:
        pass

    conn.commit()

    # 3. Seed destination IDs and seed more guides
    dests = c.execute("SELECT id FROM destinations").fetchall()
    dest_ids = [d[0] for d in dests]

    if not dest_ids:
        print("No destinations found.")
        return

    # Backfill existing guides
    existing_guides = c.execute("SELECT id FROM guides WHERE destination_id IS NULL").fetchall()
    for eg in existing_guides:
        c.execute("UPDATE guides SET destination_id = ?, rating = ?, experience = ? WHERE id = ?",
                  (random.choice(dest_ids), round(random.uniform(3.8, 5.0), 1), random.randint(2, 10), eg[0]))
    conn.commit()

    # Seed 15 extra guides
    first_names = ['Rahul', 'Aman', 'Priya', 'Sneha', 'Vikram', 'Ramesh', 'Suresh', 'Anita', 'Kavita', 'Ravi', 'Sunil', 'Vijay', 'Neha', 'Pooja', 'Deepak']
    last_names = ['Sharma', 'Verma', 'Singh', 'Kumar', 'Gupta', 'Patel', 'Joshi', 'Mishra', 'Reddy', 'Nair']
    languages = ['English, Hindi', 'English, local dialect', 'Hindi, local dialect']
    for i in range(15):
        name = f"{random.choice(first_names)} {random.choice(last_names)}"
        email = f"guide_pro_{i}_{random.randint(1000, 9999)}@tms.com"
        phone = f"98765{random.randint(10000, 99999)}"
        dest_id = random.choice(dest_ids)
        rating = round(random.uniform(4.0, 5.0), 1)
        exp = random.randint(1, 12)
        lang = random.choice(languages)
        
        try:
            c.execute('''INSERT INTO guides (name, email, phone, languages, destination_id, rating, experience) 
                         VALUES (?, ?, ?, ?, ?, ?, ?)''',
                      (name, email, phone, lang, dest_id, rating, exp))
        except sqlite3.IntegrityError:
            pass # Email duplicate ignore
            
    conn.commit()
    conn.close()
    print("Migration and Seed Success")

migrate()

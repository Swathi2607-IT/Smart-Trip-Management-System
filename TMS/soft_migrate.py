import sqlite3

DATABASE = 'database/trip_management.db'

def soft_migrate():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    print("--- Starting Soft Migration ---")

    # 1. Update Destinations Table
    print("Updating 'destinations' table columns...")
    dest_cols = [
        ("category", "TEXT DEFAULT 'Location'"),
        ("location", "TEXT DEFAULT 'India'"),
        ("latitude", "REAL"),
        ("longitude", "REAL")
    ]
    for col, type_ in dest_cols:
        try:
            cursor.execute(f"ALTER TABLE destinations ADD COLUMN {col} {type_}")
            print(f"[OK] Added column '{col}' to destinations.")
        except sqlite3.OperationalError:
            print(f"[INFO] Column '{col}' already exists in destinations.")

    # 2. Update Bookings Table
    print("\nUpdating 'bookings' table columns...")
    book_cols = [
        ("guide_requested", "BOOLEAN DEFAULT 0"),
        ("rejected_guides", "TEXT DEFAULT ''"),
        ("hotel_id", "INTEGER"),
        ("hotel_cost", "REAL DEFAULT 0"),
        ("is_hotel_booked", "BOOLEAN DEFAULT 0"),
        ("local_transport_req", "BOOLEAN DEFAULT 0"),
        ("local_transport_cost", "REAL DEFAULT 0")
    ]
    for col, type_ in book_cols:
        try:
            cursor.execute(f"ALTER TABLE bookings ADD COLUMN {col} {type_}")
            print(f"[OK] Added column '{col}' to bookings.")
        except sqlite3.OperationalError:
            print(f"[INFO] Column '{col}' already exists in bookings.")

    # 3. Create Supplemental Tables
    print("\nCreating supplemental tables if they don't exist...")
    
    # Hotels
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS hotels (
            id             INTEGER PRIMARY KEY AUTOINCREMENT,
            destination_id INTEGER NOT NULL,
            name           TEXT NOT NULL,
            description    TEXT,
            price_per_night REAL NOT NULL,
            image_url      TEXT,
            FOREIGN KEY (destination_id) REFERENCES destinations(id) ON DELETE CASCADE
        )
    ''')
    
    # Guide Accommodations
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS guide_accommodations (
            id             INTEGER PRIMARY KEY AUTOINCREMENT,
            guide_id       INTEGER NOT NULL,
            booking_id     INTEGER NOT NULL,
            hotel_name     TEXT NOT NULL,
            address        TEXT,
            check_in       DATE,
            check_out      DATE,
            FOREIGN KEY (guide_id)   REFERENCES guides(id)   ON DELETE CASCADE,
            FOREIGN KEY (booking_id) REFERENCES bookings(id) ON DELETE CASCADE
        )
    ''')
    
    # Guide Commissions
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS guide_commissions (
            id             INTEGER PRIMARY KEY AUTOINCREMENT,
            guide_id       INTEGER NOT NULL,
            booking_id     INTEGER NOT NULL,
            amount         REAL NOT NULL,
            status         TEXT DEFAULT 'Pending' CHECK(status IN ('Pending','Paid')),
            created_at     TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (guide_id)   REFERENCES guides(id)   ON DELETE CASCADE,
            FOREIGN KEY (booking_id) REFERENCES bookings(id) ON DELETE CASCADE
        )
    ''')

    # Update guides table with experience if missing
    try:
        cursor.execute("ALTER TABLE guides ADD COLUMN experience INTEGER DEFAULT 2")
        print("[OK] Added column 'experience' to guides.")
    except sqlite3.OperationalError:
        pass

    # 4. Critical Data Patch: Latitude/Longitude for existing destinations
    # This prevents the KeyError: 'latitude'
    coords = {
        'Goa': (15.2993, 74.1240),
        'Manali': (32.2432, 77.1892),
        'Munnar': (10.0889, 77.0595),
        'Rajasthan': (27.0238, 74.2179),
        'Kerala Backwaters': (9.4981, 76.3329),
        'Ladakh': (34.1526, 77.5771),
        'Shimla': (31.1048, 77.1734),
        'Ooty': (11.4102, 76.6950),
        'Rishikesh': (30.0869, 78.2676),
        'Varanasi': (25.3176, 82.9739)
    }
    
    print("\nPatching coordinates for existing destinations...")
    for name, (lat, lon) in coords.items():
        cursor.execute("UPDATE destinations SET latitude = ?, longitude = ? WHERE name = ?", (lat, lon, name))
    
    conn.commit()
    conn.close()
    print("\n--- Soft Migration Complete ---")

if __name__ == "__main__":
    soft_migrate()

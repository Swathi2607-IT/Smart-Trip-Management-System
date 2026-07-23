import sqlite3

DATABASE = 'database/trip_management.db'

def update_db():
    db = sqlite3.connect(DATABASE)
    cursor = db.cursor()

    # 1. Create Hotels table
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

    # 2. Create Guide Accommodations table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS guide_accommodations (
            id             INTEGER PRIMARY KEY AUTOINCREMENT,
            guide_id       INTEGER NOT NULL,
            booking_id     INTEGER NOT NULL,
            hotel_name     TEXT NOT NULL,
            address        TEXT,
            check_in       DATE,
            check_out      DATE,
            FOREIGN KEY (guide_id)   REFERENCES guides(id) ON DELETE CASCADE,
            FOREIGN KEY (booking_id) REFERENCES bookings(id) ON DELETE CASCADE
        )
    ''')

    # 3. Create Guide Commissions table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS guide_commissions (
            id             INTEGER PRIMARY KEY AUTOINCREMENT,
            guide_id       INTEGER NOT NULL,
            booking_id     INTEGER NOT NULL,
            amount         REAL NOT NULL,
            status         TEXT DEFAULT 'Pending' CHECK(status IN ('Pending','Paid')),
            created_at     TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (guide_id)   REFERENCES guides(id) ON DELETE CASCADE,
            FOREIGN KEY (booking_id) REFERENCES bookings(id) ON DELETE CASCADE
        )
    ''')

    # 4. Add new columns to Bookings table
    # SQLite doesn't support multiple ADD COLUMN in one statement, so we do them individually
    columns_to_add = [
        ("hotel_id", "INTEGER"),
        ("hotel_cost", "REAL DEFAULT 0"),
        ("is_hotel_booked", "BOOLEAN DEFAULT 0"),
        ("local_transport_req", "BOOLEAN DEFAULT 0"),
        ("local_transport_cost", "REAL DEFAULT 0")
    ]

    for col_name, col_type in columns_to_add:
        try:
            cursor.execute(f"ALTER TABLE bookings ADD COLUMN {col_name} {col_type}")
            print(f"[OK] Added column {col_name} to bookings.")
        except sqlite3.OperationalError:
            print(f"[INFO] Column {col_name} already exists in bookings.")

    # 5. Seed some hotels for testing
    hotels_data = [
        (1, "Goa Beach Resort", "Luxury stay near the beach", 3500.00, "https://images.unsplash.com/photo-1571896349842-bc0cc6620f4c?w=800&q=80"),
        (1, "Sun & Sand Inn", "Budget friendly beach side hotel", 1200.00, "https://images.unsplash.com/photo-1540541338287-41700207dee6?w=800&q=80"),
        (2, "Manali Snow View", "Great views of the valley", 2800.00, "https://images.unsplash.com/photo-1566073771259-6a8506099945?w=800&q=80"),
        (2, "River Side Lodge", "Right by the Beas river", 1800.00, "https://images.unsplash.com/photo-1520250497591-112f2f40a3f4?w=800&q=80"),
        (3, "Munnar Tea Estate Stay", "Surrounded by tea gardens", 4500.00, "https://images.unsplash.com/photo-1582719478250-c89cae4df85b?w=800&q=80"),
        (6, "Ladakh Cold Desert Inn", "Authentic Ladakhi experience", 3200.00, "https://images.unsplash.com/photo-1551882547-ff43c63efe81?w=800&q=80")
    ]

    cursor.executemany('''
        INSERT OR IGNORE INTO hotels (destination_id, name, description, price_per_night, image_url)
        VALUES (?, ?, ?, ?, ?)
    ''', hotels_data)

    db.commit()
    db.close()
    print("Database updated with Hotels, Guide Stays, and Commissions.")

if __name__ == "__main__":
    update_db()

import sqlite3
import random
from datetime import datetime, timedelta

DATABASE = 'database/trip_management.db'

def seed_transactions():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    print("--- Seeding Demo Bookings & Revenue ---")

    # Get some IDs
    users = cursor.execute("SELECT id FROM users WHERE role='user'").fetchall()
    destinations = cursor.execute("SELECT id, base_price FROM destinations").fetchall()
    guides = cursor.execute("SELECT id FROM guides").fetchall()

    if not users or not destinations:
        print("Missing users or destinations. Seeding stopped.")
        return

    # Create 25 demo bookings
    for i in range(25):
        uid = random.choice(users)[0]
        dest_id, base_price = random.choice(destinations)
        
        duration = random.randint(2, 7)
        passengers = random.randint(1, 4)
        
        package_cost = duration * base_price * passengers
        transport_cost = random.randint(1000, 5000)
        total_cost = package_cost + transport_cost
        
        start_date = (datetime.now() - timedelta(days=random.randint(1, 60))).strftime('%Y-%m-%d')
        end_date = (datetime.strptime(start_date, '%Y-%m-%d') + timedelta(days=duration)).strftime('%Y-%m-%d')
        
        # Insert booking
        cursor.execute('''
            INSERT INTO bookings (user_id, destination_id, start_date, duration, end_date, 
                                 package_cost, total_cost, status, payment_status, passengers)
            VALUES (?, ?, ?, ?, ?, ?, ?, 'Confirmed', 'Paid', ?)
        ''', (uid, dest_id, start_date, duration, end_date, package_cost, total_cost, passengers))
        
        booking_id = cursor.lastrowid
        
        # Insert payment
        txn_id = f"TXN{random.randint(100000, 999999)}"
        cursor.execute('''
            INSERT INTO payments (booking_id, transaction_id, amount, payment_method)
            VALUES (?, ?, ?, 'UPI')
        ''', (booking_id, txn_id, total_cost))

    conn.commit()
    conn.close()
    print(f"--- Seeding Complete: 25 bookings added ---")

if __name__ == "__main__":
    seed_transactions()

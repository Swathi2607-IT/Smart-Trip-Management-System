import sqlite3
import random
from datetime import datetime, timedelta
import binascii
import os

DATABASE = 'database/trip_management.db'

def seed_historical_history():
    db = sqlite3.connect(DATABASE)
    cursor = db.cursor()

    # 1. Fetch Users and Destinations
    user_ids = [row[0] for row in cursor.execute("SELECT id FROM users WHERE role='user'").fetchall()]
    dest_ids = [row[0] for row in cursor.execute("SELECT id FROM destinations").fetchall()]
    guide_ids = [row[0] for row in cursor.execute("SELECT id FROM guides").fetchall()]
    
    if not user_ids or not dest_ids:
        print("Required seed data missing. Run earlier seeds first.")
        return

    # Comments for reviews
    reviews_pool = [
        "The best trip of my life! Everything was perfectly organized.",
        "The weather was a bit chilly, but the views in the valley were incredible.",
        "Highly recommend the local guide; they knew all the hidden gems.",
        "Smooth transport and the hotel was very comfortable.",
        "A bit expensive but totally worth the premium experience.",
        "Varanasi is spiritual and the evening Aarti is must-watch.",
        "Goa beaches never disappoint. Perfect vacation!",
        "Rajasthan's hospitality is royal. Loved the forts.",
        "Munnar tea gardens are so peaceful. Great for photography.",
        "Ladakh was a challenge but the Pangong lake view is heaven."
    ]

    print("Generating 65 Historical Completed Trips...")
    
    historical_bookings = []
    historical_payments = []
    historical_reviews = []
    
    now = datetime.now()
    
    for i in range(65):
        uid = random.choice(user_ids)
        did = random.choice(dest_ids)
        gid = random.choice(guide_ids) if guide_ids else None
        
        # Random historical dates (last 6 months)
        days_ago = random.randint(10, 180)
        duration = random.randint(3, 7)
        start_date = (now - timedelta(days=days_ago)).strftime('%Y-%m-%d')
        end_date = (now - timedelta(days=days_ago - duration)).strftime('%Y-%m-%d')
        
        # Calculate Costs (simplified mock)
        package_cost = duration * 4500.0
        total_cost = package_cost + random.randint(2000, 5000)
        
        receipt_token = binascii.hexlify(os.urandom(16)).decode()
        txn_id = 'UPI' + (now - timedelta(days=days_ago)).strftime('%Y%m%d%H%M') + str(random.randint(1000, 9999))
        
        # Create Booking
        cursor.execute('''
            INSERT INTO bookings
              (user_id, destination_id, guide_id, start_date, duration, end_date,
               package_cost, total_cost, status, payment_status, receipt_token, passengers)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'Completed', 'Paid', ?, ?)
        ''', (uid, did, gid, start_date, duration, end_date, package_cost, total_cost, receipt_token, random.randint(1, 4)))
        
        booking_id = cursor.lastrowid
        
        # Create Payment
        cursor.execute('''
            INSERT INTO payments (booking_id, transaction_id, amount, payment_method, payment_date)
            VALUES (?, ?, ?, 'UPI', ?)
        ''', (booking_id, txn_id, total_cost, start_date))

        # Create Verified Review
        rating = random.randint(4, 5)
        comment = random.choice(reviews_pool)
        cursor.execute('''
            INSERT INTO reviews (user_id, destination_id, rating, comment, created_at)
            VALUES (?, ?, ?, ?, ?)
        ''', (uid, did, rating, comment, end_date))

    db.commit()
    db.close()
    print("Historical scaling complete! 65 trips, payments, and reviews added.")

if __name__ == "__main__":
    seed_historical_history()

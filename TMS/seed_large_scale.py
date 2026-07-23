import sqlite3
import random
from werkzeug.security import generate_password_hash

DATABASE = 'database/trip_management.db'

def seed_large_data():
    db = sqlite3.connect(DATABASE)
    cursor = db.cursor()

    # Pre-defined lists for randomization
    first_names = ["Arjun", "Aditi", "Rahul", "Priya", "Vikram", "Sneha", "Karan", "Anjali", "Rohan", "Meera", 
                   "Siddharth", "Ishani", "Aakash", "Tanvi", "Varun", "Riya", "Manish", "Kavita", "Sameer", "Neha",
                   "Amit", "Sonal", "Deepak", "Asha", "Suresh", "Pooja", "Rajesh", "Sunita", "Vijay", "Anil"]
    last_names  = ["Sharma", "Verma", "Gupta", "Malhotra", "Kapoor", "Singh", "Reddy", "Iyer", "Nair", "Patel",
                   "Joshi", "Bose", "Das", "Chatterjee", "Mishra", "Pandey", "Yadav", "Chauhan", "Thakur", "Rao"]
    domains     = ["gmail.com", "yahoo.com", "outlook.com", "icloud.com", "tms.com"]
    cities      = ["Mumbai", "Delhi", "Bangalore", "Hyderabad", "Ahmedabad", "Chennai", "Kolkata", "Surat", "Pune", "Jaipur"]
    languages   = ["English", "Hindi", "French", "German", "Spanish", "Bengali", "Telugu", "Marathi", "Tamil", "Gujarati"]
    comments    = [
        "Amazing experience! Highly recommended.",
        "Beautiful place, loved every moment.",
        "The guide was very professional and helpful.",
        "A bit crowded, but the views were worth it.",
        "Perfectly planned trip. Everything went smooth.",
        "Loved the local food and culture.",
        "Great value for money. Efficient transport.",
        "Snowy peaks were breathtaking! Unforgettable.",
        "Very peaceful and spiritual atmosphere.",
        "The hotel stay was premium and comfortable."
    ]

    # 1. Seed 110 Users
    print("Seeding 110 Users...")
    password_hash = generate_password_hash('password123')
    users_data = []
    for i in range(110):
        first = random.choice(first_names)
        last  = random.choice(last_names)
        name  = f"{first} {last}"
        email = f"{first.lower()}.{last.lower()}.{i+100}@{random.choice(domains)}"
        phone = f"{random.randint(7000000000, 9999999999)}"
        users_data.append((name, email, phone, password_hash, 'user'))
    
    cursor.executemany("INSERT OR IGNORE INTO users (name, email, phone, password, role) VALUES (?, ?, ?, ?, ?)", users_data)

    # 2. Seed 110 Guides
    print("Seeding 110 Guides...")
    guides_data = []
    guide_user_accounts = []
    for i in range(110):
        first = random.choice(first_names)
        last  = random.choice(last_names)
        name  = f"Guide {first} {last}"
        email = f"guide.{first.lower()}.{i+100}@tms.com"
        phone = f"{random.randint(7000000000, 9999999999)}"
        lang  = f"English, {random.choice(languages)}, {random.choice(languages)}"
        guides_data.append((name, email, phone, lang))
        guide_user_accounts.append((name, email, phone, password_hash, 'guide'))

    cursor.executemany("INSERT OR IGNORE INTO guides (name, email, phone, languages) VALUES (?, ?, ?, ?)", guides_data)
    cursor.executemany("INSERT OR IGNORE INTO users (name, email, phone, password, role) VALUES (?, ?, ?, ?, ?)", guide_user_accounts)

    # 3. Seed 85 Reviews
    print("Seeding 85 Reviews...")
    # Get user IDs and destination IDs
    user_ids = [row[0] for row in cursor.execute("SELECT id FROM users WHERE role='user'").fetchall()]
    dest_ids = [row[0] for row in cursor.execute("SELECT id FROM destinations").fetchall()]
    
    reviews_data = []
    for _ in range(85):
        uid = random.choice(user_ids)
        did = random.choice(dest_ids)
        rating  = random.randint(3, 5) # Mostly good reviews
        comment = random.choice(comments)
        reviews_data.append((uid, did, rating, comment))
    
    cursor.executemany("INSERT INTO reviews (user_id, destination_id, rating, comment) VALUES (?, ?, ?, ?)", reviews_data)

    db.commit()
    db.close()
    print("Large scale seeding complete!")

if __name__ == "__main__":
    seed_large_data()

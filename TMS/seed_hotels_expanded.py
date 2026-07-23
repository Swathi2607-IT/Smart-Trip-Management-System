import sqlite3
import random

db_path = 'c:/TMS/database/trip_management.db'
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Get all destinations
cursor.execute("SELECT id, name FROM destinations")
destinations = cursor.fetchall()

# Hotel names mix 
prefixes = ['The Grand', 'Sunrise', 'Royal', 'Paradise', 'Budget', 'Luxury', 'Majestic', 'Serene', 'Elite', 'Cozy']
suffixes = ['Inn', 'Resort', 'Hotel', 'Palace', 'Lodge', 'Suites', 'Retreat', 'Stay']
images = [
    'https://images.unsplash.com/photo-1566073771259-6a8506099945?w=200&q=80',
    'https://images.unsplash.com/photo-1445019980597-93fa8acb246c?w=200&q=80',
    'https://images.unsplash.com/photo-1496417263034-38ec4f0b665a?w=200&q=80',
    'https://images.unsplash.com/photo-1517840901100-8179e982acb7?w=200&q=80',
    'https://images.unsplash.com/photo-1522798514323-46ce1ea6038c?w=200&q=80'
]

# Clear existing hotels
cursor.execute("DELETE FROM hotels")

tiers = [
    ("Budget", 1500),
    ("Standard", 3000),
    ("Comfort", 5000),
    ("Premium", 8500),
    ("Luxury", 15000)
]

for dest in destinations:
    dest_id = dest[0]
    dest_name = dest[1]
    
    for _ in range(5):
        prefix = random.choice(prefixes)
        suffix = random.choice(suffixes)
        tier_idx = _ % 5
        tier_name, base_price = tiers[tier_idx]
        
        hotel_name = f"{prefix} {dest_name} {suffix}"
        # randomize price somewhat
        price = base_price + random.randint(-200, 500)
        img = random.choice(images)
        desc = f"A beautiful {tier_name.lower()} stay located in the heart of {dest_name}."
        
        cursor.execute('''
            INSERT INTO hotels (destination_id, name, description, price_per_night, image_url)
            VALUES (?, ?, ?, ?, ?)
        ''', (dest_id, hotel_name, desc, float(price), img))

conn.commit()
conn.close()
print("Seeded 5 hotels per destination successfully.")

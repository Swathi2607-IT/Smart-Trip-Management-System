import sqlite3

db = sqlite3.connect('database/trip_management.db')
cursor = db.cursor()

# Ensure we aren't creating literal duplicates if script is run multiple times
existing = cursor.execute("SELECT name FROM destinations").fetchall()
existing_names = [r[0] for r in existing]

destinations = [
    ("Jaipur", "The Pink City of India, known for its fascinating monuments, majestic palaces, and vibrant artisan markets.", 4000.00, "https://images.unsplash.com/photo-1477587458883-47145ed94245?w=800&q=80", 35, "Sunny"),
    ("Agra", "Home to the iconic Taj Mahal, Agra offers a magnificent glimpse into the architectural brilliance of the Mughal era.", 3500.00, "https://images.unsplash.com/photo-1564507592333-c60657eea523?w=800&q=80", 40, "Sunny"),
    ("Andaman", "A beautiful archipelago with pristine white beaches, vibrant coral reefs, and incredible underwater experiences.", 8000.00, "https://plus.unsplash.com/premium_photo-1661962386375-742aa029f6d6?w=800&q=80", 28, "Sunny"),
    ("Darjeeling", "Famous worldwide for its lush tea plantations, nostalgic toy train, and breathtaking views of the Himalayas.", 4200.00, "https://images.unsplash.com/photo-1627883262489-0d12e69aa799?w=800&q=80", 15, "Cloudy"),
    ("Kerala", "Tranquil backwaters offering peaceful houseboat cruises through palm-fringed coastlines and beautiful rural landscapes.", 5500.00, "https://images.unsplash.com/photo-1593693397690-362cb9666fc2?w=800&q=80", 29, "Cloudy")
]

added_count = 0
for d in destinations:
    if d[0] not in existing_names:
        cursor.execute("INSERT INTO destinations (name, description, base_price, image_url, weather_temp, weather_status) VALUES (?, ?, ?, ?, ?, ?)", d)
        dest_id = cursor.lastrowid
        
        # Add beautiful places for the Visual Itinerary Module
        places = [
            (dest_id, f"{d[0]} Observation Deck", "Sightseeing", d[3]),
            (dest_id, f"Historic Center of {d[0]}", "Monument", "https://images.unsplash.com/photo-1548013146-72479768bada?w=800&q=80"),
            (dest_id, f"{d[0]} Local Crafts Market", "Shopping", "https://images.unsplash.com/photo-1596422846543-7ec40cb29ff5?w=800&q=80")
        ]
        
        for p in places:
            cursor.execute("INSERT INTO places (destination_id, name, category, image_url) VALUES (?, ?, ?, ?)", p)
        
        added_count += 1

db.commit()
db.close()

print(f"Successfully injected {added_count} new premium destinations (with attached visual attractions) directly into the live database.")

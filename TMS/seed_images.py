import sqlite3

db = sqlite3.connect('database/trip_management.db')
cursor = db.cursor()

# Get all current destinations
destinations = cursor.execute("SELECT id, name FROM destinations").fetchall()

added_count = 0
for dest in destinations:
    dest_id, name = dest
    
    # Generate 3 new scenic places based on the destination name
    new_places = [
        (dest_id, f"{name} Sunset Point", "Viewpoint", "https://images.unsplash.com/photo-1507525428034-b723cf961d3e?w=800&q=80"),
        (dest_id, f"{name} Heritage Walk", "Historical", "https://images.unsplash.com/photo-1533105079780-92b9be482077?w=800&q=80"),
        (dest_id, f"{name} Nature Reserve", "Nature", "https://images.unsplash.com/photo-1542273917363-3b1817f69a5d?w=800&q=80")
    ]
    
    for p in new_places:
        cursor.execute("INSERT INTO places (destination_id, name, category, image_url) VALUES (?, ?, ?, ?)", p)
        added_count += 1

db.commit()
db.close()

print(f"Successfully injected {added_count} new images/attractions for existing destinations into the visual itinerary!")

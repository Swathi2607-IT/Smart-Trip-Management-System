import sqlite3

DATABASE = 'database/trip_management.db'

def seed_visuals_and_hotels():
    db = sqlite3.connect(DATABASE)
    cursor = db.cursor()

    # 1. Update Destination Images with high-quality real URLs
    visual_updates = [
        ('Rishikesh', 'https://www.chardham-tours.com/wp-content/uploads/2020/02/How-to-Reach-Rishikesh.jpg'),
        ('Shimla',    'https://tripandtales.com/wp-content/uploads/2025/08/Shimla.jpg'),
        ('Ladakh',    'https://s7ap1.scene7.com/is/image/incredibleindia/2-lamayuru-or-yuru-monastery-kargil-j_k-city-hero?qlt=82&ts=1726667854003'),
        ('Munnar',    'https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSh37V3dJvIiYwj9oFlSdq_xFPBfyo2qYgCVQ&s'),
        ('Manali',    'https://c.ndtvimg.com/2025-05/tvo5sgd_manali_625x300_01_May_25.jpg?im=FaceCrop,algorithm=dnn,width=1200,height=738'),
        ('Rajasthan', 'https://s7ap1.scene7.com/is/image/incredibleindia/hawa-mahal-jaipur-rajasthan-city-1-hero?qlt=82&ts=1742200253577')
    ]

    for name, url in visual_updates:
        cursor.execute("UPDATE destinations SET image_url = ? WHERE name = ?", (url, name))
        print(f"[OK] Updated image for {name}")

    # 2. Seed Hotels for ALL destinations (1 to 10)
    # Clear current hotels first (optional, safer for fresh data)
    cursor.execute("DELETE FROM hotels")
    
    hotels_data = [
        # Goa (1)
        (1, "Grand Hyatt Goa", "5-star luxury by the sea", 8500.00, "https://images.unsplash.com/photo-1542314831-068cd1dbfeeb?w=800&q=80"),
        (1, "Hotel Sea Breeze", "Cozy budget stay near beach", 1500.00, "https://images.unsplash.com/photo-1566073771259-6a8506099945?w=800&q=80"),
        # Manali (2)
        (2, "Span Resort & Spa", "Luxury resort by the river", 7200.00, "https://images.unsplash.com/photo-1582719478250-c89cae4df85b?w=800&q=80"),
        (2, "Snow View Lodge", "Affordable valley stay", 1800.00, "https://images.unsplash.com/photo-1520250497591-112f2f40a3f4?w=800&q=80"),
        # Munnar (3)
        (3, "Amber Dale Luxury", "Majestic view of the tea estates", 6500.00, "https://images.unsplash.com/photo-1571896349842-bc0cc6620f4c?w=800&q=80"),
        (3, "Green Tea Guest House", "Stay inside a tea plantation", 2200.00, "https://images.unsplash.com/photo-1540541338287-41700207dee6?w=800&q=80"),
        # Rajasthan (4)
        (4, "The Oberoi Rajvilas", "Royal luxury in Pink City", 15000.00, "https://images.unsplash.com/photo-1542314831-068cd1dbfeeb?w=800&q=80"),
        (4, "Chokhi Dhani Resort", "Authentic Rajasthani experience", 4500.00, "https://images.unsplash.com/photo-1566073771259-6a8506099945?w=800&q=80"),
        # Kerala Backwaters (5)
        (5, "Kumarakom Lake Resort", "Luxury stay by the lake", 9500.00, "https://images.unsplash.com/photo-1582719478250-c89cae4df85b?w=800&q=80"),
        (5, "Backwater Houseboat", "Authentic floating stay", 6000.00, "https://images.unsplash.com/photo-1540541338287-41700207dee6?w=800&q=80"),
        # Ladakh (6)
        (6, "Grand Dragon Ladakh", "Premier luxury in Leh", 8500.00, "https://images.unsplash.com/photo-1551882547-ff43c63efe81?w=800&q=80"),
        (6, "Himalayan Retreat", "Cozy high-altitude stay", 3500.00, "https://images.unsplash.com/photo-1571896349842-bc0cc6620f4c?w=800&q=80"),
        # Shimla (7)
        (7, "Wildflower Hall", "Shimla's iconic luxury hotel", 12000.00, "https://images.unsplash.com/photo-1566073771259-6a8506099945?w=800&q=80"),
        (7, "Ridge View Hotel", "Centrally located with city view", 2800.00, "https://images.unsplash.com/photo-1542314831-068cd1dbfeeb?w=800&q=80"),
        # Ooty (8)
        (8, "Savoy Hotel IHCL", "Colonial luxury in Nilgiris", 8500.00, "https://images.unsplash.com/photo-1582719478250-c89cae4df85b?w=800&q=80"),
        (8, "Nilgiris Stay", "Economical hill-top guest house", 2200.00, "https://images.unsplash.com/photo-1520250497591-112f2f40a3f4?w=800&q=80"),
        # Rishikesh (9)
        (9, "Taj Rishikesh Resort", "Luxury on the banks of Ganges", 14000.00, "https://images.unsplash.com/photo-1544550285-f813152fb2fd?w=800&q=80"),
        (9, "Ganga Kinare", "Riverside heritage hotel", 4500.00, "https://images.unsplash.com/photo-1589308078059-be1415eab4c3?w=800&q=80"),
        # Varanasi (10)
        (10, "BrijRama Palace", "Luxury over the ghats", 12000.00, "https://images.unsplash.com/photo-1561359313-0639aad49ca6?w=800&q=80"),
        (10, "Kashi Inn", "Safe and budget stay", 2500.00, "https://images.unsplash.com/photo-1582510003544-4d00b7f74220?w=800&q=80")
    ]

    cursor.executemany('''
        INSERT INTO hotels (destination_id, name, description, price_per_night, image_url)
        VALUES (?, ?, ?, ?, ?)
    ''', hotels_data)
    print(f"[OK] Inserted {len(hotels_data)} hotels.")

    db.commit()
    db.close()
    print("Database visual and hotel seeding complete!")

if __name__ == "__main__":
    seed_visuals_and_hotels()

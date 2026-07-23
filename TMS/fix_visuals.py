import sqlite3
import os

DATABASE = 'database/trip_management.db'

def fix_visuals():
    if not os.path.exists(DATABASE):
        print(f"Error: {DATABASE} not found!")
        return

    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    print("--- Patching Database with Reliable Visuals ---")

    # Destination Images (Unsplash - reliable)
    dest_visuals = [
        ('Goa', 'https://images.unsplash.com/photo-1512343879784-a960bf40e7f2?w=1200&q=80'),
        ('Manali', 'https://images.unsplash.com/photo-1598511757337-fe2cafc31dee?w=1200&q=80'),
        ('Munnar', 'https://images.unsplash.com/photo-1593642632823-8f785ba67e45?w=1200&q=80'),
        ('Rajasthan', 'https://images.unsplash.com/photo-1598511726613-5487d6567073?w=1200&q=80'),
        ('Kerala Backwaters', 'https://images.unsplash.com/photo-1602216056096-3b40cc0c9944?w=1200&q=80'),
        ('Ladakh', 'https://s7ap1.scene7.com/is/image/incredibleindia/2-lamayuru-or-yuru-monastery-kargil-j_k-city-hero?qlt=82&ts=1726667854003'),
        ('Shimla', 'https://images.unsplash.com/photo-1562534215-7ad5dad3aeeb?w=1200&q=80'),
        ('Ooty', 'https://images.unsplash.com/photo-1507525428034-b723cf961d3e?w=1200&q=80'),
        ('Rishikesh', 'https://images.unsplash.com/photo-1544550285-f813152fb2fd?w=1200&q=80'),
        ('Varanasi', 'https://images.unsplash.com/photo-1561359313-0639aad49ca6?w=1200&q=80'),
        ('Agra', 'https://images.unsplash.com/photo-1564507592333-c60657eea223?w=1200&q=80'),
        ('Andaman', 'https://images.unsplash.com/photo-1589197331516-4d8458bb8412?w=1200&q=80'),
        ('Darjeeling', 'https://images.unsplash.com/photo-1547843023-e69d7bdf9223?w=1200&q=80')
    ]

    for name, url in dest_visuals:
        cursor.execute("UPDATE destinations SET image_url = ? WHERE name = ?", (url, name))
        if cursor.rowcount > 0:
            print(f"[OK] Fixed destination: {name}")

    # Hotel Images (Broad high-quality hotel photos)
    hotel_img = "https://images.unsplash.com/photo-1566073771259-6a8506099945?w=800&q=80"
    luxury_img = "https://images.unsplash.com/photo-1542314831-068cd1dbfeeb?w=800&q=80"
    
    cursor.execute("UPDATE hotels SET image_url = ? WHERE price_per_night < 5000", (hotel_img,))
    cursor.execute("UPDATE hotels SET image_url = ? WHERE price_per_night >= 5000", (luxury_img,))
    print(f"[OK] Patched hotel images ({cursor.rowcount} updated)")

    conn.commit()
    conn.close()
    print("--- Database Image Patching Complete ---")

if __name__ == "__main__":
    fix_visuals()

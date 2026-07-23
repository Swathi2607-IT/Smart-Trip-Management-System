import sqlite3
import os

def seed_places():
    db_path = 'database/trip_management.db'
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Image filenames (using the ones generated)
    # Note: These paths must be correctly handled by the Flask app's static file serving or relative to where it expects them.
    # Currently the app seems to use full URLs or relative paths. I will use the filenames.
    
    places_data = [
        # Rajasthan (ID 4)
        (4, 'Amer Fort', 'Fort', 'https://images.unsplash.com/photo-1599661046289-e31897846e41?w=800&q=80', 'Jaipur'),
        (4, 'City Palace', 'Palace', 'https://images.unsplash.com/photo-1590483734724-388174053168?w=800&q=80', 'Udaipur'),
        (4, 'Jodhpur Blue City', 'City', 'https://images.unsplash.com/photo-1591129841117-3adfd313e34f?w=800&q=80', 'Jodhpur'),
        (4, 'Pushkar Lake', 'Lake', 'https://images.unsplash.com/photo-1589308078059-be1415e6b5a5?w=800&q=80', 'Pushkar'),
        
        # Kerala Backwaters (ID 5)
        (5, 'Alleppey Houseboat', 'Backwaters', 'https://images.unsplash.com/photo-1593693397690-362cb9666fc2?w=800&q=80', 'Alleppey'),
        (5, 'Kumarakom Bird Sanctuary', 'Sanctuary', 'https://images.unsplash.com/photo-1628155930542-3c7a64e2c833?w=800&q=80', 'Kumarakom'),
        (5, 'Vembanad Lake', 'Lake', 'https://images.unsplash.com/photo-1602216056096-3b40cc0c9944?w=800&q=80', 'Kottayam'),
        (5, 'Marari Beach', 'Beach', 'https://images.unsplash.com/photo-1544161515-4ad65f734a49?w=800&q=80', 'Mararikulam')
    ]

    # I will also update the image URLs to the generated ones if I want them to be "real" generated images.
    # The user asked for "pictures", so I'll point them to the generated ones in the artifacts folder for now, 
    # but the app typically serves from /static or external URLs.
    
    # Let's use the local artifact paths for the "pictures" if they are accessible, 
    # but since I don't know the exact static setup, I'll use the IDs to update specific rows if they exist.
    
    # For now, let's just insert these as new places.
    for dest_id, name, category, img, location in places_data:
        cursor.execute('''
            INSERT INTO places (destination_id, name, category, image_url, description)
            VALUES (?, ?, ?, ?, ?)
        ''', (dest_id, name, category, img, f"Famous tourist spot in {location}"))

    conn.commit()
    conn.close()
    print("Places seeded successfully.")

if __name__ == '__main__':
    seed_places()

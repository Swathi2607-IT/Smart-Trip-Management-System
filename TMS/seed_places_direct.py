import sqlite3
db_path = 'c:/TMS/database/trip_management.db'
conn = sqlite3.connect(db_path)
cursor = conn.cursor()
data = [
    (4, 'Amer Fort', 'Fort', 'https://images.unsplash.com/photo-1599661046289-e31897846e41?w=800&q=80'),
    (4, 'City Palace', 'Palace', 'https://images.unsplash.com/photo-1590483734724-388174053168?w=800&q=80'),
    (4, 'Jodhpur Blue City', 'City', 'https://images.unsplash.com/photo-1591129841117-3adfd313e34f?w=800&q=80'),
    (4, 'Pushkar Lake', 'Lake', 'https://images.unsplash.com/photo-1589308078059-be1415e6b5a5?w=800&q=80'),
    (5, 'Alleppey Houseboat', 'Backwaters', 'https://images.unsplash.com/photo-1593693397690-362cb9666fc2?w=800&q=80'),
    (5, 'Kumarakom Bird Sanctuary', 'Sanctuary', 'https://images.unsplash.com/photo-1628155930542-3c7a64e2c833?w=800&q=80'),
    (5, 'Vembanad Lake', 'Lake', 'https://images.unsplash.com/photo-1602216056096-3b40cc0c9944?w=800&q=80'),
    (5, 'Marari Beach', 'Beach', 'https://images.unsplash.com/photo-1544161515-4ad65f734a49?w=800&q=80')
]
for d in data:
    cursor.execute('INSERT INTO places (destination_id, name, category, image_url) VALUES (?, ?, ?, ?)', d)
conn.commit()
conn.close()
print("Success")

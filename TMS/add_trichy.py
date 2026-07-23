import sqlite3
import requests
from datetime import datetime

db_path = 'database/trip_management.db'

# 1. Fetch Weather for Samayapuram (10.92, 78.74)
lat, lon = 10.92, 78.74
weather_status = 'Clear'
weather_temp = 25
weather_icon = '☀️'

try:
    url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&daily=weather_code,temperature_2m_max&timezone=auto"
    resp = requests.get(url, timeout=5)
    if resp.status_code == 200:
        data = resp.json()['daily']
        code = data['weather_code'][0]
        weather_temp = int(data['temperature_2m_max'][0])
        icons = {0: '☀️', 1: '⛅', 2: '⛅', 3: '☁️', 45: '🌫️', 51: '🌧️', 61: '🌦️', 71: '❄️', 95: '⛈️'}
        weather_icon = icons.get(code, '🌡️')
        
        if code == 0: weather_status = 'Sunny'
        elif code in [1, 2, 3, 45]: weather_status = 'Cloudy'
        elif code in [51, 61]: weather_status = 'Rainy'
        elif code == 95: weather_status = 'Stormy'
except Exception as e:
    print(f"Weather Fetch Error: {e}")

print(f"Adding Trichy - Samayapuram with Weather: {weather_temp}C ({weather_status})")

# 2. Insert into Database
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Insert Destination
dest_data = (
    'Trichy - Samayapuram',
    'Experience the spiritual aura of the Arulmigu Mariamman Temple, a historic pilgrimage site near Tiruchirappalli. Known for its powerful deity and vibrant festivals, it offers a deep cultural dive into Tamil Nadu traditions.',
    2800.0,
    '/static/images/destinations/samayapuram.png',
    weather_temp,
    weather_status,
    'Pilgrimage',
    'Tamil Nadu, India',
    lat,
    lon
)

cursor.execute('''
    INSERT INTO destinations (name, description, base_price, image_url, weather_temp, weather_status, category, location, latitude, longitude)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
''', dest_data)

dest_id = cursor.lastrowid

# Insert Places for this destination
places = [
    (dest_id, 'Arulmigu Mariamman Temple', 'Temple', 'https://images.unsplash.com/photo-1614583225154-5feaba071595?w=800&q=80'),
    (dest_id, 'Rockfort Ucchi Pillayar Temple', 'Landmark', 'https://images.unsplash.com/photo-1621255556209-e85df6469446?w=800&q=80'),
    (dest_id, 'Sri Ranganathaswamy Temple', 'Temple', 'https://images.unsplash.com/photo-1596402184320-417d7178b2cd?w=800&q=80'),
    (dest_id, 'Kallanai Dam', 'Historic Site', 'https://images.unsplash.com/photo-1582512355163-45607374828b?w=800&q=80')
]

cursor.executemany('INSERT INTO places (destination_id, name, category, image_url) VALUES (?, ?, ?, ?)', places)

conn.commit()
conn.close()

print(f"Successfully added Trichy - Samayapuram with ID: {dest_id}")

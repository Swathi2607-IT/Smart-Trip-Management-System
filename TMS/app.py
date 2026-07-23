import os
import math
import sqlite3
import random
import binascii
from datetime import datetime, timedelta
from functools import wraps
import requests
from flask import (Flask, render_template, request, redirect,
                   url_for, session, flash, g, jsonify)
from werkzeug.security import generate_password_hash, check_password_hash

# ─────────────────────────────────────────
#  APP SETUP
# ─────────────────────────────────────────
app = Flask(__name__)
app.secret_key = 'tms_super_secret_key_2026'
DATABASE = 'database/trip_management.db'


# ─────────────────────────────────────────
#  DATABASE HELPERS
# ─────────────────────────────────────────
def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
        db.row_factory = sqlite3.Row
        db.execute("PRAGMA foreign_keys = ON")
    return db


@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()


def init_db():
    if not os.path.exists('database'):
        os.makedirs('database')
    is_new = not os.path.exists(DATABASE)
    with app.app_context():
        db = get_db()
        if is_new:
            with app.open_resource('database/schema_sqlite.sql', mode='r') as f:
                db.cursor().executescript(f.read())
            db.commit()
            print("[OK] Database initialized with seed data.")


# ─────────────────────────────────────────
#  DECORATORS
# ─────────────────────────────────────────
def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            flash("Please log in to access this page.", "warning")
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated


def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if session.get('role') != 'admin':
            flash("Admin access required.", "danger")
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated


def guide_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if session.get('role') != 'guide':
            flash("Guide access required.", "danger")
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated


# ─────────────────────────────────────────
#  WEATHER API HELPER
# ─────────────────────────────────────────
def get_weather_forecast(lat, lon):
    """Fetch 5-day forecast from Open-Meteo API"""
    if not lat or not lon:
        return None
    try:
        url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&daily=weather_code,temperature_2m_max,temperature_2m_min&timezone=auto"
        resp = requests.get(url, timeout=5)
        if resp.status_code == 200:
            data = resp.json()['daily']
            forecast = []
            # Map weather codes to icons (simplified)
            icons = {0: '☀️', 1: '⛅', 2: '⛅', 3: '☁️', 45: '🌫️', 51: '🌧️', 61: '🌦️', 71: '❄️', 95: '⛈️'}
            for i in range(5):
                code = data['weather_code'][i]
                icon = icons.get(code, '🌡️')
                date_obj = datetime.strptime(data['time'][i], '%Y-%m-%d')
                forecast.append({
                    'day': date_obj.strftime('%a'),
                    'temp': f"{int(data['temperature_2m_max'][i])}°",
                    'icon': icon
                })
            return forecast
    except Exception as e:
        print(f"Weather API Error: {e}")
    return None

def get_weather_for_date(lat, lon, target_date):
    """Fetch weather for a specific date (Forecast or Historical)"""
    if not lat or not lon:
        return None
    
    try:
        today = datetime.now()
        target = datetime.strptime(target_date, '%Y-%m-%d')
        diff_days = (target - today).days

        # Weather Icons mapping
        icons = {0: '☀️', 1: '⛅', 2: '⛅', 3: '☁️', 45: '🌫️', 51: '🌧️', 61: '🌦️', 71: '❄️', 95: '⛈️'}

        if 0 <= diff_days <= 15:
            # Use Forecast API (16 day support)
            url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&daily=weather_code,temperature_2m_max&timezone=auto&forecast_days=16"
            resp = requests.get(url, timeout=5)
            if resp.status_code == 200:
                data = resp.json()['daily']
                for i in range(len(data['time'])):
                    if data['time'][i] == target_date:
                        code = data['weather_code'][i]
                        return {
                            'temp': f"{int(data['temperature_2m_max'][i])}°C",
                            'icon': icons.get(code, '🌡️'),
                            'label': 'Forecast Prediction',
                            'class': 'forecast'
                        }
        else:
            # Shift back 1 year to provide a "Historical Suggestion"
            hist_date = (target.replace(year=target.year - 1)).strftime('%Y-%m-%d')
            url = f"https://archive-api.open-meteo.com/v1/archive?latitude={lat}&longitude={lon}&start_date={hist_date}&end_date={hist_date}&daily=weather_code,temperature_2m_max&timezone=auto"
            resp = requests.get(url, timeout=5)
            if resp.status_code == 200:
                data = resp.json()['daily']
                code = data['weather_code'][0]
                return {
                    'temp': f"{int(data['temperature_2m_max'][0])}°C",
                    'icon': icons.get(code, '🌡️'),
                    'label': 'Historical Suggestion (Based on Last Year)',
                    'class': 'historic'
                }
    except Exception as e:
        print(f"Weather prediction error: {e}")
    return None
def enhance_destinations_with_weather(destinations):
    enhanced = []
    for d in destinations:
        dest_dict = dict(d)
        lat = dest_dict.get('latitude')
        lon = dest_dict.get('longitude')
        
        if lat and lon:
            forecast = get_weather_forecast(lat, lon)
            if forecast and len(forecast) > 0:
                today = forecast[0]
                dest_dict['weather_temp'] = today['temp'].replace('°', '')
                icon = today['icon']
                dest_dict['weather_icon'] = icon
                if '☀️' in icon: dest_dict['weather_status'] = 'Sunny'
                elif '⛅' in icon or '☁️' in icon or '🌫️' in icon: dest_dict['weather_status'] = 'Cloudy'
                elif '🌧️' in icon or '🌦️' in icon: dest_dict['weather_status'] = 'Rainy'
                elif '⛈️' in icon: dest_dict['weather_status'] = 'Stormy'
                elif '❄️' in icon: dest_dict['weather_status'] = 'Snowy'
                else: dest_dict['weather_status'] = 'Clear'
        else:
            # Fallback for missing coordinates
            dest_dict['weather_status'] = 'Clear'
            dest_dict['weather_temp'] = '25'
            dest_dict['weather_icon'] = '☀️'
            
        enhanced.append(dest_dict)
    return enhanced


def generate_smart_itinerary(dest, places, duration, start_date, transport_mode=None, hotel_name=None):
    dest = dict(dest) if not isinstance(dest, dict) else dest
    indoor_cats = ['Museum', 'Church', 'Monastery', 'Temple', 'Shopping', 'Fort', 'Landmark']
    
    places_dicts = [dict(p) for p in places]
    # Sort places into indoor and outdoor
    indoor_places = [p for p in places_dicts if p.get('category') in indoor_cats]
    outdoor_places = [p for p in places_dicts if p.get('category') not in indoor_cats]
    
    # Fetch 5-day forecast
    lat = dest.get('latitude')
    lon = dest.get('longitude')
    
    forecast = None
    if lat and lon:
        forecast = get_weather_forecast(lat, lon)
        
    forecast_map = {}
    if forecast:
        for f in forecast:
            status = 'Clear'
            if '🌧️' in f['icon'] or '⛈️' in f['icon'] or '❄️' in f['icon']:
                status = 'Rainy'
            forecast_map[f['day']] = status
            
    itinerary_plan = {}
    breakfast = {'name': 'Breakfast at Hotel', 'category': 'Dining', 'image_url': 'https://images.unsplash.com/photo-1533089860892-a7c6f0a88666?w=800&q=80'}
    lunch     = {'name': 'Lunch at Local Restaurant', 'category': 'Dining', 'image_url': 'https://images.unsplash.com/photo-1504674900247-0877df9cc836?w=800&q=80'}
    dinner    = {'name': 'Dinner & Evening Walk', 'category': 'Dining', 'image_url': 'https://images.unsplash.com/photo-1517248135467-4c7edcad34c4?w=800&q=80'}
    leisure   = {'name': 'Leisure & Local Exploration', 'category': 'Relaxation', 'image_url': 'https://images.unsplash.com/photo-1499793983690-e29da59ef1c2?w=800&q=80'}

    for day in range(1, duration + 1):
        schedule = []
        current_date = start_date + timedelta(days=day - 1)
        day_str = current_date.strftime('%a')
        weather_today = forecast_map.get(day_str, 'Clear')
        
        # Decide list to pull from based on weather
        if weather_today == 'Rainy' and indoor_places:
            primary_list, secondary_list = indoor_places, outdoor_places
            alert = '🌧 Rainy day forecasted. Prioritized indoor activities!'
        else:
            primary_list, secondary_list = outdoor_places, indoor_places
            alert = '☀️ Clear weather forecasted. Prioritized outdoor activities!' if weather_today != 'Rainy' else None

        # Slot 1: Morning
        if day == 1 and transport_mode:
            schedule.append({'time': '08:00 AM', 'name': f'Arrival via {transport_mode}', 'category': 'Transit'})
        else:
            b_dict = dict(breakfast)
            b_dict['time'] = '08:30 AM'
            schedule.append(b_dict)

        # Slot 2: Late Morning
        if primary_list:
            p = primary_list.pop(0)
            p['time'] = '10:30 AM'
            schedule.append(p)
        elif secondary_list:
            p = secondary_list.pop(0)
            p['time'] = '10:30 AM'
            schedule.append(p)
        else:
            l_dict = dict(leisure)
            l_dict['time'] = '10:30 AM'
            schedule.append(l_dict)

        # Slot 3: Lunch or Check-in
        if day == 1 and hotel_name:
            schedule.append({'time': '14:00 PM', 'name': f'Hotel Check-in at {hotel_name}', 'category': 'Accommodation'})
        else:
            l_dict = dict(lunch)
            l_dict['time'] = '13:00 PM'
            schedule.append(l_dict)
            
        # Slot 4: Afternoon
        if primary_list:
            p = primary_list.pop(0)
            p['time'] = '15:30 PM'
            schedule.append(p)
        elif secondary_list:
            p = secondary_list.pop(0)
            p['time'] = '15:30 PM'
            schedule.append(p)
        else:
            l_dict = dict(leisure)
            l_dict['time'] = '15:30 PM'
            schedule.append(l_dict)

        # Slot 5: Dinner
        d_dict = dict(dinner)
        d_dict['time'] = '19:00 PM'
        schedule.append(d_dict)

        itinerary_plan[day] = {
            'date_str': current_date.strftime('%d %b %Y'),
            'alert': alert,
            'slots': schedule
        }

    return itinerary_plan

# ─────────────────────────────────────────
#  AUTH ROUTES
# ─────────────────────────────────────────
@app.route('/login', methods=['GET', 'POST'])
def login():
    if 'user_id' in session:
        return redirect(url_for('index'))
    if request.method == 'POST':
        email    = request.form['email'].strip()
        password = request.form['password']
        db   = get_db()
        user = db.execute("SELECT * FROM users WHERE email = ?", (email,)).fetchone()

        if user and check_password_hash(user['password'], password):
            session['user_id'] = user['id']
            session['name']    = user['name']
            session['email']   = user['email']
            session['role']    = user['role']

            if user['role'] == 'admin':
                flash(f"Welcome back, Admin {user['name']}!", "success")
                return redirect(url_for('admin_dashboard'))
            elif user['role'] == 'guide':
                flash(f"Welcome, Guide {user['name']}!", "success")
                return redirect(url_for('guide_dashboard'))
            else:
                flash(f"Welcome back, {user['name']}! 🌍", "success")
                return redirect(url_for('user_dashboard'))
        else:
            flash("Invalid email or password.", "danger")
    return render_template('login.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if 'user_id' in session:
        return redirect(url_for('index'))
    if request.method == 'POST':
        name     = request.form['name'].strip()
        email    = request.form['email'].strip().lower()
        phone    = request.form['phone'].strip()
        password = generate_password_hash(request.form['password'])
        db = get_db()
        try:
            db.execute(
                "INSERT INTO users (name, email, phone, password, role) VALUES (?, ?, ?, ?, 'user')",
                (name, email, phone, password)
            )
            db.commit()
            flash("Account created! You can now log in.", "success")
            return redirect(url_for('login'))
        except sqlite3.IntegrityError:
            flash("That email is already registered.", "danger")
    return render_template('register.html')


@app.route('/logout')
def logout():
    session.clear()
    flash("You've been logged out. Safe travels! ✈️", "info")
    return redirect(url_for('index'))


# ─────────────────────────────────────────
#  HOME
# ─────────────────────────────────────────
@app.route('/')
def index():
    db           = get_db()
    # Fetch top 6 destinations by average rating
    destinations = db.execute('''
        SELECT d.*, IFNULL(AVG(r.rating), 0) as avg_rating, COUNT(r.id) as review_count
        FROM destinations d
        LEFT JOIN reviews r ON d.id = r.destination_id
        GROUP BY d.id
        ORDER BY avg_rating DESC, d.id DESC
        LIMIT 6
    ''').fetchall()
    destinations = enhance_destinations_with_weather(destinations)
    
    total_dests  = db.execute("SELECT COUNT(*) FROM destinations").fetchone()[0]
    # "Happy Travellers" includes both Confirmed and Completed bookings
    booking_count= db.execute("SELECT COUNT(*) FROM bookings WHERE status IN ('Confirmed', 'Completed')").fetchone()[0]
    guide_count  = db.execute("SELECT COUNT(*) FROM guides").fetchone()[0]
    
    # Calculate overall site satisfaction
    avg_site_rating = db.execute("SELECT IFNULL(AVG(rating), 4.9) FROM reviews").fetchone()[0]

    return render_template('index.html',
                           destinations=destinations,
                           total_dests=total_dests,
                           booking_count=booking_count,
                           guide_count=guide_count,
                           dest_count=total_dests,
                           avg_site_rating=round(float(avg_site_rating), 1))


# ─────────────────────────────────────────
#  DESTINATIONS
# ─────────────────────────────────────────
@app.route('/api/weather-prediction')
def weather_prediction_api():
    lat = request.args.get('lat')
    lon = request.args.get('lon')
    date = request.args.get('date')
    
    if not lat or not lon or not date:
        return jsonify({'error': 'Missing parameters'}), 400
        
    result = get_weather_for_date(lat, lon, date)
    if result:
        return jsonify(result)
    return jsonify({'error': 'Prediction unavailable'}), 404


@app.route('/destinations')
def destinations():
    db           = get_db()
    destinations = db.execute('''
        SELECT d.*, IFNULL(AVG(r.rating), 0) as avg_rating, COUNT(r.id) as review_count
        FROM destinations d
        LEFT JOIN reviews r ON d.id = r.destination_id
        GROUP BY d.id
        ORDER BY avg_rating DESC, d.id DESC
    ''').fetchall()
    destinations = enhance_destinations_with_weather(destinations)
    return render_template('destinations.html', destinations=destinations)


@app.route('/destination/<int:id>')
def destination_details(id):
    db   = get_db()
    dest = db.execute("SELECT * FROM destinations WHERE id = ?", (id,)).fetchone()
    if not dest:
        return redirect(url_for('destinations'))

    # Apply real-time weather
    dest = enhance_destinations_with_weather([dest])[0]

    places     = db.execute("SELECT * FROM places WHERE destination_id = ?", (id,)).fetchall()
    transports = db.execute("SELECT * FROM transports").fetchall()

    bad_weather  = {'Rainy', 'Stormy', 'Snowy'}
    is_bad_weather = dest['weather_status'] in bad_weather

    # Fetch 5-Day Forecast
    weather_forecast = get_weather_forecast(dest['latitude'], dest['longitude'])

    # Fetch Recent Reviews
    reviews = db.execute('''
        SELECT r.*, u.name as user_name 
        FROM reviews r 
        JOIN users u ON r.user_id = u.id 
        WHERE r.destination_id = ? 
        ORDER BY r.id DESC LIMIT 5
    ''', (id,)).fetchall()

    avg_rating = db.execute("SELECT AVG(rating) FROM reviews WHERE destination_id = ?", (id,)).fetchone()[0] or 0

    return render_template('destination_details.html',
                           dest=dest, places=places,
                           transports=transports,
                           is_bad_weather=is_bad_weather,
                           weather_forecast=weather_forecast,
                           reviews=reviews,
                           avg_rating=round(avg_rating, 1))

@app.route('/destination/<int:id>/preview-itinerary')
def preview_itinerary(id):
    db   = get_db()
    dest = db.execute("SELECT * FROM destinations WHERE id = ?", (id,)).fetchone()
    if not dest:
        return redirect(url_for('destinations'))

    places = db.execute("SELECT * FROM places WHERE destination_id = ?", (id,)).fetchall()
    
    # Simulate a 3-day trip starting tomorrow
    start_date = datetime.now() + timedelta(days=1)
    
    itinerary_plan = generate_smart_itinerary(dest, places, duration=3, start_date=start_date)
    
    # We will reuse the itinerary.html template with a dummy booking object
    dummy_booking = {
        'id': 'PREVIEW',
        'duration': 3,
        'start_date': start_date.strftime('%Y-%m-%d'),
        'end_date': (start_date + timedelta(days=2)).strftime('%Y-%m-%d'),
        'passengers': 2,
        'transport_mode': 'To be selected',
        'total_cost': 0,
        'guide_name': None
    }
    
    return render_template('itinerary.html',
                           booking=dummy_booking,
                           itinerary=itinerary_plan,
                           is_preview=True,
                           dest_id=id)

# ─────────────────────────────────────────
#  BOOKING FLOW
# ─────────────────────────────────────────
@app.route('/book')
@login_required
def book():
    if session.get('role') != 'user':
        flash("Only traveller accounts can make bookings.", "warning")
        return redirect(url_for('destinations'))

    dest_id = request.args.get('dest_id')
    if not dest_id:
        return redirect(url_for('destinations'))

    db         = get_db()
    dest       = db.execute("SELECT * FROM destinations WHERE id = ?", (dest_id,)).fetchone()
    transports = db.execute("SELECT * FROM transports").fetchall()
    hotels     = db.execute("SELECT * FROM hotels WHERE destination_id = ?", (dest_id,)).fetchall()
    guides     = db.execute("SELECT * FROM guides WHERE destination_id = ? OR destination_id IS NULL ORDER BY rating DESC LIMIT 5", (dest_id,)).fetchall()
    today_date = datetime.now().strftime('%Y-%m-%d')

    if not dest:
        return redirect(url_for('destinations'))

    return render_template('book.html', dest=dest,
                           transports=transports,
                           hotels=hotels,
                           guides=guides,
                           today_date=today_date)


@app.route('/checkout', methods=['POST'])
@login_required
def checkout():
    dest_id         = request.form['dest_id']
    start_date      = request.form['start_date']
    duration        = int(request.form.get('duration', 1))
    trip_start_mode = request.form.get('trip_start_mode', 'From Departure')
    transport_id    = int(request.form.get('transport_id', 0))
    hotel_id        = int(request.form.get('hotel_id', 0))
    local_transport = 1 if request.form.get('local_transport_req') == 'on' else 0
    passengers      = max(1, int(request.form.get('passengers', 1)))
    guide_id_input  = request.form.get('guide_id', '')

    db   = get_db()
    dest = db.execute("SELECT * FROM destinations WHERE id = ?", (dest_id,)).fetchone()
    if not dest:
        flash("Destination not found.", "danger")
        return redirect(url_for('destinations'))

    # 1. Transport Cost
    transport_cost = 0.0
    transport_mode = 'Self-Arranged'
    if transport_id > 0:
        t = db.execute("SELECT * FROM transports WHERE id = ?", (transport_id,)).fetchone()
        if t:
            transport_cost = float(t['average_cost']) * passengers
            transport_mode = t['mode']

    # 2. Hotel Cost
    hotel_cost = 0.0
    is_hotel_booked = 0
    if hotel_id > 0:
        h = db.execute("SELECT * FROM hotels WHERE id = ?", (hotel_id,)).fetchone()
        if h:
            # Rooms = 1 room for every 2 passengers
            rooms = math.ceil(passengers / 2)
            # Duration - 1 for nights
            nights = max(1, duration - 1)
            hotel_cost = float(h['price_per_night']) * nights * rooms
            is_hotel_booked = 1

    # 3. Local Transport Cost
    local_transport_cost = 0.0
    if local_transport:
        local_transport_cost = 1500.0 * duration

    # 4. Guide Cost & Assignment Initialization
    guide_cost = 0.0
    guide_requested = 0
    guide_id = None
    guide_status = 'Unassigned'
    
    if guide_id_input == 'auto':
        guide_requested = 1
        avg_price = db.execute("SELECT AVG(price) FROM guides WHERE destination_id = ?", (dest_id,)).fetchone()[0]
        guide_price_per_day = float(avg_price) if avg_price else 1000.0
        guide_cost = guide_price_per_day * duration
    elif guide_id_input.isdigit():
        guide_requested = 1
        guide_id = int(guide_id_input)
        guide_status = 'Pending'
        g = db.execute("SELECT * FROM guides WHERE id = ?", (guide_id,)).fetchone()
        if g:
            guide_cost = float(g['price']) * duration

    # 5. Total Calculation
    start_obj    = datetime.strptime(start_date, '%Y-%m-%d')
    package_cost = duration * float(dest['base_price']) * passengers
    total_cost   = package_cost + transport_cost + hotel_cost + local_transport_cost + guide_cost

    if trip_start_mode == 'After Arrival':
        actual_start = start_obj + timedelta(days=1)
    else:
        actual_start = start_obj

    end_date = actual_start + timedelta(days=duration - 1)

    departure_city = request.form.get('departure_city', '')

    cursor = db.execute('''
        INSERT INTO bookings
          (user_id, destination_id, start_date, duration, end_date,
           trip_start_mode, transport_mode, transport_cost,
           package_cost, total_cost, status, payment_status, passengers,
           hotel_id, hotel_cost, is_hotel_booked, local_transport_req, local_transport_cost,
           guide_requested, guide_id, guide_status, guide_cost, departure_city)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'Pending', 'Unpaid', ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (session['user_id'], dest['id'],
          actual_start.strftime('%Y-%m-%d'),
          duration,
          end_date.strftime('%Y-%m-%d'),
          trip_start_mode, transport_mode,
          transport_cost, package_cost, total_cost, passengers,
          hotel_id if hotel_id > 0 else None, hotel_cost, is_hotel_booked,
          local_transport, local_transport_cost, guide_requested, guide_id, guide_status, guide_cost, departure_city))
    db.commit()

    return render_template('checkout.html',
        booking_id=cursor.lastrowid,
        dest_base_price=dest['base_price'],
        duration=duration,
        package_cost=package_cost,
        transport_cost=transport_cost,
        transport_mode=transport_mode,
        hotel_cost=hotel_cost,
        is_hotel_booked=is_hotel_booked,
        local_transport_cost=local_transport_cost,
        local_transport_req=local_transport,
        start_date_obj=start_obj,
        trip_start_mode=trip_start_mode,
        actual_start_date=actual_start,
        end_date_obj=end_date,
        total_cost=total_cost,
        passengers=passengers,
        guide_requested=guide_requested,
        guide_cost=guide_cost)


@app.route('/cancel_pending', methods=['POST'])
@login_required
def cancel_pending():
    booking_id = request.form['booking_id']
    db = get_db()
    db.execute(
        "DELETE FROM bookings WHERE id = ? AND user_id = ? AND status = 'Pending'",
        (booking_id, session['user_id'])
    )
    db.commit()
    flash("Pending booking discarded.", "info")
    return redirect(url_for('destinations'))


# ─────────────────────────────────────────
#  PAYMENT
# ─────────────────────────────────────────
@app.route('/payment', methods=['GET', 'POST'])
@login_required
def payment():
    if request.method == 'GET':
        return redirect(url_for('my_bookings'))

    booking_id = request.form.get('booking_id')
    db         = get_db()
    booking    = db.execute(
        "SELECT * FROM bookings WHERE id = ? AND user_id = ? AND status = 'Pending'",
        (booking_id, session['user_id'])
    ).fetchone()

    if not booking:
        flash("Booking not found or already paid.", "danger")
        return redirect(url_for('my_bookings'))

    if 'pay_now' in request.form:
        txn_id  = 'UPI' + datetime.now().strftime('%Y%m%d%H%M%S') + str(random.randint(100, 999))
        receipt_token = binascii.hexlify(os.urandom(16)).decode()

        if booking['guide_requested']:
            if booking['guide_status'] == 'Unassigned' or not booking['guide_id']:
                guide = db.execute('''
                    SELECT id FROM guides 
                    WHERE destination_id = ? 
                    ORDER BY rating DESC LIMIT 1
                ''', (booking['destination_id'],)).fetchone()
                # If no specific guide found for dest, fallback
                if not guide:
                    guide = db.execute("SELECT id FROM guides ORDER BY rating DESC LIMIT 1").fetchone()
                
                final_guide_id = guide['id'] if guide else None
                final_guide_status = 'Pending' if final_guide_id else 'Unassigned'
            else:
                final_guide_id = booking['guide_id']
                final_guide_status = 'Pending'
        else:
            final_guide_id = None
            final_guide_status = 'Unassigned'

        db.execute(
            "INSERT INTO payments (booking_id, transaction_id, amount, payment_method) VALUES (?, ?, ?, 'UPI')",
            (booking_id, txn_id, booking['total_cost'])
        )
        db.execute(
            "UPDATE bookings SET status='Confirmed', payment_status='Paid', receipt_token=?, guide_id=?, guide_status=? WHERE id=?",
            (receipt_token, final_guide_id, final_guide_status, booking_id)
        )
        db.commit()
        flash("Payment successful! 🎉 Booking confirmed.", "success")
        return redirect(url_for('receipt', token=receipt_token))

    return render_template('payment.html', booking=booking)


# ─────────────────────────────────────────
#  RECEIPT
# ─────────────────────────────────────────
@app.route('/receipt/<token>')
@login_required
def receipt(token):
    db = get_db()
    receipt = db.execute('''
        SELECT b.*, d.name AS dest_name,
               u.name AS traveler_name, u.email AS traveler_email,
               g.name AS guide_name, g.phone AS guide_phone,
               p.transaction_id, p.payment_date
        FROM bookings b
        JOIN destinations d ON b.destination_id = d.id
        JOIN users u        ON b.user_id = u.id
        LEFT JOIN guides g  ON b.guide_id = g.id
        LEFT JOIN payments p ON b.id = p.booking_id
        WHERE b.receipt_token = ?
    ''', (token,)).fetchone()

    if not receipt:
        flash("Invalid receipt token.", "danger")
        return redirect(url_for('my_bookings'))

    if session['role'] != 'admin' and session['user_id'] != receipt['user_id']:
        flash("Unauthorized.", "danger")
        return redirect(url_for('index'))

    return render_template('receipt.html', receipt=receipt)


# ─────────────────────────────────────────
#  MY BOOKINGS
# ─────────────────────────────────────────
@app.route('/my_bookings')
@login_required
def my_bookings():
    db   = get_db()
    rows = db.execute('''
        SELECT b.*, d.name AS dest_name, d.image_url, 
               g.name AS guide_name, g.phone AS guide_phone
        FROM bookings b
        JOIN destinations d ON b.destination_id = d.id
        LEFT JOIN guides g ON b.guide_id = g.id
        WHERE b.user_id = ?
        ORDER BY b.id DESC
    ''', (session['user_id'],)).fetchall()

    bookings = []
    today = datetime.now()
    for b in rows:
        bd = dict(b)
        try:
            trip_start = datetime.strptime(bd['start_date'], '%Y-%m-%d')
            bd['can_cancel']  = today < trip_start
            bd['has_started'] = today >= trip_start
        except Exception:
            bd['can_cancel']  = False
            bd['has_started'] = False
        bookings.append(bd)

    return render_template('my_bookings.html', bookings=bookings)


# ─────────────────────────────────────────
#  CANCEL BOOKING
# ─────────────────────────────────────────
@app.route('/cancel_booking/<int:id>', methods=['GET', 'POST'])
@login_required
def cancel_booking(id):
    db      = get_db()
    booking = db.execute(
        "SELECT * FROM bookings WHERE id = ? AND user_id = ? AND status = 'Confirmed'",
        (id, session['user_id'])
    ).fetchone()

    if not booking:
        return redirect(url_for('my_bookings'))

    today      = datetime.now()
    trip_start = datetime.strptime(booking['start_date'], '%Y-%m-%d')
    days_diff  = (trip_start - today).days

    if days_diff < 0:
        flash("Trip has already started. Cancellation not allowed.", "danger")
        return redirect(url_for('my_bookings'))

    refund_amount = 0.0
    if days_diff > 5:
        refund_amount = float(booking['total_cost'])
    elif 2 <= days_diff <= 5:
        refund_amount = float(booking['total_cost']) * 0.5

    if request.method == 'POST' and 'confirm_cancel' in request.form:
        db.execute(
            "UPDATE bookings SET status='Cancelled', refund_amount=?, cancellation_date=CURRENT_TIMESTAMP WHERE id=?",
            (refund_amount, id)
        )
        db.execute(
            "UPDATE payments SET payment_method='Refund Processed' WHERE booking_id=?",
            (id,)
        )
        db.commit()
        flash(f"Booking cancelled. Refund of ₹{refund_amount:,.0f} will be processed.", "success")
        return redirect(url_for('my_bookings'))

    return render_template('cancel_booking.html',
                           booking=booking,
                           days_diff=days_diff,
                           refund_amount=refund_amount)


# ─────────────────────────────────────────
#  ITINERARY
# ─────────────────────────────────────────
@app.route('/itinerary/<int:booking_id>')
@login_required
def itinerary(booking_id):
    db      = get_db()
    booking = db.execute('''
        SELECT b.*, d.name AS dest_name, g.name AS guide_name, g.phone AS guide_phone
        FROM bookings b
        JOIN destinations d ON b.destination_id = d.id
        LEFT JOIN guides g ON b.guide_id = g.id
        WHERE b.id = ?
    ''', (booking_id,)).fetchone()

    if not booking:
        flash("Booking not found.", "danger")
        return redirect(url_for('my_bookings'))

    if session['role'] not in ('admin', 'guide') and session['user_id'] != booking['user_id']:
        flash("Unauthorized.", "danger")
        return redirect(url_for('index'))

    places = db.execute("SELECT * FROM places WHERE destination_id = ?", (booking['destination_id'],)).fetchall()
    
    # Get hotel details if booked
    hotel_name = None
    # We don't have hotel_id strictly stored in bookings in schema, let's just say "Your Hotel"
    # Actually wait: let's query the payment or something? Or just default.
    hotel_name = "Your Reserved Stay"

    dest = db.execute("SELECT * FROM destinations WHERE id = ?", (booking['destination_id'],)).fetchone()

    itinerary_plan = generate_smart_itinerary(
        dest=dict(dest),
        places=places,
        duration=int(booking['duration']),
        start_date=datetime.strptime(booking['start_date'], '%Y-%m-%d'),
        transport_mode=booking['transport_mode'],
        hotel_name=hotel_name
    )

    # Note: we need dest for meteor forecast, let's fetch it:
    dest_obj = db.execute("SELECT latitude, longitude FROM destinations WHERE id = ?", (booking['destination_id'],)).fetchone()
    if dest_obj:
        itinerary_plan = generate_smart_itinerary(
            dest=dest_obj,
            places=places,
            duration=int(booking['duration']),
            start_date=datetime.strptime(booking['start_date'], '%Y-%m-%d'),
            transport_mode=booking['transport_mode'],
            hotel_name=hotel_name
        )

    return render_template('itinerary.html',
                           booking=dict(booking),
                           itinerary=itinerary_plan,
                           is_preview=False)



# ─────────────────────────────────────────
#  FEEDBACK
# ─────────────────────────────────────────
@app.route('/feedback/<int:booking_id>', methods=['GET', 'POST'])
@login_required
def feedback(booking_id):
    db      = get_db()
    booking = db.execute('''
        SELECT b.*, d.name as dest_name, d.image_url,
               g.name as guide_name, g.phone as guide_phone
        FROM bookings b 
        JOIN destinations d ON b.destination_id = d.id 
        LEFT JOIN guides g ON b.guide_id = g.id
        WHERE b.id = ? AND b.user_id = ?
    ''', (booking_id, session['user_id'])).fetchone()

    if not booking:
        flash("Feedback is only for your own bookings.", "warning")
        return redirect(url_for('my_bookings'))

    # Check if trip is completed or in-progress
    today = datetime.now().strftime('%Y-%m-%d')
    if booking['status'] != 'Completed' and booking['start_date'] > today:
        flash("You can only give feedback during or after your trip.", "warning")
        return redirect(url_for('my_bookings'))

    if request.method == 'POST':
        rating  = int(request.form.get('rating', 5))
        comment = request.form.get('comment', '').strip()
        
        # Double check no fake reviews: ensure user actually had this booking
        try:
            db.execute(
                "INSERT INTO reviews (user_id, destination_id, rating, comment) VALUES (?, ?, ?, ?)",
                (session['user_id'], booking['destination_id'], rating, comment)
            )
            db.commit()
            flash("Thank you for your verified review! ⭐", "success")
            return redirect(url_for('my_bookings'))
        except Exception:
            flash("Could not submit review.", "danger")

    return render_template('feedback.html',
                           booking_id=booking_id,
                           dest_name=booking['dest_name'])


# ─────────────────────────────────────────
#  USER DASHBOARD
# ─────────────────────────────────────────
@app.route('/dashboard')
@login_required
def user_dashboard():
    if session.get('role') == 'admin':
        return redirect(url_for('admin_dashboard'))
    if session.get('role') == 'guide':
        return redirect(url_for('guide_dashboard'))

    db = get_db()
    uid = session['user_id']

    total_bookings     = db.execute("SELECT COUNT(*) FROM bookings WHERE user_id=?", (uid,)).fetchone()[0]
    confirmed_bookings = db.execute("SELECT COUNT(*) FROM bookings WHERE user_id=? AND status='Confirmed'", (uid,)).fetchone()[0]
    cancelled_bookings = db.execute("SELECT COUNT(*) FROM bookings WHERE user_id=? AND status='Cancelled'", (uid,)).fetchone()[0]
    total_spent_row    = db.execute("SELECT SUM(total_cost) FROM bookings WHERE user_id=? AND payment_status='Paid'", (uid,)).fetchone()
    total_spent        = total_spent_row[0] or 0

    recent_bookings = db.execute('''
        SELECT b.*, d.name AS dest_name
        FROM bookings b JOIN destinations d ON b.destination_id=d.id
        WHERE b.user_id=? ORDER BY b.id DESC LIMIT 5
    ''', (uid,)).fetchall()

    today = datetime.now().strftime('%Y-%m-%d')
    upcoming_trips = db.execute('''
        SELECT b.*, d.name AS dest_name, d.image_url
        FROM bookings b JOIN destinations d ON b.destination_id=d.id
        WHERE b.user_id=? AND b.status='Confirmed' AND b.start_date >= ?
        ORDER BY b.start_date ASC
    ''', (uid, today)).fetchall()

    return render_template('user_dashboard.html',
                           total_bookings=total_bookings,
                           confirmed_bookings=confirmed_bookings,
                           cancelled_bookings=cancelled_bookings,
                           total_spent=total_spent,
                           recent_bookings=recent_bookings,
                           upcoming_trips=upcoming_trips)


# ─────────────────────────────────────────
#  GUIDE DASHBOARD
# ─────────────────────────────────────────
@app.route('/guide')
@guide_required
def guide_dashboard():
    db = get_db()
    guide = db.execute("SELECT * FROM guides WHERE email=?", (session.get('email', ''),)).fetchone()

    # Fallback: match by user name
    if not guide:
        guide = db.execute("SELECT * FROM guides WHERE name=?", (session.get('name', ''),)).fetchone()

    if not guide:
        flash("Guide profile not found. Contact admin.", "warning")
        return redirect(url_for('index'))

    trips = db.execute('''
        SELECT b.*, d.name AS dest_name, u.name AS user_name, u.email AS user_email, u.phone AS user_phone
        FROM bookings b
        JOIN destinations d ON b.destination_id=d.id
        JOIN users u ON b.user_id=u.id
        WHERE b.guide_id=? AND b.payment_status='Paid'
        ORDER BY b.start_date ASC
    ''', (guide['id'],)).fetchall()

    today = datetime.now().strftime('%Y-%m-%d')
    assigned_count  = len(trips)
    completed_count = sum(1 for t in trips if t['status'] == 'Completed')
    upcoming_count  = sum(1 for t in trips if t['status'] == 'Confirmed' and t['start_date'] >= today)

    # Fetch Stays
    stays = db.execute('''
        SELECT a.*, d.name AS dest_name, b.start_date
        FROM guide_accommodations a
        JOIN bookings b ON a.booking_id = b.id
        JOIN destinations d ON b.destination_id = d.id
        WHERE a.guide_id = ?
        ORDER BY b.start_date DESC
    ''', (guide['id'],)).fetchall()

    # Fetch Commissions
    commissions = db.execute('''
        SELECT c.*, b.destination_id, d.name AS dest_name, b.start_date
        FROM guide_commissions c
        JOIN bookings b ON c.booking_id = b.id
        JOIN destinations d ON b.destination_id = d.id
        WHERE c.guide_id = ?
        ORDER BY c.id DESC
    ''', (guide['id'],)).fetchall()

    total_earned = sum(c['amount'] for c in commissions if c['status'] == 'Paid')
    pending_earned = sum(c['amount'] for c in commissions if c['status'] == 'Pending')

    return render_template('guide_dashboard.html',
                           guide=guide, trips=trips,
                           stays=stays, commissions=commissions,
                           total_earned=total_earned,
                           pending_earned=pending_earned,
                           assigned_count=assigned_count,
                           completed_count=completed_count,
                           upcoming_count=upcoming_count)


@app.route('/guide/trips')
@guide_required
def guide_trips():
    return redirect(url_for('guide_dashboard'))


@app.route('/guide/update_status', methods=['POST'])
@guide_required
def guide_update_status():
    booking_id = request.form.get('booking_id')
    new_status = request.form.get('new_status', 'Completed')
    db = get_db()
    db.execute("UPDATE bookings SET status=? WHERE id=?", (new_status, booking_id))
    db.commit()
    flash(f"Booking #{booking_id} marked as {new_status}.", "success")
    return redirect(url_for('guide_dashboard'))


@app.route('/guide/respond_trip/<int:booking_id>/<action>', methods=['POST'])
@guide_required
def guide_respond_trip(booking_id, action):
    db = get_db()
    booking = db.execute("SELECT * FROM bookings WHERE id=?", (booking_id,)).fetchone()
    
    if not booking:
        flash("Booking not found.", "danger")
        return redirect(url_for('guide_dashboard'))

    if action == 'accept':
        db.execute("UPDATE bookings SET guide_status='Accepted' WHERE id=?", (booking_id,))
        flash("You have accepted the trip!", "success")
    elif action == 'reject':
        # Re-assign logic
        next_guide = db.execute('''
            SELECT id FROM guides 
            WHERE destination_id = ? AND id != ?
            ORDER BY rating DESC LIMIT 1
        ''', (booking['destination_id'], booking['guide_id'])).fetchone()
        
        if next_guide:
            db.execute("UPDATE bookings SET guide_id=?, guide_status='Pending' WHERE id=?", (next_guide['id'], booking_id))
            flash("Trip rejected. Automatically assigned to the next best guide.", "info")
        else:
            db.execute("UPDATE bookings SET guide_id=NULL, guide_status='Unassigned' WHERE id=?", (booking_id,))
            flash("Trip rejected. No other guide available at this location.", "warning")
            
    db.commit()
    return redirect(url_for('guide_dashboard'))


# ─────────────────────────────────────────
#  ADMIN ROUTES
# ─────────────────────────────────────────
@app.route('/admin')
@admin_required
def admin_dashboard():
    db = get_db()
    user_count     = db.execute("SELECT COUNT(*) FROM users WHERE role='user'").fetchone()[0]
    dest_count     = db.execute("SELECT COUNT(*) FROM destinations").fetchone()[0]
    guide_count    = db.execute("SELECT COUNT(*) FROM guides").fetchone()[0]
    booking_count  = db.execute("SELECT COUNT(*) FROM bookings WHERE status='Confirmed'").fetchone()[0]
    completed_count= db.execute("SELECT COUNT(*) FROM bookings WHERE status='Completed'").fetchone()[0]
    pending_count  = db.execute("SELECT COUNT(*) FROM bookings WHERE status='Pending'").fetchone()[0]
    cancelled_count= db.execute("SELECT COUNT(*) FROM bookings WHERE status='Cancelled'").fetchone()[0]
    
    revenue_row    = db.execute("SELECT SUM(total_cost) FROM bookings WHERE payment_status='Paid' AND status != 'Cancelled'").fetchone()
    total_revenue  = revenue_row[0] or 0

    recent_bookings = db.execute('''
        SELECT b.*, u.name AS user_name, u.email AS user_email, d.name AS dest_name
        FROM bookings b
        JOIN users u ON b.user_id=u.id
        JOIN destinations d ON b.destination_id=d.id
        ORDER BY b.id DESC LIMIT 8
    ''').fetchall()

    return render_template('admin_dashboard.html',
                           user_count=user_count,
                           dest_count=dest_count,
                           guide_count=guide_count,
                           booking_count=booking_count,
                           completed_count=completed_count,
                           pending_count=pending_count,
                           cancelled_count=cancelled_count,
                           total_revenue=total_revenue,
                           recent_bookings=recent_bookings)


@app.route('/admin/destinations', methods=['GET', 'POST'])
@admin_required
def manage_destinations():
    db = get_db()

    if request.method == 'POST':
        if 'update_dest' in request.form:
            db.execute(
                "UPDATE destinations SET base_price=? WHERE id=?",
                (float(request.form['base_price']),
                 request.form['id'])
            )
            db.commit()
            flash("Destination updated successfully.", "success")

        elif 'add_dest' in request.form:
            name   = request.form['dest_name'].strip()
            desc   = request.form['dest_desc'].strip()
            image  = request.form.get('dest_image', '').strip()
            price  = float(request.form['base_price'])
            db.execute(
                "INSERT INTO destinations (name, description, base_price, image_url) VALUES (?,?,?,?)",
                (name, desc, price, image or None)
            )
            db.commit()
            flash(f"Destination '{name}' added.", "success")

    destinations = db.execute("SELECT * FROM destinations ORDER BY id DESC").fetchall()
    return render_template('manage_destinations.html', destinations=destinations)


@app.route('/admin/bookings', methods=['GET', 'POST'])
@admin_required
def manage_bookings():
    db = get_db()

    if request.method == 'POST' and 'assign_guide' in request.form:
        booking_id = request.form['booking_id']
        guide_id   = request.form['guide_id']
        db.execute("UPDATE bookings SET guide_id=?, guide_status='Accepted' WHERE id=?", (guide_id, booking_id))
        
        # Auto-generate Guide Stay for the booking
        booking = db.execute('''
            SELECT b.*, d.name AS dest_name 
            FROM bookings b JOIN destinations d ON b.destination_id = d.id 
            WHERE b.id = ?
        ''', (booking_id,)).fetchone()
        
        if booking:
            # Simple logic: stay at a placeholder or destination base
            hotel_name = f"Stay at {booking['dest_name']} Base"
            db.execute('''
                INSERT INTO guide_accommodations (guide_id, booking_id, hotel_name, check_in, check_out)
                VALUES (?, ?, ?, ?, ?)
            ''', (guide_id, booking_id, hotel_name, booking['start_date'], booking['end_date']))
            
            # Simple logic: 10% commission
            commission = float(booking['package_cost']) * 0.10
            db.execute('''
                INSERT INTO guide_commissions (guide_id, booking_id, amount, status)
                VALUES (?, ?, ?, 'Pending')
            ''', (guide_id, booking_id, commission))
            
        db.commit()
        flash(f"Guide assigned, stay & commission generated for Booking #{booking_id}.", "success")

    bookings = db.execute('''
        SELECT b.*, u.name AS user_name, u.email AS user_email,
               d.name AS dest_name, g.name AS guide_name
        FROM bookings b
        JOIN users u ON b.user_id=u.id
        JOIN destinations d ON b.destination_id=d.id
        LEFT JOIN guides g ON b.guide_id=g.id
        ORDER BY b.id DESC
    ''').fetchall()

    guides = db.execute("SELECT id, name FROM guides ORDER BY name").fetchall()
    return render_template('manage_bookings.html', bookings=bookings, guides=guides)


@app.route('/admin/guides', methods=['GET', 'POST'])
@admin_required
def manage_guides():
    db = get_db()

    if request.method == 'POST' and 'add_guide' in request.form:
        name      = request.form['name'].strip()
        email     = request.form['email'].strip().lower()
        phone     = request.form['phone'].strip()
        languages = request.form['languages'].strip()
        try:
            # Add to guides table
            db.execute(
                "INSERT INTO guides (name, email, phone, languages) VALUES (?,?,?,?)",
                (name, email, phone, languages)
            )
            # Also create a user account with role 'guide'
            hashed_pw = generate_password_hash('password123')
            db.execute(
                "INSERT OR IGNORE INTO users (name, email, phone, password, role) VALUES (?,?,?,?,'guide')",
                (name, email, phone, hashed_pw)
            )
            db.commit()
            flash(f"Guide '{name}' added. Login: {email} / password123", "success")
        except sqlite3.IntegrityError:
            flash("Email already exists.", "danger")

    guides = db.execute('''
        SELECT g.*, d.name AS dest_name, COUNT(b.id) AS trip_count
        FROM guides g
        LEFT JOIN destinations d ON g.destination_id = d.id
        LEFT JOIN bookings b ON g.id = b.guide_id
        GROUP BY g.id
        ORDER BY g.name
    ''').fetchall()
    return render_template('manage_guides.html', guides=guides)


@app.route('/admin/feedback')
@admin_required
def manage_feedback():
    db = get_db()
    reviews = db.execute('''
        SELECT r.*, u.name AS user_name, d.name AS dest_name
        FROM reviews r
        JOIN users u ON r.user_id=u.id
        JOIN destinations d ON r.destination_id=d.id
        ORDER BY r.id DESC
    ''').fetchall()

    avg_row    = db.execute("SELECT AVG(rating) FROM reviews").fetchone()
    avg_rating = f"{avg_row[0]:.1f}" if avg_row[0] else "N/A"

    return render_template('manage_feedback.html', reviews=reviews, avg_rating=avg_rating)


@app.route('/admin/hotels', methods=['GET', 'POST'])
@admin_required
def manage_hotels():
    db = get_db()
    if request.method == 'POST':
        if 'add_hotel' in request.form:
            dest_id = request.form['dest_id']
            name = request.form['name'].strip()
            desc = request.form['desc'].strip()
            price = float(request.form['price'])
            image = request.form.get('image', '').strip()
            db.execute(
                "INSERT INTO hotels (destination_id, name, description, price_per_night, image_url) VALUES (?,?,?,?,?)",
                (dest_id, name, desc, price, image or None)
            )
            db.commit()
            flash(f"Hotel '{name}' added successfully.", "success")
        elif 'delete_hotel' in request.form:
            hotel_id = request.form['hotel_id']
            db.execute("DELETE FROM hotels WHERE id = ?", (hotel_id,))
            db.commit()
            flash("Hotel deleted.", "info")

    hotels = db.execute('''
        SELECT h.*, d.name AS dest_name 
        FROM hotels h JOIN destinations d ON h.destination_id = d.id
        ORDER BY d.name, h.name
    ''').fetchall()
    destinations = db.execute("SELECT id, name FROM destinations ORDER BY name").fetchall()
    return render_template('manage_hotels.html', hotels=hotels, destinations=destinations)


@app.route('/admin/commissions')
@admin_required
def manage_commissions():
    db = get_db()
    commissions = db.execute('''
        SELECT c.*, g.name AS guide_name, b.destination_id, d.name AS dest_name, b.total_cost
        FROM guide_commissions c
        JOIN guides g ON c.guide_id = g.id
        JOIN bookings b ON c.booking_id = b.id
        JOIN destinations d ON b.destination_id = d.id
        ORDER BY c.id DESC
    ''').fetchall()
    return render_template('manage_commissions.html', commissions=commissions)


# ─────────────────────────────────────────
#  RUN
# ─────────────────────────────────────────
if __name__ == '__main__':
    init_db()
    print("\n" + "="*55)
    print("  TMS Journey -- Flask Application")
    print("="*55)
    print("  URL     : http://localhost:5000")
    print("  Admin   : admin@tms.com  / password123")
    print("  User    : john@example.com / password123")
    print("  Guide   : add via Admin Panel -> Guides")
    print("="*55 + "\n")
    app.run(host='0.0.0.0', port=5000, debug=True)


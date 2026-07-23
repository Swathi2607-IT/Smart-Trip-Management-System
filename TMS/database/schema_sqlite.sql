-- =====================================================
--  TMS Journey — SQLite Schema v2.0
-- =====================================================

CREATE TABLE IF NOT EXISTS users (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    name       TEXT NOT NULL,
    email      TEXT NOT NULL UNIQUE,
    phone      TEXT NOT NULL,
    password   TEXT NOT NULL,
    role       TEXT DEFAULT 'user' CHECK(role IN ('admin','user','guide')),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS destinations (
    id             INTEGER PRIMARY KEY AUTOINCREMENT,
    name           TEXT NOT NULL,
    description    TEXT NOT NULL,
    base_price     REAL NOT NULL,
    image_url      TEXT,
    category       TEXT DEFAULT 'Location',
    location       TEXT DEFAULT 'India',
    latitude       REAL,
    longitude      REAL,
    weather_temp   INTEGER DEFAULT 25,
    weather_status TEXT DEFAULT 'Sunny',
    created_at     TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS places (
    id             INTEGER PRIMARY KEY AUTOINCREMENT,
    destination_id INTEGER NOT NULL,
    name           TEXT NOT NULL,
    category       TEXT DEFAULT 'Other',
    image_url      TEXT,
    FOREIGN KEY (destination_id) REFERENCES destinations(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS hotels (
    id             INTEGER PRIMARY KEY AUTOINCREMENT,
    destination_id INTEGER NOT NULL,
    name           TEXT NOT NULL,
    description    TEXT,
    price_per_night REAL NOT NULL,
    image_url      TEXT,
    FOREIGN KEY (destination_id) REFERENCES destinations(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS guides (
    id        INTEGER PRIMARY KEY AUTOINCREMENT,
    name      TEXT NOT NULL,
    email     TEXT NOT NULL UNIQUE,
    phone     TEXT NOT NULL,
    languages TEXT DEFAULT 'English',
    rating    REAL DEFAULT 4.8,
    price     REAL DEFAULT 1000.0,
    experience INTEGER DEFAULT 2,
    destination_id INTEGER,
    FOREIGN KEY (destination_id) REFERENCES destinations(id) ON DELETE SET NULL
);

CREATE TABLE IF NOT EXISTS guide_accommodations (
    id             INTEGER PRIMARY KEY AUTOINCREMENT,
    guide_id       INTEGER NOT NULL,
    booking_id     INTEGER NOT NULL,
    hotel_name     TEXT NOT NULL,
    address        TEXT,
    check_in       DATE,
    check_out      DATE,
    FOREIGN KEY (guide_id)   REFERENCES guides(id)   ON DELETE CASCADE,
    FOREIGN KEY (booking_id) REFERENCES bookings(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS guide_commissions (
    id             INTEGER PRIMARY KEY AUTOINCREMENT,
    guide_id       INTEGER NOT NULL,
    booking_id     INTEGER NOT NULL,
    amount         REAL NOT NULL,
    status         TEXT DEFAULT 'Pending' CHECK(status IN ('Pending','Paid')),
    created_at     TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (guide_id)   REFERENCES guides(id)   ON DELETE CASCADE,
    FOREIGN KEY (booking_id) REFERENCES bookings(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS transports (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    type         TEXT NOT NULL,
    mode         TEXT NOT NULL,
    average_cost REAL NOT NULL,
    description  TEXT
);

CREATE TABLE IF NOT EXISTS bookings (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id         INTEGER NOT NULL,
    destination_id  INTEGER NOT NULL,
    guide_id        INTEGER,
    booking_date    TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    start_date      DATE NOT NULL,
    duration        INTEGER NOT NULL,
    end_date        DATE NOT NULL,
    trip_start_mode TEXT DEFAULT 'From Departure',
    transport_mode  TEXT DEFAULT 'Self-Arranged',
    transport_cost  REAL DEFAULT 0,
    package_cost    REAL NOT NULL,
    total_cost      REAL NOT NULL,
    status          TEXT DEFAULT 'Pending',
    payment_status  TEXT DEFAULT 'Unpaid',
    passengers      INTEGER DEFAULT 1,
    guide_requested BOOLEAN DEFAULT 0,
    guide_status    TEXT DEFAULT 'Unassigned',
    rejected_guides TEXT DEFAULT '',
    guide_cost      REAL DEFAULT 0,
    departure_city  TEXT,
    hotel_id        INTEGER,
    hotel_cost      REAL DEFAULT 0,
    is_hotel_booked BOOLEAN DEFAULT 0,
    local_transport_req BOOLEAN DEFAULT 0,
    local_transport_cost REAL DEFAULT 0,
    refund_amount   REAL DEFAULT 0,
    cancellation_date TIMESTAMP,
    receipt_token   TEXT UNIQUE,
    FOREIGN KEY (user_id)        REFERENCES users(id)        ON DELETE CASCADE,
    FOREIGN KEY (destination_id) REFERENCES destinations(id) ON DELETE CASCADE,
    FOREIGN KEY (guide_id)       REFERENCES guides(id)       ON DELETE SET NULL
);

CREATE TABLE IF NOT EXISTS payments (
    id             INTEGER PRIMARY KEY AUTOINCREMENT,
    booking_id     INTEGER NOT NULL,
    transaction_id TEXT NOT NULL UNIQUE,
    amount         REAL NOT NULL,
    payment_method TEXT DEFAULT 'UPI',
    payment_date   TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (booking_id) REFERENCES bookings(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS reviews (
    id             INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id        INTEGER NOT NULL,
    destination_id INTEGER NOT NULL,
    rating         INTEGER CHECK(rating BETWEEN 1 AND 5),
    comment        TEXT,
    created_at     TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id)        REFERENCES users(id)        ON DELETE CASCADE,
    FOREIGN KEY (destination_id) REFERENCES destinations(id) ON DELETE CASCADE
);

-- =====================================================
--  SEED DATA
-- =====================================================

-- Users (password = 'password123')
INSERT OR IGNORE INTO users (name, email, phone, password, role) VALUES
('System Admin',  'admin@tms.com',       '1234567890', 'scrypt:32768:8:1$wZH2NAPZUNChfHsP$c0cacb53fef87af05ad2e834dc6dc8a698999919f17f68dcc6bd0e87ac4fbd192ce2521d03a9664f4092b279550a2f8f0660f6b6aef397741412f2404b455b32', 'admin'),
('John Doe',      'john@example.com',    '9876543210', 'scrypt:32768:8:1$wZH2NAPZUNChfHsP$c0cacb53fef87af05ad2e834dc6dc8a698999919f17f68dcc6bd0e87ac4fbd192ce2521d03a9664f4092b279550a2f8f0660f6b6aef397741412f2404b455b32', 'user'),
('Priya Sharma',  'priya@example.com',   '9123456780', 'scrypt:32768:8:1$wZH2NAPZUNChfHsP$c0cacb53fef87af05ad2e834dc6dc8a698999919f17f68dcc6bd0e87ac4fbd192ce2521d03a9664f4092b279550a2f8f0660f6b6aef397741412f2404b455b32', 'user');

-- Destinations
INSERT OR IGNORE INTO destinations (name, description, base_price, image_url, weather_temp, weather_status) VALUES
('Goa',     'Famed for its pristine beaches, vibrant nightlife, and rich Portuguese heritage, Goa offers a perfect blend of relaxation and adventure.', 3500.00, 'https://images.unsplash.com/photo-1512343879784-a960bf40e7f2?w=1200&q=80', 32, 'Sunny'),
('Manali',  'A snow-carpeted paradise for mountain lovers and adventure seekers, Manali is the gateway to some of the Himalayas'' most stunning vistas.', 4200.00, 'https://images.unsplash.com/photo-1598511757337-fe2cafc31dee?w=1200&q=80', 12, 'Snowy'),
('Munnar',  'A serene hill station in Kerala''s Western Ghats, blanketed in rolling tea plantations, waterfalls, and misty mountain trails.', 4500.00, 'https://images.unsplash.com/photo-1593642632823-8f785ba67e45?w=1200&q=80', 20, 'Rainy'),
('Rajasthan', 'The Land of Kings — a kaleidoscope of majestic forts, colourful culture, camel safaris, and golden desert landscapes.', 7000.00, 'https://s7ap1.scene7.com/is/image/incredibleindia/hawa-mahal-jaipur-rajasthan-city-1-hero?qlt=82&ts=1742200253577', 38, 'Sunny'),
('Kerala Backwaters', 'Glide through tranquil palm-fringed canals on traditional houseboats while experiencing the lush green beauty of Kerala.', 5500.00, 'https://images.unsplash.com/photo-1602216056096-3b40cc0c9944?w=1200&q=80', 28, 'Cloudy'),
('Ladakh',  'A high-altitude cold desert offering jaw-dropping landscapes, ancient monasteries, and the world-famous Pangong Lake.', 8500.00, 'https://s7ap1.scene7.com/is/image/incredibleindia/2-lamayuru-or-yuru-monastery-kargil-j_k-city-hero?qlt=82&ts=1726667854003', 8, 'Sunny'),
('Shimla',  'The Queen of Hills — a historic colonial summer capital offering scenic vistas, the Mall Road, and snow-capped peaks.', 5500.00, 'https://images.unsplash.com/photo-1562534215-7ad5dad3aeeb?w=1200&q=80', 15, 'Cloudy'),
('Ooty',    'The Queen of Hill Stations in the Nilgiris, famous for its toy train, botanical gardens, and rolling tea estates.', 4800.00, 'https://images.unsplash.com/photo-1507525428034-b723cf961d3e?w=1200&q=80', 18, 'Sunny'),
('Rishikesh', 'The Yoga Capital of the World — a spiritual hub on the banks of the Ganges, offering adventure sports and serene ghats.', 4200.00, 'https://images.unsplash.com/photo-1544550285-f813152fb2fd?w=1200&q=80', 24, 'Sunny'),
('Varanasi', 'One of the oldest living cities in the world — a sacred destination known for its spiritual atmosphere and evening Ganga Aarti.', 3800.00, 'https://images.unsplash.com/photo-1561359313-0639aad49ca6?w=1200&q=80', 28, 'Sunny');



-- Places
INSERT OR IGNORE INTO places (destination_id, name, category, image_url) VALUES
-- Goa (1)
(1, 'Calangute Beach',         'Beach',    'https://images.unsplash.com/photo-1590523741831-2996a79462a2?w=800&q=80'),
(1, 'Baga Beach',              'Beach',    'https://images.unsplash.com/photo-1540202404-a2f290328295?w=800&q=80'),
(1, 'Basilica of Bom Jesus',   'Church',   'https://images.unsplash.com/photo-1605731776518-e3258a699c85?w=800&q=80'),
(1, 'Fort Aguada',             'Fort',     'https://images.unsplash.com/photo-1622312643501-c8ef634ad68b?w=800&q=80'),
(1, 'Dudhsagar Waterfalls',    'Waterfall','https://images.unsplash.com/photo-1621619856624-42f1b8a5fc0a?w=800&q=80'),
-- Manali (2)
(2, 'Rohtang Pass',            'Mountain', 'https://images.unsplash.com/photo-1598511757337-fe2cafc31dee?w=800&q=80'),
(2, 'Solang Valley',           'Valley',   'https://images.unsplash.com/photo-1571003123894-1f0594d2b5d9?w=800&q=80'),
(2, 'Hadimba Temple',          'Temple',   'https://images.unsplash.com/photo-1582510003544-4d00b7f74220?w=800&q=80'),
(2, 'Beas River',              'River',    'https://images.unsplash.com/photo-1559827291-72ee739d0d9a?w=800&q=80'),
-- Munnar (3)
(3, 'Eravikulam National Park','Wildlife', 'https://images.unsplash.com/photo-1548013146-72479768bada?w=800&q=80'),
(3, 'Tea Museum',              'Museum',   'https://images.unsplash.com/photo-1556909078-1b03c0de6d11?w=800&q=80'),
(3, 'Attukad Waterfalls',      'Waterfall','https://images.unsplash.com/photo-1433086966358-54859d0ed716?w=800&q=80'),
-- Ladakh (6)
(6, 'Pangong Tso Lake',        'Lake',     'https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=800&q=80'),
(6, 'Nubra Valley',            'Valley',   'https://images.unsplash.com/photo-1562534215-7ad5dad3aeeb?w=800&q=80'),
(6, 'Thiksey Monastery',       'Monastery','https://images.unsplash.com/photo-1589308078059-be1415eab4c3?w=800&q=80'),
-- Shimla (7)
(7, 'The Ridge',               'Landmark', 'https://images.unsplash.com/photo-1562534215-7ad5dad3aeeb?w=800&q=80'),
(7, 'Jakhu Temple',            'Temple',   'https://images.unsplash.com/photo-1582510003544-4d00b7f74220?w=800&q=80'),
(7, 'Mall Road Shimla',        'Shopping', 'https://images.unsplash.com/photo-1562534215-7ad5dad3aeeb?w=800&q=80'),
-- Ooty (8)
(8, 'Botanical Gardens',       'Garden',   'https://images.unsplash.com/photo-1593642632823-8f785ba67e45?w=800&q=80'),
(8, 'Ooty Lake',               'Lake',     'https://images.unsplash.com/photo-1507525428034-b723cf961d3e?w=800&q=80'),
(8, 'Doddabetta Peak',         'Peak',     'https://images.unsplash.com/photo-1506905925346-21bda4d32df4?w=800&q=80'),
-- Rishikesh (9)
(9, 'Laxman Jhula',            'Bridge',   'https://images.unsplash.com/photo-1544550285-f813152fb2fd?w=800&q=80'),
(9, 'Triveni Ghat',            'Spiritual','https://images.unsplash.com/photo-1589308078059-be1415eab4c3?w=800&q=80'),
(9, 'Neer Garh Waterfall',     'Waterfall','https://images.unsplash.com/photo-1433086966358-54859d0ed716?w=800&q=80'),
-- Varanasi (10)
(10, 'Dashashwamedh Ghat',      'Ghat',     'https://images.unsplash.com/photo-1561359313-0639aad49ca6?w=800&q=80'),
(10, 'Kashi Vishwanath Temple', 'Temple',   'https://images.unsplash.com/photo-1582510003544-4d00b7f74220?w=800&q=80'),
(10, 'Assi Ghat',               'Ghat',     'https://images.unsplash.com/photo-1594142404563-64cccaf5a10f?w=800&q=80');



-- Transport
INSERT OR IGNORE INTO transports (type, mode, average_cost, description) VALUES
('Luxury AC Sleeper Bus', 'Bus',    1500.00, 'Comfortable sleeper seats. Best for overnight journeys up to 600 km.'),
('Express Train (3A AC)',  'Train',  2500.00, 'Cost-effective train travel with air-conditioned 3-tier coaches.'),
('Domestic Flight',        'Flight', 6000.00, 'Fastest mode. Ideal for distances over 800 km. Saves travel time.');

-- Guides
INSERT OR IGNORE INTO guides (name, email, phone, languages, rating, price, destination_id) VALUES
('Ramesh Kumar', 'ramesh.guide@tms.com', '9988776655', 'English, Hindi, Marathi', 4.9, 1200.0, 1),
('Anita Sharma', 'anita.guide@tms.com',  '8877665544', 'English, Hindi, Tamil', 4.8, 1000.0, 1),
('Sandeep Singh', 'sandeep.guide@tms.com', '7766554433', 'English, Hindi, Punjabi', 4.6, 1100.0, 2),
('Vikram Joshi', 'vikram.guide@tms.com', '6655443322', 'English, Hindi', 4.7, 950.0, 1);

-- Guide user accounts (password: password123)
INSERT OR IGNORE INTO users (name, email, phone, password, role) VALUES
('Ramesh Kumar', 'ramesh.guide@tms.com', '9988776655', 'scrypt:32768:8:1$wZH2NAPZUNChfHsP$c0cacb53fef87af05ad2e834dc6dc8a698999919f17f68dcc6bd0e87ac4fbd192ce2521d03a9664f4092b279550a2f8f0660f6b6aef397741412f2404b455b32', 'guide'),
('Anita Sharma', 'anita.guide@tms.com',  '8877665544', 'scrypt:32768:8:1$wZH2NAPZUNChfHsP$c0cacb53fef87af05ad2e834dc6dc8a698999919f17f68dcc6bd0e87ac4fbd192ce2521d03a9664f4092b279550a2f8f0660f6b6aef397741412f2404b455b32', 'guide'),
('Sandeep Singh', 'sandeep.guide@tms.com', '7766554433', 'scrypt:32768:8:1$wZH2NAPZUNChfHsP$c0cacb53fef87af05ad2e834dc6dc8a698999919f17f68dcc6bd0e87ac4fbd192ce2521d03a9664f4092b279550a2f8f0660f6b6aef397741412f2404b455b32', 'guide'),
('Vikram Joshi', 'vikram.guide@tms.com', '6655443322', 'scrypt:32768:8:1$wZH2NAPZUNChfHsP$c0cacb53fef87af05ad2e834dc6dc8a698999919f17f68dcc6bd0e87ac4fbd192ce2521d03a9664f4092b279550a2f8f0660f6b6aef397741412f2404b455b32', 'guide');


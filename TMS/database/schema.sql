-- Trip Management System Schema
-- Create Database
CREATE DATABASE IF NOT EXISTS trip_management;
USE trip_management;

-- 1. Users Table (Admin & Travelers)
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(100) NOT NULL UNIQUE,
    phone VARCHAR(20) NOT NULL,
    password VARCHAR(255) NOT NULL,
    role ENUM('admin', 'user') DEFAULT 'user',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 2. Destinations Table
CREATE TABLE IF NOT EXISTS destinations (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    description TEXT NOT NULL,
    base_price DECIMAL(10,2) NOT NULL,
    image_url TEXT,
    weather_temp INT DEFAULT 25,
    weather_status ENUM('Sunny', 'Cloudy', 'Rainy', 'Stormy', 'Snowy') DEFAULT 'Sunny',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 3. Places Table (For Itineraries)
CREATE TABLE IF NOT EXISTS places (
    id INT AUTO_INCREMENT PRIMARY KEY,
    destination_id INT NOT NULL,
    name VARCHAR(100) NOT NULL,
    category ENUM('Beach', 'Temple', 'Museum', 'Park', 'Monument', 'Market', 'Fort', 'Waterfall', 'Other') DEFAULT 'Other',
    image_url TEXT,
    FOREIGN KEY (destination_id) REFERENCES destinations(id) ON DELETE CASCADE
);

-- 4. Guides Table
CREATE TABLE IF NOT EXISTS guides (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(100) NOT NULL UNIQUE,
    phone VARCHAR(20) NOT NULL,
    languages VARCHAR(255) DEFAULT 'English'
);

-- 5. Transports Table
CREATE TABLE IF NOT EXISTS transports (
    id INT AUTO_INCREMENT PRIMARY KEY,
    type VARCHAR(50) NOT NULL,
    mode ENUM('Bus', 'Train', 'Flight') NOT NULL,
    average_cost DECIMAL(10,2) NOT NULL,
    description TEXT
);

-- 6. Bookings Table (Core Engine)
CREATE TABLE IF NOT EXISTS bookings (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    destination_id INT NOT NULL,
    guide_id INT NULL,
    booking_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    start_date DATE NOT NULL,
    duration INT NOT NULL,
    end_date DATE NOT NULL,
    trip_start_mode ENUM('After Arrival', 'Includes Travel') NOT NULL,
    transport_mode ENUM('None', 'Bus', 'Train', 'Flight') DEFAULT 'None',
    transport_cost DECIMAL(10,2) DEFAULT 0,
    package_cost DECIMAL(10,2) NOT NULL,
    total_cost DECIMAL(10,2) NOT NULL,
    status ENUM('Pending', 'Confirmed', 'Cancelled', 'Completed') DEFAULT 'Pending',
    payment_status ENUM('Unpaid', 'Paid', 'Refunded') DEFAULT 'Unpaid',
    refund_amount DECIMAL(10,2) DEFAULT 0,
    cancellation_date TIMESTAMP NULL,
    receipt_token VARCHAR(100) UNIQUE NULL,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (destination_id) REFERENCES destinations(id) ON DELETE CASCADE,
    FOREIGN KEY (guide_id) REFERENCES guides(id) ON DELETE SET NULL
);

-- 7. Reviews (Feedback) Table
CREATE TABLE IF NOT EXISTS reviews (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    destination_id INT NOT NULL,
    rating INT CHECK (rating >= 1 AND rating <= 5),
    comment TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (destination_id) REFERENCES destinations(id) ON DELETE CASCADE
);

-- 8. Payments Table
CREATE TABLE IF NOT EXISTS payments (
    id INT AUTO_INCREMENT PRIMARY KEY,
    booking_id INT NOT NULL,
    transaction_id VARCHAR(100) NOT NULL UNIQUE,
    amount DECIMAL(10,2) NOT NULL,
    payment_method VARCHAR(50) DEFAULT 'UPI',
    payment_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (booking_id) REFERENCES bookings(id) ON DELETE CASCADE
);

-- --------------------------------------------------------
-- SEED DATA (For Testing Purposes)
-- --------------------------------------------------------

-- Insert Default Admin & User (Password is 'password123' hashed using PHP password_hash)
INSERT INTO users (name, email, phone, password, role) VALUES 
('System Admin', 'admin@tms.com', '1234567890', '$2y$10$92IXUNpkjO0rOQ5byMi.Ye4oKoEa3Ro9llC/.og/at2.uheWG/igi', 'admin'),
('John Doe', 'john@example.com', '9876543210', '$2y$10$92IXUNpkjO0rOQ5byMi.Ye4oKoEa3Ro9llC/.og/at2.uheWG/igi', 'user');

-- Insert Destinations
INSERT INTO destinations (name, description, base_price, image_url, weather_temp, weather_status) VALUES
('Goa', 'A coastal state in western India, known for its beautiful beaches, vibrant nightlife, and Portuguese culture.', 5000.00, 'https://images.unsplash.com/photo-1512343879784-a960bf40e7f2?w=800&q=80', 32, 'Sunny'),
('Manali', 'A high-altitude Himalayan resort town in India\'s northern Himachal Pradesh state. Known for skiing and trekking.', 6500.00, 'https://images.unsplash.com/photo-1626621341517-bbf3d9990a23?w=800&q=80', 12, 'Cloudy'),
('Munnar', 'A town in the Western Ghats mountain range in India’s Kerala state. Surrounded by rolling hills dotted with tea plantations.', 4500.00, 'https://images.unsplash.com/photo-1593642632823-8f785ba67e45?w=800&q=80', 20, 'Rainy');

-- Insert Places for Goa
INSERT INTO places (destination_id, name, category, image_url) VALUES
(1, 'Calangute Beach', 'Beach', 'https://images.unsplash.com/photo-1614082242765-7c98ca0f3df3?w=800&q=80'),
(1, 'Baga Beach', 'Beach', 'https://images.unsplash.com/photo-1594950346002-861f1bfebbd6?w=800&q=80'),
(1, 'Basilica of Bom Jesus', 'Church', 'https://images.unsplash.com/photo-1621808620242-20516dd2bb4e?w=800&q=80'),
(1, 'Fort Aguada', 'Fort', 'https://images.unsplash.com/photo-1622312643501-c8ef634ad68b?w=800&q=80'),
(1, 'Dudhsagar Waterfalls', 'Waterfall', 'https://images.unsplash.com/photo-1611082691512-ab7dbb6957c5?w=800&q=80');

-- Insert Transports
INSERT INTO transports (type, mode, average_cost, description) VALUES
('Luxury AC Bus', 'Bus', 1500.00, 'Comfortable sleeper seats, recommended for overnight journeys.'),
('Express Train (3A)', 'Train', 2500.00, 'Air-conditioned train travel, medium distance, cost-effective.'),
('Domestic Flight', 'Flight', 6000.00, 'Fastest mode of transport for long distances.');

-- Insert Guides
INSERT INTO guides (name, email, phone, languages) VALUES
('Ramesh Kumar', 'ramesh.guide@tms.com', '9988776655', 'English, Hindi, Marathi'),
('Anita Sharma', 'anita.guide@tms.com', '8877665544', 'English, Hindi');

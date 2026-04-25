-- Hotel Management System Database Setup

USE flaskdb;

-- Create rooms table
CREATE TABLE IF NOT EXISTS rooms (
    id INT AUTO_INCREMENT PRIMARY KEY,
    room_number VARCHAR(10) UNIQUE NOT NULL,
    type ENUM('single', 'double', 'suite') DEFAULT 'single',
    price DECIMAL(10, 2) NOT NULL,
    status ENUM('available', 'occupied', 'maintenance') DEFAULT 'available',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create reservations table
CREATE TABLE IF NOT EXISTS reservations (
    id INT AUTO_INCREMENT PRIMARY KEY,
    guest_name VARCHAR(100) NOT NULL,
    email VARCHAR(100) NOT NULL,
    phone VARCHAR(20),
    room_id INT NOT NULL,
    check_in DATE NOT NULL,
    check_out DATE NOT NULL,
    status ENUM('pending', 'confirmed', 'cancelled') DEFAULT 'pending',
    downpayment_amount DECIMAL(10, 2) DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (room_id) REFERENCES rooms(id)
);

-- Create checkins table
CREATE TABLE IF NOT EXISTS checkins (
    id INT AUTO_INCREMENT PRIMARY KEY,
    reservation_id INT,
    room_id INT NOT NULL,
    guest_name VARCHAR(100) NOT NULL,
    check_in_time DATETIME NOT NULL,
    check_out_time DATETIME,
    status ENUM('checked-in', 'checked-out') DEFAULT 'checked-in',
    total_price DECIMAL(10, 2) DEFAULT 0,
    downpayment_amount DECIMAL(10, 2) DEFAULT 0,
    remaining_balance DECIMAL(10, 2) DEFAULT 0,
    payment_status ENUM('unpaid', 'partial', 'fully_paid') DEFAULT 'unpaid',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (room_id) REFERENCES rooms(id),
    FOREIGN KEY (reservation_id) REFERENCES reservations(id)
);

-- Create foods menu table
CREATE TABLE IF NOT EXISTS foods (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    price DECIMAL(10, 2) NOT NULL,
    category ENUM('drinks', 'appetizers', 'mains', 'desserts') DEFAULT 'mains',
    available BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create food_orders table
CREATE TABLE IF NOT EXISTS food_orders (
    id INT AUTO_INCREMENT PRIMARY KEY,
    checkin_id INT NOT NULL,
    item_name VARCHAR(100) NOT NULL,
    quantity INT DEFAULT 1,
    price DECIMAL(10, 2) NOT NULL,
    order_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status ENUM('pending', 'prepared', 'delivered') DEFAULT 'pending',
    FOREIGN KEY (checkin_id) REFERENCES checkins(id)
);

-- Insert sample food items
INSERT INTO foods (name, price, category) VALUES
('Coffee', 50.00, 'drinks'),
('Tea', 40.00, 'drinks'),
('Orange Juice', 60.00, 'drinks'),
('Soft Drinks', 45.00, 'drinks'),
('Chips', 80.00, 'appetizers'),
('Sandwich', 120.00, 'appetizers'),
('Fried Rice', 180.00, 'mains'),
('Pasta', 200.00, 'mains'),
('Grilled Chicken', 350.00, 'mains'),
('Beef Steak', 450.00, 'mains'),
('Cake', 150.00, 'desserts'),
('Ice Cream', 100.00, 'desserts');

-- Create addons table
CREATE TABLE IF NOT EXISTS addons (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    price DECIMAL(10, 2) NOT NULL,
    available BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Insert sample addons
INSERT INTO addons (name, price) VALUES
('Spa Treatment', 500.00),
('Airport Transfer', 300.00),
('Breakfast Buffet', 250.00),
('Late Checkout', 200.00),
('Extra Bed', 150.00),
('Gym Access', 100.00),
('Pool Access', 80.00),
('WiFi Premium', 50.00);

-- Create settings table
CREATE TABLE IF NOT EXISTS settings (
    id INT AUTO_INCREMENT PRIMARY KEY,
    setting_key VARCHAR(50) UNIQUE NOT NULL,
    setting_value TEXT
);

-- Insert default settings
INSERT INTO settings (setting_key, setting_value) VALUES
('currency', 'USD'),
('currency_symbol', '$'),
('language', 'en'),
('theme', 'light'),
('logo', '');

-- Create users table
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    email VARCHAR(100) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    name VARCHAR(100),
    role ENUM('admin', 'staff') DEFAULT 'staff',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Insert default admin user
INSERT INTO users (email, password, name, role) VALUES
('admin@hotel.com', 'admin123', 'Administrator', 'admin');

-- Create payments table
CREATE TABLE IF NOT EXISTS payments (
    id INT AUTO_INCREMENT PRIMARY KEY,
    checkin_id INT NOT NULL,
    amount DECIMAL(10, 2) NOT NULL,
    payment_type ENUM('cash', 'card', 'transfer') DEFAULT 'cash',
    status ENUM('pending', 'completed') DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (checkin_id) REFERENCES checkins(id)
);

-- Insert sample rooms
INSERT INTO rooms (room_number, type, price, status) VALUES
('101', 'single', 100.00, 'available'),
('102', 'single', 100.00, 'available'),
('201', 'double', 150.00, 'available'),
('202', 'double', 150.00, 'available'),
('301', 'suite', 300.00, 'available');

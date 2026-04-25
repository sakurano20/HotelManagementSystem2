-- phpMyAdmin SQL Dump
-- version 5.2.3
-- https://www.phpmyadmin.net/
--
-- Host: 127.0.0.1:3306
-- Generation Time: Apr 18, 2026 at 02:44 AM
-- Server version: 8.4.7
-- PHP Version: 8.3.28

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `flaskdb`
--

-- --------------------------------------------------------

--
-- Table structure for table `addons`
--

DROP TABLE IF EXISTS `addons`;
CREATE TABLE IF NOT EXISTS `addons` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL,
  `price` decimal(10,2) NOT NULL,
  `available` tinyint(1) DEFAULT '1',
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`)
) ENGINE=MyISAM AUTO_INCREMENT=25 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Dumping data for table `addons`
--

INSERT INTO `addons` (`id`, `name`, `price`, `available`, `created_at`) VALUES
(1, 'Spa Treatment', 500.00, 1, '2026-04-17 23:53:28'),
(2, 'Airport Transfer', 300.00, 1, '2026-04-17 23:53:28'),
(3, 'Breakfast Buffet', 250.00, 1, '2026-04-17 23:53:28'),
(4, 'Late Checkout', 200.00, 1, '2026-04-17 23:53:28'),
(5, 'Extra Bed', 150.00, 1, '2026-04-17 23:53:28'),
(6, 'Gym Access', 100.00, 1, '2026-04-17 23:53:28'),
(7, 'Pool Access', 80.00, 1, '2026-04-17 23:53:28'),
(9, 'Spa Treatment', 500.00, 1, '2026-04-17 23:53:45'),
(10, 'Airport Transfer', 300.00, 1, '2026-04-17 23:53:45'),
(11, 'Breakfast Buffet', 250.00, 1, '2026-04-17 23:53:45'),
(12, 'Late Checkout', 200.00, 1, '2026-04-17 23:53:45'),
(13, 'Extra Bed', 150.00, 1, '2026-04-17 23:53:45'),
(14, 'Gym Access', 100.00, 1, '2026-04-17 23:53:45'),
(15, 'Pool Access', 80.00, 1, '2026-04-17 23:53:45'),
(16, 'WiFi Premium', 50.00, 1, '2026-04-17 23:53:45'),
(17, 'Spa Treatment', 500.00, 1, '2026-04-17 23:55:25'),
(18, 'Airport Transfer', 300.00, 1, '2026-04-17 23:55:25'),
(19, 'Breakfast Buffet', 250.00, 1, '2026-04-17 23:55:25'),
(20, 'Late Checkout', 200.00, 1, '2026-04-17 23:55:25'),
(21, 'Extra Bed', 150.00, 1, '2026-04-17 23:55:25'),
(22, 'Gym Access', 100.00, 1, '2026-04-17 23:55:25'),
(23, 'Pool Access', 80.00, 1, '2026-04-17 23:55:25'),
(24, 'WiFi Premium', 50.00, 1, '2026-04-17 23:55:25');

-- --------------------------------------------------------

--
-- Table structure for table `checkins`
--

DROP TABLE IF EXISTS `checkins`;
CREATE TABLE IF NOT EXISTS `checkins` (
  `id` int NOT NULL AUTO_INCREMENT,
  `reservation_id` int DEFAULT NULL,
  `room_id` int NOT NULL,
  `guest_name` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL,
  `check_in_time` datetime NOT NULL,
  `check_out_time` datetime DEFAULT NULL,
  `status` enum('checked-in','checked-out') COLLATE utf8mb4_unicode_ci DEFAULT 'checked-in',
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `room_id` (`room_id`),
  KEY `reservation_id` (`reservation_id`)
) ENGINE=MyISAM AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Dumping data for table `checkins`
--

INSERT INTO `checkins` (`id`, `reservation_id`, `room_id`, `guest_name`, `check_in_time`, `check_out_time`, `status`, `created_at`) VALUES
(1, 1, 1, 'DENZ BALILI', '2026-04-18 01:35:32', '2026-04-18 01:43:40', 'checked-out', '2026-04-17 16:35:31'),
(2, 2, 2, 'MADEL', '2026-04-18 01:53:55', NULL, 'checked-in', '2026-04-17 16:53:54'),
(3, 3, 3, 'Kyle Vince', '2026-04-18 02:08:42', NULL, 'checked-in', '2026-04-17 17:08:41');

-- --------------------------------------------------------

--
-- Table structure for table `foods`
--

DROP TABLE IF EXISTS `foods`;
CREATE TABLE IF NOT EXISTS `foods` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL,
  `price` decimal(10,2) NOT NULL,
  `category` enum('drinks','appetizers','mains','desserts') COLLATE utf8mb4_unicode_ci DEFAULT 'mains',
  `available` tinyint(1) DEFAULT '1',
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`)
) ENGINE=MyISAM AUTO_INCREMENT=13 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Dumping data for table `foods`
--

INSERT INTO `foods` (`id`, `name`, `price`, `category`, `available`, `created_at`) VALUES
(1, 'Coffee', 50.00, 'drinks', 1, '2026-04-17 23:41:16'),
(2, 'Tea', 40.00, 'drinks', 1, '2026-04-17 23:41:16'),
(3, 'Orange Juice', 60.00, 'drinks', 1, '2026-04-17 23:41:16'),
(4, 'Soft Drinks', 45.00, 'drinks', 1, '2026-04-17 23:41:16'),
(5, 'Chips', 80.00, 'appetizers', 1, '2026-04-17 23:41:16'),
(6, 'Sandwich', 120.00, 'appetizers', 1, '2026-04-17 23:41:16'),
(7, 'Fried Rice', 180.00, 'mains', 1, '2026-04-17 23:41:16'),
(8, 'Pasta', 200.00, 'mains', 1, '2026-04-17 23:41:16'),
(9, 'Grilled Chicken', 350.00, 'mains', 1, '2026-04-17 23:41:16'),
(10, 'Beef Steak', 450.00, 'mains', 1, '2026-04-17 23:41:16'),
(11, 'Cake', 150.00, 'desserts', 1, '2026-04-17 23:41:16'),
(12, 'Ice Cream', 100.00, 'desserts', 1, '2026-04-17 23:41:16');

-- --------------------------------------------------------

--
-- Table structure for table `food_orders`
--

DROP TABLE IF EXISTS `food_orders`;
CREATE TABLE IF NOT EXISTS `food_orders` (
  `id` int NOT NULL AUTO_INCREMENT,
  `checkin_id` int NOT NULL,
  `item_name` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL,
  `quantity` int DEFAULT '1',
  `price` decimal(10,2) NOT NULL,
  `order_time` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `status` enum('pending','prepared','delivered') COLLATE utf8mb4_unicode_ci DEFAULT 'pending',
  PRIMARY KEY (`id`),
  KEY `checkin_id` (`checkin_id`)
) ENGINE=MyISAM AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Dumping data for table `food_orders`
--

INSERT INTO `food_orders` (`id`, `checkin_id`, `item_name`, `quantity`, `price`, `order_time`, `status`) VALUES
(1, 1, 'jolibeset', 1, 2500.00, '2026-04-17 16:36:08', 'delivered'),
(2, 2, 'adobo', 1, 3500.00, '2026-04-17 16:54:15', 'delivered'),
(3, 3, 'Buko Salad', 1, 10.00, '2026-04-17 17:09:38', 'delivered');

-- --------------------------------------------------------

--
-- Table structure for table `loan_db`
--

DROP TABLE IF EXISTS `loan_db`;
CREATE TABLE IF NOT EXISTS `loan_db` (
  `ID` int NOT NULL,
  `name` text COLLATE utf8mb4_unicode_ci NOT NULL,
  `email` text COLLATE utf8mb4_unicode_ci NOT NULL,
  `phoneNum` int NOT NULL,
  `loanAmount` int NOT NULL,
  `loanDuration` text COLLATE utf8mb4_unicode_ci NOT NULL,
  `loanType` text COLLATE utf8mb4_unicode_ci NOT NULL
) ENGINE=MyISAM DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Dumping data for table `loan_db`
--

INSERT INTO `loan_db` (`ID`, `name`, `email`, `phoneNum`, `loanAmount`, `loanDuration`, `loanType`) VALUES
(0, 'Balili denzcio', 'balilidenz@yahoo.com', 1083196772, 2000, '36', 'Personal Loan'),
(0, 'Madel Aguilar', 'madel@gmail.com', 1024567894, 4560, '36', 'Personal Loan');

-- --------------------------------------------------------

--
-- Table structure for table `payments`
--

DROP TABLE IF EXISTS `payments`;
CREATE TABLE IF NOT EXISTS `payments` (
  `id` int NOT NULL AUTO_INCREMENT,
  `checkin_id` int NOT NULL,
  `amount` decimal(10,2) NOT NULL,
  `payment_type` enum('cash','card','transfer') COLLATE utf8mb4_unicode_ci DEFAULT 'cash',
  `status` enum('pending','completed') COLLATE utf8mb4_unicode_ci DEFAULT 'pending',
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `checkin_id` (`checkin_id`)
) ENGINE=MyISAM AUTO_INCREMENT=6 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Dumping data for table `payments`
--

INSERT INTO `payments` (`id`, `checkin_id`, `amount`, `payment_type`, `status`, `created_at`) VALUES
(1, 1, 3000.00, 'cash', 'completed', '2026-04-17 16:36:39'),
(2, 2, 3500.00, 'cash', 'completed', '2026-04-17 16:58:56'),
(3, 2, 3960.00, 'card', 'completed', '2026-04-17 17:04:26'),
(4, 3, 168.00, 'cash', 'pending', '2026-04-17 18:29:49'),
(5, 2, 3780.00, 'card', 'pending', '2026-04-18 00:38:52');

-- --------------------------------------------------------

--
-- Table structure for table `registrations`
--

DROP TABLE IF EXISTS `registrations`;
CREATE TABLE IF NOT EXISTS `registrations` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `email` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `password` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `contact` varchar(20) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=MyISAM AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Dumping data for table `registrations`
--

INSERT INTO `registrations` (`id`, `name`, `email`, `password`, `contact`) VALUES
(1, 'denzbalili', 'dfasd@gmail.com', 'scrypt:32768:8:1$Vl1ieXmRfQZwfuhi$fcb1731cf8810c326ef8abbe1e52f2b20448763da21a49d662b2155a0034b74803901c129802f1a0dde78bf319a5cd385f86db9f719ad1c249b2807a5093614c', 'asdfads'),
(2, 'madel', 'madel@aguilar', 'scrypt:32768:8:1$UdBGjkqMlwkJwHfW$a1e935b6769e64632c208015780325fb1201e95226dd4bb52cc0f2b86c7b1326cdbecd76e50bb966a892977129d6365088a94685bc9fb18ec4adadf8133d25be', '101456878');

-- --------------------------------------------------------

--
-- Table structure for table `reservations`
--

DROP TABLE IF EXISTS `reservations`;
CREATE TABLE IF NOT EXISTS `reservations` (
  `id` int NOT NULL AUTO_INCREMENT,
  `guest_name` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL,
  `email` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL,
  `phone` varchar(20) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `room_id` int NOT NULL,
  `check_in` date NOT NULL,
  `check_out` date NOT NULL,
  `status` enum('pending','confirmed','cancelled') COLLATE utf8mb4_unicode_ci DEFAULT 'pending',
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `room_id` (`room_id`)
) ENGINE=MyISAM AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Dumping data for table `reservations`
--

INSERT INTO `reservations` (`id`, `guest_name`, `email`, `phone`, `room_id`, `check_in`, `check_out`, `status`, `created_at`) VALUES
(1, 'DENZ BALILI', 'balilidenz@yahoo.com', '01083196772', 1, '2026-04-18', '2026-04-19', 'confirmed', '2026-04-17 16:34:48'),
(2, 'MADEL', 'sakurano20@gmail.com', '01083196772', 2, '2026-04-18', '2026-04-19', 'confirmed', '2026-04-17 16:53:33'),
(3, 'Kyle Vince', 'kyle@gmail.com', '01083196772', 3, '2026-04-18', '2026-04-21', 'confirmed', '2026-04-17 17:08:04');

-- --------------------------------------------------------

--
-- Table structure for table `rooms`
--

DROP TABLE IF EXISTS `rooms`;
CREATE TABLE IF NOT EXISTS `rooms` (
  `id` int NOT NULL AUTO_INCREMENT,
  `room_number` varchar(10) COLLATE utf8mb4_unicode_ci NOT NULL,
  `type` enum('single','double','suite') COLLATE utf8mb4_unicode_ci DEFAULT 'single',
  `price` decimal(10,2) NOT NULL,
  `status` enum('available','occupied','maintenance') COLLATE utf8mb4_unicode_ci DEFAULT 'available',
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `room_number` (`room_number`)
) ENGINE=MyISAM AUTO_INCREMENT=7 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Dumping data for table `rooms`
--

INSERT INTO `rooms` (`id`, `room_number`, `type`, `price`, `status`, `created_at`) VALUES
(1, '101', 'single', 100.00, 'available', '2026-04-17 16:49:48'),
(2, '102', 'single', 100.00, 'occupied', '2026-04-17 16:49:48'),
(3, '201', 'double', 150.00, 'occupied', '2026-04-17 16:49:48'),
(4, '202', 'double', 150.00, 'available', '2026-04-17 16:49:48'),
(5, '301', 'suite', 300.00, 'available', '2026-04-17 16:49:48'),
(6, '108', 'double', 2500.00, 'available', '2026-04-17 18:33:45');

-- --------------------------------------------------------

--
-- Table structure for table `settings`
--

DROP TABLE IF EXISTS `settings`;
CREATE TABLE IF NOT EXISTS `settings` (
  `id` int NOT NULL AUTO_INCREMENT,
  `setting_key` varchar(50) COLLATE utf8mb4_unicode_ci NOT NULL,
  `setting_value` text COLLATE utf8mb4_unicode_ci,
  PRIMARY KEY (`id`),
  UNIQUE KEY `setting_key` (`setting_key`)
) ENGINE=MyISAM AUTO_INCREMENT=6 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Dumping data for table `settings`
--

INSERT INTO `settings` (`id`, `setting_key`, `setting_value`) VALUES
(1, 'currency', 'PHP'),
(2, 'currency_symbol', 'Php'),
(3, 'language', 'en'),
(4, 'theme', 'blue'),
(5, 'logo', 'logo.png');

-- --------------------------------------------------------

--
-- Table structure for table `users`
--

DROP TABLE IF EXISTS `users`;
CREATE TABLE IF NOT EXISTS `users` (
  `id` int NOT NULL AUTO_INCREMENT,
  `email` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL,
  `password` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `name` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `role` enum('admin','staff') COLLATE utf8mb4_unicode_ci DEFAULT 'staff',
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `email` (`email`)
) ENGINE=MyISAM AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Dumping data for table `users`
--

INSERT INTO `users` (`id`, `email`, `password`, `name`, `role`, `created_at`) VALUES
(1, 'admin@hotel.com', 'admin123', 'Administrator', 'admin', '2026-04-17 23:57:22');
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;

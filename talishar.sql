-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Host: 127.0.0.1
-- Generation Time: Oct 15, 2024 at 02:10 AM
-- Server version: 10.4.32-MariaDB
-- PHP Version: 8.2.12

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `talishar`
--

-- --------------------------------------------------------

--
-- Table structure for table `cards`
--

CREATE TABLE `cards` (
  `card_id` varchar(6) NOT NULL,
  `hand_1` int(11) NOT NULL,
  `hand_2` int(11) NOT NULL,
  `deck_1` int(11) NOT NULL,
  `deck_2` int(11) NOT NULL,
  `gy_1` int(11) NOT NULL,
  `gy_2` int(11) NOT NULL,
  `banish_1` int(11) NOT NULL,
  `banish_2` int(11) NOT NULL,
  `arena_1` int(11) NOT NULL,
  `arena_2` int(11) NOT NULL,
  `arsenal_1` int(11) NOT NULL,
  `arsenal_2` int(11) NOT NULL,
  `state` int(11) NOT NULL,
  `pitch_1` int(11) NOT NULL,
  `pitch_2` int(11) NOT NULL,
  `played_p1` int(11) NOT NULL,
  `played_p2` int(11) NOT NULL,
  `blocked_p1` int(11) NOT NULL,
  `blocked_p2` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for table `game`
--

CREATE TABLE `game` (
  `game_id` int(11) NOT NULL,
  `date` date NOT NULL,
  `hero_1` varchar(50) NOT NULL,
  `hero_2` varchar(50) NOT NULL,
  `first` enum('p1','p2') NOT NULL,
  `winner` enum('p1','p2','draw') NOT NULL,
  `concede` enum('p1','p2','None') NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for table `state`
--

CREATE TABLE `state` (
  `game_id` int(11) NOT NULL,
  `health_1` int(11) NOT NULL,
  `health_2` int(11) NOT NULL,
  `cards_played_p1` int(11) NOT NULL,
  `cards_played_p2` int(11) NOT NULL,
  `cards_blocked_p1` int(11) NOT NULL,
  `cards_blocked_p2` int(11) NOT NULL,
  `cards_pitched_p1` int(11) NOT NULL,
  `cards_pitched_p2` int(11) NOT NULL,
  `cards_left_p1` int(11) NOT NULL,
  `cards_left_p2` int(11) NOT NULL,
  `res_left_p1` int(11) NOT NULL,
  `res_left_p2` int(11) NOT NULL,
  `res_used_p1` int(11) NOT NULL,
  `res_used_p2` int(11) NOT NULL,
  `dam_threat_p1` int(11) NOT NULL,
  `dam_threat_p2` int(11) NOT NULL,
  `dam_dealt_p1` int(11) NOT NULL,
  `dam_dealt_p2` int(11) NOT NULL,
  `dam_block_p1` int(11) NOT NULL,
  `dam_block_p2` int(11) NOT NULL,
  `dam_prevent_p1` int(11) NOT NULL,
  `dam_prevent_p2` int(11) NOT NULL,
  `dam_taken_p1` int(11) NOT NULL,
  `dam_taken_p2` int(11) NOT NULL,
  `life_gain_p1` int(11) NOT NULL,
  `life_gain_p2` int(11) NOT NULL,
  `value_p1` int(11) NOT NULL,
  `value_p2` int(11) NOT NULL,
  `state` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Indexes for dumped tables
--

--
-- Indexes for table `cards`
--
ALTER TABLE `cards`
  ADD KEY `state` (`state`);

--
-- Indexes for table `game`
--
ALTER TABLE `game`
  ADD KEY `game_id` (`game_id`);

--
-- Indexes for table `state`
--
ALTER TABLE `state`
  ADD KEY `game_id` (`game_id`),
  ADD KEY `state` (`state`);

--
-- Constraints for dumped tables
--

--
-- Constraints for table `state`
--
ALTER TABLE `state`
  ADD CONSTRAINT `state_ibfk_1` FOREIGN KEY (`game_id`) REFERENCES `game` (`game_id`),
  ADD CONSTRAINT `state_ibfk_2` FOREIGN KEY (`state`) REFERENCES `cards` (`state`);
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;

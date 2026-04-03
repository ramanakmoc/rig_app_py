-- MySQL dump 10.13  Distrib 8.0.45, for Linux (x86_64)
--
-- Host: localhost    Database: rig_operations
-- ------------------------------------------------------
-- Server version	8.0.45-0ubuntu0.24.04.1

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8mb4 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `diesel_equipment_log`
--

DROP TABLE IF EXISTS `diesel_equipment_log`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `diesel_equipment_log` (
  `id` int NOT NULL AUTO_INCREMENT,
  `date` date DEFAULT NULL,
  `rig` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `equipment_id` int DEFAULT NULL,
  `consumption` float DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `diesel_equipment_log`
--

LOCK TABLES `diesel_equipment_log` WRITE;
/*!40000 ALTER TABLE `diesel_equipment_log` DISABLE KEYS */;
/*!40000 ALTER TABLE `diesel_equipment_log` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `equipment`
--

DROP TABLE IF EXISTS `equipment`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `equipment` (
  `id` int NOT NULL AUTO_INCREMENT,
  `equipment_no` varchar(30) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `registration_no` varchar(50) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `equipment_type` enum('Crane','Trailer','Forklift','Hydra','Generator','Pump','Other') CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `make_model` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `capacity` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `year_of_mfg` year DEFAULT NULL,
  `vendor_id` int DEFAULT NULL,
  `assigned_rig` varchar(30) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `status` enum('Available','In Use','Under Maintenance','Retired') CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT 'Available',
  `last_service_date` date DEFAULT NULL,
  `next_service_date` date DEFAULT NULL,
  `notes` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `equipment_no` (`equipment_no`),
  KEY `idx_type` (`equipment_type`),
  KEY `idx_status` (`status`),
  KEY `idx_rig` (`assigned_rig`),
  KEY `idx_vendor` (`vendor_id`)
) ENGINE=InnoDB AUTO_INCREMENT=16 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `equipment`
--

LOCK TABLES `equipment` WRITE;
/*!40000 ALTER TABLE `equipment` DISABLE KEYS */;
INSERT INTO `equipment` VALUES (1,'TRAILER-01','RJ04-GD-0258','Trailer','','',NULL,2,'PPE-4','Available',NULL,NULL,'DRIVER NAME: Purna Ram H Prema Ram','2026-03-31 10:57:19','2026-03-31 12:15:30'),(2,'TRAILER-02','RJ19-GG2900','Trailer','','',NULL,2,'PPE-4','Available',NULL,NULL,'DRIVER NAME: Kanwara Ram H prem','2026-03-31 10:58:20','2026-03-31 12:15:45'),(3,'TRAILER-03','RJ04-GB-7139','Trailer','','',NULL,2,'PPE-4','Available',NULL,NULL,'DRIVER NAME: Bhanwara Ram H jasraj','2026-03-31 10:59:42','2026-03-31 12:15:53'),(4,'TRAILER-04','RJ04-GB-6897','Trailer','','',NULL,2,'PPE-4','Available',NULL,NULL,'DRIVER NAME: Joga Ram','2026-03-31 11:06:13','2026-03-31 12:16:01'),(5,'TRAILER-05','RJ27-GD-7618','Trailer','','',NULL,2,'PPE-4','Available',NULL,NULL,'DRIVER NAME: Kharta Ram','2026-03-31 11:09:38','2026-03-31 12:16:12'),(6,'TRAILER-06','RJ04-GB-3775','Trailer','','',NULL,2,'PPE-4','Available',NULL,NULL,'DRIVER NAME: MANA RAM','2026-03-31 11:10:49','2026-03-31 12:16:22'),(7,'TRAILER-07','RJ04-GC-7577','Trailer','','',NULL,3,'PPE-4','Available',NULL,NULL,'DRIVER NAME: Narapat H jasraj','2026-03-31 11:12:17','2026-03-31 12:16:39'),(8,'TRAILER-08','RJ46-GA-4441','Trailer','','',NULL,3,'PPE-4','Available',NULL,NULL,'DRIVER NAME: Jeta Ram H virender','2026-03-31 11:13:40','2026-03-31 12:19:08'),(9,'TRAILER-09','RJ36-GA-5267','Trailer','','',NULL,3,'PPE-4','Available',NULL,NULL,'DRIVER NAME: Omparkash H parkash','2026-03-31 11:14:36','2026-03-31 12:19:18'),(10,'TRAILER-10','RJ04-GC-3815','Trailer','','',NULL,3,'PPE-4','Available',NULL,NULL,'DRIVER NAME: Bhanwara Ram H Babu Ram','2026-03-31 11:16:34','2026-03-31 12:19:32'),(11,'TRAILER-11','RJ04-GC-8185','Trailer','','',NULL,3,'PPE-4','Available',NULL,NULL,'DRIVER NAME: Dwarka Ram','2026-03-31 11:17:45','2026-03-31 12:19:40'),(12,'TRAILER-12','RJ04-GC-5085','Trailer','','',NULL,3,'PPE-4','Available',NULL,NULL,'DRIVER NAME: Thakra Ram H Likhma Ram','2026-03-31 11:18:33','2026-03-31 12:19:47'),(13,'CRANE-01','RJ04-EA-3975','Crane','','60T',NULL,4,'PPE-4','Available',NULL,NULL,'Crane Operator: Arjun','2026-03-31 11:22:50','2026-03-31 11:32:25'),(14,'CRANE-02','RJ04-EA-3939','Crane','','60T',NULL,2,'','Available',NULL,NULL,'Crane Operator: Prakash','2026-03-31 11:24:57','2026-03-31 11:26:04'),(15,'CRANE-03','RJ04-EA-3393','Crane','','60T',NULL,2,'','Available',NULL,NULL,'Crane Operator: Indra','2026-03-31 11:25:54','2026-03-31 11:25:54');
/*!40000 ALTER TABLE `equipment` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `equipment_master`
--

DROP TABLE IF EXISTS `equipment_master`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `equipment_master` (
  `id` int NOT NULL AUTO_INCREMENT,
  `equipment_type` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `registration_no` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `short_name` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `category` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `is_active` tinyint DEFAULT '1',
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `equipment_master`
--

LOCK TABLES `equipment_master` WRITE;
/*!40000 ALTER TABLE `equipment_master` DISABLE KEYS */;
INSERT INTO `equipment_master` VALUES (1,'Crane','RJ-04-EB-3378','Crane-1','crane',1,'2026-03-25 14:33:59'),(2,'Crane','RJ-04-EA-3939','Crane-2','crane',1,'2026-03-25 14:33:59'),(3,'Hydra','RJ-04-EA-3099','Hydra-1','hydra',1,'2026-03-25 14:33:59'),(4,'Forklift','RJ-04-EA-2424','Forklift-1','forklift',1,'2026-03-25 14:33:59');
/*!40000 ALTER TABLE `equipment_master` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `ilm_locations`
--

DROP TABLE IF EXISTS `ilm_locations`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `ilm_locations` (
  `id` int NOT NULL AUTO_INCREMENT,
  `location` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `location` (`location`)
) ENGINE=InnoDB AUTO_INCREMENT=119 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `ilm_locations`
--

LOCK TABLES `ilm_locations` WRITE;
/*!40000 ALTER TABLE `ilm_locations` DISABLE KEYS */;
INSERT INTO `ilm_locations` VALUES (1,'BWP#01','2026-03-20 07:25:12'),(2,'BWP#02','2026-03-20 07:25:12'),(3,'BWP#03','2026-03-20 07:25:12'),(4,'BWP#04','2026-03-20 07:25:12'),(5,'BWP#05','2026-03-20 07:25:12'),(6,'BWP#06','2026-03-20 07:25:12'),(7,'BWP#07','2026-03-20 07:25:12'),(8,'BWP#08','2026-03-20 07:25:12'),(9,'BWP#09','2026-03-20 07:25:12'),(10,'BWP#10','2026-03-20 07:25:12'),(11,'BWP#11','2026-03-20 07:25:12'),(12,'BWP#12','2026-03-20 07:25:12'),(13,'BWP#13','2026-03-20 07:25:12'),(14,'AWP#01','2026-03-20 07:25:12'),(15,'AWP#02','2026-03-20 07:25:12'),(16,'AWP#03','2026-03-20 07:25:12'),(17,'MWP#01','2026-03-20 07:25:12'),(18,'MWP#02','2026-03-20 07:25:12'),(19,'MWP#03','2026-03-20 07:25:12'),(20,'MWP#04','2026-03-20 07:25:12'),(21,'MWP#05','2026-03-20 07:25:12'),(22,'MWP#06','2026-03-20 07:25:12'),(23,'MWP#07','2026-03-20 07:25:12'),(24,'MWP#08','2026-03-20 07:25:12'),(25,'MWP#09','2026-03-20 07:25:12'),(26,'MWP#10','2026-03-20 07:25:12'),(27,'MWP#11','2026-03-20 07:25:12'),(28,'MWP#12','2026-03-20 07:25:12'),(29,'MWP#13','2026-03-20 07:25:12'),(30,'NI#01','2026-03-20 07:25:12'),(31,'NI#02','2026-03-20 07:25:12'),(32,'NI#03','2026-03-20 07:25:12'),(33,'INTERNAL','2026-03-20 07:25:12'),(73,'3.8','2026-03-30 14:40:39'),(74,'30','2026-03-30 14:40:39'),(77,'-','2026-03-30 14:40:39');
/*!40000 ALTER TABLE `ilm_locations` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `ilm_vendors`
--

DROP TABLE IF EXISTS `ilm_vendors`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `ilm_vendors` (
  `id` int NOT NULL AUTO_INCREMENT,
  `vendor_name` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `vendor_type` enum('Trailer','Crane','Both') CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT 'Both',
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `vendor_name` (`vendor_name`)
) ENGINE=InnoDB AUTO_INCREMENT=9 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `ilm_vendors`
--

LOCK TABLES `ilm_vendors` WRITE;
/*!40000 ALTER TABLE `ilm_vendors` DISABLE KEYS */;
INSERT INTO `ilm_vendors` VALUES (1,'SBTC','Trailer','2026-03-20 07:25:12'),(2,'ACC','Both','2026-03-20 07:25:12'),(3,'JEET','Trailer','2026-03-20 07:25:12'),(4,'ARC','Crane','2026-03-20 07:25:12'),(5,'ACC/JEET','Trailer','2026-03-20 07:25:12'),(6,'SBTC/ACC','Both','2026-03-20 07:25:12'),(7,'ARC/ACC','Crane','2026-03-20 07:25:12');
/*!40000 ALTER TABLE `ilm_vendors` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `rig_daily_log`
--

DROP TABLE IF EXISTS `rig_daily_log`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `rig_daily_log` (
  `id` int NOT NULL AUTO_INCREMENT,
  `date` date DEFAULT NULL,
  `rig` varchar(20) DEFAULT NULL,
  `operating_hours` float DEFAULT NULL,
  `standby_hours` float DEFAULT NULL,
  `breakdown_hours` float DEFAULT NULL,
  `ilm_hours` float DEFAULT NULL,
  `zero_rate_hours` float DEFAULT NULL,
  `reason` text,
  `status` varchar(20) DEFAULT NULL,
  `created_by` varchar(60) DEFAULT NULL,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `unique_rig_date` (`rig`,`date`),
  CONSTRAINT `hours_limit` CHECK ((((((`operating_hours` + `standby_hours`) + `breakdown_hours`) + `ilm_hours`) + `zero_rate_hours`) <= 24))
) ENGINE=InnoDB AUTO_INCREMENT=262 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `rig_daily_log`
--

LOCK TABLES `rig_daily_log` WRITE;
/*!40000 ALTER TABLE `rig_daily_log` DISABLE KEYS */;
INSERT INTO `rig_daily_log` VALUES (1,'2026-02-08','PPE-1',24,0,0,0,0,'','Running',NULL,'2026-03-13 09:17:28'),(2,'2026-02-09','PPE-1',22,2,0,0,0,'','Running',NULL,'2026-03-13 09:17:28'),(3,'2026-02-10','PPE-1',12.5,11.5,0,0,0,'','Running',NULL,'2026-03-13 09:17:28'),(4,'2026-02-11','PPE-1',24,0,0,0,0,'','Running',NULL,'2026-03-13 09:17:28'),(5,'2026-02-12','PPE-1',24,0,0,0,0,'','Running',NULL,'2026-03-13 09:17:28'),(6,'2026-02-13','PPE-1',11,9.5,3.5,0,0,'','Running',NULL,'2026-03-13 09:17:28'),(7,'2026-02-14','PPE-1',19,0,5,0,0,'','Running',NULL,'2026-03-13 09:17:28'),(8,'2026-02-15','PPE-1',24,0,0,0,0,'','Running',NULL,'2026-03-13 09:17:28'),(9,'2026-02-16','PPE-1',23.5,0,0,0,0.5,'','Running',NULL,'2026-03-13 09:17:28'),(10,'2026-02-17','PPE-1',6,0,0,18,0,'','Running',NULL,'2026-03-13 09:17:28'),(11,'2026-02-18','PPE-1',0,0,0,12,12,'','Running',NULL,'2026-03-13 09:17:28'),(12,'2026-02-19','PPE-1',4,0,0,0,20,'','Running',NULL,'2026-03-13 09:17:28'),(13,'2026-02-20','PPE-1',24,0,0,0,0,'','Running',NULL,'2026-03-13 09:17:28'),(14,'2026-02-21','PPE-1',24,0,0,0,0,'','Running',NULL,'2026-03-13 09:17:28'),(15,'2026-02-22','PPE-1',24,0,0,0,0,'','Running',NULL,'2026-03-13 09:17:28'),(16,'2026-02-23','PPE-1',24,0,0,0,0,'','Running',NULL,'2026-03-13 09:17:28'),(17,'2026-02-24','PPE-1',24,0,0,0,0,'','Running',NULL,'2026-03-13 09:17:28'),(18,'2026-02-25','PPE-1',24,0,0,0,0,'','Running',NULL,'2026-03-13 09:17:28'),(19,'2026-02-26','PPE-1',24,0,0,0,0,'','Running',NULL,'2026-03-13 09:17:28'),(21,'2026-02-27','PPE-1',23,0,0,0,1,'','Running',NULL,'2026-03-13 09:17:28'),(22,'2026-02-28','PPE-1',24,0,0,0,0,'','Running',NULL,'2026-03-13 09:17:28'),(23,'2026-03-01','PPE-1',24,0,0,0,0,'','Running',NULL,'2026-03-13 09:17:28'),(24,'2026-03-02','PPE-1',23,1,0,0,0,'','Running',NULL,'2026-03-13 09:17:28'),(25,'2026-03-03','PPE-1',23,0,0,0,1,'','Running',NULL,'2026-03-13 09:17:28'),(26,'2026-03-04','PPE-1',23.5,0.5,0,0,0,'','Running',NULL,'2026-03-13 09:17:28'),(27,'2026-03-05','PPE-1',12,0,0,12,0,'','Running',NULL,'2026-03-13 09:17:28'),(28,'2026-03-06','PPE-1',6,0,0,18,0,'','Running',NULL,'2026-03-13 09:17:28'),(29,'2026-03-07','PPE-1',9.5,0,14.5,0,0,'','Running',NULL,'2026-03-13 09:17:28'),(30,'2026-03-08','PPE-1',14.5,0,9.5,0,0,'','Running',NULL,'2026-03-13 09:17:28'),(31,'2026-03-09','PPE-1',22,0,0,0,2,'','Running',NULL,'2026-03-13 09:17:28'),(32,'2026-03-10','PPE-1',24,0,0,0,0,'','Running',NULL,'2026-03-13 09:17:28'),(33,'2026-02-08','PPE-2',5,0,0,19,0,'','Running',NULL,'2026-03-13 09:17:28'),(34,'2026-02-09','PPE-2',24,0,0,0,0,'','Running',NULL,'2026-03-13 09:17:28'),(35,'2026-02-10','PPE-2',24,0,0,0,0,'','Running',NULL,'2026-03-13 09:17:28'),(36,'2026-02-11','PPE-2',24,0,0,0,0,'','Running',NULL,'2026-03-13 09:17:28'),(37,'2026-02-12','PPE-2',24,0,0,0,0,'','Running',NULL,'2026-03-13 09:17:28'),(38,'2026-02-13','PPE-2',24,0,0,0,0,'','Running',NULL,'2026-03-13 09:17:28'),(39,'2026-02-14','PPE-2',21,0,0,0,3,'','Running',NULL,'2026-03-13 09:17:28'),(40,'2026-02-15','PPE-2',24,0,0,0,0,'','Running',NULL,'2026-03-13 09:17:28'),(42,'2026-02-17','PPE-2',21.5,2.5,0,0,0,'','Running',NULL,'2026-03-13 09:17:28'),(43,'2026-02-18','PPE-2',19.25,3.75,1,0,0,'','Running',NULL,'2026-03-13 09:17:28'),(44,'2026-02-19','PPE-2',24,0,0,0,0,'','Running',NULL,'2026-03-13 09:17:28'),(45,'2026-02-20','PPE-2',18,0,0,0,6,'','Running',NULL,'2026-03-13 09:17:28'),(46,'2026-02-21','PPE-2',12.25,0,1.25,0,10.5,'','Running',NULL,'2026-03-13 09:17:28'),(47,'2026-02-22','PPE-2',24,0,0,0,0,'','Running',NULL,'2026-03-13 09:17:28'),(48,'2026-02-23','PPE-2',24,0,0,0,0,'','Running',NULL,'2026-03-13 09:17:28'),(49,'2026-02-24','PPE-2',24,0,0,0,0,'','Running',NULL,'2026-03-13 09:17:28'),(50,'2026-02-25','PPE-2',24,0,0,0,0,'','Running',NULL,'2026-03-13 09:17:28'),(51,'2026-02-26','PPE-2',24,0,0,0,0,'','Running',NULL,'2026-03-13 09:17:28'),(52,'2026-02-27','PPE-2',24,0,0,0,0,'','Running',NULL,'2026-03-13 09:17:28'),(53,'2026-02-28','PPE-2',23,0,1,0,0,'','Running',NULL,'2026-03-13 09:17:28'),(54,'2026-03-01','PPE-2',23.5,0,0.5,0,0,'','Running',NULL,'2026-03-13 09:17:28'),(55,'2026-03-02','PPE-2',23.5,0,0,0,0.5,'','Running',NULL,'2026-03-13 09:17:28'),(56,'2026-03-03','PPE-2',24,0,0,0,0,'','Running',NULL,'2026-03-13 09:17:28'),(57,'2026-03-04','PPE-2',18,0,0,6,0,'','Running',NULL,'2026-03-13 09:17:28'),(58,'2026-03-05','PPE-2',0,0,0,24,0,'','Running',NULL,'2026-03-13 09:17:28'),(59,'2026-03-06','PPE-2',0,0,0,24,0,'','Running',NULL,'2026-03-13 09:17:28'),(60,'2026-03-07','PPE-2',20.5,3.5,0,0,0,'','Running',NULL,'2026-03-13 09:17:28'),(61,'2026-03-08','PPE-2',24,0,0,0,0,'','Running',NULL,'2026-03-13 09:17:28'),(62,'2026-03-09','PPE-2',22.5,0,0,0,1.5,'','Running',NULL,'2026-03-13 09:17:28'),(63,'2026-03-10','PPE-2',19.5,0,0,0,4.5,'','Running',NULL,'2026-03-13 09:17:28'),(64,'2026-02-08','PPE-3',0,0,0,24,0,'','Running',NULL,'2026-03-13 09:17:28'),(65,'2026-02-09','PPE-3',0,0,0,24,0,'','Running',NULL,'2026-03-13 09:17:28'),(66,'2026-02-10','PPE-3',12.5,2.5,0,6,3,'','Running',NULL,'2026-03-13 09:17:28'),(67,'2026-02-11','PPE-3',22,2,0,0,0,'','Running',NULL,'2026-03-13 09:17:28'),(68,'2026-02-12','PPE-3',24,0,0,0,0,'','Running',NULL,'2026-03-13 09:17:28'),(69,'2026-02-13','PPE-3',24,0,0,0,0,'','Running',NULL,'2026-03-13 09:17:28'),(70,'2026-02-14','PPE-3',24,0,0,0,0,'','Running',NULL,'2026-03-13 09:17:28'),(71,'2026-02-15','PPE-3',24,0,0,0,0,'','Running',NULL,'2026-03-13 09:17:28'),(72,'2026-02-16','PPE-3',24,0,0,0,0,'','Running',NULL,'2026-03-13 09:17:28'),(73,'2026-02-17','PPE-3',23,1,0,0,0,'','Running',NULL,'2026-03-13 09:17:28'),(74,'2026-02-18','PPE-3',20,4,0,0,0,'','Running',NULL,'2026-03-13 09:17:28'),(75,'2026-02-19','PPE-3',12,0,0,12,0,'','Running',NULL,'2026-03-13 09:17:28'),(76,'2026-02-20','PPE-3',6,0,0,18,0,'','Running',NULL,'2026-03-13 09:17:28'),(77,'2026-02-21','PPE-3',24,0,0,0,0,'','Running',NULL,'2026-03-13 09:17:28'),(78,'2026-02-22','PPE-3',24,0,0,0,0,'','Running',NULL,'2026-03-13 09:17:28'),(79,'2026-02-23','PPE-3',24,0,0,0,0,'','Running',NULL,'2026-03-13 09:17:28'),(80,'2026-02-24','PPE-3',24,0,0,0,0,'','Running',NULL,'2026-03-13 09:17:28'),(81,'2026-02-25','PPE-3',19,5,0,0,0,'','Running',NULL,'2026-03-13 09:17:28'),(82,'2026-02-26','PPE-3',24,0,0,0,0,'','Running',NULL,'2026-03-13 09:17:28'),(83,'2026-02-27','PPE-3',24,0,0,0,0,'','Running',NULL,'2026-03-13 09:17:28'),(84,'2026-02-28','PPE-3',24,0,0,0,0,'','Running',NULL,'2026-03-13 09:17:28'),(85,'2026-03-01','PPE-3',16,1.5,0,6.5,0,'','Running',NULL,'2026-03-13 09:17:28'),(86,'2026-03-02','PPE-3',0,1.5,0,22.5,0,'','Running',NULL,'2026-03-13 09:17:28'),(87,'2026-03-03','PPE-3',24,0,0,0,0,'','Running',NULL,'2026-03-13 09:17:28'),(88,'2026-03-04','PPE-3',24,0,0,0,0,'','Running',NULL,'2026-03-13 09:17:28'),(89,'2026-03-05','PPE-3',24,0,0,0,0,'','Running',NULL,'2026-03-13 09:17:28'),(90,'2026-03-06','PPE-3',24,0,0,0,0,'','Running',NULL,'2026-03-13 09:17:28'),(91,'2026-03-07','PPE-3',14,2,0,8,0,'','Running',NULL,'2026-03-13 09:17:28'),(92,'2026-03-08','PPE-3',0,5,0,19,0,'','Running',NULL,'2026-03-13 09:17:28'),(93,'2026-03-09','PPE-3',19,2,0,3,0,'','Running',NULL,'2026-03-13 09:17:28'),(94,'2026-03-10','PPE-3',17.5,1.5,5,0,0,'','Running',NULL,'2026-03-13 09:17:28'),(95,'2026-02-08','PPE-4',24,0,0,0,0,'','Running',NULL,'2026-03-13 09:17:28'),(96,'2026-02-09','PPE-4',24,0,0,0,0,'','Running',NULL,'2026-03-13 09:17:28'),(97,'2026-02-10','PPE-4',24,0,0,0,0,'','Running',NULL,'2026-03-13 09:17:28'),(98,'2026-02-11','PPE-4',24,0,0,0,0,'','Running',NULL,'2026-03-13 09:17:28'),(99,'2026-02-12','PPE-4',8,4,0,2,10,'','Running',NULL,'2026-03-13 09:17:28'),(100,'2026-02-13','PPE-4',0,0,0,15,9,'','Running',NULL,'2026-03-13 09:17:28'),(101,'2026-02-14','PPE-4',0,0,0,24,0,'','Running',NULL,'2026-03-13 09:17:28'),(103,'2026-02-16','PPE-4',24,0,0,0,0,'','Running',NULL,'2026-03-13 09:17:28'),(104,'2026-02-17','PPE-4',24,0,0,0,0,'','Running',NULL,'2026-03-13 09:17:28'),(105,'2026-02-18','PPE-4',24,0,0,0,0,'','Running',NULL,'2026-03-13 09:17:28'),(106,'2026-02-19','PPE-4',24,0,0,0,0,'','Running',NULL,'2026-03-13 09:17:28'),(107,'2026-02-20','PPE-4',11,0,0,13,0,'','Running',NULL,'2026-03-13 09:17:28'),(108,'2026-02-21','PPE-4',0,0,0,24,0,'','Running',NULL,'2026-03-13 09:17:28'),(109,'2026-02-24','PPE-4',0,0,0,24,0,'','Running',NULL,'2026-03-13 09:17:28'),(110,'2026-02-23','PPE-4',5,0,0,19,0,'','Running',NULL,'2026-03-13 09:17:28'),(111,'2026-02-25','PPE-4',24,0,0,0,0,'','Running',NULL,'2026-03-13 09:17:28'),(112,'2026-02-26','PPE-4',24,0,0,0,0,'','Running',NULL,'2026-03-13 09:17:28'),(113,'2026-02-27','PPE-4',24,0,0,0,0,'','Running',NULL,'2026-03-13 09:17:28'),(114,'2026-02-28','PPE-4',24,0,0,0,0,'','Running',NULL,'2026-03-13 09:17:28'),(115,'2026-03-01','PPE-4',24,0,0,0,0,'','Running',NULL,'2026-03-13 09:17:28'),(116,'2026-03-02','PPE-4',24,0,0,0,0,'','Running',NULL,'2026-03-13 09:17:28'),(117,'2026-03-03','PPE-4',24,0,0,0,0,'','Running',NULL,'2026-03-13 09:17:28'),(118,'2026-03-04','PPE-4',22.5,1.5,0,0,0,'','Running',NULL,'2026-03-13 09:17:28'),(119,'2026-03-05','PPE-4',24,0,0,0,0,'','Running',NULL,'2026-03-13 09:17:28'),(120,'2026-03-06','PPE-4',23,1,0,0,0,'','Running',NULL,'2026-03-13 09:17:28'),(121,'2026-03-07','PPE-4',20.75,3.25,0,0,0,'','Running',NULL,'2026-03-13 09:17:28'),(122,'2026-03-08','PPE-4',24,0,0,0,0,'','Running',NULL,'2026-03-13 09:17:28'),(123,'2026-03-09','PPE-5',9,0,0,15,0,'','Running',NULL,'2026-03-13 09:17:28'),(124,'2026-03-10','PPE-4',9,0,0,15,0,'','Running',NULL,'2026-03-13 09:17:28'),(125,'2026-03-09','PPE-4',9,0,0,0,15,'','Running',NULL,'2026-03-13 09:17:28'),(126,'2026-02-08','PPE-5',0,0,0,24,0,'','Running',NULL,'2026-03-13 09:17:28'),(127,'2026-02-09','PPE-5',0,0,0,6,18,'','Running',NULL,'2026-03-13 09:17:28'),(128,'2026-02-10','PPE-5',12,0,0,0,12,'','Running',NULL,'2026-03-13 09:17:28'),(129,'2026-02-11','PPE-5',23,0,1,0,0,'','Running',NULL,'2026-03-13 09:17:28'),(130,'2026-02-12','PPE-5',24,0,0,0,0,'','Running',NULL,'2026-03-13 09:17:28'),(131,'2026-02-13','PPE-5',24,0,0,0,0,'','Running',NULL,'2026-03-13 09:17:28'),(132,'2026-02-14','PPE-5',15,9,0,0,0,'','Running',NULL,'2026-03-13 09:17:28'),(133,'2026-02-15','PPE-5',23,0,1,0,0,'','Running',NULL,'2026-03-13 09:17:28'),(134,'2026-02-16','PPE-5',22.5,0,1.5,0,0,'','Running',NULL,'2026-03-13 09:17:28'),(135,'2026-02-17','PPE-5',6,0,0,18,0,'','Running',NULL,'2026-03-13 09:17:28'),(136,'2026-02-18','PPE-5',10.5,1.5,0,12,0,'','Running',NULL,'2026-03-13 09:17:28'),(137,'2026-02-19','PPE-5',23,1,0,0,0,'','Running',NULL,'2026-03-13 09:17:28'),(139,'2026-02-21','PPE-5',21,0,3,0,0,'','Running',NULL,'2026-03-13 09:17:28'),(140,'2026-02-22','PPE-5',6,0,0,18,0,'','Running',NULL,'2026-03-13 09:17:28'),(141,'2026-02-23','PPE-5',13,0,0,11,0,'','Running',NULL,'2026-03-13 09:17:28'),(142,'2026-02-24','PPE-5',20,2,0,0,2,'','Running',NULL,'2026-03-13 09:17:28'),(143,'2026-02-25','PPE-5',23.5,0.5,0,0,0,'','Running',NULL,'2026-03-13 09:17:28'),(144,'2026-02-26','PPE-5',24,0,0,0,0,'','Running',NULL,'2026-03-13 09:17:28'),(145,'2026-02-27','PPE-5',24,0,0,0,0,'','Running',NULL,'2026-03-13 09:17:28'),(146,'2026-02-28','PPE-5',0,0,0,24,0,'','Running',NULL,'2026-03-13 09:17:28'),(147,'2026-03-01','PPE-5',10.5,1.5,0,0,12,'','Running',NULL,'2026-03-13 09:17:28'),(148,'2026-03-02','PPE-5',21,3,0,0,0,'','Running',NULL,'2026-03-13 09:17:28'),(149,'2026-03-03','PPE-5',24,0,0,0,0,'','Running',NULL,'2026-03-13 09:17:28'),(150,'2026-03-04','PPE-5',22,2,0,0,0,'','Running',NULL,'2026-03-13 09:17:28'),(151,'2026-03-05','PPE-5',14,0,0,10,0,'','Running',NULL,'2026-03-13 09:17:28'),(152,'2026-03-06','PPE-5',0,0,0,24,0,'','Running',NULL,'2026-03-13 09:17:28'),(153,'2026-03-07','PPE-5',0,0,0,24,0,'','Running',NULL,'2026-03-13 09:17:28'),(154,'2026-03-08','PPE-5',9,5.5,0,0,9.5,'','Running',NULL,'2026-03-13 09:17:28'),(155,'2026-03-10','PPE-5',0,24,0,0,0,'','Running',NULL,'2026-03-13 09:17:28'),(156,'2026-03-11','PPE-1',24,0,0,0,0,'','Running',NULL,'2026-03-13 09:17:28'),(157,'2026-03-11','PPE-2',22,0,0,0,2,'','Running',NULL,'2026-03-13 09:17:28'),(158,'2026-03-11','PPE-3',22,0,0.5,0,1.5,'','Running',NULL,'2026-03-13 09:17:28'),(159,'2026-03-11','PPE-4',21.25,1.75,0,0,1,'','Running',NULL,'2026-03-13 09:17:28'),(160,'2026-03-11','PPE-5',6,0,0,18,0,'','Running',NULL,'2026-03-13 09:17:28'),(161,'2026-02-15','PPE-4',11,0,0,13,0,'','Running',NULL,'2026-03-13 09:17:28'),(162,'2026-02-16','PPE-2',24,0,0,0,0,'','Running',NULL,'2026-03-13 09:17:28'),(163,'2026-02-20','PPE-5',24,0,0,0,0,'','Running',NULL,'2026-03-13 09:17:28'),(164,'2026-02-22','PPE-4',0,0,0,24,0,'','Running',NULL,'2026-03-13 09:17:28'),(165,'2026-03-12','PPE-1',24,0,0,0,0,'','Running',NULL,'2026-03-13 10:56:15'),(166,'2026-03-12','PPE-2',24,0,0,0,0,'','Running',NULL,'2026-03-13 10:56:37'),(167,'2026-03-12','PPE-3',22,2,0,0,0,'','Running',NULL,'2026-03-13 10:57:59'),(168,'2026-03-12','PPE-4',24,0,0,0,0,'','Running',NULL,'2026-03-13 10:58:32'),(169,'2026-03-12','PPE-5',6,0,0,6,12,'','Running',NULL,'2026-03-13 10:59:30'),(170,'2026-03-13','PPE-1',15,0,0,9,0,'','Running',NULL,'2026-03-14 07:01:43'),(171,'2026-03-13','PPE-2',24,0,0,0,0,'','Running',NULL,'2026-03-14 07:04:16'),(172,'2026-03-13','PPE-3',22,2,0,0,0,'','Running',NULL,'2026-03-14 07:04:54'),(173,'2026-03-13','PPE-4',22,0,2,0,0,'','Running',NULL,'2026-03-14 07:05:26'),(174,'2026-03-13','PPE-5',12,4,0,0,8,'','Running',NULL,'2026-03-14 07:05:59'),(175,'2026-03-17','PPE-1',2,0,0,0,22,'','Running','admin','2026-03-18 06:46:10'),(176,'2026-03-17','PPE-2',22,2,0,0,0,'','Running','admin','2026-03-18 06:47:07'),(177,'2026-03-17','PPE-3',23,1,0,0,0,'','Running','admin','2026-03-18 06:47:35'),(178,'2026-03-17','PPE-4',24,0,0,0,0,'','Running','admin','2026-03-18 06:47:53'),(179,'2026-03-17','PPE-5',12,6,0,5,1,'','Running','admin','2026-03-18 06:48:33'),(180,'2026-03-22','PPE-4',24,0,0,0,0,'','Running','krissadmin','2026-03-22 23:42:44'),(181,'2026-03-14','PPE-1',0,0,0,21,3,'','Running','krissadmin','2026-03-22 23:51:48'),(182,'2026-03-23','PPE-1',21,3,0,0,0,'','Running','krissadmin','2026-03-22 23:52:50'),(183,'2026-03-15','PPE-1',0,0,0,0,24,'','Running','krissadmin','2026-03-22 23:55:18'),(184,'2026-03-16','PPE-1',0,0,0,0,24,'','Running','krissadmin','2026-03-22 23:56:36'),(185,'2026-03-18','PPE-1',8.5,15.5,0,0,0,'','Running','krissadmin','2026-03-22 23:58:35'),(186,'2026-03-19','PPE-1',22,2,0,0,0,'','Running','krissadmin','2026-03-23 00:00:35'),(187,'2026-03-20','PPE-1',16,8,0,0,0,'','Running','krissadmin','2026-03-23 00:01:54'),(188,'2026-03-21','PPE-1',23,1,0,0,0,'','Running','krissadmin','2026-03-23 00:03:20'),(189,'2026-03-22','PPE-1',21.5,2.5,0,0,0,'','Running','krissadmin','2026-03-23 00:04:35'),(190,'2026-03-14','PPE-2',20,4,0,0,0,'','Running','krissadmin','2026-03-23 00:24:01'),(191,'2026-03-15','PPE-2',23,1,0,0,0,'','Running','krissadmin','2026-03-23 00:25:07'),(192,'2026-03-16','PPE-2',24,0,0,0,0,'','Running','krissadmin','2026-03-23 00:33:40'),(193,'2026-03-18','PPE-2',24,0,0,0,0,'','Running','krissadmin','2026-03-23 00:36:59'),(194,'2026-03-19','PPE-2',23,0,0,0,1,'','Running','krissadmin','2026-03-23 00:38:30'),(195,'2026-03-20','PPE-2',24,0,0,0,0,'','Running','krissadmin','2026-03-23 00:39:18'),(196,'2026-03-21','PPE-2',20,4,0,0,0,'','Running','krissadmin','2026-03-23 00:40:08'),(197,'2026-03-22','PPE-2',24,0,0,0,0,'','Running','krissadmin','2026-03-23 00:40:39'),(198,'2026-03-14','PPE-3',12,4,0,8,0,'','Running','krissadmin','2026-03-23 00:57:38'),(199,'2026-03-15','PPE-3',20,4,0,0,0,'','Running','krissadmin','2026-03-23 01:00:12'),(200,'2026-03-16','PPE-3',22,2,0,0,0,'','Running','krissadmin','2026-03-23 01:00:57'),(201,'2026-03-18','PPE-3',24,0,0,0,0,'','Running','krissadmin','2026-03-23 01:01:35'),(202,'2026-03-19','PPE-3',24,0,0,0,0,'','Running','krissadmin','2026-03-23 01:02:01'),(203,'2026-03-20','PPE-3',22,2,0,0,0,'','Running','krissadmin','2026-03-23 01:02:27'),(204,'2026-03-21','PPE-3',19.25,4.75,0,0,0,'','Running','krissadmin','2026-03-23 01:03:51'),(205,'2026-03-22','PPE-3',19.75,4.25,0,0,0,'','Running','krissadmin','2026-03-23 01:04:21'),(206,'2026-03-14','PPE-4',24,0,0,0,0,'','Running','krissadmin','2026-03-23 01:07:23'),(207,'2026-03-15','PPE-4',24,0,0,0,0,'','Running','krissadmin','2026-03-23 01:07:42'),(208,'2026-03-16','PPE-4',24,0,0,0,0,'','Running','krissadmin','2026-03-23 01:08:00'),(209,'2026-03-18','PPE-4',24,0,0,0,0,'','Running','krissadmin','2026-03-23 01:08:17'),(210,'2026-03-19','PPE-4',18.5,0,5.5,0,0,'','Running','krissadmin','2026-03-23 01:08:51'),(211,'2026-03-20','PPE-4',23.25,0.75,0,0,0,'','Running','krissadmin','2026-03-23 01:09:20'),(212,'2026-03-21','PPE-4',24,0,0,0,0,'','Running','krissadmin','2026-03-23 01:09:36'),(213,'2026-03-14','PPE-5',22,0,0,0,2,'','Running','krissadmin','2026-03-23 01:19:33'),(214,'2026-03-15','PPE-5',22,0,0,0,2,'','Running','krissadmin','2026-03-23 01:20:02'),(215,'2026-03-16','PPE-5',22,0,0,0,2,'','Running','krissadmin','2026-03-23 01:20:26'),(216,'2026-03-18','PPE-5',0,0,0,24,0,'','Running','krissadmin','2026-03-23 01:28:46'),(217,'2026-03-19','PPE-5',22,0,0,0,2,'','Running','krissadmin','2026-03-23 01:29:07'),(218,'2026-03-20','PPE-5',22,0,0,0,2,'','Running','krissadmin','2026-03-23 01:29:27'),(219,'2026-03-21','PPE-5',22,0,0,0,2,'','Running','krissadmin','2026-03-23 01:29:47'),(220,'2026-03-22','PPE-5',16,0,0,6,2,'','Running','krissadmin','2026-03-23 01:30:17'),(221,'2026-02-01','PPE-1',22.5,0,1.5,0,0,'','Running','krissadmin','2026-03-23 02:33:55'),(222,'2026-02-02','PPE-1',24,0,0,0,0,'','Running','krissadmin','2026-03-23 02:34:38'),(223,'2026-02-03','PPE-1',24,0,0,0,0,'','Running','krissadmin','2026-03-23 02:34:57'),(224,'2026-02-04','PPE-1',24,0,0,0,0,'','Running','krissadmin','2026-03-23 02:36:25'),(225,'2026-02-05','PPE-1',6,0,0,18,0,'','Running','krissadmin','2026-03-23 02:36:59'),(226,'2026-02-06','PPE-1',24,0,0,0,0,'','Running','krissadmin','2026-03-23 02:37:26'),(227,'2026-02-07','PPE-1',24,0,0,0,0,'','Running','krissadmin','2026-03-23 02:37:44'),(228,'2026-02-01','PPE-2',11,0,0,13,0,'','Running','krissadmin','2026-03-23 02:43:45'),(229,'2026-02-02','PPE-2',0,0,0,24,0,'','Running','krissadmin','2026-03-23 02:44:18'),(230,'2026-02-03','PPE-2',9,0,0,3,12,'','Running','krissadmin','2026-03-23 02:46:12'),(231,'2026-02-04','PPE-2',24,0,0,0,0,'','Running','krissadmin','2026-03-23 02:46:39'),(232,'2026-02-05','PPE-2',24,0,0,0,0,'','Running','krissadmin','2026-03-23 02:46:56'),(233,'2026-02-06','PPE-2',24,0,0,0,0,'','Running','krissadmin','2026-03-23 02:47:14'),(234,'2026-02-07','PPE-2',13,0,0,11,0,'','Running','krissadmin','2026-03-23 02:47:36'),(235,'2026-02-01','PPE-3',0,0,6,18,0,'','Breakdown','krissadmin','2026-03-23 03:44:15'),(236,'2026-02-02','PPE-3',15,0,0,9,0,'','Running','krissadmin','2026-03-23 03:44:51'),(237,'2026-02-03','PPE-3',24,0,0,0,0,'','Running','krissadmin','2026-03-23 03:45:11'),(238,'2026-02-04','PPE-3',15,0,9,0,0,'','Running','krissadmin','2026-03-23 03:46:20'),(239,'2026-02-05','PPE-3',22,0,0,0,2,'','Running','krissadmin','2026-03-23 03:46:44'),(240,'2026-02-06','PPE-3',24,0,0,0,0,'','Running','krissadmin','2026-03-23 03:47:04'),(241,'2026-02-07','PPE-3',24,0,0,0,0,'','Running','krissadmin','2026-03-23 03:47:58'),(242,'2026-02-01','PPE-4',24,0,0,0,0,'','Running','krissadmin','2026-03-23 03:49:29'),(243,'2026-02-02','PPE-4',23,0,1,0,0,'','Running','krissadmin','2026-03-23 03:49:52'),(244,'2026-02-03','PPE-4',22.5,0,1.5,0,0,'','Running','krissadmin','2026-03-23 03:50:21'),(245,'2026-02-04','PPE-4',24,0,0,0,0,'','Running','krissadmin','2026-03-23 03:50:54'),(246,'2026-02-05','PPE-4',12,12,0,0,0,'','Running','krissadmin','2026-03-23 03:51:22'),(247,'2026-02-06','PPE-4',0,10.5,0,13.5,0,'','Standby','krissadmin','2026-03-23 03:52:06'),(248,'2026-02-07','PPE-4',0,7.5,0,16.5,0,'','Standby','krissadmin','2026-03-23 03:53:02'),(249,'2026-02-01','PPE-5',14,0,0,0,10,'','Running','krissadmin','2026-03-23 03:57:02'),(250,'2026-02-02','PPE-5',24,0,0,0,0,'','Running','krissadmin','2026-03-23 03:57:20'),(251,'2026-02-03','PPE-5',24,0,0,0,0,'','Running','krissadmin','2026-03-23 03:57:38'),(252,'2026-02-04','PPE-5',19.5,4.5,0,0,0,'','Running','krissadmin','2026-03-23 03:58:07'),(253,'2026-02-05','PPE-5',16,8,0,0,0,'','Running','krissadmin','2026-03-23 03:58:32'),(254,'2026-02-06','PPE-5',24,0,0,0,0,'','Running','krissadmin','2026-03-23 03:58:51'),(255,'2026-02-07','PPE-5',24,0,0,0,0,'','Running','krissadmin','2026-03-23 03:59:14'),(256,'2026-03-23','PPE-3',18,6,0,0,0,'','Running','krissadmin','2026-03-23 21:56:09'),(257,'2026-03-23','PPE-4',0,0,0,24,0,'','Running','krissadmin','2026-03-23 21:58:06'),(258,'2026-03-23','PPE-5',0,0,0,24,0,'','Running','krissadmin','2026-03-24 01:59:35'),(259,'2026-03-23','PPE-2',18,0,0,6,0,'','Running','krissadmin','2026-03-24 02:12:21'),(260,'2026-03-24','PPE-4',18,0,0,6,0,'','Running','krissadmin','2026-03-24 23:36:16'),(261,'2026-03-24','PPE-3',23,1,0,0,0,'','Running','krissadmin','2026-03-24 23:57:22');
/*!40000 ALTER TABLE `rig_daily_log` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `rig_diesel_full`
--

DROP TABLE IF EXISTS `rig_diesel_full`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `rig_diesel_full` (
  `id` int NOT NULL AUTO_INCREMENT,
  `date` date DEFAULT NULL,
  `rig` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `opening_stock` float DEFAULT NULL,
  `received` float DEFAULT NULL,
  `total_in_tank` float DEFAULT NULL,
  `rig_engine` float DEFAULT NULL,
  `dg1` float DEFAULT NULL,
  `dg2` float DEFAULT NULL,
  `mud_pump` float DEFAULT NULL,
  `total_rig` float DEFAULT NULL,
  `crane_3378` float DEFAULT NULL,
  `crane_3939` float DEFAULT NULL,
  `crane_3975` float DEFAULT NULL,
  `crane_3393` float DEFAULT NULL,
  `crane_3154` float DEFAULT NULL,
  `crane_3483` float DEFAULT NULL,
  `ambulance` float DEFAULT NULL,
  `hydra` float DEFAULT NULL,
  `forklift` float DEFAULT NULL,
  `fire_pump` float DEFAULT NULL,
  `guma_pump` float DEFAULT NULL,
  `compressor` float DEFAULT NULL,
  `welding` float DEFAULT NULL,
  `camper` float DEFAULT NULL,
  `cleaning` float DEFAULT NULL,
  `total_resources` float DEFAULT NULL,
  `its_trs` float DEFAULT NULL,
  `transfer_cairn` float DEFAULT NULL,
  `total_third_party` float DEFAULT NULL,
  `total_consumption` float DEFAULT NULL,
  `balance` float DEFAULT NULL,
  `cairn_supply` float DEFAULT NULL,
  `excess_short` float DEFAULT NULL,
  `remarks` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci,
  PRIMARY KEY (`id`),
  UNIQUE KEY `date` (`date`,`rig`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `rig_diesel_full`
--

LOCK TABLES `rig_diesel_full` WRITE;
/*!40000 ALTER TABLE `rig_diesel_full` DISABLE KEYS */;
/*!40000 ALTER TABLE `rig_diesel_full` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `rig_diesel_log`
--

DROP TABLE IF EXISTS `rig_diesel_log`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `rig_diesel_log` (
  `id` int NOT NULL AUTO_INCREMENT,
  `date` date NOT NULL,
  `rig` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `opening_balance` float DEFAULT '0',
  `received_qty` float DEFAULT '0',
  `total_available` float GENERATED ALWAYS AS ((`opening_balance` + `received_qty`)) STORED,
  `consumption_ltr` float DEFAULT '0',
  `closing_balance` float DEFAULT '0',
  `rate_per_ltr` float DEFAULT '0',
  `total_cost` float GENERATED ALWAYS AS ((`consumption_ltr` * `rate_per_ltr`)) STORED,
  `vendor` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `remarks` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci,
  `created_by` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `unique_rig_date` (`rig`,`date`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `rig_diesel_log`
--

LOCK TABLES `rig_diesel_log` WRITE;
/*!40000 ALTER TABLE `rig_diesel_log` DISABLE KEYS */;
/*!40000 ALTER TABLE `rig_diesel_log` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `rig_ilm_log`
--

DROP TABLE IF EXISTS `rig_ilm_log`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `rig_ilm_log` (
  `id` int NOT NULL AUTO_INCREMENT,
  `date` date NOT NULL,
  `rig` varchar(30) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `move_status` varchar(20) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `ilm_from_location` varchar(150) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `ilm_to_location` varchar(150) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `distance_kms` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `expected_ilm_hrs` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `during_ilm_hrs` decimal(5,2) DEFAULT NULL,
  `rig_move_extra_hrs` decimal(5,2) DEFAULT '0.00',
  `rig_move_saving_hrs` decimal(5,2) DEFAULT '0.00',
  `trailer_reported` int DEFAULT '0',
  `trailer_loss` int DEFAULT '0',
  `trailer_vendor` varchar(150) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `crane_reported` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `crane_vendor` varchar(150) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `remarks` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci,
  `created_by` varchar(60) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `trailer_reg` text COLLATE utf8mb4_unicode_ci,
  `crane_reg` text COLLATE utf8mb4_unicode_ci,
  PRIMARY KEY (`id`),
  KEY `idx_ilm_date` (`date`),
  KEY `idx_ilm_rig` (`rig`),
  KEY `idx_ilm_status` (`move_status`)
) ENGINE=InnoDB AUTO_INCREMENT=26 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `rig_ilm_log`
--

LOCK TABLES `rig_ilm_log` WRITE;
/*!40000 ALTER TABLE `rig_ilm_log` DISABLE KEYS */;
INSERT INTO `rig_ilm_log` VALUES (21,'2026-03-01','PPE-4','Active','BWP#04','BWP#01','3.8','30',30.00,0.00,0.00,11,1,'SBTC','1','ARC','','admin','2026-03-31 09:31:40','2026-03-31 09:40:46',NULL,NULL),(22,'2026-03-02','PPE-4','Active','BWP#04','BWP#01','3.8','30',NULL,0.00,0.00,11,1,'SBTC','1','ARC','CANCEL','admin','2026-03-31 09:33:30','2026-03-31 09:33:30',NULL,NULL),(23,'2026-03-08','PPE-4','Active','BWP#04','BWP#13','3.8','30',30.00,0.00,0.00,7,5,'JEET&ACC','1','ARC — ARC','','admin','2026-03-31 09:39:29','2026-03-31 09:40:21',NULL,NULL),(24,'2026-03-09','PPE-4','Active','BWP#04','BWP#13','3.8','30',NULL,0.00,0.00,15,0,'JEET & ACC & SBTCS','2','ARC & ACC','','admin','2026-03-31 09:47:11','2026-03-31 09:47:11',NULL,NULL),(25,'2026-03-10','PPE-4','Active','BWP#04','BWP#13','3.8','30',30.00,0.00,0.00,15,0,'JEET & ACC & SBTCS','2','ARC & ACC','','admin','2026-03-31 09:50:56','2026-03-31 09:50:56',NULL,NULL);
/*!40000 ALTER TABLE `rig_ilm_log` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `rigs`
--

DROP TABLE IF EXISTS `rigs`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `rigs` (
  `id` int NOT NULL AUTO_INCREMENT,
  `rig_name` varchar(30) NOT NULL,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `rig_model` varchar(80) DEFAULT NULL,
  `rig_type` varchar(50) DEFAULT NULL,
  `horse_power` int DEFAULT NULL,
  `depth_capacity` int DEFAULT NULL COMMENT 'metres',
  `year_commissioned` year DEFAULT NULL,
  `current_location` varchar(100) DEFAULT NULL,
  `rig_status` enum('Active','Standby','Breakdown','Demobilised') DEFAULT 'Active',
  `notes` text,
  PRIMARY KEY (`id`),
  UNIQUE KEY `rig_name` (`rig_name`)
) ENGINE=InnoDB AUTO_INCREMENT=8 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `rigs`
--

LOCK TABLES `rigs` WRITE;
/*!40000 ALTER TABLE `rigs` DISABLE KEYS */;
INSERT INTO `rigs` VALUES (1,'PPE-1','2026-03-15 05:27:41',NULL,NULL,NULL,NULL,NULL,NULL,'Active',NULL),(2,'PPE-2','2026-03-15 05:27:41',NULL,NULL,NULL,NULL,NULL,NULL,'Active',NULL),(3,'PPE-3','2026-03-15 05:27:41',NULL,NULL,NULL,NULL,NULL,NULL,'Active',NULL),(4,'PPE-4','2026-03-15 05:27:41',NULL,NULL,NULL,NULL,NULL,NULL,'Active',NULL),(5,'PPE-5','2026-03-15 05:27:41',NULL,NULL,NULL,NULL,NULL,NULL,'Active',NULL),(6,'PPE-6','2026-03-18 06:06:09',NULL,NULL,NULL,NULL,NULL,NULL,'Active',NULL);
/*!40000 ALTER TABLE `rigs` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `users`
--

DROP TABLE IF EXISTS `users`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `users` (
  `id` int NOT NULL AUTO_INCREMENT,
  `username` varchar(50) DEFAULT NULL,
  `password` varchar(255) DEFAULT NULL,
  `role` varchar(20) DEFAULT NULL,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `username` (`username`)
) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `users`
--

LOCK TABLES `users` WRITE;
/*!40000 ALTER TABLE `users` DISABLE KEYS */;
INSERT INTO `users` VALUES (1,'admin','$2y$10$VJNwUoIgyFu8T4W5AUsW3uylpzH7s9AVQR5E2n76PAAvkzshmwDli','admin','2026-03-13 05:43:38'),(3,'mamta','$2y$10$C3K3EpHnrV5JVi/AGzz2luabmdE34xVka91JXq7WFZl50O0RpwBQG','viewer','2026-03-14 05:15:15'),(4,'management','$2y$10$jDc5mBjyq3ljPWwvId01R.lPDwT8SvCYn9ThpltUK61g8fYlyfgTa','supervisor','2026-03-14 06:43:11');
/*!40000 ALTER TABLE `users` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `vendors`
--

DROP TABLE IF EXISTS `vendors`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `vendors` (
  `id` int NOT NULL AUTO_INCREMENT,
  `vendor_code` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `vendor_name` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `vendor_type` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `contact_person` varchar(80) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `phone` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `email` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `address` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci,
  `contract_no` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `contract_from` date DEFAULT NULL,
  `contract_to` date DEFAULT NULL,
  `rate_per_day` decimal(10,2) DEFAULT NULL,
  `status` enum('Active','Inactive') CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT 'Active',
  `notes` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `vendor_code` (`vendor_code`),
  KEY `idx_status` (`status`)
) ENGINE=InnoDB AUTO_INCREMENT=10 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `vendors`
--

LOCK TABLES `vendors` WRITE;
/*!40000 ALTER TABLE `vendors` DISABLE KEYS */;
INSERT INTO `vendors` VALUES (1,'SBTC','SBTC','Trailer',NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,'Active',NULL,'2026-03-20 07:05:33','2026-03-20 07:05:33'),(2,'ACC','ACC','Trailer,Crane,Forklift,Hydra','','','','','',NULL,NULL,NULL,'Active','','2026-03-20 07:05:33','2026-03-31 09:09:29'),(3,'JEET','JEET','Trailer',NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,'Active',NULL,'2026-03-20 07:05:33','2026-03-20 07:05:33'),(4,'ARC','ARC','Crane',NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,'Active',NULL,'2026-03-20 07:05:33','2026-03-20 07:05:33');
/*!40000 ALTER TABLE `vendors` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `well_locations`
--

DROP TABLE IF EXISTS `well_locations`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `well_locations` (
  `id` int NOT NULL AUTO_INCREMENT,
  `location` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `category` enum('BWP','AWP','MWP','NI','INTERNAL','OTHER') CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT 'OTHER',
  `block` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `district` varchar(80) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `latitude` decimal(10,6) DEFAULT NULL,
  `longitude` decimal(10,6) DEFAULT NULL,
  `status` enum('Active','Inactive') CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT 'Active',
  `notes` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `location` (`location`),
  KEY `idx_category` (`category`),
  KEY `idx_status` (`status`)
) ENGINE=InnoDB AUTO_INCREMENT=72 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `well_locations`
--

LOCK TABLES `well_locations` WRITE;
/*!40000 ALTER TABLE `well_locations` DISABLE KEYS */;
INSERT INTO `well_locations` VALUES (1,'BWP#01','BWP',NULL,NULL,NULL,NULL,'Active',NULL,'2026-03-20 07:05:33','2026-03-20 07:05:33'),(2,'BWP#02','BWP',NULL,NULL,NULL,NULL,'Active',NULL,'2026-03-20 07:05:33','2026-03-20 07:05:33'),(3,'BWP#03','BWP',NULL,NULL,NULL,NULL,'Active',NULL,'2026-03-20 07:05:33','2026-03-20 07:05:33'),(4,'BWP#04','BWP',NULL,NULL,NULL,NULL,'Active',NULL,'2026-03-20 07:05:33','2026-03-20 07:05:33'),(5,'BWP#05','BWP',NULL,NULL,NULL,NULL,'Active',NULL,'2026-03-20 07:05:33','2026-03-20 07:05:33'),(6,'BWP#06','BWP',NULL,NULL,NULL,NULL,'Active',NULL,'2026-03-20 07:05:33','2026-03-20 07:05:33'),(7,'BWP#07','BWP',NULL,NULL,NULL,NULL,'Active',NULL,'2026-03-20 07:05:33','2026-03-20 07:05:33'),(8,'BWP#08','BWP',NULL,NULL,NULL,NULL,'Active',NULL,'2026-03-20 07:05:33','2026-03-20 07:05:33'),(9,'BWP#09','BWP',NULL,NULL,NULL,NULL,'Active',NULL,'2026-03-20 07:05:33','2026-03-20 07:05:33'),(10,'BWP#10','BWP',NULL,NULL,NULL,NULL,'Active',NULL,'2026-03-20 07:05:33','2026-03-20 07:05:33'),(11,'BWP#11','BWP',NULL,NULL,NULL,NULL,'Active',NULL,'2026-03-20 07:05:33','2026-03-20 07:05:33'),(12,'BWP#12','BWP',NULL,NULL,NULL,NULL,'Active',NULL,'2026-03-20 07:05:33','2026-03-20 07:05:33'),(13,'BWP#13','BWP',NULL,NULL,NULL,NULL,'Active',NULL,'2026-03-20 07:05:33','2026-03-20 07:05:33'),(14,'BWP#14','BWP',NULL,NULL,NULL,NULL,'Active',NULL,'2026-03-20 07:05:33','2026-03-20 07:05:33'),(15,'BWP#15','BWP',NULL,NULL,NULL,NULL,'Active',NULL,'2026-03-20 07:05:33','2026-03-20 07:05:33'),(16,'AWP#01','AWP',NULL,NULL,NULL,NULL,'Active',NULL,'2026-03-20 07:05:33','2026-03-20 07:05:33'),(17,'AWP#02','AWP',NULL,NULL,NULL,NULL,'Active',NULL,'2026-03-20 07:05:33','2026-03-20 07:05:33'),(18,'AWP#03','AWP',NULL,NULL,NULL,NULL,'Active',NULL,'2026-03-20 07:05:33','2026-03-20 07:05:33'),(19,'MWP#01','MWP',NULL,NULL,NULL,NULL,'Active',NULL,'2026-03-20 07:05:33','2026-03-20 07:05:33'),(20,'MWP#02','MWP',NULL,NULL,NULL,NULL,'Active',NULL,'2026-03-20 07:05:33','2026-03-20 07:05:33'),(21,'MWP#03','MWP',NULL,NULL,NULL,NULL,'Active',NULL,'2026-03-20 07:05:33','2026-03-20 07:05:33'),(22,'MWP#04','MWP',NULL,NULL,NULL,NULL,'Active',NULL,'2026-03-20 07:05:33','2026-03-20 07:05:33'),(23,'MWP#05','MWP',NULL,NULL,NULL,NULL,'Active',NULL,'2026-03-20 07:05:33','2026-03-20 07:05:33'),(24,'MWP#06','MWP',NULL,NULL,NULL,NULL,'Active',NULL,'2026-03-20 07:05:33','2026-03-20 07:05:33'),(25,'MWP#07','MWP',NULL,NULL,NULL,NULL,'Active',NULL,'2026-03-20 07:05:33','2026-03-20 07:05:33'),(26,'MWP#08','MWP',NULL,NULL,NULL,NULL,'Active',NULL,'2026-03-20 07:05:33','2026-03-20 07:05:33'),(27,'MWP#09','MWP',NULL,NULL,NULL,NULL,'Active',NULL,'2026-03-20 07:05:33','2026-03-20 07:05:33'),(28,'MWP#10','MWP',NULL,NULL,NULL,NULL,'Active',NULL,'2026-03-20 07:05:33','2026-03-20 07:05:33'),(29,'MWP#11','MWP',NULL,NULL,NULL,NULL,'Active',NULL,'2026-03-20 07:05:33','2026-03-20 07:05:33'),(30,'MWP#12','MWP',NULL,NULL,NULL,NULL,'Active',NULL,'2026-03-20 07:05:33','2026-03-20 07:05:33'),(31,'MWP#13','MWP',NULL,NULL,NULL,NULL,'Active',NULL,'2026-03-20 07:05:33','2026-03-20 07:05:33'),(32,'NI#01','NI',NULL,NULL,NULL,NULL,'Active',NULL,'2026-03-20 07:05:33','2026-03-20 07:05:33'),(33,'NI#02','NI',NULL,NULL,NULL,NULL,'Active',NULL,'2026-03-20 07:05:33','2026-03-20 07:05:33'),(34,'NI#03','NI',NULL,NULL,NULL,NULL,'Active',NULL,'2026-03-20 07:05:33','2026-03-20 07:05:33'),(35,'INTERNAL','INTERNAL',NULL,NULL,NULL,NULL,'Active',NULL,'2026-03-20 07:05:33','2026-03-20 07:05:33');
/*!40000 ALTER TABLE `well_locations` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2026-04-01 10:58:49

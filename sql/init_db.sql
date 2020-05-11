CREATE DATABASE ufodb;
USE ufodb;

SET FOREIGN_KEY_CHECKS=0;

-- ----------------------------
-- Table structure for tbl_stat_info_detail_30m
-- ----------------------------
DROP TABLE IF EXISTS `tbl_stat_info_detail_30m`;
CREATE TABLE `tbl_stat_info_detail_30m` (
  `id` bigint(20) unsigned NOT NULL AUTO_INCREMENT,
  `uname` varchar(128) NOT NULL,
  `worker` varchar(128) NOT NULL,
  `totaldiff` decimal(32,8) NOT NULL,
  `validcount` bigint(20) DEFAULT '0',
  `invalidcount` bigint(20) DEFAULT '0',
  `periodtime` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `idx_detail_periodtime` (`periodtime`)
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8mb4;

-- ----------------------------
-- Table structure for tbl_stat_info_total_30m
-- ----------------------------
DROP TABLE IF EXISTS `tbl_stat_info_total_30m`;
CREATE TABLE `tbl_stat_info_total_30m` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `totaldiff` decimal(32,8) NOT NULL,
  `hashrate` decimal(32,8) NOT NULL,
  `validcount` bigint(20) DEFAULT NULL,
  `invalidcount` bigint(20) DEFAULT NULL,
  `periodtime` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `idx_total_periodtime` (`periodtime`)
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8mb4;
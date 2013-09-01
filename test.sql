/*
Navicat MySQL Data Transfer

Source Server         : TEST
Source Server Version : 50612
Source Host           : localhost:3306
Source Database       : gulong_xli_qq

Target Server Type    : MYSQL
Target Server Version : 50612
File Encoding         : 65001

Date: 2013-09-01 03:48:34
*/

SET FOREIGN_KEY_CHECKS=0;

-- ----------------------------
-- Table structure for `blog_user1`
-- ----------------------------
CREATE TABLE `blog_user1` (
  `user_Name` char(15) NOT NULL,
  `user_Password` char(15) NOT NULL,
  `user_emial` varchar(20) NOT NULL,
  PRIMARY KEY (`user_Name`),
  UNIQUE KEY `user_emial` (`user_emial`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- ----------------------------
-- Records of blog_user1
-- ----------------------------


/*
Navicat MySQL Data Transfer

Source Server         : TEST
Source Server Version : 50612
Source Host           : localhost:3306
Source Database       : gulong_xli_qq

Target Server Type    : MYSQL
Target Server Version : 50612
File Encoding         : 65001

Date: 2013-09-01 03:48:34
*/

SET FOREIGN_KEY_CHECKS=0;

-- ----------------------------
-- Table structure for `blog_user2`
-- ----------------------------
CREATE TABLE `blog_user2` (
  `user_Name` char(15) NOT NULL,
  `user_Password` char(15) NOT NULL,
  `user_emial` varchar(20) NOT NULL,
  PRIMARY KEY (`user_Name`),
  UNIQUE KEY `user_emial` (`user_emial`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- ----------------------------
-- Records of blog_user2
-- ----------------------------


/*
Navicat MySQL Data Transfer

Source Server         : TEST
Source Server Version : 50612
Source Host           : localhost:3306
Source Database       : gulong_xli_qq

Target Server Type    : MYSQL
Target Server Version : 50612
File Encoding         : 65001

Date: 2013-09-01 03:48:34
*/

SET FOREIGN_KEY_CHECKS=0;

-- ----------------------------
-- Table structure for `blog_user3`
-- ----------------------------
CREATE TABLE `blog_user3` (
  `user_Name` char(15) NOT NULL,
  `user_Password` char(15) NOT NULL,
  `user_emial` varchar(20) NOT NULL,
  PRIMARY KEY (`user_Name`),
  UNIQUE KEY `user_emial` (`user_emial`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- ----------------------------
-- Records of blog_user3
-- ----------------------------



-- MySQL dump 10.11
--
-- Host: localhost    Database: s3bacula
-- ------------------------------------------------------
-- Server version       5.0.32-Debian_7etch10-log

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Current Database: `s3bacula`
--

CREATE DATABASE /*!32312 IF NOT EXISTS*/ `s3bacula` /*!40100 DEFAULT CHARACTER SET utf8 */;

USE `s3bacula`;

--
-- Table structure for table `arquivos`
--

DROP TABLE IF EXISTS `arquivos`;
CREATE TABLE `arquivos` (
  `id` int(11) NOT NULL auto_increment,
  `nomearquivo` varchar(30) character set latin1 NOT NULL,
  `data` varchar(30) character set latin1 NOT NULL,
  `status` varchar(30) character set latin1 NOT NULL,
  `stacked` varchar(10) character set latin1 NOT NULL default 'no',
  PRIMARY KEY  (`id`)
) ENGINE=MyISAM AUTO_INCREMENT=4294 DEFAULT CHARSET=utf8;

--
-- Table structure for table `logging`
--

DROP TABLE IF EXISTS `logging`;
CREATE TABLE `logging` (
  `id` int(30) NOT NULL auto_increment,
  `date` varchar(30) character set latin1 NOT NULL,
  `usuario` varchar(30) character set latin1 NOT NULL,
  `operation` varchar(10) character set latin1 NOT NULL,
  `path` varchar(128) character set latin1 NOT NULL,
  `datalen` varchar(30) character set latin1 NOT NULL default 'NODATA',
  `httpcode` varchar(10) character set latin1 NOT NULL default 'NOCODE',
  PRIMARY KEY  (`id`)
) ENGINE=MyISAM AUTO_INCREMENT=15642 DEFAULT CHARSET=utf8;


--
-- Table structure for table `usuarios`
--

DROP TABLE IF EXISTS `usuarios`;
CREATE TABLE `usuarios` (
  `id` int(10) NOT NULL auto_increment,
  `login` varchar(20) character set latin1 NOT NULL,
  `senha` varchar(80) character set latin1 NOT NULL,
  `bucketname` varchar(30) character set latin1 NOT NULL default 'nimbus.linconet.com.br',
  PRIMARY KEY  (`id`)
) ENGINE=MyISAM AUTO_INCREMENT=4 DEFAULT CHARSET=utf8;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2009-08-25 14:52:23


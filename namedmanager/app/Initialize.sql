/*
SQLyog v10.2 
MySQL - 5.1.73 : Database - powerdns
*********************************************************************
*/


/*!40101 SET NAMES utf8 */;

/*!40101 SET SQL_MODE=''*/;

/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;
CREATE DATABASE /*!32312 IF NOT EXISTS*/`powerdns` /*!40100 DEFAULT CHARACTER SET utf8 */;

USE `powerdns`;

/*Data for the table `app_permission` */

insert  into `app_permission`(`id`,`pid`,`permission`) values (1,'1','add_domain'),(2,'2','add_record'),(3,'3','update_record'),(4,'4','delete_record'),(5,'5','user_manager');

/*Data for the table `app_users` */

insert  into `app_users`(`id`,`username`,`permission`) values (1,'user1','1,2,3,4,5'),(2,'user2','2'),(3,'lvzhihong','2'),(4,'user3','2');

/*Data for the table `record_type` */

insert  into `record_type`(`id`,`type`) values (1,'A'),(2,'AAAA'),(3,'CNAME'),(4,'MX'),(5,'AXFR'),(6,'NS'),(7,'PTR'),(9,'TXT');

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;


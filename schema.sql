-- MySQL Workbench Forward Engineering

SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0;
SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0;
SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='TRADITIONAL,ALLOW_INVALID_DATES';

-- -----------------------------------------------------
-- Schema mydb
-- -----------------------------------------------------
-- -----------------------------------------------------
-- Schema waterusedb
-- -----------------------------------------------------

-- -----------------------------------------------------
-- Schema waterusedb
-- -----------------------------------------------------
CREATE SCHEMA IF NOT EXISTS `waterusedb` DEFAULT CHARACTER SET utf8 ;
USE `waterusedb` ;

-- -----------------------------------------------------
-- Table `waterusedb`.`sites`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `waterusedb`.`sites` (
  `site_id` INT(11) NOT NULL,
  `site_code` VARCHAR(45) CHARACTER SET 'utf8' NULL DEFAULT NULL,
  `site_name` VARCHAR(45) CHARACTER SET 'utf8' NULL DEFAULT NULL,
  `site_lat` FLOAT NULL DEFAULT NULL,
  `site_long` FLOAT NULL DEFAULT NULL,
  `site_type` VARCHAR(45) CHARACTER SET 'utf8' NULL DEFAULT NULL,
  `site_comments` VARCHAR(45) CHARACTER SET 'utf8' NULL DEFAULT NULL,
  PRIMARY KEY (`site_id`))
ENGINE = InnoDB
DEFAULT CHARACTER SET = utf8
COLLATE = utf8_unicode_ci;


-- -----------------------------------------------------
-- Table `waterusedb`.`variable`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `waterusedb`.`variable` (
  `variable_id` INT(11) NOT NULL,
  `variable_code` VARCHAR(45) CHARACTER SET 'utf8' NULL DEFAULT NULL,
  `variable_name` VARCHAR(45) CHARACTER SET 'utf8' NULL DEFAULT NULL,
  `variable_unit` VARCHAR(45) CHARACTER SET 'utf8' NULL DEFAULT NULL,
  `variable_method` VARCHAR(45) NULL,
  PRIMARY KEY (`variable_id`))
ENGINE = InnoDB
DEFAULT CHARACTER SET = utf8
COLLATE = utf8_unicode_ci;


-- -----------------------------------------------------
-- Table `waterusedb`.`timeseries`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `waterusedb`.`timeseries` (
  `timeseries_id` INT(11) NOT NULL,
  `timeseries_utc_offset` FLOAT NULL DEFAULT NULL,
  `timeseries_begin_timestamp_utc` INT NOT NULL,
  `timeseries_end_timestamp_utc` INT NOT NULL,
  `variable_variable_id` INT(11) NOT NULL,
  `sites_site_id` INT(11) NOT NULL,
  `timeseries_dst` INT NOT NULL,
  PRIMARY KEY (`timeseries_id`),
  UNIQUE INDEX `timeseries_id_UNIQUE` (`timeseries_id` ASC),
  INDEX `fk_timeseries_variable1_idx` (`variable_variable_id` ASC),
  INDEX `fk_timeseries_sites1_idx` (`sites_site_id` ASC),
  CONSTRAINT `fk_timeseries_sites1`
    FOREIGN KEY (`sites_site_id`)
    REFERENCES `waterusedb`.`sites` (`site_id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `fk_timeseries_variable1`
    FOREIGN KEY (`variable_variable_id`)
    REFERENCES `waterusedb`.`variable` (`variable_id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB
DEFAULT CHARACTER SET = utf8
COLLATE = utf8_unicode_ci;


-- -----------------------------------------------------
-- Table `waterusedb`.`datavalue`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `waterusedb`.`datavalue` (
  `datavalue_id` INT(11) NOT NULL,
  `datavalue_value` FLOAT NOT NULL,
  `datavalue_index` INT NOT NULL,
  `datavalue_timestamp_utc` INT NOT NULL,
  `timeseries_timeseries_id` INT(11) NOT NULL,
  PRIMARY KEY (`datavalue_id`),
  UNIQUE INDEX `iddatavalue_id_UNIQUE` (`datavalue_id` ASC),
  INDEX `fk_datavalue_timeseries1_idx` (`timeseries_timeseries_id` ASC),
  CONSTRAINT `fk_datavalue_timeseries1`
    FOREIGN KEY (`timeseries_timeseries_id`)
    REFERENCES `waterusedb`.`timeseries` (`timeseries_id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB
DEFAULT CHARACTER SET = utf8
COLLATE = utf8_unicode_ci;


SET SQL_MODE=@OLD_SQL_MODE;
SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS;
SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS;

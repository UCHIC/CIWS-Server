-- MySQL Workbench Forward Engineering

SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0;
SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0;
SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='TRADITIONAL,ALLOW_INVALID_DATES';

-- -----------------------------------------------------
-- Schema mydb
-- -----------------------------------------------------

-- -----------------------------------------------------
-- Schema mydb
-- -----------------------------------------------------
CREATE SCHEMA IF NOT EXISTS `mydb` DEFAULT CHARACTER SET utf8 COLLATE utf8_unicode_ci ;
USE `mydb` ;

-- -----------------------------------------------------
-- Table `mydb`.`sites`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `mydb`.`sites` (
  `site_id` INT NOT NULL,
  `site_code` VARCHAR(45) NULL,
  `site_name` VARCHAR(45) NULL,
  `site_lat` VARCHAR(45) NULL,
  `site_long` VARCHAR(45) NULL,
  `site_type` VARCHAR(45) NULL,
  `site_comments` VARCHAR(45) NULL,
  `site_state` VARCHAR(45) NULL,
  PRIMARY KEY (`site_id`))
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `mydb`.`variable`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `mydb`.`variable` (
  `variable_id` INT NOT NULL,
  `variable_code` VARCHAR(45) NULL,
  `variable_name` VARCHAR(45) NULL,
  `variable_unit` VARCHAR(45) NULL,
  PRIMARY KEY (`variable_id`))
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `mydb`.`timeseries`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `mydb`.`timeseries` (
  `timeseries_id` INT NOT NULL,
  `timeseries_utc_offset` FLOAT NULL,
  `timeseries_begin_datatime_utc` DATETIME NULL,
  `timeseries_end_datetime_utc` DATETIME NULL,
  `variable_variable_id` INT NOT NULL,
  `sites_site_id` INT NOT NULL,
  PRIMARY KEY (`timeseries_id`),
  UNIQUE INDEX `timeseries_id_UNIQUE` (`timeseries_id` ASC),
  INDEX `fk_timeseries_variable1_idx` (`variable_variable_id` ASC),
  INDEX `fk_timeseries_sites1_idx` (`sites_site_id` ASC),
  CONSTRAINT `fk_timeseries_variable1`
    FOREIGN KEY (`variable_variable_id`)
    REFERENCES `mydb`.`variable` (`variable_id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `fk_timeseries_sites1`
    FOREIGN KEY (`sites_site_id`)
    REFERENCES `mydb`.`sites` (`site_id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `mydb`.`datavalue`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `mydb`.`datavalue` (
  `datavalue_id` INT NOT NULL,
  `datavalue_utc_offset` FLOAT NULL,
  `datavalue_datetime_utc` DATETIME NULL,
  `timeseries_timeseries_id` INT NOT NULL,
  `datavalue_value` FLOAT NULL,
  PRIMARY KEY (`datavalue_id`),
  UNIQUE INDEX `iddatavalue_id_UNIQUE` (`datavalue_id` ASC),
  INDEX `fk_datavalue_timeseries_idx` (`timeseries_timeseries_id` ASC),
  CONSTRAINT `fk_datavalue_timeseries`
    FOREIGN KEY (`timeseries_timeseries_id`)
    REFERENCES `mydb`.`timeseries` (`timeseries_id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


SET SQL_MODE=@OLD_SQL_MODE;
SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS;
SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS;


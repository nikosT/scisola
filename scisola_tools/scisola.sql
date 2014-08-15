SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0;
SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0;
SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='TRADITIONAL';

CREATE database `scisola`;

-- -----------------------------------------------------
-- Table `scisola`.`Station`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `scisola`.`Station` ;

CREATE  TABLE IF NOT EXISTS `scisola`.`Station` (
  `id` INT(11) NOT NULL ,
  `code` CHAR(8) NOT NULL ,
  `network` CHAR(8) NOT NULL ,
  `description` VARCHAR(80) NULL DEFAULT NULL ,
  `latitude` DOUBLE NOT NULL ,
  `longitude` DOUBLE NOT NULL ,
  `elevation` DOUBLE NULL DEFAULT NULL ,
  `priority` INT(11) NOT NULL DEFAULT 5 ,
  PRIMARY KEY (`id`) ,
  UNIQUE INDEX `Station_code_Station_network` (`code` ASC, `network` ASC) ,
  UNIQUE INDEX `code_UNIQUE` (`code` ASC) )
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `scisola`.`Stream`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `scisola`.`Stream` ;

CREATE  TABLE IF NOT EXISTS `scisola`.`Stream` (
  `id` INT(11) NOT NULL ,
  `Station_id` INT(11) NOT NULL ,
  `code` CHAR(3) NOT NULL ,
  `azimuth` DOUBLE NOT NULL ,
  `dip` DOUBLE NOT NULL ,
  `gain_sensor` DOUBLE NOT NULL ,
  `gain_datalogger` DOUBLE NOT NULL ,
  `norm_factor` DOUBLE UNSIGNED NOT NULL ,
  `nzeros` TINYINT UNSIGNED NOT NULL ,
  `zeros_content` BLOB NOT NULL ,
  `npoles` TINYINT UNSIGNED NOT NULL ,
  `poles_content` BLOB NOT NULL ,
  `priority` INT(11) NOT NULL DEFAULT 5 ,
  PRIMARY KEY (`id`) ,
  INDEX `fk_Stream_Station1` (`Station_id` ASC) ,
  UNIQUE INDEX `station_id_stream_code` (`Station_id` ASC, `code` ASC) ,
  CONSTRAINT `fk_Stream_Station1`
    FOREIGN KEY (`Station_id` )
    REFERENCES `scisola`.`Station` (`id` )
    ON DELETE CASCADE
    ON UPDATE CASCADE)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `scisola`.`Origin`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `scisola`.`Origin` ;

CREATE  TABLE IF NOT EXISTS `scisola`.`Origin` (
  `id` INT NOT NULL AUTO_INCREMENT ,
  `timestamp` VARCHAR(255) NOT NULL ,
  `description` VARCHAR(255) NULL DEFAULT NULL ,
  `datetime` VARCHAR(255) NOT NULL ,
  `magnitude` DOUBLE NOT NULL ,
  `latitude` DOUBLE NOT NULL ,
  `longitude` DOUBLE NOT NULL ,
  `depth` DOUBLE NOT NULL ,
  `automatic` TINYINT(1) NOT NULL ,
  `results_dir` VARCHAR(255) NOT NULL ,
  PRIMARY KEY (`id`) ,
  UNIQUE INDEX `timestamp_UNIQUE` (`timestamp` ASC) )
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `scisola`.`Event`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `scisola`.`Event` ;

CREATE  TABLE IF NOT EXISTS `scisola`.`Event` (
  `id` VARCHAR(255) NOT NULL ,
  `Origin_id` INT NOT NULL ,
  CONSTRAINT `fk_Event_Origin1`
    FOREIGN KEY (`Origin_id` )
    REFERENCES `scisola`.`Origin` (`id` )
    ON DELETE CASCADE
    ON UPDATE CASCADE)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `scisola`.`Moment_Tensor`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `scisola`.`Moment_Tensor` ;

CREATE  TABLE IF NOT EXISTS `scisola`.`Moment_Tensor` (
  `cent_shift` INT NOT NULL ,
  `cent_time` DOUBLE NOT NULL ,
  `cent_latitude` DOUBLE NOT NULL ,
  `cent_longitude` DOUBLE NOT NULL ,
  `cent_depth` DOUBLE NOT NULL ,
  `correlation` DOUBLE NOT NULL ,
  `var_reduction` DOUBLE NOT NULL ,
  `mw` DOUBLE NOT NULL ,
  `mrr` DOUBLE NOT NULL ,
  `mtt` DOUBLE NOT NULL ,
  `mpp` DOUBLE NOT NULL ,
  `mrt` DOUBLE NOT NULL ,
  `mrp` DOUBLE NOT NULL ,
  `mtp` DOUBLE NOT NULL ,
  `vol` DOUBLE NOT NULL ,
  `dc` DOUBLE NOT NULL ,
  `clvd` DOUBLE NOT NULL ,
  `mo` DOUBLE NOT NULL ,
  `strike` DOUBLE NOT NULL ,
  `dip` DOUBLE NOT NULL ,
  `rake` DOUBLE NOT NULL ,
  `strike_2` DOUBLE NOT NULL ,
  `dip_2` DOUBLE NOT NULL ,
  `rake_2` DOUBLE NOT NULL ,
  `p_azm` DOUBLE NOT NULL ,
  `p_plunge` DOUBLE NOT NULL ,
  `t_azm` DOUBLE NOT NULL ,
  `t_plunge` DOUBLE NOT NULL ,
  `b_azm` DOUBLE NOT NULL ,
  `b_plunge` DOUBLE NOT NULL ,
  `minSV` DOUBLE NOT NULL ,
  `maxSV` DOUBLE NOT NULL ,
  `CN` DOUBLE NOT NULL ,
  `stVar` DOUBLE NOT NULL ,
  `fmVar` DOUBLE NOT NULL ,
  `frequency_1` DOUBLE NOT NULL ,
  `frequency_2` DOUBLE NOT NULL ,
  `frequency_3` DOUBLE NOT NULL ,
  `frequency_4` DOUBLE NOT NULL ,
  `Origin_id` INT NOT NULL ,
  PRIMARY KEY (`Origin_id`) ,
  CONSTRAINT `fk_Moment_Tensor_Origin1`
    FOREIGN KEY (`Origin_id` )
    REFERENCES `scisola`.`Origin` (`id` )
    ON DELETE CASCADE
    ON UPDATE CASCADE)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `scisola`.`Stream_Contribution`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `scisola`.`Stream_Contribution` ;

CREATE  TABLE IF NOT EXISTS `scisola`.`Stream_Contribution` (
  `streamNetworkCode` CHAR(8) NOT NULL ,
  `streamStationCode` CHAR(8) NOT NULL ,
  `streamCode` CHAR(3) NOT NULL ,
  `var_reduction` DOUBLE NOT NULL ,
  `mseed_path` VARCHAR(255) NOT NULL ,
  `Origin_id` INT NOT NULL ,
  CONSTRAINT `fk_Stream_Contribution_Origin1`
    FOREIGN KEY (`Origin_id` )
    REFERENCES `scisola`.`Origin` (`id` )
    ON DELETE CASCADE
    ON UPDATE CASCADE)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `scisola`.`Settings`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `scisola`.`Settings` ;

CREATE  TABLE IF NOT EXISTS `scisola`.`Settings` (
  `id` INT NOT NULL ,
  `timestamp` TIMESTAMP NOT NULL ,
  `center_latitude` DOUBLE NOT NULL ,
  `center_longitude` DOUBLE NOT NULL ,
  `distance_range` INT NOT NULL ,
  `magnitude_threshold` DOUBLE NOT NULL ,
  `min_sectors` INT NOT NULL ,
  `stations_per_sector` INT NOT NULL ,
  `sources` INT NOT NULL ,
  `source_step` INT NOT NULL ,
  `clipping_threshold` DOUBLE NOT NULL ,
  `time_grid_start` INT NOT NULL ,
  `time_grid_step` INT NOT NULL ,
  `time_grid_end` INT NOT NULL ,
  `watch_interval` INT NOT NULL ,
  `process_delay` INT NOT NULL ,
  `process_timeout` INT NOT NULL ,
  `crustal_model_path` VARCHAR(255) NOT NULL ,
  `output_dir` VARCHAR(255) NOT NULL ,
  `isola_path` VARCHAR(255) NOT NULL ,
  `sc3_path` VARCHAR(255) NOT NULL ,
  `sc3_scevtls` VARCHAR(255) NOT NULL ,
  `sc3_scxmldump` VARCHAR(255) NOT NULL ,
  `seedlink_path` VARCHAR(255) NOT NULL ,
  `seedlink_host` VARCHAR(255) NOT NULL ,
  `seedlink_port` INT NOT NULL ,
  PRIMARY KEY (`id`) )
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `scisola`.`Distance_selection`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `scisola`.`Distance_selection` ;

CREATE  TABLE IF NOT EXISTS `scisola`.`Distance_selection` (
  `min_magnitude` DOUBLE NOT NULL ,
  `max_magnitude` DOUBLE NOT NULL ,
  `min_distance` INT NOT NULL ,
  `max_distance` INT NOT NULL ,
  `Settings_id` INT NOT NULL ,
  CONSTRAINT `fk_Distance_selection_Settings1`
    FOREIGN KEY (`Settings_id` )
    REFERENCES `scisola`.`Settings` (`id` )
    ON DELETE CASCADE
    ON UPDATE CASCADE)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `scisola`.`Inversion_time`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `scisola`.`Inversion_time` ;

CREATE  TABLE IF NOT EXISTS `scisola`.`Inversion_time` (
  `min_magnitude` DOUBLE NOT NULL ,
  `max_magnitude` DOUBLE NOT NULL ,
  `tl` DOUBLE NOT NULL ,
  `Settings_id` INT NOT NULL ,
  CONSTRAINT `fk_Inversion_time_Settings1`
    FOREIGN KEY (`Settings_id` )
    REFERENCES `scisola`.`Settings` (`id` )
    ON DELETE CASCADE
    ON UPDATE CASCADE)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `scisola`.`Inversion_frequency`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `scisola`.`Inversion_frequency` ;

CREATE  TABLE IF NOT EXISTS `scisola`.`Inversion_frequency` (
  `min_magnitude` DOUBLE NOT NULL ,
  `max_magnitude` DOUBLE NOT NULL ,
  `frequency_1` DOUBLE NOT NULL ,
  `frequency_2` DOUBLE NOT NULL ,
  `frequency_3` DOUBLE NOT NULL ,
  `frequency_4` DOUBLE NOT NULL ,
  `Settings_id` INT NOT NULL ,
  CONSTRAINT `fk_Inversion_frequency_Settings1`
    FOREIGN KEY (`Settings_id` )
    REFERENCES `scisola`.`Settings` (`id` )
    ON DELETE CASCADE
    ON UPDATE CASCADE)
ENGINE = InnoDB;



SET SQL_MODE=@OLD_SQL_MODE;
SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS;
SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS;

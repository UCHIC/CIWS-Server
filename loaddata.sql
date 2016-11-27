-- Connect to database
USE waterusedb;

-- Insert data into sites
INSERT INTO `sites` (`site_id`,`site_code`,`site_name`,`site_lat`, `site_long`, `site_type`, `site_comments`, `site_dst`)              
VALUES (1, 'LLC_A', 'Living and Learning Center', 35, 111, 'hot', 'None', 0);

-- Insert data into variable
INSERT INTO `variable` (`variable_id`, `variable_code`, `variable_name`, `variable_unit`, `variable_method`)
VALUES (1, 'inst_water_vol', 'water usage', 'gal/min', '4-20mA reading using Raspberry Pi');

-- Insert data into timeseries
INSERT INTO `timeseries` (`timeseries_id`, `timeseries_utc_offset`, `timeseries_begin_datetime_utc`, `timeseries_begin_datetime_local`, `timeseries_end_datetime_utc`, `timeseries_end_datetime_local`, `variable_variable_id`, `sites_site_id`)
VALUES (1, -7, '2016-11-10 00:00:00', '2016-11-09 17:00:00', '2016-11-10 00:05:00', '2016-11-09 17:05:00', 1, 1);
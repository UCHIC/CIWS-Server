-- Connect to database
USE waterusedb;

-- Insert data into sites
INSERT INTO `sites` (`site_id`,`site_code`,`site_name`,`site_lat`, `site_long`, `site_type`, `site_comments`)              
VALUES (1, 'LLC_A', 'Living and Learning Center', 35, 111, 'hot', 'None');

-- Insert data into variable
INSERT INTO `variable` (`variable_id`, `variable_code`, `variable_name`, `variable_unit`, `variable_method`)
VALUES (1, 'inst_water_vol', 'water usage', 'gal/min', '4-20mA reading using Raspberry Pi');

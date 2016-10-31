#Import necessary modules
import pymysql.cursors
import json
from bson import json_util

serverconfig = json.load(open('serverconfig.json'))

#Write water usage data to timeseries table in db
def writewaterusagedb(timeseries_id, timeseries_utc_offset, timeseries_begin_datetime_utc, timeseries_end_datetime_utc, timeseries_datavalues, variable_id, site_id):
    #Open connection to db
    connection = pymysql.connect(host=serverconfig["server_db_host"],
                             user=serverconfig["server_db_user"],
                             password=serverconfig["server_db_pwd"],
                             db=serverconfig["server_db_name"],
                             charset=serverconfig["server_db_charset"],
                             cursorclass=pymysql.cursors.DictCursor)
    try:
        with connection.cursor() as cursor:
            # Create a new record
            sql = "INSERT INTO `timeseries` (`timeseries_id`, `timeseries_utc_offset`," + \
                  "`timeseries_begin_datetime_utc`, `timeseries_end_datetime_utc`, `variable_variable_id`," + \
                  " `sites_site_id`) VALUES (%s, %s, %s, %s, %s, %s)"
            cursor.execute(sql, (timeseries_id, timeseries_utc_offset, timeseries_begin_datetime_utc, timeseries_end_datetime_utc, variable_id, site_id))
            
            # connection is not autocommit by default. So you must commit to save
            # your changes.
            connection.commit()
            
    finally:
        connection.close()       

#Read all water usage timeseries data 
def readwaterusagedb():        
    #Open connection to db
    connection = pymysql.connect(host=serverconfig["server_db_host"],
                             user=serverconfig["server_db_user"],
                             password=serverconfig["server_db_pwd"],
                             db=serverconfig["server_db_name"],
                             charset=serverconfig["server_db_charset"],
                             cursorclass=pymysql.cursors.DictCursor)
    try:
        with connection.cursor() as cursor:
            sql = "SELECT * FROM `timeseries`"
            cursor.execute(sql)
            result = cursor.fetchall()

    finally:
        connection.close()
    
    result = json.dumps(result, default = json_util.default)
    return result

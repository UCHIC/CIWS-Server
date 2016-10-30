#Import necessary modules
import pymysql.cursors
import json

serverconfig = json.load(open('serverconfig.json'))

#Write water usage data to timeseries table in db
def waterusagedb(timeseries_id, timeseries_utc_offset, timeseries_begin_datetime_utc, timeseries_end_datetime_utc, variable_id, site_id):
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

#Read water usage data 
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
            # Read a recod. TODO write sql query
            #sql = "SELECT `id`, `password` FROM `timeseries` WHERE `email`=%s"
            #cursor.execute(sql, ('webmaster@python.org',))
            #result = cursor.fetchone()
            #print(result)
            print "TODO, not yet implemented"

    finally:
        connection.close()

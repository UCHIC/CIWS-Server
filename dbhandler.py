#Import necessary modules
import pymysql.cursors
import json
from bson import json_util

serverconfig = json.load(open('serverconfig.json'))

#Write water usage data to timeseries table in db
def writewaterusagedb(timeseries_id, timeseries_utc_offset, timeseries_begin_timestamp_utc, timeseries_end_timestamp_utc, timeseries_datavalue, timeseries_variable_id, timeseries_site_id, timeseries_dst):
    #Open connection to db
    connection = pymysql.connect(host=serverconfig["server_db_host"],
                             user=serverconfig["server_db_user"],
                             password=serverconfig["server_db_pwd"],
                             db=serverconfig["server_db_name"],
                             charset=serverconfig["server_db_charset"],
                             cursorclass=pymysql.cursors.DictCursor)
    try:
        with connection.cursor() as cursor:
            # Create a new timeseries record
            sql = "INSERT INTO `timeseries` (`timeseries_id`, `timeseries_utc_offset`," + \
                  "`timeseries_begin_timestamp_utc`, `timeseries_end_timestamp_utc`, `timeseries_dst`, `variable_variable_id`," + \
                  " `sites_site_id`) VALUES (%s, %s, %s, %s, %s, %s, %s)"
            cursor.execute(sql, (timeseries_id, timeseries_utc_offset, timeseries_begin_timestamp_utc, timeseries_end_timestamp_utc, timeseries_dst, timeseries_variable_id, timeseries_site_id))
            
            # Create new datavalue records
            timeseries_datavalue_id = []
            timeseries_datavalue_value = []
            timeseries_datavalue_index = []
            timeseries_datavalue_timestamp_utc = [] 
            for datavalue in timeseries_datavalue:
                timeseries_datavalue_id.append(datavalue['timeseries_datavalue_id'])
                timeseries_datavalue_value.append(datavalue['timeseries_datavalue_value'])
                timeseries_datavalue_index.append(datavalue['timeseries_datavalue_index'])
                timeseries_datavalue_timestamp_utc.append(datavalue['timeseries_datavalue_timestamp_utc'])            
            
            print timeseries_datavalue_id, timeseries_datavalue_value, timeseries_datavalue_index, timeseries_datavalue_timestamp_utc
 
            #Assuming only 2 datavalues per timeseries
            sql = "INSERT INTO `datavalue` (`datavalue_id`, `datavalue_value`, `datavalue_index`," + \
                  " `datavalue_timestamp_utc`, `timeseries_timeseries_id`) VALUES (%s, %s, %s, %s, %s)," + \
                  " (%s, %s, %s, %s, %s)"

            cursor.execute(sql, (timeseries_datavalue_id[0], timeseries_datavalue_value[0], timeseries_datavalue_index[0], timeseries_datavalue_timestamp_utc[0], timeseries_id, timeseries_datavalue_id[1], timeseries_datavalue_value[1], timeseries_datavalue_index[1], timeseries_datavalue_timestamp_utc[1], timeseries_id))

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

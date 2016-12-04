#Import necessary modules
import pymysql.cursors
import json
from bson import json_util

serverconfig = json.load(open('serverconfig.json'))

#Write water usage data to timeseries table in db
def writewaterusedb(datavalues, timeseries_id):
    #Open connection to db
    connection = pymysql.connect(host=serverconfig["server_db_host"],
                             user=serverconfig["server_db_user"],
                             password=serverconfig["server_db_pwd"],
                             db=serverconfig["server_db_name"],
                             charset=serverconfig["server_db_charset"],
                             cursorclass=pymysql.cursors.DictCursor)
    try:
        with connection.cursor() as cursor:
            # TODO: Update timeseries record with begin end time
            
            # Create new datavalue records 
            datavalue_value = []
            datavalue_datetime_local = []
            for datavalue in datavalues:
                datavalue_value.append(datavalue['datavalue_value'])
                datavalue_datetime_local.append(datavalue['datavalue_datetime_local'])
            print datavalue_value, datavalue_datetime_local 
 
            #Assuming only 2 datavalues per object
            sql = "INSERT INTO `datavalue` (`datavalue_value`, `datavalue_datetime_local`, `timeseries_timeseries_id`) VALUES (%s, %s, %s), (%s, %s, %s)"
            cursor.execute(sql, (datavalue_value[0], datavalue_datetime_local[0], timeseries_id, datavalue_value[1], datavalue_datetime_local[1], timeseries_id))

            # connection is not autocommit by default. So you must commit to save
            # your changes.
            connection.commit()
            
    finally:
        connection.close()       

#Read water use datavalues for a particular timeserie 
def readwaterusedatavalues(timeseries_id):        
    #Open connection to db
    connection = pymysql.connect(host=serverconfig["server_db_host"],
                             user=serverconfig["server_db_user"],
                             password=serverconfig["server_db_pwd"],
                             db=serverconfig["server_db_name"],
                             charset=serverconfig["server_db_charset"],
                             cursorclass=pymysql.cursors.DictCursor)
    try:
        with connection.cursor() as cursor:
            sql = "SELECT * FROM `datavalue` WHERE `timeseries_timeseries_id` = %s"
            cursor.execute(sql, (timeseries_id))
            result = cursor.fetchall()

    finally:
        connection.close()
    
    result = json.dumps(result, default = json_util.default)
    return result

#Read sites
def readsites():
    #Open connection to db
    connection = pymysql.connect(host=serverconfig["server_db_host"],
                             user=serverconfig["server_db_user"],
                             password=serverconfig["server_db_pwd"],
                             db=serverconfig["server_db_name"],
                             charset=serverconfig["server_db_charset"],
                             cursorclass=pymysql.cursors.DictCursor)
    try:
        with connection.cursor() as cursor:
            sql = "SELECT * FROM `sites`"
            cursor.execute(sql)
            result = cursor.fetchall()

    finally:
        connection.close()

    result = json.dumps(result, default = json_util.default)
    return result

#Read timeseries
def readtimeseries():
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

#Read variable
def readvariable():
    #Open connection to db
    connection = pymysql.connect(host=serverconfig["server_db_host"],
                             user=serverconfig["server_db_user"],
                             password=serverconfig["server_db_pwd"],
                             db=serverconfig["server_db_name"],
                             charset=serverconfig["server_db_charset"],
                             cursorclass=pymysql.cursors.DictCursor)
    try:
        with connection.cursor() as cursor:
            sql = "SELECT * FROM `variable`"
            cursor.execute(sql)
            result = cursor.fetchall()

    finally:
        connection.close()

    result = json.dumps(result, default = json_util.default)
    return result

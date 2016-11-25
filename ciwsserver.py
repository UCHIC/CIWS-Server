from bottle import request, post, get, run 
import json
from gevent import monkey;
monkey.patch_all()

#import serverconfig file and its parameters
serverconfig = json.load(open('serverconfig.json'))
server_ip = serverconfig["server_ip"]
server_port = serverconfig["server_port"]

#module to save building json data to db
import dbhandler

@post('/rpiminute')
def rpiminute():
    #endoint to receive rpi json and write to local db
    try:
        timeseries_id = request.json['timeseries_id']
        datavalues = request.json['datavalues']
        dbhandler.writewaterusedb(datavalues, timeseries_id)
        return "Water usage data received!"
    
    except Exception as e: 
        print e, type(e), e.args
        return "No data received!"

@get('/all')
def getall():
    #endpoint to fetch all data
    alldata = dbhandler.readwaterusagedb()
    print alldata
    return alldata

@get('/daily')
def getdaily():
    #endoint to send daily water usage stats as json 
    return "Daily data!"

@get('/weekly')
def getweekly():
    #endpoint to send weekly water usage stats as json
    return "Weekly data!"

@get('/monthly')
def getmonthly():
    #endpoint to send monthly water usage stats as json
    return "Monthly data!"

if __name__ == '__main__':
    run(host=server_ip, port=server_port, server = 'gevent', debug=True)

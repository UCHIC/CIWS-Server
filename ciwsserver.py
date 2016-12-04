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
        print timeseries_id, datavalues
        dbhandler.writewaterusedb(datavalues, timeseries_id)
        return "Water usage data received!"
    
    except Exception as e: 
        print e, type(e), e.args
        return "No data received!"

@get('/datavalues/<timeseries_id:int>')
def getdatavalues(timeseries_id):
    #endpoint to send datavalues for a particular timeseries
    datavalues = dbhandler.readwaterusedatavalues(timeseries_id)
    print datavalues
    return datavalues

@get('/sites')
def getsites():
    #endoint to send all sites attributes as json 
    sites = dbhandler.readsites()
    print sites
    return sites

@get('/timeseries')
def gettimeseries():
    #endpoint to send all timeseries attributes as json
    timeseries = dbhandler.readtimeseries()
    print timeseries
    return timeseries

@get('/variable')
def getvariable():
    #endpoint to send all variable attributes as json
    variable = dbhandler.readvariable()
    print variable
    return variable


if __name__ == '__main__':
    run(host=server_ip, port=server_port, server = 'gevent', debug=True)

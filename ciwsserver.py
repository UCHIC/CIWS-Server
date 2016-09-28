from bottle import request, post, get, run 
import json

#import serverconfig file
serverconfig = json.load(open('serverconfig.json'))
server_ip = serverconfig["server_ip"]
server_port = serverconfig["server_port"]


#module to save building json data to db
import dbhandler

@post('/rpiminute')
def rpiminute():
	#endoint to receive rpi json and write to local db
	buildingid = request.json['buildingid']
	water_usage_inst = request.json['water_usage_inst']
	waterusagedb(buildingid, water_usage_inst)
	return "Data received!"

@get('/daily')
def getdaily():
	#endoint to send daily water usage stats as json
	#parse input for building id
	#function(buildingid,dailytag) 
	return "Daily data!"

@get('/weekly')
def getweekly():
	#endpoint to send weekly water usage stats as json
	return "Weekly data!"

@get('/monthly')
def getmonthly():
	#endpoint to send monthly water usage stats as json
	return "Monthly data!"


run(host=server_ip, port=server_port, debug=True) 


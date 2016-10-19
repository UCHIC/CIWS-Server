from flask import Flask, request
import json
import requests

app = Flask(__name__)

#import serverconfig file
serverconfig = json.load(open('serverconfig.json'))
server_ip = serverconfig["server_ip"]
server_port = serverconfig["server_port"]

#module to save building json data to db
import dbhandler


@app.route('/rpiminute', methods = ['POST'])
def rpiminute():
	#endpoinat to receive water usage json data and write to local db
	return "Data received!"

@app.route('/daily', methods = ['GET'])
def getdaily():
	#endoint to send daily water usage stats as json
	return "Daily data!"

@app.route('/weekly', methods = ['GET'])
def getweekly():
	#endpoint to send weekly water usage stats as json
	return "Weekly data!"

@app.route('/monthly', methods = ['GET'])
def getmonthly():
	#endpoint to send monthly water usage stats as json
	return "Monthly data!"

@app.route('/')
def hello():
    return 'Hello World'


if __name__ == '__main__':
    #run(host=server_ip, port=server_port, debug=True) 
    app.run(host = server_ip, port = server_port)


###Simple script to pull datavalues for a particular script and create a time series plot

import requests
import json
import datetime
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

getdatavalues_api = requests.get('http://54.191.109.25:8080/datavalues/2') #Replace URL with your server public IP
datavalues = getdatavalues_api.json()

datavalue_value = []
datavalue_timestamp =[]

[datavalue_value.append(x['datavalue_value']) for x in datavalues]
[datavalue_timestamp.append(x['datavalue_datetime_local']['$date']) for x in datavalues]

datavalue_datetime=[datetime.datetime.utcfromtimestamp(timestamp/ 1e3) for timestamp in datavalue_timestamp]

plt.title("Water use at Richards Hall")
plt.ylabel("Water use, gallons per minute")
plt.xlabel("Local datetime")
plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%m/%d/%Y'))
plt.plot(datavalue_datetime, datavalue_value, 'b-')
plt.gcf().autofmt_xdate()
plt.show()
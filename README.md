Cyberinfrastructure for Intelligent Water Supply (CIWS) 

CIWS is an end to end system for residential water consumption data collection, processing and analysis. This repository contains code for a back-end database and web service related to an implementation in USU's students residential buildings. These buildings are fitted with a water meter that has an external 4-20mA output whose voltage varies depending on instantaneous water use.

A high level system architecture diagram is as follows: 
![alt tag](https://github.com/UCHIC/ciws-server/blob/master/figs/CIWS_server_fig.png)

## Design decisions
The back-end service is currently Python based. For now, we have decided to go with a microframework instead of macro, full stack frameworks like Django, because of its simplicity and ease to add/ switch components. We chose Bottle over Flask due to its single file approach and zero dependencies. This can be replaced if necessary in the future. The Bottle app is served through Gevent, an aysnchronous server which can handle multiple connections. Back-end information will be exposed using a simple RESTful API though Bottle.

MySQL db, a popular relational database management system, is currently used to manage and store data. The database schema is as follows:
![alt tag] (https://github.com/UCHIC/ciws-server/blob/master/figs/ciws_campus_db_ER.png)

## Implementation
A Python MySQL client library, PyMySQL was used to create, write and read data to the database. This codebase can be cloned to your local machine or a cloud server instance such as AWS EC2, within a Linux environment.

The server is currently expecting water use pushes every minute in a JSON format. This JSON would contain timeseries_id and two datavalues and local date time objects. Each of these datavalue is an average of instantaneous water use measured over 30s.

### File overview
serverconfig.json: JSON file with server and database parameters
schema.sql: SQL script to create a database
loaddata.sql: SQL script to pre load sites, variables and timeseries attributes
ciwsserver.py: Python script with API endpoints definition
dbhandler.py: Python script to write and read database

## Development
Test changes on a local machine (localhost).

## Deployment
Pull this repository code to your server. Create a copy of serverconfig_proto.json and rename to serverconfig.json with your instance details. Start the server by running ciwsserver.py

## Contribution
Fork and branch gitflow.

## Credits

This work was supported by National Science Foundation Grant [1552444](https://www.nsf.gov/awardsearch/showAward?AWD_ID=1552444). Any opinions, findings, and conclusions or recommendations expressed in this material are those of the author(s) and do not necessarily reflect the views of the National Science Foundation.


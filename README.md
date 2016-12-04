Cyberinfrastructure for Intelligent Water Supply (ciws) is an end to end system for residential water consumption data collection, processing and analysis. It primarily has three components, namely ciws-node (data collection with raspberry pi), ciws-server (back-end) and ciws-client (website/ mobile app).

# ciws-campus-server
This repository will hold server code and files related to a ciws implementation in USU's Living and Learning Centre housing facility. <br />
A high level system architecture diagram is as follows: 
![alt tag](https://github.com/UCHIC/ciws-server/blob/master/figs/CIWS_server_fig.png)

## Design decisions
The back-end service will be Python based. We decided to go with a microframework instead of macro, full stack frameworks like Django, because of its simplicity and ease to add/ switch components. We chose Bottle over Flask due to its single file approach and zero dependencies. Currenly, the web app is served through the defualt Bottle server which is not production ready. We will change it to servers like Tornado or Twisted that can support async methods and web sockets. <br />
MySQL db, a popular relational database management system, will manage and store data. A Python MySQL client library such as PyMySQl will be used to create, write and read data to the database. <br />
Back-end information will be exposed using a simple RESTful API though Bottle.

## Development
Test changes on a local machine (localhost).

## Deployment
Pull this repository code to your server and change serverconfig.json details.

## Contribution
Fork and branch gitflow.


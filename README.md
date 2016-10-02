Cyberinfrastructure for Intelligent Water Supply (ciws) is an end to end system for residential water consumption data collection, processing and analysis. It primarily has three components, namely ciws-node (data collection), ciws-server (back-end) and ciws-client (website/ mobile app).

# ciws-server
The back-end server, web service and analysis code reside in this repository. <br />
A high level system architecture diagram is as follows: 
![alt tag](https://github.com/UCHIC/ciws-server/blob/master/figs/CIWS_server_fig.png)

## Design decisions
The back-end service will be Python based. We decided to go with a microframework instead of macro, full stack frameworks like Django, because of its simplicity and ease to add/ switch components. We chose Bottle over Flask due to its single file approach and zero dependencies. If things get messy as we move forward, we will switch to favourable frameworks. HTTP requests method will be used as the data exchange mechanism. Long term, it will ideally be through web sockets which would mandate use of frameworks like Tornado or Twisted for asynchronous methods. <br />
We chose MongoDB, a popular NoSQL option over SQL because of its flexibility and scalability. <br />
Back-end information will be exposed using a simple RESTful API though Bottle.

## Development
Test changes on a local machine (localhost).

## Deployment
Pull this repository code to your server and change serverconfig.json details.

## Contribution
Fork and branch gitflow.


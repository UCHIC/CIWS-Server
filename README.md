Cyberinfrastructure for Intelligent Water Supply (ciws) is an end to end system for residential water consumption data collection, processing and analysis. It primarily has three components, namely ciws-node (data collection), ciws-server (back-end) and ciws-client (website/ mobile app).

# ciws-server
The back-end server, web service and analysis code reside in this repository. <br />
A high level system architecture diagram is as follows: 
![alt tag](https://github.com/UCHIC/ciws-server/blob/master/figs/CIWS_server_fig.png)

## Design decisions
The back-end service will be Python based. We decided to go with a microframework instead of a macro, full stack framework like Django, because of its simplicity and ease to add/ switch components. We chose Flask over Bottle due to its larger documentation, community and support. The Flask app's default server only handles synchronous requests which is not production ready. We will change it to servers like Twisted or Tornado that can support async and web sockets.  <br />
We chose MongoDB, a popular NoSQL option over SQL because of its flexibility and scalability. <br />
Back-end information will be exposed using the Flask RESTful API.

## Development
Test changes on a local machine (localhost).

## Deployment
Pull this repository code to your server and change serverconfig.json details.

## Contribution
Fork and branch gitflow.


## Cyberinfrastructure for Intelligent Water Supply (CIWS) 

CIWS is a project funded by the U.S. National Science Foundation to develop cyberinfrastructure for smart water metering and high resolution water-use data collection. We are developing systems for high resolution residential water consumption data collection, processing and analysis.

This repository contains source code for back-end database, data loaders, and web service functionality for smart water metering data management. Some of this work is being prototyped using an implementation in Utah State University's student residential buildings. These buildings are fitted with a water meter that has an external 4-20mA output whose voltage varies depending on instantaneous water use.



### Deploying

- **1** :Clone repo to desired directory: 
``` git clone https://github.com/UCHIC/CIWS-Server ```

- **2** Create conda environment
``` conda create --name %name python=3.6 ```

- **3** Activate conda environment and install requirements
``` 
activate %name 
pip install -r requirements.txt
```

- **4** create a settings.json file in src/ follow the template below:

        {
        "secret_key": "%secretkey",
        "hosts":[
            {
            "hostname": "%hostname"
            },
            {
            "hostname": "%hostname"
            },
            {
            "hostname": "%hostname"
            }

        ],
        "local":{

            "target": "%path to local data_target",
            "source": "path to local data_source"
        }  
        ,
        "database":
            {
            "name": "%dbname",
            "schema": "%schema",
            "engine": "%dbengine",
            "user": "%dbuser",
            "password": "%dbuser_password",
            "host": "%db_hostname",
            "port": "%db_port (Note, port is 8086 for influxdb)",
            "measurement": "%measurement_name for multi_remote_source mode"
            },

        "sshinfo":{
            "username": "%ssh username for remote device",
            "password": "%PW for remote device"
        },
        "testDateBegin" : "'%datetime for return_flow_script start'",
        "testDateEnd" : "'%datetime for return_flow_script end'",
        "target": "%target for return_flow script",
        "slack_webhook": "%webhook url"
        }


- **5** Set up cronjob
```
crontab -e
```  
Then insert this line
```
0 0 * * * /home/eli/anaconda3/envs/ciwsconda/bin/python /opt/ciws/CIWS-Server/src/main.py
```  
In this line, it says: 
"Run script located at /opt/ciws/CIWS-Server/src/main.py 
using python executable located at: /home/eli/anaconda3/envs/ciwsconda/bin/python 
at time: 0 0 * * *" (The time meaning, 0 seconds, 0 hours(midnight), every day, every week, every month)

- **6** Troubleshooting
If you are having troubles setting up the cronjob, ensure that the folders and files are owned by the user running the cronjob. i.e. make sure the folders and files are owned by elijah, not root. 




### Sponsors and Credits
[![NSF-1552444](https://img.shields.io/badge/NSF-1552444-blue.svg)](https://nsf.gov/awardsearch/showAward?AWD_ID=1552444)

This work was supported by National Science Foundation Grant [CBET 1552444](https://www.nsf.gov/awardsearch/showAward?AWD_ID=1552444). Any opinions, findings, and conclusions or recommendations expressed in this material are those of the author(s) and do not necessarily reflect the views of the National Science Foundation.

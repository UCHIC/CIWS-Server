# CIWS-Server
## Deployment Guide for Ubuntu with GUnicorn and NGINX.
This guide is an adaptation of DigitalOcean's guide on [how to install a Flask web application on Ubuntu](https://www.digitalocean.com/community/tutorials/how-to-serve-flask-applications-with-gunicorn-and-nginx-on-ubuntu-20-04).

In this guide, we will demonstrate how to install and configure the CIWS Server scripts and web application. We will configure the Gunicorn application as an interface to the CIWS Server application, translating client requests from HTTP to Python calls that our application can process. We will then set up Nginx in front of Gunicorn to take advantage of its high performance connection handling mechanisms and its easy-to-implement security features.

### Prerequisites
To follow this guide, you should have a Ubuntu 18.04+ server instance, a Python 3.6 installation, and have an InfluxDB instance running either locally or remotely. If you want to install InfluxDB locally, you can follow [this guide](https://computingforgeeks.com/install-influxdb-on-ubuntu-and-debian/) or see the [official documentation](https://docs.influxdata.com/influxdb/v2.0/get-started/) on how to install and configure.

### Installing the required packages from the Ubuntu repository
```
$ sudo apt update
$ sudo apt install python3-pip python3-dev nginx curl
```

### Creating the InfluxDB Database
First we open the Influx Command Line Interface by typing
```
$ influx
```

Then, when the Influx Command Line Interface opens, we create the database that will hold all the data

```
> CREATE DATABASE ciwsdb
```

We also create a user that will be used to interact with the database
```
> CREATE USER ciws_user WITH PASSWORD '<password>' WITH ALL PRIVILEGES
```

When we are done creating the database and the user, exit the Influx Command Line Interface
```
> exit
```

### Creating a Python virtual environment for the project
We will be installing our Python requirements within a virtual environment for easier management.
To do this, we first need access to the virtualenv command. We can install if by upgrading and getting the package with `pip`.
```
$ sudo -H pip3 install --upgrade pip
$ sudo -H pip3 install virtualenv
```

We can now create a project directory where we are going to keep the project files
```
$ mkdir ~/ciws
$ cd ~/ciws
```

Within the project directory, create a Python virtual environment by typing:
```
$ virtualenv ciws_environment
```
This will create a directory called `ciws_environment` within the project directory. Inside, it will install a local version of Python and a local version of pip. We can use this to install and configure an isolated Python environment.

### Downloading the project source
Now we will get the project source code. To do this, we need to clone GitHub Repository into our recently created project directory.

```
$ git clone https://github.com/UCHIC/CIWS-Server.git 
```

A directory called `CIWS-Server` with all the source code and requirements will be created in `~/ciws`.

### Installing the project requirements
Before we install the Python requirements, we need to activate the virtual environment. You can do that by typing:

```
$ source ciws_environment/bin/activate
```
The terminal prompt should change to indicate that you are now operating within a Python virtual environment. It should look like this: `(ciws_environment)user@host:~/ciws$`.

After activating the virtual environment, we are now going to install the project's requirements.
```
(ciws_environment) $ cd ~/ciws/CIWS-Server
(ciws_environment) $ pip install -r requirements.txt
(ciws_environment) $ pip install gunicorn
```

### Configuring the projects through the `settings.json` files

We will now write the configuration files for both the Data Loading Service/Data Posting Service and the Data Transfer Manager by copying the `settings_template.json` files into a file called `settings.json` in the same directory.

#### Data Loading Service/Data Posting Service settings
First create the `settings.json` file from the settings template and edit it
```
$ cd ~/ciws/CIWS-Server/src/ciws_ci
$ cp settings_template.json settings.json
$ nano settings.json
```
Then edit and fill out the necessary settings information into the json formatted file.
Here's an example of a settings file for the Data Posting Service and Data Loading Service after filling out all the required information

Note: In these file, `<user>` is your linux username.
```
{
    "log_directory": "/home/<user>/ciws/logs",
    "source_directory": "/home/<user>/ciws/data",
    "target_directory":  "/home/<user>/ciws/datatarget",
    "quarantine_directory": "/home/<user>/ciws/dataquarantine",
    "client_token":  "#k06u9)k6r$em0j8#cultc23(7#4^=jrr+e+bx2$-0=gk4j^zo",
    "secret_key": "$8mr@#668ov+@ar2nhbb20j_z7as6t&lgu-064k==c)=2pad8$",
    "database": {
        "name": "ciwsdb",
        "user": "ciws_user",
        "password": "<password>",
        "host": "localhost",
        "port": "8086"
    }
}
```

#### Data Transfer Manager settings
First create the `settings.json` file from the settings template and edit it
```
$ cd ~/ciws/CIWS-Server/src/data_transfer_manager
$ cp settings_template.json settings.json
$ nano settings.json
```

Then edit and fill out the necessary settings information into the json formatted file.
Here's an example of a settings file for the Data Transfer Manager after filling out all the required information

Note: In these file, `<user>` is your linux username.

```
{
        "connections": 5,
        "log_directory": "/home/<user>/ciws/logs",
        "hosts":["10.0.0.2", "10.0.0.3"],
        "database": {
                "name": "ciwsdb",
                "user": "ciws_user",
                "password": "<password>",
                "host": "localhost",
                "port": "8086",
                "measurement": "CampusData"
        },
        "sshinfo":{
                "username": "raspberry_pi_user",
                "password": "<password>"
        }
}
```

### Creating systemd Socket and Service Files for Gunicorn
In this next part, we’ll make systemd service and socket files to allow Gunicorn to run as a linux service.

The Gunicorn socket will be created at boot and will listen for connections. When a connection occurs, systemd will automatically start the Gunicorn process to handle the connection.

Start by creating and opening a systemd socket file for Gunicorn:
```
$ sudo nano /etc/systemd/system/ciws.socket
```

Here we'll write a description of the socket and the socket location.
```
[Unit]
Description=ciws gunicorn socket

[Socket]
ListenStream=/run/ciws.sock

[Install]
WantedBy=sockets.target
```
Save and close the file when you are finished.

Next, we'll create and edit a file for the Gunicorn service
```
$ sudo nano /etc/systemd/system/ciws.service
```

Inside, we'll write all the Gunicorn configuration that specifies how the Data Posting Service application will run.

Note: In these file, `<user>` is your linux username.

```
[Unit]
Description=ciws gunicorn daemon
Requires=ciws.socket
After=network.target

[Service]
User=<user>
Group=www-data
WorkingDirectory=/home/<user>/ciws/CIWS-Server/src/ciws_ci/
ExecStart=/home/<user>/ciws/ciws_environment/bin/gunicorn \
          --access-logfile - \
          --workers 5 \
          --bind unix:/run/milton.sock \
          data_posting_service.web_service:application

[Install]
WantedBy=multi-user.target
```
Save and close the service file.

We can now start and enable the Gunicorn socket. This will create the socket file at /run/ciws.sock now and at boot. When a connection is made to that socket, systemd will automatically start the gunicorn.service to handle it.
```
$ sudo systemctl start ciws.socket
$ sudo systemctl enable ciws.socket
```

### Configuring Nginx to Proxy Pass to Gunicorn
Now that Gunicorn is set up, we need to configure Nginx to pass traffic to the process.
Fist, let's create and open a new server block in Nginx’s sites-available directory:
```
$ sudo nano /etc/nginx/sites-available/ciws
```
In this file, we'll create a new server block specifying the domain name of the server, and a proxy pass to the previously created socket file.
```
server {
    listen 80;
    server_name domain_name_or_ip_address;

    location / {
        include proxy_params;
        proxy_pass http://unix:/run/ciws.sock;
    }
}
```

Save and close the file. 
Now, we can enable the file by creating a link on the sites-enabled directory:
```
$ sudo ln -s /etc/nginx/sites-available/ciws /etc/nginx/sites-enabled
```

After this, the last step is to restart the NGINX service by typing
```
$ sudo systemctl restart nginx
```
We can now send requests to the server and use the web api endpoints to authorize and upload files.


## Running the Data Loading Service

Before running the loader script, let's make sure that the script path is in the `PYTHONPATH` environment variable so it can correctly find the source files inside the project.
```
$ echo 'export PYTHONPATH="${PYTHONPATH}:/opt/milton/CIWS-Server/src/ciws_ci"' >> ~/.bashrc
$ source ~/.bashrc
```

Now we can run the data loading service script by first activating the ciws virtual environment, then calling the script.
```
$ source ~/ciws/ciws_environment/bin/activate
$ python ~/ciws/CIWS-Server/src/ciws_ci/data_loading_service/loader.py
```

### Setting up a cronjob for the data loader
If the goal is to set a cronjob so the script runs periodically, open crontab
```
$ crontab -e
```
Then add this line to the end of the file
```
0 0 * * * ~/ciws/ciws_environment/bin/python ~/ciws/CIWS-Server/src/ciws_ci/data_loading_service/loader.py
```
In this line, we're telling cron to run the script located at `~/ciws/CIWS-Server/src/ciws_ci/data_loading_service/loader.py` using python executable located at `~/ciws/ciws_environment/bin/python` at time: `0 0 * * *` (The time meaning, 0 seconds, 0 hours(midnight), every day, every week, every month)

You can use a tool like [Crontab Guru](https://crontab.guru/) to help with setting up the cronjob time correctly.

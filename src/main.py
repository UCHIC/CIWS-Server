import json
import paramiko
import os
import sys, argparse
import csv
import getopt
from stat import *
import pandas as pd
from influxdb import DataFrameClient
from timeit import default_timer as timer
from datetime import datetime
import requests

from queue import Queue
from threading import Thread


class Worker(Thread):
    """ Thread executing tasks from a given tasks queue """
    def __init__(self, tasks):
        Thread.__init__(self)
        self.tasks = tasks
        self.daemon = True
        self.start()

    def run(self):
        while True:
            func, args, kargs = self.tasks.get()
            try:
                func(*args, **kargs)
            except Exception as e:
                print(e)
            finally:
                # Mark this task as done, whether an exception happened or not
                self.tasks.task_done()


class ThreadPool:
    """ Pool of threads consuming tasks from a queue """
    def __init__(self, num_threads):
        self.tasks = Queue(num_threads)
        for _ in range(num_threads):
            Worker(self.tasks)

    def add_task(self, func, *args, **kargs):
        """ Add a task to the queue """
        self.tasks.put((func, args, kargs))

    def map(self, func, args_list):
        """ Add a list of tasks to the queue """
        for args in args_list:
            self.add_task(func, args)

    def wait_completion(self):
        """ Wait for completion of all the tasks in the eweue """
        self.tasks.join()

def parse_site_name(site):
    translation = {ord(' '): None, ord('#'): '_', ord(':'): None, ord('0'): None}
    site_name = site.translate(translation).lower()
    return site_name

def write_to_db(item, building, target):

        if item.filename.endswith('.csv'):
            user = config["database"]["user"]
            password = config["database"]["password"]
            dbname = config["database"]["name"]
            protocol = 'json'
            port = config["database"]["port"]
            host = config["database"]["host"]

            client = DataFrameClient(host, port, user, password, dbname)

            # Attempt to write using temp, if it fails, try to write using a different
            # (in this case, old) structure of data.)
            try:
                df = pd.read_csv(
                    os.path.join(target, item.filename),
                    skiprows=[0],
                    index_col=0,
                    sep=',',
                    parse_dates=True,
                    infer_datetime_format=True,
                    usecols=[
                        'Date',
                        'coldInFlowRate',
                        'hotInFlowRate',
                        'hotOutFlowRate',
                        'hotInTemp',
                        'hotOutTemp',
                        'coldInTemp'
                    ]
                )
            except:
                try:
                    df = pd.read_csv(
                        os.path.join(target, item.filename),
                        skiprows=[0],
                        index_col=0,
                        sep=',',
                        parse_dates=True,
                        infer_datetime_format=True,
                        usecols=[
                            'Date',
                            'coldInFlowRate',
                            'hotInFlowRate',
                            'hotOutFlowRate'
                        ]
                    )
                except:
                    send_error("ERROR({0}): Failed to read {1} to pandas dataframe".format(datetime.now(), item.filename))

            df['buildingID'] = building.upper()
            print("Writing to DataBase")
            start = timer()
            try:
                if 'hotOutTemp' in df.columns:
                    client.write_points(
                        dataframe=df,
                        measurement=config['database']['measurement'],
                        field_columns={
                            'coldInFlowRate': df[['coldInFlowRate']],
                            'hotInFlowRate': df[['hotInFlowRate']],
                            'hotOutFlowRate': df[['hotOutFlowRate']],
                            'hotInTemp': df[['hotInTemp']],
                            'hotOutTemp': df[['hotOutTemp']],
                            'coldInTemp': df[['coldInTemp']]
                        },
                        tag_columns={'buildingID': building.upper()},
                        protocol='line',
                        numeric_precision=10,
                        batch_size=2000
                    )
                else:
                    client.write_points(
                        dataframe=df,
                        measurement=config['database']['measurement'],
                        field_columns={
                            'coldInFlowRate': df[['coldInFlowRate']],
                            'hotInFlowRate': df[['hotInFlowRate']],
                            'hotOutFlowRate': df[['hotOutFlowRate']]
                        },
                        tag_columns={'buildingID': building.upper()},
                        protocol='line',
                        numeric_precision=10,
                        batch_size=2000
                    )
                end = timer()
                print("Completed writing to database for: " + item.filename, "Time Elapsed: ", (end - start))
            except:
                send_error("FAILED TO WRITE ERROR<<{0}>> ({1}) failed to write to database".format(datetime.now(), item.filename))
                raise Exception("Unable to upload to database")
    
def write_to_db_local(*args, **kwargs):
    item = kwargs["item"]

    if item.name.lower().endswith('.csv'):
        user = config["database"]["user"]
        password = config["database"]["password"]
        dbname = config["database"]["name"]
        protocol = 'json'
        port = config["database"]["port"]
        host = config["database"]["host"]

        client = DataFrameClient(host, port, user, password, dbname)

        with open(item.path, newline='') as f:
            reader = csv.reader(f)
            site = next(reader)[0]
            dataloggerID = next(reader)[0]
            meterSize = next(reader)[0]
        
        site = parse_site_name(site)
        dataloggerID = parse_site_name(dataloggerID)
        dateparse = lambda x: pd.to_datetime(x, yearfirst=True)

 
        try:
            df = pd.read_csv(
                item.path,
                # skiprows=3,
                index_col=0,
                sep=',',
                date_parser=dateparse,
                header=3,
                usecols=["Time", "Pulses"]
            )
        except:
            send_error("ERROR({0}): Failed to read {1} to pandas dataframe".format(datetime.now(), item.name))

        print("Writing to DataBase")
        df['Site'] = site
        df['Filename'] = item.name
        df['DataloggerID'] = dataloggerID
     
        try:
            client.write_points(
                dataframe=df,
                measurement=site,
                field_columns={
                    'Pulses': df[['Pulses']],
                    'Filename': item.name,
                    'DataloggerID': dataloggerID
                },
                tag_columns ={
                    'Site': site,
                }
            )
            print("Completed writing to database for: " + item.name)
        except:
            # send_error("FAILED TO WRITE ERROR<<{0}>> ({1}) failed to write to database".format(datetime.now(), item.name))
            raise Exception("Unable to upload to database")


  # Function to be executed in a thread
def connect(host):
        print("Starting connection")
        source = '/home/pi/CampusMeter/'
        building = host[host.find('llc-') + 4]
        target = config["target"] + building

        transport = paramiko.Transport(host, 22)
        try:
            transport.connect(
                username=config['sshinfo']['username'],
                password=config['sshinfo']['password']
            )
        except:
            send_error("Unable to connect to {}".format(host))

        sftp = paramiko.SFTPClient.from_transport(transport)

        if not os.path.isdir(target):
            os.makedirs('%s' % (target))

        channel = transport.open_channel(kind="session")

        current_time = datetime.now()
        for item in sftp.listdir_attr(source):  # Iterate on files on datalogger, check datetime values to exclude one being currently written.
            if not datetime.fromtimestamp(sftp.stat(source + item.filename).st_mtime) > current_time:
                if not S_ISDIR(item.st_mode):
                    if os.path.isfile(os.path.join(target, item.filename)) and os.stat(os.path.join(target, item.filename)).st_size != item.st_size:
                        start = timer()
                        print("Updating Data: ", item.filename)
                        sftp.get('%s%s' % (source, item.filename), '%s/%s' % (target, item.filename))
                        end = timer()
                        print(item.filename + " updated successfully, time elapsed: ", (end - start))
                        write_to_db(item, building, target)
                    elif not os.path.isfile(os.path.join(target, item.filename)):
                        start = timer()
                        print("Copying Data: ", item.filename)
                        sftp.get('%s%s' % (source, item.filename), '%s/%s' % (target, item.filename))
                        end = timer()
                        print(item.filename + " copied successfully, time elapsed: ", (end - start))
                        write_to_db(item, building, target)
                else:
                    os.mkdir('%s%s' % (target, item.filename), ignore_existing=True)
                    sftp.get_dir('%s%s' % (source, item.filename), '%s%s' % (target, item.filename))

        # if we don't want the whole directory,  find latest file with ls -1t | head -1 instead

        sftp.close()
        transport.close()
        print("Closing Connection")
def connect_local_source():
    os.environ["OS"]
    print("Starting connection")
    source = config['local']['source']
    target = config['local']['target']
    kwargs = {"target": target, "source": source}

    if not os.path.isdir(target):
        os.makedirs('%s' % (target))

    current_time = datetime.now()
    source_files = [f for f in os.scandir(source) if f.is_file]
    target_files = [f.path for f in os.scandir(target) if f.is_file]
    for item in source_files:
        item_stat = os.stat(item.path)
        kwargs["item"] = item  # Iterate on files on datalogger, check datetime values to exclude one being currently written.
        if not datetime.fromtimestamp(item_stat.st_mtime) > current_time:
            if not S_ISDIR(item_stat[ST_MODE]): #isfile check
                if os.path.isfile(os.path.join(target, item.name)) and os.stat(os.path.join(target, item.name)).st_size != item_stat.st_size:
                    start = timer()
                    try:
                        write_to_db_local(**kwargs)
                        print("Copying Data: ", item.name)
                        if sys.platform == 'win32':
                            os.system('copy ' + item.path + ' ' + target + item.name)
                        elif sys.platform == 'linux':
                            os.system('cp ' + item.path + ' ' + target + item.name)
                        end = timer()
                        print(item.name + " copied successfully, time elapsed: ", (end - start))
                    except:
                        print("Data Upload failed for: {0}\n{0} has not been copied", item.name)
                        pass
                elif not os.path.isfile(os.path.join(target, item.name)):
                    start = timer()
                    try:
                        write_to_db_local(**kwargs)
                        print("Copying Data: ", item.name)
                        if sys.platform == 'win32':
                            os.system('copy ' + item.path + ' ' + target + item.name)
                        elif sys.platform == 'linux':
                            os.system('cp ' + item.path + ' ' + target + item.name)
                        end = timer()
                        print(item.name + " copied successfully, time elapsed: ", (end - start))
                    except:
                        print("Data Upload failed for: {0}\n{0} has not been copied", item.name)
                        pass
                   
                    
                else: 
                    print(item.name + ": already up to date.")
            else:
                os.mkdir('%s%s' % (target, item.filename), ignore_existing=True)
                # sftp.get_dir('%s%s' % (source, item.filename), '%s%s' % (target, item.filename))

    # if we don't want the whole directory,  find latest file with ls -1t | head -1 instead

    print("Process complete")
def send_error(data):
        message = {
            "text": data
        }
        response = requests.post(
            url=config['slack_webhook'],
            data=json.dumps(message),
            headers={'Content-Type': 'application/json'}
        )
        if response.status_code != 200:
            raise ValueError(
                'Request to slack returned an error %s, the response is:\n%s'
                % (response.status_code, response.text)
            )


if __name__ == "__main__":
    try:
        settingspath = os.path.abspath(".\\settings.json")
    except:
        settingspath = os.path.abspath("./settings.json")
    availableArgs = "Available arguments at this time are: single_source=true"
    parser = argparse.ArgumentParser(description= availableArgs)
    parser.add_argument("-single_source", "--single_source", 
        help="Collect data from single local source, instead of multiple remote sources",
        action="store_true"
        )
    args = parser.parse_args()

    if args.single_source:
        config = {}
        try:
            with open(settingspath, 'r') as data_file:
                config = json.load(data_file)
        except OSError:
            print("Unable to read settings.json.")
            exit(1)
        connect_local_source()
    elif os.environ['slacktest']:
        config = {}
        try:
            with open("settings.json", 'r') as data_file:
                config = json.load(data_file)
        except OSError:
            print("No list of hostnames found.")
            exit(1)
        send_error("testing post request from MILTON script.")
    else:
        #Import settings.json file
        hosts = []
        config = {}
        try:
            with open("settings.json", 'r') as data_file:
                config = json.load(data_file)
        except OSError:
            print("No list of hostnames found.")
            exit(1)

        for host in config['hosts']:
            hosts.append(host['hostname'])

        # Instantiate a thread pool with 5 worker threads
        pool = ThreadPool(6)

        # Add the jobs in bulk to the thread pool. Alternatively you could use
        # `pool.add_task` to add single jobs. The code will block here, which
        # makes it possible to cancel the thread pool with an exception when
        # the currently running batch of workers is finished.
        pool.map(connect, hosts)
        print("Wait_completion")
        pool.wait_completion()
        print("Complete")
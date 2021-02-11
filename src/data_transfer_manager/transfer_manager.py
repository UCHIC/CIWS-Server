import json
import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path

import paramiko
import os
import sys
import argparse
import csv
from stat import *
import pandas as pd
from influxdb import DataFrameClient
from timeit import default_timer as timer
from datetime import datetime
import requests

from queue import Queue
from threading import Thread

DEFAULT_THREADS = 2


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
            log.info(f'completed writing file {item.filename} to database in {end - start} seconds.')
            print("Completed writing to database for: " + item.filename, "Time Elapsed: ", (end - start))
        except:
            send_error(
                "FAILED TO WRITE ERROR<<{0}>> ({1}) failed to write to database".format(datetime.now(), item.filename))
            raise Exception("Unable to upload to database")


# Function to be executed in a thread
def connect(host):
    log.info(f'Starting connection to {host}')

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
        log.error(f'Unable to connect to {host}')
        send_error("Unable to connect to {}".format(host))

    sftp = paramiko.SFTPClient.from_transport(transport)

    if not os.path.isdir(target):
        os.makedirs('%s' % (target))

    channel = transport.open_channel(kind="session")

    current_time = datetime.now()
    log.info(f'downloading these files from {host}: {sftp.listdir_attr(source)}')

    for item in sftp.listdir_attr(source):  # Iterate on files on datalogger, check datetime values to exclude one being currently written.
        log.info(f'-- working with file {item.filename} in {host}')
        if not datetime.fromtimestamp(sftp.stat(source + item.filename).st_mtime) > current_time:
            if not S_ISDIR(item.st_mode):
                if os.path.isfile(os.path.join(target, item.filename)) and os.stat(
                        os.path.join(target, item.filename)).st_size != item.st_size:
                    start = timer()
                    print("Updating Data: ", item.filename)
                    log.info(f'getting file {item.filename} from {host}')
                    sftp.get('%s%s' % (source, item.filename), '%s/%s' % (target, item.filename))
                    end = timer()
                    log.info(f'file {item.filename} downloaded from {host} in {end - start} seconds.')
                    print(item.filename + " updated successfully, time elapsed: ", (end - start))
                    write_to_db(item, building, target)
                elif not os.path.isfile(os.path.join(target, item.filename)):
                    start = timer()
                    print("Copying Data: ", item.filename)
                    log.info(f'getting file {item.filename} from {host}')
                    sftp.get('%s%s' % (source, item.filename), '%s/%s' % (target, item.filename))
                    end = timer()
                    log.info(f'file {item.filename} downloaded from {host} in {end - start} seconds.')
                    print(item.filename + " copied successfully, time elapsed: ", (end - start))
                    write_to_db(item, building, target)
            else:
                os.mkdir('%s%s' % (target, item.filename), ignore_existing=True)
                sftp.get_dir('%s%s' % (source, item.filename), '%s%s' % (target, item.filename))
        else:
            log.warning(f'file modified time: {datetime.fromtimestamp(sftp.stat(source + item.filename).st_mtime)} '
                        f'is greater than the current time {current_time}')

    # if we don't want the whole directory,  find latest file with ls -1t | head -1 instead

    sftp.close()
    transport.close()
    log.info('Finished downloading all files! closing connection.')
    print("Closing Connection")


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


def get_logger():
    # Create a logger
    log: logging.Logger = logging.getLogger('transfer_manager')
    log.setLevel(logging.DEBUG)

    # create console handler with a debug level
    ch: logging.StreamHandler = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)

    # Get logger path and create directories if it doesn't exist
    file_path: Path = Path(config.get('log_directory', 'logs')) / 'transfer_manager.log'
    file_path.parent.mkdir(parents=True, exist_ok=True)

    # create file handler with an error level
    fh: RotatingFileHandler = RotatingFileHandler(file_path, maxBytes=5 * 1024 * 1024, backupCount=5)
    fh.setLevel(logging.INFO)

    # create formatter and add it to the handlers
    formatter: logging.Formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    fh.setFormatter(formatter)
    ch.setFormatter(formatter)

    # add the handlers to the logger
    log.addHandler(fh)
    log.addHandler(ch)
    return log


if __name__ == "__main__":
    settings_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'settings.json')

    if 'slacktest' in os.environ:
        config = {}
        try:
            with open(settings_path, 'r') as data_file:
                config = json.load(data_file)
        except OSError:
            print("No list of hostnames found.")
            exit(1)
        send_error("testing post request from MILTON script.")
    else:
        # Import settings.json file

        config = {}
        try:
            with open(settings_path, 'r') as data_file:
                config = json.load(data_file)
        except OSError:
            print("No list of hostnames found.")
            exit(1)

        log = get_logger()
        hosts = config['hosts']
        log.info(f'{len(hosts)} hosts detected: {", ".join(hosts)} ')

        # Instantiate a thread pool with worker threads
        pool = ThreadPool(config.get('connections', DEFAULT_THREADS))

        # Add the jobs in bulk to the thread pool. Alternatively you could use
        # `pool.add_task` to add single jobs. The code will block here, which
        # makes it possible to cancel the thread pool with an exception when
        # the currently running batch of workers is finished.
        pool.map(connect, hosts)
        print("Wait_completion")
        pool.wait_completion()
        print("Complete")

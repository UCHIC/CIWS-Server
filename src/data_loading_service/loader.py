import json
import os
import sys
import csv
from stat import *
import pandas as pd
from influxdb import DataFrameClient
from timeit import default_timer as timer
from datetime import datetime
import requests


def parse_site_name(site):
    translation = {ord(' '): None, ord('#'): '_', ord(':'): None, ord('0'): None}
    site_name = site.translate(translation).lower()
    return site_name


def write_to_db_local(*args, **kwargs):
    item = kwargs["item"]

    if not item.name.lower().endswith('.csv'):
        return

    user = config["database"]["user"]
    password = config["database"]["password"]
    dbname = config["database"]["name"]
    port = config["database"]["port"]
    host = config["database"]["host"]
    protocol = 'json'

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
            tag_columns={
                'Site': site,
            }
        )
        print("Completed writing to database for: " + item.name)
    except:
        # send_error("FAILED TO WRITE ERROR<<{0}>> ({1}) failed to write to database".format(datetime.now(), item.name))
        raise Exception("Unable to upload to database")


def connect_local_source():
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
        kwargs["item"] = item
        # Iterate on files on datalogger, check datetime values to exclude one being currently written.
        if not datetime.fromtimestamp(item_stat.st_mtime) > current_time:
            if not S_ISDIR(item_stat[ST_MODE]):  # isfile check
                if os.path.isfile(os.path.join(target, item.name)) and os.stat(
                        os.path.join(target, item.name)).st_size != item_stat.st_size:
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
                        print(f"Data Upload failed for: {item.name}\n{item.name} has not been copied")
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
                        print(f"Data Upload failed for: {item.name}\n{item.name} has not been copied")
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
    settings_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'settings.json')

    config = {}
    try:
        with open(settings_path, 'r') as data_file:
            config = json.load(data_file)
    except OSError:
        print("Unable to read settings.json.")
        sys.exit("Unable to read settings.json.")
    connect_local_source()

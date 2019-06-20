from influxdb import InfluxDBClient
import time
import json
import pandas as pdw


def determine_interval(time):
    result = (1/time)*60
    return result


def time_elapsed(time1, time2):
    epoch1 = time.mktime(time.strptime(time1, "%Y-%m-%d %H:%M:%S"))
    epoch2 = time.mktime(time.strptime(time2, "%Y-%m-%d"+"T"+"%H:%M:%S"))
    elapsed_time = epoch2 - epoch1
    return elapsed_time


def write_data(value, df, update_range):
    df.loc[update_range[0]:update_range[1], 'hotOutFlowRate'] = value

if __name__ == "__main__":

    config = {}
    try:
        with open("settings.json", 'r') as data_file:
            config = json.load(data_file)
    except OSError:
        print("No list of hostnames found.")
        exit(1)

    # TODO: URGENT Create new database and measurement to run this against.
    user = config["database"]["user"]
    password = config["database"]["password"]
    dbname = config["database"]["name"]
    measurement = config['database']['measurement']
    port = config["database"]["port"]
    host = config["database"]["host"]
    testDateBegin = "'2019-03-23T00:00:00Z'"
    hotOutFlag = 0
    hotOutTime = {
        'startTime': 0,
        'endTime': 0
    }
    df = pd.DataFrame(columns=['time', 'hotOutFlowRate'])
    to_write = []
    update_range = []

    client = InfluxDBClient(host, port, user, password, dbname)

    sql_string = """SELECT "hotOutFlowRate" FROM "flow" WHERE time > """+testDateBegin+""""""

    result_set = client.query(sql_string)
    results = result_set.get_points()
    for index, res in enumerate(results):
        if not res['hotOutFlowRate'] == 0:
            if len(update_range) is 0:
                # TODO: URGENT! Make script inclusive of start of range index, but exclusive to end of index range
                update_range.append(index + 1)
            else:
                update_range.append(index - 1)
            df2 = pd.DataFrame([res['time'], res['hotOutFlowRate']], columns=['time', 'hotOutFlowRate'])
            df.append(df2, ignore_index=True)
            hotOutFlag += 1
            if hotOutFlag == 1:
                hotOutTime['startTime'] = res[0]
            if hotOutFlag == 2:
                hotOutTime['endTime'] = res[1]
                timeElapsed = time_elapsed(hotOutTime['startTime'], hotOutTime['endTime'])
                value_to_write = determine_interval(timeElapsed)
                # Write Data here
                write_data(value_to_write, df, update_range)
                hotOutFlag = 0
                update_range = []
            counter = 0
        else:
            df2 = pd.DataFrame([res['time'], res['hotOutFlowRate']], columns=['time', 'hotOutFlowRate'])
            df.append(df2, ignore_index=True)
            counter += 1
        print(res)





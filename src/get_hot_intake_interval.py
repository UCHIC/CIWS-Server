from influxdb import InfluxDBClient, DataFrameClient
import time
import json
import pandas as pd
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


def determine_interval(time):
    result = (1/time)*60
    return result


def time_elapsed(time1, time2):
    epoch1 = time.mktime(time.strptime(time1, "%Y-%m-%d"+"T"+"%H:%M:%S"+"Z"))
    epoch2 = time.mktime(time.strptime(time2, "%Y-%m-%d"+"T"+"%H:%M:%S"+"Z"))
    elapsed_time = epoch2 - epoch1
    return elapsed_time + 1


def write_data(value, df, building, measurement):
    # df.loc[update_range[0]:update_range[1], 'hotOutFlowRate'] = value
    # df_transformed = df.loc[df['hotOutFlowRate']==value,:].copy()
    df['hotOutFlowRate'] = value
    df.set_index(['time'], inplace=True)
    df.index = pd.to_datetime(df.index)
    client = DataFrameClient('odm2equipment.uwrl.usu.edu', 8086, 'root', 'foobar123', 'ciws')
    client.write_points(
        dataframe=df, 
        measurement=measurement, 
        field_columns={
            'hotOutFlowRate': df['hotOutFlowRate']
        },
        protocol='line',
        tag_columns={'buildingID': building},
        time_precision='ms'



    )

if __name__ == "__main__":

    def transform(building):

        config = {}
        try:
            with open("C:/Users/Elijah/Desktop/Projects/CIWS-Server/src/settings.json", 'r') as data_file:
                config = json.load(data_file)
        except OSError:
            print("No list of hostnames found.")
            exit(1)
        df = pd.DataFrame(columns=['time', 'hotOutFlowRate', 'buildingID'])
        to_write = []
        update_range = []
        testDateBegin = config["testDateBegin"]
        testDateEnd = config["testDateEnd"]
        hotOutFlag = 0
        hotOutTime = {
        'startTime': 0,
        'endTime': 0
        }   
        user = config["database"]["user"]
        password = config["database"]["password"]
        dbname = config["database"]["name"]
        measurement = config['database']['measurement']
        port = config["database"]["port"]
        host = config["database"]["host"]

        client = InfluxDBClient(host, port, user, password, dbname)


        

        sql_string = """SELECT "hotOutFlowRate", "buildingID" FROM "flow" WHERE "buildingID" = """+building+""" AND time >= """+testDateBegin+""" AND time <= """+testDateEnd+""""""

        result_set = client.query(sql_string)
        results = result_set.get_points()
        firstPulse = False
        dataset_flag = False
        for index, res in enumerate(results):
            if res['hotOutFlowRate'] != 0:
                hotOutFlag += 1
                if not firstPulse:  # Ensure we start from a complete dataset by only beginning to write to dataframes after an initial pulse
                    firstPulse = True # Denotes the first non-zero value has been hit, and the rest processing can begin
                    dataset_flag = True # Denotes that the next entry should be the startflag for the dataset
                if hotOutFlag == 2:
                    hotOutTime['endTime'] = res['time']
                    timeElapsed = time_elapsed(hotOutTime['startTime'], hotOutTime['endTime'])
                    value_to_write = determine_interval(timeElapsed)
                    df2 = pd.DataFrame([[res['time'], res['hotOutFlowRate'], res['buildingID']]], columns=['time', 'hotOutFlowRate', 'buildingID'])
                    df = df.append(df2, ignore_index=True)
                    # Write Data here
                    write_data(value_to_write, df, building, measurement)
                    hotOutFlag = 1
                    dataset_flag = True
                    df = pd.DataFrame(columns=['time', 'hotOutFlowRate'])

            elif firstPulse:
                if dataset_flag:
                    hotOutTime['startTime'] = res['time']
                    dataset_flag = False
                df2 = pd.DataFrame([[res['time'], res['hotOutFlowRate'], res['buildingID']]], columns=['time', 'hotOutFlowRate', 'buildingID'])
                df = df.append(df2, ignore_index=True)
            print(res)

    
    
    buildings = {"'A'", "'B'", "'C'", "'D'", "'E'", "'F'"}

    # Instantiate a thread pool with 5 worker threads
    pool = ThreadPool(6)

    # Add the jobs in bulk to the thread pool. Alternatively you could use
    # `pool.add_task` to add single jobs. The code will block here, which
    # makes it possible to cancel the thread pool with an exception when
    # the currently running batch of workers is finished.
    pool.map(transform, buildings)
    print("Wait_completion")
    pool.wait_completion()
    print("Complete")

    
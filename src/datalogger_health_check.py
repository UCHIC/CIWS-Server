import json
import paramiko
import os
import datetime
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


if __name__ == "__main__" and not os.environ['testing']:

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

    # Function to be executed in a thread
    def connect(host):
        print("Starting connection")

        transport = paramiko.Transport(host, 22)
        try:
            transport.connect(
                username=config['sshinfo']['username'],
                password=config['sshinfo']['password']
            )
        except:
            send_error("Unable to connect to {0} during hourly uptime check".format(host))

        sftp = paramiko.SFTPClient.from_transport(transport)
        latest = 0
        latestfile = None

        for file in sftp.listdir_attr():
            if file.filename.startswith('multi_meter') and file.st_mtime > latest:
                latest = file.st_mtime
                latestfile = file.filename
        current_time = datetime.datetime.now()
        if latestfile.st_mtime < current_time - datetime.timedelta(days=2):
            send_error("Possible uncaught logging error: Latest file update more than two days ago on host: {0}".format(host))

        sftp.close()
        transport.close()
        print("Closing Connection")

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

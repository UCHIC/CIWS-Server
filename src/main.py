import sys
import paramiko
import os
from stat import S_ISDIR
import time
from timeit import default_timer as timer

IS_PY2 = sys.version_info < (3, 0)

if IS_PY2:
    from Queue import Queue
else:
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


if __name__ == "__main__":


    # Function to be executed in a thread
    def connect(host):
        source = '/home/pi/CampusMeter/'
        building = host[host.find('llc-') + 4] + '/'
        target = 'C:/Users/Elijah/Documents/' + building

        transport = paramiko.Transport(host, 22)
        transport.connect(username='pi', password='p1w4t3r')
        sftp = paramiko.SFTPClient.from_transport(transport)

        if not os.path.isdir(target):
            os.mkdir('%s' % (target) )

        for item in sftp.listdir_attr(source):
            if not S_ISDIR(item.st_mode):
                if os.path.isfile(os.path.join(target, item.filename)) and os.stat(os.path.join(target, item.filename)).st_size != item.st_size:
                    start = timer()
                    sftp.get('%s%s' % (source, item.filename), '%s%s' % (target, item.filename))
                    end = timer()
                    print(item.filename + " updated successfully, time elapsed: ", (end - start))
                elif not os.path.isfile(os.path.join(target, item.filename)):
                    start = timer()
                    sftp.get('%s%s' % (source, item.filename), '%s%s' % (target, item.filename))
                    end = timer()
                    print(item.filename + " copied successfully, time elapsed: ", (end - start))
            else:
                os.mkdir('%s%s' % (target, item.filename), ignore_existing=True)
                sftp.get_dir('%s%s' % (source, item.filename), '%s%s' % (target, item.filename))

        # if we don't want the whole directory,  find latest file with ls -1t | head -1 instead

        sftp.close()
        transport.close()



    hosts = []
    try:
        with open("hosts", 'r') as ins:
            for line in ins:
                line = line.rstrip('\n')
                hosts.append(line)
    except OSError:
        print("No list of hostnames found.")
        exit(1)



    # Instantiate a thread pool with 5 worker threads
    pool = ThreadPool(6)

    # Add the jobs in bulk to the thread pool. Alternatively you could use
    # `pool.add_task` to add single jobs. The code will block here, which
    # makes it possible to cancel the thread pool with an exception when
    # the currently running batch of workers is finished.
    pool.map(connect, hosts)
    pool.wait_completion()
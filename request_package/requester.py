import http.client as client
from threading import Thread
from queue import Queue


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
                # An exception happened in this thread
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
        """ Wait for completion of all the tasks in the queue """
        self.tasks.join()


class Requester:
    def __init__(self, requests, response_queue, config):
        self.response_queue = response_queue
        self.requests = requests
        self.config = config

        self.num_threads = int(self.config['Main']['threads'])
        self.pool = ThreadPool(self.num_threads)

        self.pool.map(self._send_request, self.requests)

    def add_response(self, response):
        """ Add a response to the response_queue """
        self.response_queue.put(response)

    def _send_request(self, request):
        protocol = self.config['RequestInfo']['protocol'].lower()
        port = self.config['RequestInfo']['port']

        if protocol == 'http':
            connection = client.HTTPConnection(request.host)
        elif protocol == 'https':
            connection = client.HTTPSConnection(request.host)
        else:
            """Exception"""
            pass

        headers = dict([i.split(': ') for i in request.headers])

        connection.request(request.method, request.url_path, request.data, headers=headers)

        resp = connection.getresponse()
        request.raw_response = resp.read()
        connection.close()

        self.add_response(request)

    def wait_completion(self):
        self.pool.wait_completion()


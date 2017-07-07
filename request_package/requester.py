import http.client as client
from queue import Queue, Empty
from threading import Thread


class Worker(Thread):
    """ Thread executing tasks from a given tasks queue """

    def __init__(self, tasks):
        Thread.__init__(self)
        self.tasks = tasks
        self.daemon = True

    def run(self):
        while True:
            try:
                func, args, kargs = self.tasks.get(block=False)
            except Empty as e:
                # Если очередь tasks пустая
                break

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
        self.tasks = Queue()
        self.workers = []
        for _ in range(num_threads):
            self.workers.append(Worker(self.tasks))

    def add_task(self, func, *args, **kargs):
        """ Add a task to the queue """
        self.tasks.put((func, args, kargs))

    def map(self, func, args_list):
        """ Add a list of tasks to the queue """
        for args in args_list:
            self.add_task(func, args)

    def run(self):
        for worker in self.workers:
            worker.start()

    def is_running(self):
        if any([worker.is_alive() for worker in self.workers]):
            return True
        return False

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

    def run(self):
        self.pool.run()

    def is_running(self):
        return self.pool.is_running()

    def add_response(self, response):
        """ Add a response to the response_queue """
        self.response_queue.put(response)

    def _send_request(self, request):
        scheme = self.config['RequestInfo']['scheme'].lower()
        port = int(self.config['RequestInfo']['port'])

        if scheme == 'http':
            connection = client.HTTPConnection(request.host, port)
        elif scheme == 'https':
            connection = client.HTTPSConnection(request.host, port)
        else:
            raise Exception('Протокол {} не поддерживается'.format(scheme))

        connection.request(request.method, request.url_path, request.data, headers=request.headers)

        resp = connection.getresponse()
        request.raw_response = resp.read()
        connection.close()

        self.add_response(request)

    def wait_completion(self):
        self.pool.wait_completion()

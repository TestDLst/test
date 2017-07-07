from queue import Queue

from core.analyzer import Analyzer
from request_package.requester import Requester


class SqlAnalyzer(Analyzer):
    def __init__(self, marked_raw_request, config):
        self.config = config
        self.marked_raw_request = marked_raw_request

        self.sql_payloads = self.get_payloads('/fuzzing/sql.txt')
        self.modified_requests = self.get_modified_requests(self.sql_payloads)

        self.response_queue = Queue()
        requester = Requester(self.modified_requests, self.response_queue, self.config)
        requester.run()

        while requester.is_running():
            item = self.response_queue.get()
            print(item)

        # requester.wait_completion()

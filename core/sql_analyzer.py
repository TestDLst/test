from queue import Queue

from core.analyzer import Analyzer
from request_package.requester import Requester


class SqlAnalyzer(Analyzer):
    def __init__(self, marked_raw_request, config):
        Analyzer.__init__(self, marked_raw_request, config)

        self.sql_payloads = self.get_payloads('/fuzzing/test.txt')
        self.modified_requests = self.get_modified_requests(self.sql_payloads)

        # self.analyze()

    def analyze(self):
        requester = Requester(self.modified_requests, self.response_queue, self.config)
        requester.run()
        while requester.is_running():
            response_obj = self.response_queue.get()
            # print(response_obj.testing_param, response_obj.request_time, response_obj.content_length)
            print(response_obj.raw_response)

    def get_standard_response(self):
        requester = Requester([self.get_initial_request()], self.response_queue, self.config)
        standard_response = requester.get_standard_response(self.init_request_obj)
        return standard_response

    # requester.wait_completion()

import re
import random
import string
from queue import Queue

from core.analyzer import Analyzer
from request_package.requester import Requester


class SqlAnalyzer(Analyzer):
    def __init__(self, marked_raw_request, config):
        Analyzer.__init__(self, marked_raw_request, config)

        self.sql_payloads = self.get_payloads('/fuzzing/test.txt')
        self.modified_requests = self.get_modified_requests(self.sql_payloads)

        self.detect_reflected_params()
        self.analyze()

    def analyze(self):
        requester = Requester(self.modified_requests, self.response_queue, self.config)
        requester.run()
        while requester.is_running():
            response_obj = self.response_queue.get()
            response_obj = self.clean_reflected_rows(response_obj)
            print(response_obj.testing_param, response_obj.request_time, response_obj.content_length)



    # requester.wait_completion()

    # TODO: удалять строки из ответов, которые изменили внутри свое значение

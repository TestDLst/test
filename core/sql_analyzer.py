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

    def get_standard_response(self):
        requester = Requester([self.get_initial_request()], self.response_queue, self.config)
        standard_response = requester.get_standard_response(self.init_request_obj)
        return standard_response

    # requester.wait_completion()

    # TODO: удалять строки из ответов, которые изменили внутри свое значение
    def detect_reflected_params(self):
        resp_queue = Queue()

        self._reflect_payload = ''.join([random.choice(string.ascii_letters) for i in range(6)])
        requests = self.get_modified_requests([self._reflect_payload])

        requester = Requester(requests,resp_queue,self.config)
        requester.run()

        while requester.is_running() or not resp_queue.empty():
            resp = resp_queue.get()
            pattern = '\s+?.+?({reflected}).+?\n'.format(reflected=self._reflect_payload)
            re.sub(pattern, self._feed_reflected_rows, resp.raw_response)


    def clean_reflected_rows(self, response_obj):
        raw_response = response_obj.raw_response
        for reflect_pattern in self.reflected_rows:
            try:
                raw_response = re.sub(reflect_pattern, '', raw_response)
                response_obj.rebuild(raw_response)
            except Exception as e:
                print(reflect_pattern)
                print(e)
        return response_obj

    def _feed_reflected_rows(self, match):
        start, _ = match.regs[0]
        stop, _ = match.regs[1]
        reflect_pattern = match.string[start:stop] + '.+?\n'
        reflect_pattern = reflect_pattern.replace('"', '\\"') # экранируем двойные кавычки
        reflect_pattern = reflect_pattern.replace('(', '\\(').replace(')','\\)') # экранируем скобки
        reflect_pattern = reflect_pattern.replace('[', '\\[').replace(']','\\]') # экранируем скобки
        reflect_pattern = reflect_pattern.replace('$', '\\$')
        reflect_pattern = reflect_pattern.replace('^', '\\^')

        self.reflected_rows |= set([reflect_pattern])
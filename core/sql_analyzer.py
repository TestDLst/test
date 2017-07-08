from core.analyzer import Analyzer
from request_package.requester import Requester


class SqlAnalyzer(Analyzer):
    def __init__(self, marked_raw_request, config):
        Analyzer.__init__(self, marked_raw_request, config)
        # self.standard_response = self.get_standard_response()

        self.sql_payloads = self.get_payloads('/fuzzing/sql.txt')
        self.modified_requests = self.get_modified_requests(self.sql_payloads)

        self.detect_reflected_patterns()
        self.clean_reflected_rows(self.standard_response)

    def analyze(self):
        requester = Requester(self.modified_requests, self.response_queue, self.config)
        requester.run()

        print('[!] Стандартная длина контента: {}'.format(self.standard_response.content_length))
        print('[!] Стандартное количество строк: {}'.format(self.standard_response.row_count))
        print('[!] Min/max time_delta: {}/{}'.format(*self.time_delta))
        while requester.is_running():
            response_obj = self.response_queue.get()
            response_obj = self.clean_reflected_rows(response_obj)
            if self.is_interesting_behavior(response_obj, 7 ^ 4):
                print(response_obj.testing_param, response_obj.content_length, response_obj.row_count,
                      response_obj.request_time)

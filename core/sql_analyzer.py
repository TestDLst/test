from core.analyzer import Analyzer
from request_package.requester import Requester


class SqlAnalyzer(Analyzer):
    def __init__(self, marked_raw_request, config):
        Analyzer.__init__(self, marked_raw_request, config)

        self.print_format = '{test_info: <50}|{response_code: ^5}|{content_length: ^10}|{row_count: ^10}|{testing_param: ^20}|{request_time: ^15}'

        self.sql_payloads = self.get_payloads('/fuzzing/sql.txt')
        self.modified_requests = self.get_modified_requests(self.sql_payloads, flags=7)

        self.detect_reflected_patterns()
        self.clean_reflected_rows(self.standard_response)

    def analyze(self):
        requester = Requester(self.modified_requests, self.response_queue, self.config)
        requester.run()

        responses = []
        # print('[!] Стандартная длина контента: {}'.format(self.standard_response.content_length))
        # print('[!] Стандартное количество строк: {}'.format(self.standard_response.row_count))
        # print('[!] Min/max time_delta: {}/{}\n'.format(*self.time_delta))
        self.print_standard_resp_info()

        while requester.is_running():
            response_obj = self.response_queue.get()
            response_obj = self.clean_reflected_rows(response_obj)
            if self.is_interesting_behavior(response_obj, 3):

                kwargs = {
                    'test_info':response_obj.test_info,
                    'response_code':response_obj.response_code,
                    'content_length':response_obj.content_length,
                    'row_count':response_obj.row_count,
                    'testing_param':response_obj.testing_param,
                    'request_time':response_obj.request_time
                }
                print(self.print_format.format(**kwargs))
                responses.append(response_obj)

    def analyze_blind(self):
        sql_payloads = self.get_payloads('/fuzzing/sql_blind_and.txt')
        modified_requests = self.get_payloads(sql_payloads, flags=5)

        for pair in zip(modified_requests[0::2], modified_requests[1::2]):
            pass

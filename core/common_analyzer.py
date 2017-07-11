from core.analyzer import Analyzer
from request_package.requester import Requester


class CommonAnalyzer(Analyzer):
    def __init__(self, marked_raw_request, config):
        Analyzer.__init__(self, marked_raw_request, config)
        self.print_format_size = [5, 10, 10, 10, 20, 65]
        self.print_format = '|{response_code: ^{}}|{content_length: ^{}}|{row_count: ^{}}|{word_count: ^{}}|{request_time: ^{}}|{test_info: <{}}|'

        self.sql_payloads = self.get_payloads(config['Main']['wordlist'])
        self.modified_requests = self.get_modified_requests(self.sql_payloads, flags=7)

        # self.detect_reflected_patterns()
        # self.clean_reflected_rows(self.standard_response)

    def analyze(self):
        requester = Requester(self.modified_requests, self.response_queue, self.config)
        requester.run()

        responses = []

        self.print_standard_resp_info()
        self.print_head()

        self.dump_response('standard.txt', self.standard_response)

        while requester.is_running() or not self.response_queue.empty():
            response_obj = self.response_queue.get()
            response_obj = self.clean_reflected_rows(response_obj)

            if self.is_interesting_behavior(response_obj, 3):
                # self.dump_response(response_obj.test_info, response_obj)
                self.print_resp_info(response_obj)
                responses.append(response_obj)

        self.print_footer()


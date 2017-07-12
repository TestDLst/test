from core.analyzer import Analyzer
from request_package.requester import Requester


class SqlAnalyzer(Analyzer):
    def __init__(self, marked_raw_request, config):
        Analyzer.__init__(self, marked_raw_request, config)

    def analyze(self):
        pass


class BlindBooleanBasedSqlAnalyzer(SqlAnalyzer):
    def __init__(self, marked_raw_request, config):
        SqlAnalyzer.__init__(self, marked_raw_request, config)

        self.blind_sql_and_payloads = self.get_payloads(self.config['Program']['script_path'] + '/payloads/fuzzing/sql_blind_and.txt')
        self.blind_sql_or_payloads = self.get_payloads(self.config['Program']['script_path'] + '/payloads/fuzzing/sql_blind_or.txt')

        self.modified_requests = self.get_modified_requests(self.blind_sql_and_payloads, flags=5)
        for index, request in enumerate(self.modified_requests):
            request.index = index

    # TODO Подумать, что делать в случае отсутствия каких то ответов
    def analyze(self):
        print('[!] Запускаю Blind Boolean Based SqlAnalyzer')
        requester = Requester(self.modified_requests, self.response_queue, self.config)
        requester.run()

        responses = []

        while requester.is_running() or not self.response_queue.empty():
            responses.append(self.response_queue.get())

        responses.sort(key=lambda x: x.index)

        responses = list(zip(responses[::2], responses[1::2]))

        for resp1, resp2 in responses:
            if resp1.index + 1 != resp2.index:
                print("ERROR")

        print('[!] Сравниваю ответы')
        self.print_head()
        for resp1, resp2 in responses:
            self._check_diff(resp1, resp2)
        self.print_footer()

    def _check_diff(self, resp1, resp2):
        if resp1.response_code != resp2.response_code or resp1.content_length != resp2.content_length \
                or resp1.row_count != resp2.row_count or resp1.word_count != resp2.word_count:
            self.print_resp_info(resp1)
            self.print_resp_info(resp2)


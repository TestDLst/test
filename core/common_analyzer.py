from collections import defaultdict
from core.analyzer import Analyzer
from request_package.requester import Requester
from encoders.encoder import *


class CommonAnalyzer(Analyzer):
    def __init__(self, marked_raw_request, config):
        Analyzer.__init__(self, marked_raw_request, config)


        self.detect_reflected_patterns()
        self.clean_reflected_rows(self.standard_response)

    def analyze(self):
        common_payloads = self.get_payloads(self.config['Program']['payload_path'] + 'fuzzing/common.txt')
        modified_requests = self.get_modified_requests(common_payloads, no_encode, flags=7)

        requester = Requester(modified_requests, self.response_queue, self.config)
        requester.run()

        responses = []

        self.print_standard_resp_info()
        print('[!] Фаззинг по символам пунктуации')
        self.print_head()

        payloads_info = defaultdict(list)

        while requester.is_running() or not self.response_queue.empty():
            response_obj = self.response_queue.get()
            response_obj = self.clean_reflected_rows(response_obj)

            if self.is_interesting_behavior(response_obj, 3):

                self.print_resp_info(response_obj)
                payloads_info[response_obj.testing_param].append(response_obj.payload)
                responses.append(response_obj)

        self.print_footer()

        print('[!] Информация по результативным нагрузкам')
        for key, value in payloads_info.items():
            print('\t{}: {}'.format(key, ', '.join(value)))



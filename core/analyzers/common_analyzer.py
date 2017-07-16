from collections import defaultdict
from functools import reduce
from operator import add

from core.analyzers.analyzer import Analyzer
from core.encoder import *
from core.printer import Printer

from request_package.requester import Requester


# TODO: Отправлять по 2 раза, выводить [len1/len2] по каждой метрике
class CommonAnalyzer(Analyzer):
    def __init__(self, marked_raw_request, config):
        Analyzer.__init__(self, marked_raw_request, config)

        self.detect_reflected_patterns()
        self.clean_reflected_rows(self.standard_response)

    def analyze(self):
        self._response_id = 0

        common_payloads = self.get_payloads(self.config['Program']['payload_path'] + 'fuzzing/common.txt')
        response_dict = defaultdict(lambda: defaultdict(list))

        encode_list = [url_encode, double_url_encode, overlong_utf8_encode]
        modified_request_groups = self.get_modified_request_groups(common_payloads, encode_list)
        modified_requests = reduce(add, zip(*modified_request_groups))

        self.print_standard_resp_info()

        requester = Requester(modified_requests, self.response_queue, self.config)
        requester.run()

        self.print_head()

        while requester.is_running() or not self.response_queue.empty():
            response_obj = self.response_queue.get()
            self.clean_reflected_rows(response_obj)
            response_dict[response_obj.gid][response_obj.id].append(response_obj)

            if len(response_dict[response_obj.gid].keys()) == len(encode_list):
                self.print_result_for_response_group(response_dict[response_obj.gid])

    def get_modified_request_groups(self, payloads, encode_list, flags=7):
        modified_payload_groups = []
        for encode_func in encode_list:
            modified_payload_groups.append(map(encode_func, payloads))

        modified_request_groups = []
        for payload_group in modified_payload_groups:
            modified_request_groups.append(self.get_modified_requests(payload_group, flags=flags))

        for gid, request_group in enumerate(zip(*modified_request_groups)):
            for id, request in enumerate(request_group):
                request.gid = gid
                request.id = id

        return modified_request_groups

    def print_result_for_response_group(self, response_group):
        self.print_footer()
        for key in sorted(response_group.keys()):
            response_list = response_group[key][0]
            self._response_id += 1
            self.print_resp_info(response_list, response_id=self._response_id)
        self.print_footer()
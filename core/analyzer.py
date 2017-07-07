from queue import Queue
from request_package.request_modifier import RequestModifier
from request_package.requester import Requester


class StatisticObject:
    def __init__(self, response):
        pass


# TODO: encode пейлоадов
class Analyzer:
    def __init__(self, marked_raw_request, config):
        self.config = config
        self.marked_raw_request = marked_raw_request
        self.sql_analyzer = SqlAnalyzer(self.marked_raw_request, self.config)

    def get_modified_requests(self, payloads):
        """ Возвращает список модифицированных запросов

        :param payloads: Нагрузки, дополняющие помеченные параметры
        :return: Список объектов RequestObject
        """
        request_modifier = RequestModifier(self.marked_raw_request, payloads, self.config)
        return request_modifier.get_modified_requests()

    def get_payloads(self, payload_path):
        """

        :param payload_path: путь до файла с нагрузками относительно дирестории payloads
        :return: Список нагрузок payloads
        """
        with open(self.config['Program']['script_path'] + '/payloads' + payload_path) as f:
            payloads = f.read().split('\n')
        return payloads


class SqlAnalyzer(Analyzer):
    def __init__(self, marked_raw_request, config):
        self.config = config
        self.marked_raw_request = marked_raw_request

        self.sql_payloads = self.get_payloads('/fuzzing/sql.txt')
        self.modified_requests = self.get_modified_requests(self.sql_payloads)

        self.response_queue = Queue()
        requester = Requester(self.modified_requests, self.response_queue, self.config)
        requester.wait_completion()

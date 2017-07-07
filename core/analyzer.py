from queue import Queue

from request_package.request_modifier import RequestModifier
from request_package.requester import Requester


class StatisticObject:
    def __init__(self, response):
        a = response
        self.standard_raw_response = ''
        self.standard_content_length = 0
        self.standard_row_length = 0
        self.standard_request_time = 0

        self.raw_response = ''
        self.content_length = 0
        self.row_length = 0
        self.request_time = 0


# TODO: encode пейлоадов
class Analyzer:
    def __init__(self, marked_raw_request, config):
        self.config = config
        self.marked_raw_request = marked_raw_request

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

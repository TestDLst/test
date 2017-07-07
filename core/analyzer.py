from queue import Queue

from request_package.request_object import RequestObject
from request_package.request_modifier import RequestModifier
from request_package.requester import Requester


class StatisticObject:
    def __init__(self, response):
        self.raw_response = response.raw_response
        self.content_length = len(self.raw_response)
        self.row_length = 0
        self.request_time = 0


# TODO: encode пейлоадов
# TODO: подумать над судьбой StatisticsObject и ResponseObject (StatisticsObject -> ResponseObject)
class Analyzer:
    def __init__(self, marked_raw_request, config):
        self.config = config
        self.marked_raw_request = marked_raw_request

        self.request_obj = self.get_initial_request()
        self.response_queue = Queue()

    def get_modified_requests(self, payloads):
        """ Возвращает список модифицированных запросов

        :param payloads: Нагрузки, дополняющие помеченные параметры
        :return: Список объектов RequestObject
        """
        request_modifier = RequestModifier(self.marked_raw_request, payloads, self.config)
        a = request_modifier.get_modified_requests()
        return a

    def get_payloads(self, payload_path):
        """

        :param payload_path: путь до файла с нагрузками относительно дирестории payloads
        :return: Список нагрузок payloads
        """
        with open(self.config['Program']['script_path'] + '/payloads' + payload_path) as f:
            payloads = f.read().split('\n')
        return payloads

    def get_initial_request(self):
        """ Возвращает инициализирующий запрос

        :return: Инициализирующий запрос RequestObject
        """
        with open(self.config['Main']['file']) as f:
            initial_request = f.read()
        return RequestObject(initial_request)

    def analyze(self):
        raise Exception('Не реализовано')

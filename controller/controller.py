from queue import Queue

from request_package.request_modifier import RequestModifier
from request_package.request_object import RequestObject
from request_package.request_marker import RequestMarker
from request_package.requester import Requester
from response_package.response_analyzer import Analyzer


class Controller:
    def __init__(self, config):
        # Объявления
        self.config = config
        self.initial_request = self.get_initial_request()
        self.marked_raw_request = RequestMarker(self.initial_request, self.config).get_marked_request()

        # Логика
        # Тест RequestModifier'а
        meta_payloads = self.get_payloads('/fuzzing/test.txt')
        self.modified_requests = self.get_modified_requests(meta_payloads)
        print(self.modified_requests[0]._testing_param)

        # Тест Requester
        self.response_queue = Queue()
        requester = Requester(self.modified_requests, self.response_queue, self.config)
        requester.wait_completion()
        # print("end")

        # Тест Analyzer
        analyzer = Analyzer(self.response_queue)
        analyzer.print_info()
        print("end")

    def search_hidden_parameters(self):
        pass

    def get_modified_requests(self, payloads):
        """ Возвращает список модифицированных запросов

        :param payloads: Нагрузки, дополняющие помеченные параметры
        :return: Список объектов RequestObject
        """
        request_modifier = RequestModifier(self.marked_raw_request, payloads, self.config)
        return request_modifier.get_modified_requests()

    def get_initial_request(self):
        """ Возвращает инициализирующий запрос

        :return: Инициализирующий запрос RequestObject
        """
        with open(self.config['Main']['file']) as f:
            initial_request = f.read()
        return RequestObject(initial_request)

    def get_payloads(self, payload_path):
        """

        :param payload_path: путь до файла с нагрузками относительно дирестории payloads
        :return: Список нагрузок payloads
        """
        with open(self.config['Program']['script_path']+'/payloads' + payload_path) as f:
            payloads = f.read().split('\n')
        return payloads
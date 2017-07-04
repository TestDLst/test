from queue import Queue

from request_package.request_modifier import RequestModifier
from request_package.request_object import RequestObject
from request_package.request_marker import RequestMarker

class Controller:
    def __init__(self, config):
        # Объявления
        self.config = config
        self.initial_request = self.get_initial_request()
        self.marked_request = RequestMarker(self.initial_request, self.config).get_marked_request()

        # Логика
        # Тест RequestModifier'а
        with open(self.config['Program']['script_path']+'/payloads/fuzzing/metacharacters.txt') as f:
            meta_payloads = f.read()
        # response_queue = Queue()

        self.modified_requests = self.get_modified_requests(meta_payloads)
        print(self.modified_requests)

    def search_hidden_parameters(self):
        pass

    def get_modified_requests(self, payloads):
        """ Возвращает список модифицированных запросов

        :param payloads: Нагрузки, дополняющие помеченные параметры
        :return: Список объектов RequestObject
        """
        request_modifier = RequestModifier(self.marked_request, payloads, self.config)
        return request_modifier.get_modified_requests()

    def get_initial_request(self):
        """ Возвращает инициализирующий запрос

        :return: Инициализирующий запрос RequestObject
        """
        with open(self.config['Main']['file']) as f:
            initial_request = f.read()
        return RequestObject(initial_request)
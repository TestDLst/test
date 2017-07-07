from request_package.request_object import RequestObject
from request_package.request_marker import RequestMarker
from core.analyzer import Analyzer


# TODO: добавить в Requester метку end в конец очереди после завершения запросов
class Controller:
    def __init__(self, config):
        # Объявления
        self.config = config
        self.initial_request = self.get_initial_request()
        self.marked_raw_request = RequestMarker(self.initial_request, self.config).get_marked_request()

        analyzer = Analyzer(self.marked_raw_request, self.config)

        # # Тест Requester
        # self.response_queue = Queue()
        # requester = Requester(self.modified_requests, self.response_queue, self.config)
        # requester.run()
        # while requester.is_running():
        #     pass
        # # Тест Analyzer
        # analyzer = Analyzer(self.response_queue)
        # analyzer.print_info()
        # print("end")

    def search_hidden_parameters(self):
        pass

    def get_initial_request(self):
        """ Возвращает инициализирующий запрос

        :return: Инициализирующий запрос RequestObject
        """
        with open(self.config['Main']['file']) as f:
            initial_request = f.read()
        return RequestObject(initial_request)

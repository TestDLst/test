from request_package.request_object import RequestObject
from request_package.request_marker import RequestMarker
from core.sql_analyzer import SqlAnalyzer


# TODO: добавить в Requester метку end в конец очереди после завершения запросов
class Controller:
    def __init__(self, config):
        # Объявления
        self.config = config
        self.initial_request = self.get_initial_request()
        self.marked_raw_request = RequestMarker(self.initial_request, self.config).get_marked_request()

        analyzer = SqlAnalyzer(self.marked_raw_request, self.config)
        analyzer.analyze()

    def get_initial_request(self):
        """ Возвращает инициализирующий запрос

        :return: Инициализирующий запрос RequestObject
        """
        with open(self.config['Main']['file']) as f:
            initial_request = f.read()
        return RequestObject(initial_request)

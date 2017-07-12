import codecs

from request_package.request_object import RequestObject
from request_package.request_marker import RequestMarker
from core.common_analyzer import CommonAnalyzer
from core.sql_analyzer import SqlAnalyzer, BlindBooleanBasedSqlAnalyzer


class Controller:
    def __init__(self, config):
        # Объявления
        self.config = config
        self.initial_request = self.get_initial_request()
        self.marked_raw_request = RequestMarker(self.initial_request, self.config).get_marked_request()

        analyzer = BlindBooleanBasedSqlAnalyzer(self.marked_raw_request, self.config)
        analyzer.analyze()

    def get_initial_request(self):
        """ Возвращает инициализирующий запрос

        :return: Инициализирующий запрос RequestObject
        """
        with codecs.open(self.config['Main']['file'], 'r', encoding='utf8') as f:
            initial_request = f.read()
        return RequestObject(initial_request)

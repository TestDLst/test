import codecs

from core.analyzers.common_analyzer import CommonAnalyzer
from request_package.request_marker import RequestMarker
from request_package.request_object import RequestObject
from core.analyzers.sql_analyzer import BlindBooleanBasedSqlAnalyzer


class Controller:
    def __init__(self, properties):
        # Объявления
        self.properties = properties
        self.initial_request = self.get_initial_request()
        self.marked_raw_request = RequestMarker(self.initial_request, self.properties).get_marked_request()

        analyzer = CommonAnalyzer(self.marked_raw_request, self.properties)
        analyzer.analyze()

        # analyzer = BlindBooleanBasedSqlAnalyzer(self.marked_raw_request, self.properties)
        # analyzer.analyze()

    def get_initial_request(self):
        """ Возвращает инициализирующий запрос

        :return: Инициализирующий запрос RequestObject
        """
        with codecs.open(self.properties['Main']['file'], 'r', encoding='utf8') as f:
            initial_request = f.read()
        return RequestObject(initial_request)

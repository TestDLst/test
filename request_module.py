from collections import namedtuple


class RequestAnalyzer:
    # TODO: отмечать параметры запросах REST стиля
    def __init__(self, request='', injection_mark='FUZZ'):
        """Создает экзепляр класса RequestAnalyzer

        :param request: строка, содержащая сырой валидный запрос к серверу (например запросы из burpsuite)
        :param injection_mark: символы, разделенные пробелом, помечающие точки инъекции
        """
        self.raw_request = request
        self.injection_mark = injection_mark

        self.request_object = RequestObject(self.raw_request)

    def mark_request(self):
        pass

    def _mark_query_string(self):
        pass


class RequestObject:
    def __init__(self, request):
        self.raw_request = request
        self.market_request = ''

        self.query_string = namedtuple('query_string', 'string, method, uri, http_version')
        self.host = ''

        self.headers = dict()
        self.cookies = dict()
        self.content_type = namedtuple('content_type', 'type, subtype, attributes')
        self.content_length = 0

        self.data = ''

        self._parse_request(self.raw_request)

    def _parse_request(self, raw_request):
        """ Распаковывает сырой запрос в объект"""
        # Разбиваем сырой запрос на 'хидеры' и 'дату'
        # да, разделителями строк в запросах являются \r\n, но на винде при считывании остаются \n
        self.headers, self.data = raw_request.split('\n\n')
        query_string, self.headers = self.headers.split('\n')[0], self.headers.split('\n')[1:]

        # Пакуем строку запроса
        self.query_string.string = query_string
        self.query_string.method, self.query_string.uri, self.query_string.http_version = query_string.split(' ')

        # Пакуем хидеры
        self.headers = {header.split(': ')[0]: header.split(': ')[1] for header in self.headers}

        # Переносим Host в переменную объекта для дальнейшего удобства сборки размеченного объекта
        self.host = {'Host': self.headers.pop('Host')}

        # Пакуем кукисы
        self.cookies = self.headers.get('Cookie')
        if self.cookies:
            self.cookies = {attribute.split('=')[0]: attribute.split('=')[1] for attribute in self.cookies.split('; ')}

        # Пакуем Content-Type
        self.content_type.attributes = self.headers.get('Content-Type')
        if self.content_type.attributes:
            # Выделяем type/subtype и остальную часть
            _type, *self.content_type.attributes = self.content_type.attributes.split('; ')
            self.content_type.type, self.content_type.subtype = _type.split('/')
            self.content_type.attributes = {attribute.split('=')[0]: attribute.split('=')[1] for attribute in
                                            self.content_type.attributes}

        # Выделяем content_length для удобства сборки размченного объекта

if __name__ == '__main__':
    with open('request.txt') as f:
        request_string = f.read()

    ro = RequestObject(request_string)
    exit()

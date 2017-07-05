class RequestObject:
    def __init__(self, request, _testing_param=None):
        self._testing_param = _testing_param

        self.raw_request = request
        self.raw_response = ''
        self.market_request = ''

        self.query_string = ''
        self.method = ''
        self.url_path = ''
        self.host = ''

        # хидеры должны быть в том же порядке, в котором пришли
        self.headers = []
        self.content_type = None
        self.data = ''
        self.known_types = {'text': {'html': 'plain', 'plain': 'plain', 'xml': 'xml'},
                            'application': {'atom+xml': 'xml', 'json': 'json', 'soap+xml': 'xml', 'xhtml+xml': 'xml',
                                            'xml-dtd': 'xml', 'xop+xml': 'xml', 'xml': 'xml'}}

        self.normalize_raw_request()
        self._parse_request(self.raw_request)

    def _parse_request(self, raw_request):
        """ Распаковывает сырой запрос в объект"""
        # Разбиваем сырой запрос на 'строку запроса', 'хидеры' и 'дату'
        try:
            self.headers, self.data = raw_request.split('\r\n\r\n')
        except ValueError as ve:
            self.headers, self.data = raw_request, None

        self.query_string, *self.headers = self.headers.split('\r\n')
        self.method, self.url_path, *_ = self.query_string.split()
        self.host = self.headers[0].split(': ')[1].strip()

        self._identify_content_type()

    def _identify_content_type(self):
        """Находит хидер Content-type, парсит type и subtype и определяет по known_types форму данных"""
        content_type = next((header for header in self.headers if header.startswith('Content-Type')), None)

        if content_type:
            type, subtype = content_type.split(': ')[1].split('/')
            self.content_type = self.known_types.get(type)
            self.content_type = self.content_type.get(subtype) if self.content_type else None

    def normalize_raw_request(self):
        "Приводит сырой запрос к стандарту"
        if not '\r\n' in self.raw_request:
            self.raw_request = self.raw_request.replace('\n', '\r\n')


if __name__ == '__main__':
    with open('test_requests/request.txt') as f:
        raw_request = f.read()

    ro = RequestObject(raw_request)

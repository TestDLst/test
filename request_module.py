import re
import json


class RequestAnalyzer:
    # TODO: отмечать параметры запросах REST стиля
    def __init__(self, request, injection_mark='§ §'):
        """Создает экзепляр класса RequestAnalyzer

        :param request: строка, содержащая сырой валидный запрос к серверу (например запросы из burpsuite)
        :param injection_mark: символы, разделенные пробелом, помечающие точки инъекции
        """
        self.injection_mark = injection_mark

        self.excluded_headers = {'Host'}  # Если можно будет указывать, какие параметры пропускать
        self.all_headers = set()  # Все имена распарсенных хидеров будут здесь
        # Хидеры, которые будут добавлены в запрос, если их в нем нет
        self.extra_headers = {
            'User-Agent'
        }

        self.request_object = RequestObject(request)

        self._mark_request()

    def get_marked_request(self):
        return self.request_object.market_request

    def _mark_request(self):
        """Помечает отдельные участки запроса и собирает их вместе в self.request_object.market_request"""
        self._mark_query_string()
        self._mark_headers()
        self._mark_data()

        self.request_object.market_request = '\r\n'.join(
            [self.request_object.query_string] + self.request_object.headers) + '\r\n\r\n' + self.request_object.data

    def _mark_query_string(self):
        """Помечает значения в строке запроса"""
        method, uri, http_ver = self.request_object.query_string.split(' ')

        uri = self._mark_by_regexp(uri, '=([^&]+)')
        uri = self._mark_empty_params(uri)

        self.request_object.query_string = ' '.join([method, uri, http_ver])

    def _mark_headers(self):
        """Помечает значения в хидерах"""
        modified_headers = []

        for header in self.request_object.headers:
            try:
                name, value = header.split(': ')
                self.all_headers.add(name)

                if name not in self.excluded_headers:
                    # Эвристика
                    if (' ' not in value) or (';' not in value and '=' not in value) \
                            or (';' in value and '=' not in value):
                        value = self.injection_mark.replace(' ', value)
                    else:
                        value = self._mark_by_regexp(value, '=([^\s;]+);?')

            except ValueError as ve:
                print('[!] Exception in _mark_headers. Message: {}'.format(ve))

            modified_headers.append(': '.join([name, value]))

        self.request_object.headers = modified_headers

    # TODO: Парсить xml
    # TODO: И ещё что-нибудь
    def _mark_data(self):
        """Помечает параметры в данных"""
        content_type = self.request_object.content_type

        if content_type == 'plain':
            self._mark_data_plain()
        elif content_type == 'json':
            self._mark_data_json()
        elif content_type == 'xml':
            self._mark_data_xml()
        else:
            pass

    def _mark_data_plain(self):
        """Помечаются данные вида param1=value1&param2=value2"""
        self.request_object.data = self._mark_by_regexp(self.request_object.data, '=([^&]+)')
        self.request_object.data = self._mark_empty_params(self.request_object.data)

    def _mark_data_json(self):
        """Помечаются данные, представленные json"""
        _regexp = '''[ \[]"?([^{}\]\[]+?)["',}]'''
        data = self.request_object.data
        # Нормализуем данные
        data = json.dumps(json.loads(data))
        self.request_object.data = self._mark_by_regexp(data, _regexp)

    def _mark_data_xml(self):
        """Помечаются данные, представленные xml"""
        pass

    def _mark_by_regexp(self, string, regexp, prefix='', group=1):
        """Помечает параметры в строке по regexp'у

        :param string: Строка, в которой помечаются параметры
        :param regexp: Регулярное выражение, по которому они ищутся
        :param prefix: Префикс строки, на которую заменяется найденная группа
        :return: Измененная строка string
        """
        string = re.sub(regexp,
                        lambda x: prefix + x.group(0).replace(x.group(group),
                                                              self.injection_mark.replace(' ', x.group(group))),
                        string)
        return string

    def _mark_empty_params(self, string):
        """Помечает пустые параметры

        :param string: Строка, в которой пустые параметры ищутся
        :return: Измененная строка string
        """
        return re.sub('=(&|$)', lambda x: '=' + self.injection_mark + ('&' if '&' in x.group() else ''), string)


class RequestObject:
    def __init__(self, request):
        self.raw_request = request
        self.market_request = ''

        self.query_string = ''
        self.headers = ''
        self.content_type = 'plain'
        self.data = ''

        self.known_types = {'text': {'html': 'plain', 'plain': 'plain', 'xml': 'xml'},
                            'application': {'atom+xml': 'xml', 'json': 'json', 'soap+xml': 'xml', 'xhtml+xml': 'xml',
                                            'xml-dtd': 'xml', 'xop+xml': 'xml', 'xml': 'xml'}}

        self._parse_request(self.raw_request)

    def _parse_request(self, raw_request):
        """ Распаковывает сырой запрос в объект"""
        # Разбиваем сырой запрос на 'строку запроса', 'хидеры' и 'дату'
        # на винде лажа с \r\n, остаются \n при считывании
        self.headers, self.data = raw_request.split('\n\n')
        self.query_string, self.headers = self.headers.split('\n')[0], self.headers.split('\n')[1:]


        self._identify_content_type()

    def _identify_content_type(self):
        """Находит хидер Content-type, парсит type и subtype и определяет по known_types форму данных"""
        content_type = next((header for header in self.headers if header.startswith('Content-Type')), None)

        if content_type:
            type, subtype = content_type.split(': ')[1].split('/')
            self.content_type = self.known_types.get(type).get(subtype)


if __name__ == '__main__':
    with open('request_json.txt') as f:
        request_string = f.read()

    ra = RequestAnalyzer(request_string)
    print(ra.get_marked_request())
    exit()

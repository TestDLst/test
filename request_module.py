import re
from collections import namedtuple


class RequestAnalyzer:
    # TODO: отмечать параметры запросах REST стиля
    def __init__(self, request='', injection_mark='${ }'):
        """Создает экзепляр класса RequestAnalyzer

        :param request: строка, содержащая сырой валидный запрос к серверу (например запросы из burpsuite)
        :param injection_mark: символы, разделенные пробелом, помечающие точки инъекции
        """
        self.raw_request = request
        self.injection_mark = injection_mark

        self.included_headers = {'Accept-Language', 'Authorization', 'User-Agent', 'Content-Type', 'Referer', 'Cookie'}
        # Если можно будет указывать, какие параметры пропускать
        self.excluded_headers = {'Host'}

        self.request_object = RequestObject(self.raw_request)

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

        params = re.findall('=([^&]+)', uri)
        for param in params:
            uri = uri.replace(param, self.injection_mark.replace(' ', param))

        self.request_object.query_string = ' '.join([method, uri, http_ver])

    def _mark_headers(self):
        """Помечает значения в хидерах"""
        interesting_headers = self.included_headers - self.excluded_headers
        modified_headers = []

        for header in self.request_object.headers:
            name, value = header.split(': ')
            if name in interesting_headers:
                'Эвристика'
                if (' ' not in value) or (';' not in value and '=' not in value) or (';' in value and not '=' in value):
                    value = self.injection_mark.replace(' ', value)
                else:
                    params = re.findall('=([\S]+);?', value)
                    for param in params:
                        value = value.replace(param, self.injection_mark.replace(' ', param))

            modified_headers.append(': '.join([name, value]))

        self.request_object.headers = modified_headers

    def _mark_data(self):
        """Помечает параметры в данных"""
        if self.request_object.content_type.type in ['text', 'application'] \
                and self.request_object.content_type.subtype in ['x-www-form-urlencoded', 'html', 'plain']:
            self._mark_data_plain()
        elif self.request_object.content_type.type in [''] and self.request_object.content_type.subtype in ['']:
            pass

    def _mark_data_plain(self):
        """Помечаются данные вида param1=value1&param2=value2"""
        self.request_object.data = self._mark_by_regexp(self.request_object.data, '=([^&]+)')

    def _mark_by_regexp(self, string, regexp):
        """Помечает параметры в строке по regexp'у

        :param string: Строка, в которой помечаются параметры
        :param regexp: Регулярное выражение, по которому они ищутся
        :return: Измененная строка string
        """
        # TODO: исправить: Kak_davno_Vy_rabotaete_v_universitete=${${${${${${${${${1}}}}}}}}}
        params = re.findall(regexp, string)
        for param in params:
            string = string.replace(param, self.injection_mark.replace(' ', param))
        return string


class RequestObject:
    def __init__(self, request):
        self.raw_request = request
        self.market_request = ''

        self.query_string = ''
        self.headers = ''
        self.content_type = namedtuple('content_type', 'type, subtype')
        self.data = ''

        self._parse_request(self.raw_request)

    def _parse_request(self, raw_request):
        """ Распаковывает сырой запрос в объект"""
        # Разбиваем сырой запрос на 'строку запроса', 'хидеры' и 'дату'
        # на винде лажа с \r\n, остаются \n при считывании
        self.headers, self.data = raw_request.split('\n\n')
        self.query_string, self.headers = self.headers.split('\n')[0], self.headers.split('\n')[1:]

        # Находим хидер Content-type и парсим оттуда type и subtype
        _content_type = next((header for header in self.headers if header.startswith('Content-Type')), None)
        self.content_type.type, self.content_type.subtype = _content_type.split(': ')[1].split('; ')[0].split('/')


if __name__ == '__main__':
    with open('request.txt') as f:
        request_string = f.read()

    ra = RequestAnalyzer(request_string)
    print(ra.request_object.market_request)
    exit()

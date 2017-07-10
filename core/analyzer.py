import random
import re
import string
from queue import Queue

from request_package.request_modifier import RequestModifier
from request_package.request_object import RequestObject
from request_package.requester import Requester


# TODO: encode пейлоадов
class Analyzer:
    def __init__(self, marked_raw_request, config):
        self.CONTENT_LENGTH = 1
        self.ROW_COUNT = 2
        self.REQUEST_TIME = 4

        self.config = config
        self.marked_raw_request = marked_raw_request

        self.reflected_patterns = set()
        self._reflect_payload = ''
        self.time_delta = (None, None)

        self.init_request_obj = self.get_initial_request()
        self.response_queue = Queue()
        self.standard_response = self.get_standard_response()

    def get_modified_requests(self, payloads, flags=7):
        """ Возвращает список измененных запросов

        Модифицирует части начального запроса согласно параметру flags. Для модификации строки запроса используется
        QUERY_STRING (число 1), для модификации заголовков - HEADERS (число 2), для данных - DATA (число 4). Для комби-
        нации модификаций используй сумму соответствующих констант.
        :
        param payloads: Нагрузки, дополняющие помеченные параметры
        :param flags: Число, указывающее, какие части запроса модифицировать
        :return: Список объектов RequestObject
        """
        request_modifier = RequestModifier(self.marked_raw_request, payloads, self.config)
        a = request_modifier.get_modified_requests(flags=flags)
        return a

    def get_payloads(self, payload_path):
        """ Возвращает список нагрузок из

        :param payload_path: путь до файла с нагрузками относительно дирестории payloads
        :return: Список нагрузок payloads
        """
        with open(self.config['Program']['script_path'] + '/payloads' + payload_path) as f:
            payloads = f.read().split('\n')
        return payloads

    def get_initial_request(self):
        """ Возвращает инициализирующий запрос

        :return: Инициализирующий запрос RequestObject
        """
        with open(self.config['Main']['file']) as f:
            initial_request = f.read()
        return RequestObject(initial_request)

    def get_standard_response(self):
        """ Возвращает стандартный ответ на стандартный заспрос из init_request_obj

        С помощью объекта Requester выполяет стандартный запрос и помещает ответ в объект ResponseObject. Помимо прочего
        инициализирует переменнуж self.time_delta. Является необходимой частью работы анализера.
        :return: Объект ResponseObject
        """
        print('[!] Получение стандартного ответа')
        requester = Requester([self.get_initial_request()], self.response_queue, self.config)
        standard_response = requester.get_standard_response(self.init_request_obj)
        self.time_delta = (standard_response.request_time, standard_response.request_time)
        return standard_response

    def is_interesting_behavior(self, response_obj, flags=7):
        """

        :param response_obj:
        :param flags: Число. 1 - учитывать длину контента, 2 - учитывать кол-во строк, 4 - учитывать время запроса.
        :return:
        """

        if flags & self.CONTENT_LENGTH and response_obj.content_length != self.standard_response.content_length:
            return True
        if flags & self.ROW_COUNT and response_obj.row_count != self.standard_response.row_count:
            return True
        if flags & self.REQUEST_TIME and not self.time_delta[0] <= response_obj.request_time <= self.time_delta[1]:
            return True
        return False

    def analyze(self):
        raise Exception('Не реализовано')

    def print_standard_resp_info(self):
        print_format = '[!] Информация по стандартному ответу\n\tСтандартная длина контента: {content_length}' \
                       '\n\tСтандартное количество строк: {row_count}\n\tВременной запрос: {min}/{max}\n'
        kwargs = {
            'content_length': self.standard_response.content_length,
            'row_count': self.standard_response.row_count,
            'min': self.time_delta[0],
            'max': self.time_delta[1]
        }
        print(print_format.format(**kwargs))

    def clean_reflected_rows(self, response_obj):
        """ Удаляет рефлексирующие строки в response_obj по паттернам из self.reflected_patterns

        :param response_obj: Объект ответа, который необходимо отчистить от  рефлексирующих строк
        :return:
        """
        raw_response = response_obj.raw_response
        for reflect_pattern in self.reflected_patterns:
            try:
                raw_response = re.sub(reflect_pattern, '', raw_response)
                response_obj.rebuild(raw_response)
            except Exception as e:
                print(reflect_pattern)
                print(e)
        return response_obj

    def detect_reflected_patterns(self):
        """ Определяет паттерны для рефлексирующих параметров в теле ответа

        Генерирует специальную нагрузку, которая вставляется в каждый промаркированный параметр стандартного запроса.
        Затем в телах ответов ищутся строки по паттерну \s+?.+?({reflected}).+?\n, тем самым определяя паттерны для
        рефлексирующих строк в ответах.

        Рефлексирующие паттерны кладутся во множество reflected_patterns с помощью метода self._feed_reflected_rows.
        Параллельно замеряется минимум и максимум времени запросов в переменную self.time_delta
        """
        resp_queue = Queue()

        self._reflect_payload = ''.join([random.choice(string.ascii_letters) for i in range(6)])
        requests = self.get_modified_requests([self._reflect_payload])

        requester = Requester(requests, resp_queue, self.config)
        requester.run()

        print('[!] Определение рефлексирующих паттернов')
        while requester.is_running() or not resp_queue.empty():
            resp = resp_queue.get()
            self.time_delta = (min(resp.request_time, self.time_delta[0]), max(resp.request_time, self.time_delta[1]))

            reflected = self._reflect_payload

            pattern = '\s+?.+?({reflected}).+?\n'.format(reflected=reflected)
            re.sub(pattern, self._feed_reflected_rows, resp.raw_response)

    def _feed_reflected_rows(self, match):
        start, _ = match.regs[0]
        stop, _ = match.regs[1]

        search_additional = '.+?\n'
        reflect_pattern = match.string[start:stop] + search_additional
        reflect_pattern = self._escape_pattern(reflect_pattern[:-len(search_additional)])\
                          + reflect_pattern[-len(search_additional):]

        self.reflected_patterns |= set([reflect_pattern])

    def _escape_pattern(self, pattern):
        pattern = pattern.replace('"', '\"')  # экранируем двойные кавычки
        pattern = pattern.replace('(', '\(').replace(')', '\)')  # экранируем скобки
        pattern = pattern.replace('[', '\[').replace(']', '\]')  # экранируем скобки
        pattern = pattern.replace('$', '\$')
        pattern = pattern.replace('^', '\^')
        pattern = pattern.replace('.', '\.').replace('+', '\+').replace('?', '\?')

        return pattern

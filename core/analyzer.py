import random
import re
import string

from queue import Queue

from request_package.request_object import RequestObject
from request_package.request_modifier import RequestModifier
from request_package.requester import Requester


# TODO: encode пейлоадов
class Analyzer:
    def __init__(self, marked_raw_request, config):
        self.config = config
        self.marked_raw_request = marked_raw_request

        self.init_request_obj = self.get_initial_request()
        self.response_queue = Queue()

        self.reflected_patterns = set()
        self._reflect_payload = ''
        self.time_delta = (None, None)

    def get_modified_requests(self, payloads):
        """ Возвращает список модифицированных запросов

        :param payloads: Нагрузки, дополняющие помеченные параметры
        :return: Список объектов RequestObject
        """
        request_modifier = RequestModifier(self.marked_raw_request, payloads, self.config)
        a = request_modifier.get_modified_requests()
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
        requester = Requester([self.get_initial_request()], self.response_queue, self.config)
        standard_response = requester.get_standard_response(self.init_request_obj)
        self.time_delta = (standard_response.request_time, standard_response.request_time)
        return standard_response

    def analyze(self):
        raise Exception('Не реализовано')

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

        requester = Requester(requests,resp_queue,self.config)
        requester.run()

        while requester.is_running() or not resp_queue.empty():
            resp = resp_queue.get()
            pattern = '\s+?.+?({reflected}).+?\n'.format(reflected=self._reflect_payload)
            self.time_delta = (min(resp.request_time, self.time_delta[0]), max(resp.request_time, self.time_delta[1]))
            re.sub(pattern, self._feed_reflected_rows, resp.raw_response)

    def _feed_reflected_rows(self, match):
        start, _ = match.regs[0]
        stop, _ = match.regs[1]
        reflect_pattern = match.string[start:stop] + '.+?\n'
        reflect_pattern = reflect_pattern.replace('"', '\\"') # экранируем двойные кавычки
        reflect_pattern = reflect_pattern.replace('(', '\\(').replace(')','\\)') # экранируем скобки
        reflect_pattern = reflect_pattern.replace('[', '\\[').replace(']','\\]') # экранируем скобки
        reflect_pattern = reflect_pattern.replace('$', '\\$')
        reflect_pattern = reflect_pattern.replace('^', '\\^')

        self.reflected_patterns |= set([reflect_pattern])
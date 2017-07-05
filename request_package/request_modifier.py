import re

from request_package.request_object import RequestObject


class RequestModifier:
    def __init__(self, marked_request, payloads, config):
        """ Конструктор

        :param marked_request: строка с промаркированным запросом
        :param payloads: список пейлоадов
        :param config: конфигурационный файл
        """
        self.marked_request = marked_request
        self.payloads = payloads
        self.config = config

        self.injection_mark = self.config['Program']['injection_mark']
        self.modified_requests = []

    # TODO: исправить проблему с пустым значением параметра
    def get_modified_requests(self):
        """ Возвращает список измененных запросов

        :return: Список request_object'ов с измененными параметрами
        """
        # pattern = '.+?'.join([self.injection_mark] * 2)
        pattern = '{mark}(){mark}|{mark}(.+?){mark}'.format(mark=self.injection_mark)
        re.sub(pattern, self._modify_request, self.marked_request)

        return self.modified_requests

    def _modify_request(self, match):
        """ Модифицирует промаркированный параметр всеми нагрузками из self.payloads

        :param match: match объект модуля re
        """
        start, end = match.regs[0]
        for payload in self.payloads:
            _modified_request = match.string[:start] + match.string[start:end] + payload + match.string[end:]
            _modified_request = _modified_request.replace(self.injection_mark, '')
            self.modified_requests.append(RequestObject(_modified_request))
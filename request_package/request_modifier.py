import re


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

    def get_modified_requests(self):
        """ Возвращает список измененных запросов

        :return: Список request_object'ов с измененными параметрами
        """
        # TODO: Исправить траблу с юникодом в injection_mark
        pattern = '.+?'.join([self.injection_mark] * 2)

        for payload in self.payloads:
            _modified_request = re.sub(pattern, lambda x: x.group(0) + payload, self.marked_request)
            _modified_request = _modified_request.replace(self.injection_mark, '')
            self.modified_requests.append(_modified_request)

        return self.modified_requests

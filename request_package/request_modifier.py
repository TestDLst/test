import re

from request_package.request_object import RequestObject


class RequestModifier:
    def __init__(self, marked_request, payloads, config):
        """ Конструктор

        :param marked_request: строка с промаркированным запросом
        :param payloads: список пейлоадов
        :param config: конфигурационный файл
        """
        self.marked_request = RequestObject(marked_request)
        self.payloads = payloads
        self.config = config

        self.injection_mark = self.config['Program']['injection_mark']
        self.modified_requests = []

    def get_modified_requests(self):
        """ Возвращает список измененных запросов

        :return: Список request_object'ов с измененными параметрами
        """
        # модифицируем строку запроса и собираем остальную часть
        # модифицируем хидеры и собираем остальные части
        # модифицируем data и собираем остальные части
        self._modify_query_string()
        # pattern = '{mark}(){mark}|{mark}(.+?){mark}'.format(mark=self.injection_mark)
        # re.sub(pattern, self._modify_request, self.marked_request.)

        return self.modified_requests

    def _modify_query_string(self):
        pattern = '([^?&]+)=({mark}{mark}|{mark}.+?{mark})'.format(mark=self.injection_mark)
        re.sub(pattern, self._test1, self.marked_request.query_string)

    def _test1(self, match):
        start, end = match.regs[2]
        param_name = match.string[match.regs[1][0]:match.regs[1][1]]
        for payload in self.payloads:
            modified_value = match.string[start:end] + payload
            modified_query_string = match.string[:start] + modified_value + match.string[end:]
            modified_raw_request = modified_query_string + '\r\n'.join(self.marked_request.headers)\
                                    + '\r\n\r\n' + self.marked_request.data
            modified_raw_request = modified_raw_request.replace(self.injection_mark, '')
            testing_param = param_name + '=' + modified_value.replace(self.injection_mark, '')

            self.modified_requests.append(RequestObject(modified_raw_request, _testing_param=testing_param))

    def _modify_headers(self):
        pattern = '([^?&]+)=({mark}{mark}|{mark}.+?{mark})'.format(mark=self.injection_mark)
        re.sub(pattern, self._test1, self.marked_request.query_string)

    def _test2(self, match):
        pass


    def _modify_request(self, match):
        """ Модифицирует промаркированный параметр всеми нагрузками из self.payloads

        :param match: match объект модуля re
        """
        # модифицировать отдельно строку запроса, хидеры и данные

        # start, end = match.regs[0]
        # for payload in self.payloads:
        #     _modified_request = match.string[:start] + match.string[start:end] + payload + match.string[end:]
        #     _modified_request = _modified_request.replace(self.injection_mark, '')
        #     self.modified_requests.append(RequestObject(_modified_request))

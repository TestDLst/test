from request_package.request_modifier import RequestModifier


class StatisticObject:
    def __init__(self, response):
        pass


class Analyzer:
    def __init__(self, request):
        self.request = request
        self.sql_analyzer = SqlAnalyzer(self.request)

    def get_modified_requests(self, payloads):
        """ Возвращает список модифицированных запросов

        :param payloads: Нагрузки, дополняющие помеченные параметры
        :return: Список объектов RequestObject
        """
        request_modifier = RequestModifier(self.marked_raw_request, payloads, self.config)
        return request_modifier.get_modified_requests()

    def get_payloads(self, payload_path):
        """

        :param payload_path: путь до файла с нагрузками относительно дирестории payloads
        :return: Список нагрузок payloads
        """
        with open(self.config['Program']['script_path']+'/payloads' + payload_path) as f:
            payloads = f.read().split('\n')
        return payloads


class SqlAnalyzer(Analyzer):
    def __init__(self, request):
        self.request = request
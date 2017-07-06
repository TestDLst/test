class StatisticObject:
    def __init__(self, response):
        self.raw_response = response.raw_response
        self.param = response._testing_param
        self.length = len(self.raw_response)

    def print_info(self):
        print("%d, %s" % (self.length, self.param))


class Analyzer:
    def __init__(self, response_queue):
        self.results = []

        while not response_queue.empty():
            self._analyze_response(response_queue.get())

    def _analyze_response(self, response):
        self.results.append(StatisticObject(response))

    def print_info(self):
        for statistic_obj in self.results:
            statistic_obj.print_info()
class StatisticObject:
    def __init__(self, response):
        self.raw_response = response.raw_response
        self.param = response._testing_param
        self.length = len(self.raw_response)

    def print_info(self):
        print("%s, %d" % (self.param, self.length))


class Analyzer:
    def __init__(self, response_queue):
        self.results = []

        while not response_queue.empty():
            self._analyze_response(response_queue.get())

    def _analyze_response(self, response):
        self.results.append(StatisticObject(response))
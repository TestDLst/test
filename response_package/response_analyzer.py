class StatisticObject:
    def __init__(self):
        pass


class Analyzer:
    def __init__(self, response_queue):
        self.results = []

        while not response_queue.empty():
            self._analyze_response(response_queue.get())

    def _analyze_response(self, response):
        self.results.append(StatisticObject(response))
class ResponseObject:
    def __init__(self, raw_response=None,request_object=None, request_time=None):
        self.request_object = request_object
        self.testing_param = None if not request_object else request_object.testing_param
        self.raw_response = raw_response

        self.request_time = request_time
        self.content_length = len(self.raw_response)
        self.row_length = len(self.raw_response.splitlines())

    def rebuild(self, raw_response):
        self.raw_response = raw_response

        self.content_length = len(raw_response)
        self.row_length = len(self.raw_response.splitlines())
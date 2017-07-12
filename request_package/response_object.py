import re


class ResponseObject:
    def __init__(self, raw_response=None, request_object=None, request_time=None, response_code=None, index=None):
        self.index = index

        self.request_object = request_object
        self.raw_response = raw_response

        self.test_info = self.request_object.test_info
        self.testing_param = self.request_object.testing_param
        self.payload = self.request_object.payload

        self.request_time = request_time
        self.content_length = len(self.raw_response)
        self.row_count = len(self.raw_response.splitlines())
        self.word_count = len(re.findall('[\S]+',self.raw_response))
        self.response_code = response_code

    def rebuild(self, raw_response):
        self.raw_response = raw_response

        self.content_length = len(raw_response)
        self.row_count = len(self.raw_response.splitlines())
        self.word_count = len(re.findall('[\S]+', self.raw_response))
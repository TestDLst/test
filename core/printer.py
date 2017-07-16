import re

class Printer:
    def __init__(self, properties=None, section_name=None):
        self.properties = properties
        self.section_name = section_name


        getattr(self, 'init_{}_printer')

    def init_common_analyzer_printer(self):
        pass

    # TODO: доработать
    def _translate_section_name(self, section_name):
        return re.sub('[a-z][A-Z]','',section_name)


if __name__ == '__main__':
    pass
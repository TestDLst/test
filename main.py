import argparse


class Main:
    def __init__(self):
        self.parser = self.create_parser()
        self.check_arguments()

        self.config = None
        self.controller = None

    def create_parser(self):
        parser = argparse.ArgumentParser()
        parser.add_argument('-u', '--url', dest='url', help='Адрес приложения (https://example.com:83)')
        parser.add_argument('-f', '--file', dest='file', help='Файл с запросом')
        parser.add_argument('-t', '--threads', dest='threads', type=int, help='Количество потоков')
        return parser

    def check_arguments(self):
        pass

    def read_config(self):
        pass

if __name__ == '__main__':
    main = Main()

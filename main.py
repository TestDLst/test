import argparse
import configparser
import os
import re

from controller.controller import Controller


class Main:
    def __init__(self):
        self.parser = argparse.ArgumentParser()
        self.arguments = self.get_arguments()
        self.check_arguments()

        self.config = self.read_config()
        self.merge_args_to_config()

        self.controller = Controller(self.arguments, self.config)

    def get_arguments(self):
        main_group = self.parser.add_argument_group('Main')
        main_group.add_argument('-u', '--url', dest='url', help='Адрес приложения (https://example.com:83)')
        main_group.add_argument('-f', '--file', dest='file', help='Файл с запросом')
        main_group.add_argument('-t', '--threads', dest='threads', type=int, help='Количество потоков')

        config_group = self.parser.add_argument_group('Config')
        config_group.add_argument('--update', dest='update', action='store_true',
                                  help='Обновить конфигурационный файл (config.ini по умолчанию). \
                  Используй --config-file, если файл не расположен по стандартному пути')
        config_group.add_argument('--config-file', dest='config_file', help='Путь до конфигурационного файла')

        return self.parser.parse_args()

    # Потестить
    def check_arguments(self):
        if self.arguments.file and not os.path.isfile(self.arguments.file):
            print('[!] Указанного файла по пути --file не существует')
            self.parser.print_help()
            exit()
        if self.arguments.config_file and not os.path.isfile(self.arguments.file):
            print('[!] Указанного конфигурационного файла по пути --config-file не существует')
            self.parser.print_help()
            exit()

    # Потестить
    def merge_args_to_config(self):
        self.config['MAIN']['url'] = self.arguments.url
        self.config['MAIN']['file'] = self.arguments.file
        self.config['MAIN']['threads'] = self.arguments.threads

        # Парсим --url
        protocol = self.arguments.url.split('://')[0] if '://' in self.arguments.url\
            else self.config['REQUEST_INFO']['protocol']
        port = re.search(':(\d+)\/?')
        port = port.group(1) if port else self.config['REQUEST_INFO']['port']

        # Распихиваем --url по конфигу
        self.config['REQUEST_INFO']['protocol'] = protocol
        self.config['REQUEST_INFO']['port'] = port

    def read_config(self, path=None):
        config = configparser.ConfigParser()
        # Добавить Try\Catch на корявый конфиг
        if not path:
            config.read('config.ini')
        else:
            config.read(path)
        return config

    def save_current_config(self):
        pass


if __name__ == '__main__':
    main = Main()

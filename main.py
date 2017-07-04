import argparse
import configparser
import os
import re

from controller.controller import Controller


# TODO: Создавать конфиг файл. В случае его отсутствия предлагать создать новый
class Main:
    def __init__(self):
        self.parser = argparse.ArgumentParser()
        self.arguments = self.get_arguments()

        self.check_config_exist()
        self.config_path = self.arguments.config_file if self.arguments.config_file else 'config.ini'
        self.config = self.read_config(self.config_path)

        self._test()
        self.check_arguments()

        self.merge_args_to_config()

        if self.arguments.update_config:
            self.save_current_config()

        # После merge передавать только self.config
        self.controller = Controller(self.config)

    # Потестить
    def get_arguments(self):
        main_group = self.parser.add_argument_group('Main')
        main_group.add_argument('-u', '--url', dest='url', help='Адрес приложения (https://example.com:83)')
        main_group.add_argument('-f', '--file', dest='file', help='Файл с запросом')
        main_group.add_argument('-t', '--threads', dest='threads', type=int, help='Количество потоков')

        config_group = self.parser.add_argument_group('Config')
        config_group.add_argument('--update', dest='update_config', action='store_true',
                                  help='Обновить конфигурационный файл (config.ini по умолчанию). \
                  Используй --config-file, если файл не расположен по стандартному пути')
        config_group.add_argument('--config-file', dest='config_file', help='Путь до конфигурационного файла')

        return self.parser.parse_args()

    # Потестить
    def check_arguments(self):
        _args, _cfg = self.arguments, self.config

        if not _args.url and not _cfg['MAIN']['url']:
            self._print_error_message('Не найден url адрес цели')
        if _args.file and not os.path.isfile(_args.file) or not _args.file and not _cfg['MAIN']['file']:
            self._print_error_message('Укажите коррекнтый путь до запроса через --file или в конфигурационном файле')

        del _args, _cfg

    def check_config_exist(self):
        _args = self.arguments

        if _args.config_file and not os.path.isfile(_args.file):
            self._print_error_message('Указанного конфигурационного файла по пути --config-file не существует')
        if not os.path.isfile('config.ini'):
            self._print_error_message('Не удалось найти конфигурационный файл config.ini')

        del _args

    def _print_error_message(self, message):
        print('[!] {message}'.format(message=message))
        self.parser.print_help()
        exit()

    # Потестить
    def merge_args_to_config(self):
        if self.arguments.url:
            self.config['Main']['Url'] = self.arguments.url
        if self.arguments.url:
            self.config['Main']['File'] = self.arguments.file
        if self.arguments.threads:
            self.config['Main']['Threads'] = str(self.arguments.threads)

        # Парсим --url
        protocol = self.arguments.url.split('://')[0] if '://' in self.arguments.url \
            else self.config['RequestInfo']['Protocol']
        port = re.search(':(\d+)\/?', self.arguments.url)
        port = port.group(1) if port else self.config['RequestInfo']['Port']

        # Распихиваем --url по конфигу
        self.config['RequestInfo']['Protocol'] = protocol
        self.config['RequestInfo']['Port'] = port

    # Потестить нестандартный путь
    def read_config(self, path=None):
        config = configparser.ConfigParser()
        # Добавить Try\Catch на корявый конфиг
        if not path:
            config.read('config.ini')
        else:
            config.read(path)
        return config

    def save_current_config(self):
        with open(self.config_path,'w') as config_file:
            self.config.write(config_file)

    def _test(self):
        self.arguments.url = 'http://monitoring.kantiana.ru/'
        self.arguments.file = 'request.txt'
        self.arguments.threads = 10
        self.arguments.update_config = True


if __name__ == '__main__':
    main = Main()

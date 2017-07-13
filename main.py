import argparse
import string
import codecs
import configparser
import os
import sys
from urllib.parse import urlparse

from controller.controller import Controller


# TODO: Создавать конфиг файл. В случае его отсутствия предлагать создать новый
# TODO: Добавить --exclude/--include параметры
# TODO: --max-rate пакетов
class Main:
    def __init__(self):
        self.parser = argparse.ArgumentParser()
        self.arguments = self.get_arguments()
        self.script_path = os.path.dirname(os.path.realpath(__file__))

        self.check_config_exist()
        self.config_path = self.arguments.config_file if self.arguments.config_file else 'config.ini'
        self.config = self.read_config(self.config_path)

        # Указываем параметры без консоли
        self._test()
        self.check_arguments()

        self.merge_args_to_config()

        if self.arguments.update_config:
            self.save_current_config()

        # Для импорта по пути относительно main.py
        # Потестить
        sys.path.append(self.script_path)

        self.controller = Controller(self.config)

    # Потестить
    def get_arguments(self):
        main_group = self.parser.add_argument_group('Main')
        main_group.add_argument('-u', '--url', dest='url', help='Адрес приложения (https://example.com:83)')
        main_group.add_argument('-f', '--file', dest='file', help='Файл с запросом')
        main_group.add_argument('-w', '--wordlist', dest='wordlist', default='fuzzing/metacharacters.txt',
                                help='Путь до словаря (абсолютный, относительный, от директории payloads)')
        main_group.add_argument('-t', '--threads', dest='threads', type=int, help='Количество потоков')
        main_group.add_argument('--proxy', dest='proxy',
                                help='Адрес прокси-сервера (http://127.0.0.1:8080, socks5://127.0.0.1:9050, ...)')

        config_group = self.parser.add_argument_group('Config')
        config_group.add_argument('--update', dest='update_config', action='store_true',
                                  help='Обновить конфигурационный файл (config.ini по умолчанию). \
                  Используй --config-file, если файл не расположен по стандартному пути')
        config_group.add_argument('--config-file', dest='config_file', help='Путь до конфигурационного файла')

        return self.parser.parse_args()

    # Потестить
    def check_arguments(self):
        _args, _cfg = self.arguments, self.config

        # Указан ли url
        if not _args.url and not _cfg['Main']['url']:
            self._print_error_message('Не найден url адрес цели')

        # Указан ли путь до запроса
        if _args.file and not os.path.isfile(_args.file) or not _args.file and not _cfg['Main']['file']:
            self._print_error_message('Укажите коррекнтый путь до запроса через --file или в конфигурационном файле')

        # Если словарь задан через параметр
        if _args.wordlist:
            if not os.path.isfile(_args.wordlist) and not os.path.isfile('payloads/'+_args.wordlist):
                self._print_error_message('Укажите коррекнтый путь до словаря через -w')
        # Если есть запись в конфиге (должен хранится полный путь)
        elif _cfg['Main']['wordlist']:
            if not os.path.isfile(_cfg['Main']['wordlist']):
                self._print_error_message('Укажите коррекнтый путь до словаря через -w')
        # Если нет упоминаний о словаре
        else:
            self._print_error_message('Укажите коррекнтый путь до словаря через -w')

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
        # Указываем путь до main.py
        self.config['Program']['script_path'] = self.script_path
        self.config['Program']['payload_path'] = self.script_path + '/payloads/'

        if self.arguments.url:
            self.config['Main']['url'] = self.arguments.url

            url = urlparse(self.arguments.url)
            url_scheme = url.scheme if url.scheme else 'http'
            url_port = url.port if url.port else ('80' if url_scheme == 'http' else '443')

            self.config['RequestInfo']['scheme'] = url_scheme
            self.config['RequestInfo']['port'] = url_port

        if self.arguments.file:
            self.config['Main']['file'] = self.arguments.file
        if self.arguments.threads:
            self.config['Main']['threads'] = str(self.arguments.threads)

        # Парсим --url

        # Распихиваем --url по конфигу


        # Указываем путь до словаря
        if self.arguments.wordlist:
            if os.path.isfile(self.arguments.wordlist):
                self.config['Main']['wordlist'] = self.arguments.wordlist
            elif os.path.isfile('payloads/' + self.arguments.wordlist):
                self.config['Main']['wordlist'] = self.script_path + '/payloads/' + self.arguments.wordlist
            else:
                raise Exception('Беда со словарем')

        # Парсим --proxy
        if self.arguments.proxy:
            proxy = urlparse(self.arguments.proxy)
            proxy_scheme = proxy.scheme
            proxy_host = proxy.hostname
            proxy_port = str(proxy.port)

            # Распихиваем --proxy
            self.config['Proxy']['scheme'] = proxy_scheme
            self.config['Proxy']['host'] = proxy_host
            self.config['Proxy']['port'] = proxy_port

    # Потестить нестандартный путь
    def read_config(self, path=None):
        config = configparser.ConfigParser()
        # Добавить Try\Catch на корявый конфиг
        if not path:
            # config.read_file(open('config.ini','rb',encoding='utf8'))
            config.read_file(codecs.open('config.ini', 'r', encoding='utf8'))
        else:
            config.read_file(codecs.open(path, 'r', encoding='utf8'))
        return config

    def save_current_config(self):
        with codecs.open(self.config_path, 'w', encoding='utf8') as config_file:
            self.config.write(config_file)

    def _test(self):
        self.arguments.url = 'https://a1-market.ru/'
        self.arguments.file = 'request.txt'
        self.arguments.threads = 10
        self.arguments.wordlist = 'fuzzing/metacharacters.txt'
        # self.arguments.proxy = 'http://127.0.0.1:8080'
        self.arguments.update_config = True


if __name__ == '__main__':
    main = Main()

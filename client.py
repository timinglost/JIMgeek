from socket import socket, AF_INET, SOCK_STREAM
import time, sys, logging, threading
from utils import *
import log.client_log_config
from functools import wraps
import inspect
from metaclasses import ClientVerifier


class ClientGet(threading.Thread, metaclass=ClientVerifier):
        def __init__(self, sock, client_name):
                self.s = sock
                self.client_name = client_name
                super().__init__()

        def run(self):
                while True:
                        message = get_data(self.s, config)
                        if m_config['ACTION'] in message and message[m_config['ACTION']] == m_config['JOIN'] and \
                                m_config['FROM'] in message:
                                print(f'{message[m_config["FROM"]]} присоединился к чату.')
                        if m_config['ACTION'] in message and message[m_config['ACTION']] == 'msg' and \
                                m_config['FROM'] in message and m_config['MESSAGE'] in message and \
                                m_config['TIME'] in message:
                                print(f'{message[m_config["FROM"]]}: {message[m_config["MESSAGE"]]}')
                        if config['ACTION'] in message and message[config['ACTION']] == m_config['LEAVE'] and \
                                config['TIME'] in message:
                                print(f'{message[config["ACCOUNT_NAME"]]} покинул чат.')


class ClientPost(threading.Thread):
        def __init__(self, sock, client_name):
                self.s = sock
                self.client_name = client_name
                super().__init__()
        def run(self):
                self.create_join_message()
                print(f'Добро пожаловать в чат {self.client_name}!')
                while True:
                        command = input('Введите команду "m" для сообщения, "e" для выхода: ')
                        if command == 'm':
                                self.create_message()
                        elif command == 'e':
                                self.create_exit_message()
                                print('Завершение соединения.')
                                time.sleep(0.5)
                                break
                        else:
                                print('Команда не распознана, попробойте снова.')

        def create_join_message(self):
                message_dict = {
                        m_config['ACTION']: m_config['JOIN'],
                        m_config['TIME']: time.time(),
                        m_config['FROM']: self.client_name
                }
                post_data(self.s, message_dict, config)

        def create_message(self):
                message = input('Введите сообщение для отправки: ')
                message_dict = {
                        m_config['ACTION']: 'msg',
                        m_config['FROM']: self.client_name,
                        m_config['TIME']: time.time(),
                        m_config['MESSAGE']: message
                }
                post_data(self.s, message_dict, config)

        def create_exit_message(self):
                message_dict = {
                        config['ACTION']: m_config['LEAVE'],
                        config['TIME']: time.time(),
                        config['ACCOUNT_NAME']: self.client_name
                }
                post_data(self.s, message_dict, config)


def main():
        client_log = logging.getLogger('client_log_config')
        try:
                if '-p' in sys.argv:
                        port = int(sys.argv[sys.argv.index('-p') + 1])
                else:
                        port = config['DEFAULT_PORT']
                if not 65535 >= port >= 1024:
                        raise ValueError
        except IndexError:
                client_log.warning('После -\'p\' необходимо указать порт')
                sys.exit(1)
        except ValueError:
                client_log.warning('Порт должен быть указан в пределах от 1024 до 65535')
                sys.exit(1)
        try:
                if '-a' in sys.argv:
                        address = sys.argv[sys.argv.index('-a') + 1]
                else:
                        address = config['DEFAULT_IP_ADDRESS']

        except IndexError:
                client_log.warning('После \'a\'- необходимо указать адрес для ')
                sys.exit(1)
        try:
                if '-rw' in sys.argv:
                        console = int(sys.argv[sys.argv.index('-rw') + 1])
                else:
                        console = 1
        except IndexError:
                client_log.warning('После \'rw\'- необходимо указать команду на чтение(0) или на запись (1)')
                sys.exit(1)
        try:
                if '-name' in sys.argv:
                        client_name = sys.argv[sys.argv.index('-name') + 1]
                else:
                        client_name = 'anonymous'
        except IndexError:
                client_log.warning('После \'name\'- необходимо указать имя')
                sys.exit(1)
        s = socket(AF_INET, SOCK_STREAM)
        try:
                s.connect((address, port))
                client_log.info('Установленно подключение')
                if console == 0:
                        receiver = ClientGet(s, client_name)
                        # receiver = threading.Thread(target=message_from_server, args=(s, client_name, config_message, config))
                        # receiver.daemon = True
                        receiver.start()
                if console == 1:
                        user_interface = ClientPost(s, client_name)
                        # user_interface = threading.Thread(target=massage_post, args=(s, client_name, m_config, config))
                        # receiver.daemon = True
                        user_interface.start()
        except ConnectionRefusedError:
                client_log.error('400: Bad Request')


if __name__ == '__main__':
        client_log = logging.getLogger('client_log_config')
        config = load_config('config.yaml')
        m_config = load_config('config_massag.yaml')
        main()

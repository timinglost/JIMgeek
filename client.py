from socket import socket, AF_INET, SOCK_STREAM
import time, sys, logging, threading
from utils import *
import log.client_log_config
from functools import wraps
import inspect


def log(func):
        @wraps(func)
        def call(*args, **kwargs):
                client_log_use = logging.getLogger('client_log_config_use')
                client_log_use.setLevel(logging.INFO)

                my_file_handler_use = logging.FileHandler('log/client.log')
                client_formatter_use = logging.Formatter("%(asctime)s - %(message)s ")
                my_file_handler_use.setFormatter(client_formatter_use)
                my_file_handler_use.setLevel(logging.INFO)
                client_log_use.addHandler(my_file_handler_use)
                previous_func = inspect.stack()[1][3]
                client_log_use.info(f'Функция {func.__name__} вызвана из функции {previous_func}')
                return func(*args, **kwargs)
        return call

@log
def create_massege(config):
        return {
                "action": config['PRESENCE'],
                "time": time.time(),
                "type": "status",
                "user": {
                        "account_name":  'Ivan',
                        "status":      "Yep, I am here!"
                }
        }


@log
def response_treatment(answer, config):
        if config['RESPONSE'] in answer:
                return f'"response": {answer["response"]}\n"time": {answer["time"]}\n"alert": {answer["alert"]}'


@log
def message_from_server(sock, username, m_config, config):
        while True:
            message = get_data(sock, config)
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



@log
def massage_post(sock, username, m_config, config):
        create_join_message(sock, username, m_config, config)
        print(f'Добро пожаловать в чат {username}!')
        while True:
                command = input('Введите команду "m" для сообщения, "e" для выхода: ')
                if command == 'm':
                        create_message(sock, username, m_config, config)
                elif command == 'e':
                        create_exit_message(sock, username, m_config, config)
                        print('Завершение соединения.')
                        time.sleep(0.5)
                        break
                else:
                        print('Команда не распознана, попробойте снова.')


@log
def create_join_message(sock, username, m_config, config):
        message_dict = {
                m_config['ACTION']: m_config['JOIN'],
                m_config['TIME']: time.time(),
                m_config['FROM']: username
        }
        post_data(sock, message_dict, config)


@log
def create_message(sock, username, m_config, config):
        message = input('Введите сообщение для отправки: ')
        message_dict = {
                m_config['ACTION']: 'msg',
                m_config['FROM']: username,
                m_config['TIME']: time.time(),
                m_config['MESSAGE']: message
        }
        post_data(sock, message_dict, config)


@log
def create_exit_message(sock, username, m_config, config):
        message_dict = {
                config['ACTION']: m_config['LEAVE'],
                config['TIME']: time.time(),
                config['ACCOUNT_NAME']: username
        }
        post_data(sock, message_dict, config)


def main():
        client_log = logging.getLogger('client_log_config')
        config = load_config('config.yaml')
        config_message = load_config('config_massag.yaml')
        try:
                if '-p' in sys.argv:
                        port = int(sys.argv[sys.argv.index('-p') + 1])
                else:
                        port = config['DEFAULT_PORT']
                # address = sys.argv[1]
                # port = int(sys.argv[2])
                if not 65535 >= port >= 1024:
                        raise ValueError
        # except IndexError:
        #         address = config['DEFAULT_IP_ADDRESS']
        #         port = config['DEFAULT_PORT']
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
                # client_name = input('Введите имя: ')
                if console == 0:
                        receiver = threading.Thread(target=message_from_server, args=(s, client_name, config_message, config))
                        # receiver.daemon = True
                        receiver.start()
                if console == 1:
                        user_interface = threading.Thread(target=massage_post, args=(s, client_name, config_message, config))
                        # receiver.daemon = True
                        user_interface.start()
        except ConnectionRefusedError:
                client_log.error('400: Bad Request')


if __name__ == '__main__':
        client_log = logging.getLogger('client_log_config')
        main()

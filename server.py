from socket import socket, AF_INET, SOCK_STREAM
import time, json, sys, logging, log.server_log_config, select
from utils import *
from functools import wraps
import inspect
from metaclasses import ServerVerifier


class Port:
    def __set__(self, instance, value):
        if value not in range(1024, 65536):
            server_log.critical(
                f'Порт должен быть указан в пределах от 1024 до 65535')
            exit(1)
        instance.__dict__[self.name] = value

    def __set_name__(self, owner, name):
        self.name = name


class Server(metaclass=ServerVerifier):
    port = Port()

    def __init__(self, address, port):
        self.address = address
        self.port = port
        self.clients = []

    def connect(self):
        self.s = socket(AF_INET, SOCK_STREAM)
        self.s.bind((self.address, self.port))
        self.s.listen(config['MAX_CONNECTIONS'])
        self.s.settimeout(0.2)

    def start(self):
        self.connect()
        while True:
            try:
                client, addr = self.s.accept()
            except OSError as e:
                pass
            else:
                self.clients.append(client)
            finally:
                r = []
                w = []
                e = []
                messages = []
                try:
                    r, w, e = select.select(self.clients, self.clients, [], 0)
                except Exception as e:
                    pass
                for client_i in r:
                    try:
                        massage = get_data(client_i, config)
                    except ConnectionResetError:
                        self.clients.remove(client_i)
                    messages.append(massage)
                for client_i in w:
                    try:
                        post_data(client_i, messages[0], config)

                    except Exception as e:
                        pass
                if len(messages) > 0:
                    del messages[0]


def connection_config():
    try:
        if '-p' in sys.argv:
            port = int(sys.argv[sys.argv.index('-p') + 1])
        else:
            port = config['DEFAULT_PORT']
        if not 65535 >= port >= 1024:
            raise ValueError
    except IndexError:
        server_log.warning('После -\'p\' необходимо указать порт')
        sys.exit(1)
    except ValueError:
        server_log.warning('Порт должен быть указан в пределах от 1024 до 65535')
        sys.exit(1)

    try:
        if '-a' in sys.argv:
            address = sys.argv[sys.argv.index('-a') + 1]
        else:
            address = ''

    except IndexError:
        server_log.warning('После \'a\'- необходимо указать адрес для ')
        sys.exit(1)
    return address, port


def main():
    add, port = connection_config()
    start_server = Server(add, port)
    start_server.start()


if __name__ == '__main__':
    config = load_config('config.yaml')
    config_message = load_config('config_massag.yaml')
    server_log = logging.getLogger('server_log_config')
    main()

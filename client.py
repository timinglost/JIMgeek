from socket import socket, AF_INET, SOCK_STREAM
import time, sys, logging, threading, sqlite3
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
                db_user = sqlite3.connect(f'client_db/{self.client_name}_db.db')
                cursor = db_user.cursor()
                cursor.execute(f'SELECT text FROM massege')
                results = cursor.fetchall()
                db_user.close()
                if results:
                        for i in results:
                                print(i[0])
                while True:
                        message = get_data(self.s, config)
                        if m_config['ACTION'] in message and message[m_config['ACTION']] == m_config['JOIN'] and \
                                m_config['FROM'] in message:
                                print(f'{message[m_config["FROM"]]} присоединился к чату.')
                        if m_config['ACTION'] in message and message[m_config['ACTION']] == 'msg' and \
                                m_config['FROM'] in message and m_config['MESSAGE'] in message and \
                                m_config['TIME'] in message:
                                m = f'{message[m_config["FROM"]]}: {message[m_config["MESSAGE"]]}'
                                print(m)
                                db_user = sqlite3.connect(f'client_db/{self.client_name}_db.db')
                                cursor = db_user.cursor()
                                cursor.execute(f'insert into massege(text) values ("{m}");')
                                db_user.commit()
                                db_user.close()
                        if config['ACTION'] in message and message[config['ACTION']] == m_config['LEAVE'] and \
                                config['TIME'] in message:
                                print(f'{message[config["ACCOUNT_NAME"]]} покинул чат.')
                        if 'response' in message and type(message['response']) == str:
                                print(message['response'])
                        if 'response' in message and 'alert' in message:
                                print(message['alert'])


class ClientPost(threading.Thread):
        def __init__(self, sock, client_name):
                self.s = sock
                self.client_name = client_name
                super().__init__()
        def run(self):
                self.create_join_message()
                print(f'Добро пожаловать в чат {self.client_name}!')
                while True:
                        command = input('Введите команду "gc" для получения контактов\n'
                                        '"ac" и "dc" для добовления/удаления контакта\n'
                                        '"m" для сообщения, "e" для выхода: ')
                        if command == 'm':
                                self.create_message()
                        elif command == 'gc':
                                self.get_contact()
                        elif command == 'ac':
                                self.add_contact()
                        elif command == 'dc':
                                self.delete_contact()
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

        def get_contact(self):
                message_dict = {
                    "action": "get_contacts",
                    "time": time.time(),
                    "user_login": self.client_name
                }
                post_data(self.s, message_dict, config)

        def add_contact(self):
                user_id = input('Введите ник для добавления: ')
                message_dict = {
                    "action": "add_contact",
                    "user_id": user_id,
                    "time": time.time(),
                    "user_login": self.client_name
                }
                post_data(self.s, message_dict, config)

        def delete_contact(self):
                user_id = input('Введите ник для удаления: ')
                message_dict = {
                        "action": "del_contact",
                        "user_id": user_id,
                        "time": time.time(),
                        "user_login": self.client_name
                }
                post_data(self.s, message_dict, config)


def logging_user(s):
        while True:
            name = input('Введите ник: ')
            password = input('Введите пароль: ')
            message_dict = {
                        "action": "authenticate",
                        "time": time.time(),
                        "user": {
                                "account_name": name,
                                "password": password
                        }
            }
            post_data(s, message_dict, config)
            message = get_data(s, config)
            if message['response'] == 200:
                return name
            else:
                print(message['error'])


def update_db(s, name):
        message_dict = {
                "action": "get_contacts_all",
                "time": time.time(),
                "user_login": name
        }
        post_data(s, message_dict, config)
        message = get_data(s, config)
        db_user = sqlite3.connect(f'client_db/{name}_db.db')
        cursor = db_user.cursor()
        for i in message['alert']:
                cursor.execute(f'insert OR IGNORE into contact(id, name) values ("{i[0]}", "{i[1]}");')
                db_user.commit()
        db_user.close()



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
        s = socket(AF_INET, SOCK_STREAM)
        try:
                s.connect((address, port))
                client_log.info('Установленно подключение')
                connect = logging_user(s)
                update_db(s, connect)
                if connect is not False:
                        receiver = ClientGet(s, connect)
                        receiver.daemon = True
                        receiver.start()
                        user_interface = ClientPost(s, connect)
                        # receiver.daemon = True
                        user_interface.start()
        except ConnectionRefusedError:
                client_log.error('400: Bad Request')


if __name__ == '__main__':
        client_log = logging.getLogger('client_log_config')
        config = load_config('config.yaml')
        m_config = load_config('config_massag.yaml')
        main()

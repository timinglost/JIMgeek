from socket import socket, AF_INET, SOCK_STREAM
import time
import sys
import logging
import threading
import sqlite3
from utils import *
from metaclasses import ClientVerifier


class Client:
        def __init__(self):
                self.client_log = logging.getLogger('client_log_config')
                self.config = load_config('config.yaml')
                self.m_config = load_config('config_massag.yaml')
                try:
                        if '-p' in sys.argv:
                                port = int(sys.argv[sys.argv.index('-p') + 1])
                        else:
                                port = self.config['DEFAULT_PORT']
                        if not 65535 >= port >= 1024:
                                raise ValueError
                except IndexError:
                        self.client_log.warning('После -\'p\' необходимо указать порт')
                        sys.exit(1)
                except ValueError:
                        self.client_log.warning('Порт должен быть указан в пределах от 1024 до 65535')
                        sys.exit(1)
                try:
                        if '-a' in sys.argv:
                                address = sys.argv[sys.argv.index('-a') + 1]
                        else:
                                address = self.config['DEFAULT_IP_ADDRESS']

                except IndexError:
                        self.client_log.warning('После \'a\'- необходимо указать адрес для ')
                        sys.exit(1)
                self.s = socket(AF_INET, SOCK_STREAM)
                try:
                        self.s.connect((address, port))
                        self.client_log.info('Установленно подключение')
                except ConnectionRefusedError:
                        self.client_log.error('400: Bad Request')

        class ClientGet(threading.Thread, metaclass=ClientVerifier):
                def __init__(self, sock, client_name):
                        self.client_log = logging.getLogger('client_log_config')
                        self.config = load_config('config.yaml')
                        self.m_config = load_config('config_massag.yaml')
                        self.s = sock
                        self.client_name = client_name
                        self.contact_list = []
                        self.massege_list = []
                        self.room_id_now = ''
                        self.m = ''
                        super().__init__()

                def run(self):
                        while True:
                                self.m = 'COD_NONE_MASSAGE'
                                message = get_data(self.s, self.config)
                                if self.m_config['ACTION'] in message and message[self.m_config['ACTION']] == self.m_config['JOIN'] and \
                                        self.m_config['FROM'] in message:
                                        print(f'{message[self.m_config["FROM"]]} присоединился к чату.')
                                if self.m_config['ACTION'] in message and message[self.m_config['ACTION']] == 'msg' and \
                                        self.m_config['FROM'] in message and self.m_config['MESSAGE'] in message and \
                                        self.m_config['TIME'] in message:
                                        self.m = message
                                if self.config['ACTION'] in message and message[self.config['ACTION']] == self.m_config['LEAVE'] and \
                                        self.config['TIME'] in message:
                                        print(f'{message[self.config["ACCOUNT_NAME"]]} покинул чат.')
                                if 'response' in message and type(message['response']) == str:
                                        print(message['response'])
                                if 'response' in message and 'alert' in message:
                                        self.contact_list = message['alert']
                                if 'action' in message and message['action'] == 'mh':
                                        self.massege_list = message['alert']
                                        self.room_id_now = message['to']


        class ClientPost(threading.Thread):
                def __init__(self, sock, client_name):
                        self.client_log = logging.getLogger('client_log_config')
                        self.config = load_config('config.yaml')
                        self.m_config = load_config('config_massag.yaml')
                        self.s = sock
                        self.client_name = client_name
                        self.run_script = True
                        super().__init__()
                def run(self):
                        self.create_join_message()
                        print(f'Добро пожаловать в чат {self.client_name}!')
                        while True:
                                time.sleep(1)
                                if self.run_script is False:
                                        self.create_exit_message()
                                        print('Завершение соединения.')
                                        time.sleep(0.5)
                                        break

                def create_join_message(self):
                        message_dict = {
                                self.m_config['ACTION']: self.m_config['JOIN'],
                                self.m_config['TIME']: time.time(),
                                self.m_config['FROM']: self.client_name
                        }
                        post_data(self.s, message_dict, self.config)

                def create_message(self, text, room_id):
                        message_dict = {
                                self.m_config['ACTION']: 'msg',
                                self.m_config['FROM']: self.client_name,
                                'to': room_id,
                                self.m_config['TIME']: time.time(),
                                self.m_config['MESSAGE']: text
                        }
                        post_data(self.s, message_dict, self.config)

                def create_exit_message(self):
                        message_dict = {
                                self.config['ACTION']: self.m_config['LEAVE'],
                                self.config['TIME']: time.time(),
                                self.config['ACCOUNT_NAME']: self.client_name
                        }
                        post_data(self.s, message_dict, self.config)

                def get_contact(self):
                        message_dict = {
                            "action": "get_contacts",
                            "time": time.time(),
                            "user_login": self.client_name
                        }
                        post_data(self.s, message_dict, self.config)

                def add_contact(self, user_id):
                        message_dict = {
                            "action": "add_contact",
                            "user_id": user_id,
                            "time": time.time(),
                            "user_login": self.client_name
                        }
                        post_data(self.s, message_dict, self.config)

                def delete_contact(self, user_id):
                        message_dict = {
                                "action": "del_contact",
                                "user_id": user_id,
                                "time": time.time(),
                                "user_login": self.client_name
                        }
                        post_data(self.s, message_dict, self.config)

                def get_massage_history(self, user_name):
                        message_dict = {
                                "action": "get_massage",
                                "user_name": user_name,
                                "time": time.time(),
                                "user_login": self.client_name
                        }
                        post_data(self.s, message_dict, self.config)

                def close_client(self):
                        self.run_script = False

        def logging_user(self, name, password):
            message_dict = {
                        "action": "authenticate",
                        "time": time.time(),
                        "user": {
                                "account_name": name,
                                "password": password
                        }
            }
            post_data(self.s, message_dict, self.config)
            message = get_data(self.s, self.config)
            if message['response'] == 200:
                self.name = name
                self.receiver = self.ClientGet(self.s, self.name)
                self.receiver.daemon = True
                self.receiver.start()
                self.user_interface = self.ClientPost(self.s, self.name)
                # receiver.daemon = True
                self.user_interface.start()
                return True, message
            else:
                return False, message

        def get_contact(self):
                self.user_interface.get_contact()
                time.sleep(0.5)
                return self.receiver.contact_list

        def get_massage_history(self, name):
                self.user_interface.get_massage_history(name)
                time.sleep(0.5)
                return self.receiver.massege_list, self.receiver.room_id_now

        def update_db(self, s, name):
                message_dict = {
                        "action": "get_contacts_all",
                        "time": time.time(),
                        "user_login": name
                }
                post_data(s, message_dict, self.config)
                message = get_data(s, self.config)
                db_user = sqlite3.connect(f'client_db/{name}_db.db')
                cursor = db_user.cursor()
                for i in message['alert']:
                        cursor.execute(f'insert OR IGNORE into contact(id, name) values ("{i[0]}", "{i[1]}");')
                        db_user.commit()
                db_user.close()


def main():
        client = Client()


if __name__ == '__main__':
        main()

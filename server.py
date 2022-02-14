from socket import socket, AF_INET, SOCK_STREAM
import time
import sys
import logging
import select
from utils import *
from metaclasses import ServerVerifier
import sqlite3


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
        self.info_client = []

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
                ip_addres = client.getpeername()
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
                        check_masseng = self.check_masseng(massage, client_i)
                        if check_masseng is not True:
                            post_data(client_i, check_masseng, config)
                    except ConnectionResetError:
                        self.clients.remove(client_i)
                    except json.decoder.JSONDecodeError:
                        self.clients.remove(client_i)
                    if check_masseng is True:
                        messages.append(massage)
                for client_i in w:
                    try:
                        post_data(client_i, messages[0], config)

                    except Exception as e:
                        pass
                if len(messages) > 0:
                    del messages[0]

    def check_masseng(self, massege, client):
        if massege['action'] == 'join':
            return self.add_user(massege, client)
        if massege['action'] == 'authenticate':
            return self.login_client(massege, client)
        if massege['action'] == 'get_contacts':
            return self.get_contacts(massege)
        if massege['action'] == 'add_contact':
            return self.add_contact(massege)
        if massege['action'] == 'del_contact':
            return self.del_contact(massege)
        if massege['action'] == 'get_contacts_all':
            return self.get_contacts_all(massege)
        if massege['action'] == 'msg':
            return self.post_massage(massege)
        if massege['action'] == 'get_massage':
            return self.get_massage(massege)
        if massege['action'] == 'leave':
            return self.del_user(massege)
        if massege['action'] == 'check_authenticate':
            return self.check_authenticate(massege)
        return True

    def check_authenticate(self, massage):
        for i in self.info_client:
            if i[1] == massage['user_login']:
                return {
                    "action": 'cl',
                    "alert": True
                }
            return {
                    "action": 'cl',
                    "alert": False
                }

    def del_user(self, massage):
        for i in self.info_client:
            if i[1] == massage['account_name']:
                self.info_client.remove(i)

    def get_massage(self, massage):
        conn = sqlite3.connect("messenger.db")
        cursor = conn.cursor()
        cursor.execute(f"SELECT id FROM users WHERE name = '{massage['user_name']}';")
        client_id = cursor.fetchone()[0]
        cursor.execute(f"SELECT id FROM users WHERE name = '{massage['user_login']}';")
        user_id = cursor.fetchone()[0]
        cursor.execute(f"SELECT id FROM room WHERE name = '{client_id}-{user_id}' OR name = '{user_id}-{client_id}';")
        room_id = cursor.fetchone()[0]
        cursor.execute(f"SELECT * FROM massage WHERE id_room = '{room_id}';")
        results = cursor.fetchall()
        conn.close()
        answer = []
        if len(results) != 0:
            for i in results:
                if i[1] == user_id:
                    answer.append(f'{massage["user_login"]}: {i[3]}')
                elif i[1] == client_id:
                    answer.append(f'{massage["user_name"]}: {i[3]}')
        answer = {
            "action": 'mh',
            "alert": answer,
            "to": room_id
        }
        return answer

    def post_massage(self, massage):
        conn = sqlite3.connect("messenger.db")
        cursor = conn.cursor()
        cursor.execute(f"SELECT id FROM users WHERE name = '{massage['from']}';")
        user_id = cursor.fetchone()[0]
        cursor.execute(f'SELECT id_user FROM roomchat WHERE id_room = {massage["to"]}')
        results = cursor.fetchall()
        for i in results:
            if i[0] != user_id:
                client_id = i[0]
        cursor.execute(
            f'insert into massage(id_user, id_room, text) values ("{user_id}", "{massage["to"]}", "{massage["message"]}");')
        conn.commit()
        conn.close()
        for i in self.info_client:
            if i[0] == client_id:
                post_data(i[2], massage, config)
        return massage

    def add_user(self, massage, client):
        conn = sqlite3.connect("messenger.db")
        cursor = conn.cursor()
        cursor.execute(f"SELECT id FROM users WHERE name = '{massage['from']}';")
        user_id = cursor.fetchone()[0]
        conn.close()
        self.info_client.append([user_id, massage['from'], client])
        return massage

    def login_client(self, massege, client):
        conn = sqlite3.connect("messenger.db")
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users")
        results = cursor.fetchall()
        conn.close()
        answer = ''
        for i in results:
            if i[1] == massege['user']['account_name'] and \
                    i[2] == massege['user']['password']:
                answer = {
                    "response": 200,
                    "alert": "Логин и пароль верны"
                }
                ip_addres = client.getpeername()
                conn = sqlite3.connect("messenger.db")
                cursor = conn.cursor()
                cursor.execute(f'insert into user_history(id_user, time_connect, ip_addr) values ("{i[0]}", "{time.time()}", "{ip_addres}");')
                conn.commit()
                conn.close()
                break
        if answer == '':
            answer = {
                "response": 402,
                "error": 'Неверный логин или пароль'
            }
        return answer

    def get_contacts(self, massege):
        conn = sqlite3.connect("messenger.db")
        cursor = conn.cursor()
        cursor.execute(f"SELECT id FROM users WHERE name = '{massege['user_login']}';")
        user_id = cursor.fetchone()[0]
        cursor.execute(f"SELECT id_client FROM contact_list WHERE id_user = '{user_id}';")
        results = cursor.fetchall()
        users_name = []
        for i in results:
            cursor.execute(f"SELECT name FROM users WHERE id = '{i[0]}';")
            user_name = cursor.fetchone()[0]
            users_name.append(user_name)
        conn.close()
        return {
            "response": 202,
            "alert": users_name
        }

    def get_contacts_all(self, massege):
        conn = sqlite3.connect("messenger.db")
        cursor = conn.cursor()
        cursor.execute(f"SELECT id FROM users WHERE name = '{massege['user_login']}';")
        user_id = cursor.fetchone()[0]
        cursor.execute(f"SELECT id_client FROM contact_list WHERE id_user = '{user_id}';")
        results = cursor.fetchall()
        users_name = []
        for i in results:
            cursor.execute(f"SELECT id, name FROM users WHERE id = '{i[0]}';")
            user_name = cursor.fetchone()
            users_name.append(user_name)
        conn.close()
        return {
            "response": 202,
            "alert": users_name
        }

    def add_contact(self, massege):
        conn = sqlite3.connect("messenger.db")
        cursor = conn.cursor()
        cursor.execute(f"SELECT id FROM users WHERE name = '{massege['user_login']}';")
        id_user = cursor.fetchone()[0]
        cursor.execute(f"SELECT id FROM users WHERE name = '{massege['user_id']}';")
        id_client_chek = cursor.fetchone()
        if id_client_chek is not None:
            id_client = id_client_chek[0]
            cursor.execute(f'insert into contact_list(id_user, id_client) values ("{id_user}", "{id_client}");')
            conn.commit()
            cursor.execute(f'insert into contact_list(id_user, id_client) values ("{id_client}", "{id_user}");')
            conn.commit()
            cursor.execute(f'insert into room(name) values ("{id_client}-{id_user}");')
            conn.commit()
            cursor.execute(f"SELECT id FROM room WHERE name = '{id_client}-{id_user}';")
            id_room = cursor.fetchone()[0]
            cursor.execute(f'insert into roomchat(id_room, id_user) values ("{id_room}", "{id_user}");')
            conn.commit()
            cursor.execute(f'insert into roomchat(id_room, id_user) values ("{id_room}", "{id_client}");')
            conn.commit()
            conn.close()
            return {
                    "response": f"{massege['user_id']} успешно добавлен",
                }
        else:
            conn.close()
            return {
                "response": f"{massege['user_id']} не существует",
            }

    def del_contact(self, massege):
        conn = sqlite3.connect("messenger.db")
        cursor = conn.cursor()
        cursor.execute(f"SELECT id FROM users WHERE name = '{massege['user_login']}';")
        id_user = cursor.fetchone()[0]
        cursor.execute(f"SELECT id FROM users WHERE name = '{massege['user_id']}';")
        id_client = cursor.fetchone()[0]
        cursor.execute(f'DELETE FROM contact_list WHERE id_user = "{id_user}" AND id_client = "{id_client}";')
        conn.commit()
        cursor.execute(f'DELETE FROM contact_list WHERE id_user = "{id_client}" AND id_client = "{id_user}";')
        conn.commit()
        cursor.execute(f"SELECT id FROM room WHERE name = '{id_client}-{id_user}';")
        id_room = cursor.fetchone()[0]
        cursor.execute(f'DELETE FROM roomchat WHERE id_room = "{id_room}" AND id_user = "{id_user}";')
        conn.commit()
        cursor.execute(f'DELETE FROM roomchat WHERE id_room = "{id_room}" AND id_user = "{id_client}";')
        conn.commit()
        cursor.execute(f'DELETE FROM room WHERE name = "{id_client}-{id_user}";')
        conn.commit()
        conn.close()
        return {
            "response": f"{massege['user_id']} успешно удален",
        }


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

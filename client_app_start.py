import sys
import time
from socket import socket, AF_INET, SOCK_STREAM
from PyQt5 import QtWidgets
from PyQt5.QtCore import QThread
from PyQt5.QtWidgets import QInputDialog, QMessageBox
from client import Client
import client_app
from utils import *
import hashlib


# def login_required(func):
#     def decor(self, *args, **kwargs):
#         config = load_config('config.yaml')
#         s = socket(AF_INET, SOCK_STREAM)
#         try:
#             s.connect(('127.0.0.1', 8888))
#         except ConnectionRefusedError:
#             print('400: Bad Request')
#         message_dict = {
#             "action": "check_authenticate",
#             "time": time.time(),
#             "user_login": self.client.name
#         }
#         post_data(s, message_dict, config)
#         answer = get_data(s, config)
#         s.close()
#         if answer['alert'] is True:
#             return func(self, *args, **kwargs)
#         elif answer['alert'] is False:
#             print('login error')
#         else:
#             print('massage error')
#     return decor


class SlowTask(QThread):
    """Класс поток для динамического получения сообщений"""

    def __init__(self, client, list_widget, room_id):
        """Метод __init__ выполняющий инициализацию атребутов"""
        super().__init__()
        self.client = client
        """Атрибут с экземпляром класса Client"""
        self.list_widget = list_widget
        """Атрибут виджета поля сообщений"""
        self.room_id = room_id
        """Атрибут текущей переписки"""
        self.time = 0.1
        """Атрибут времени для контроля отрисовки сообщения"""

    def run(self):
        """Метод отрисовки сообщений"""
        print('start thread')
        while True:
            massage = self.client.receiver.m
            if massage != 'COD_NONE_MASSAGE':
                if massage['to'] == self.room_id and self.time != massage['time']:
                    self.list_widget.addItem(f'{massage["from"]}: {massage["message"]}')
                    self.time = massage['time']


class ExampleApp(QtWidgets.QMainWindow, client_app.Ui_MainForm):
    """Класс графического приложения клиента"""
    def __init__(self):
        """Метод __init__ выполняющий инициализацию атребутов"""
        super().__init__()
        self.setupUi(self)
        self.salt = load_config('salt.yaml')['SALT']
        self.client = Client()
        self.logining_client()
        self.get_contact()
        self.pushButtonContactUpdate.clicked.connect(self.get_contact)
        self.pushButtonAddContact.clicked.connect(self.add_contact)
        self.pushButtonDeleteContact.clicked.connect(self.del_contact)
        self.pushButtonPostMassege.clicked.connect(self.enter_massege)
        self.listWidgetContact.itemClicked.connect(self.get_message)

    def logining_client(self):
        """Метод авторизации пользователя"""
        while True:
            login_text, ok_login = QInputDialog.getText(self, 'Вход', 'Введите имя:')
            if ok_login is True:
                password_text, ok_password = QInputDialog.getText(self, 'Вход', 'Введите пароль:')
                if ok_password is True:
                    hashed_password = hashlib.sha512(
                        password_text.encode('utf-8') + self.salt.encode('utf-8')).hexdigest()
                    answer = self.client.logging_user(login_text, hashed_password)
                    if answer[0] is True:
                        QMessageBox.information(self, 'Вход', answer[1]['alert'], QMessageBox.Yes)
                        break
                    else:
                        QMessageBox.information(self, 'Вход', answer[1]['error'], QMessageBox.Yes)

    # @login_required
    def get_contact(self):
        """Метод получения и отрисовки списка контактов"""
        self.listWidgetContact.clear()
        contact_l = self.client.get_contact()
        if len(contact_l) != 0:
            for i in contact_l:
                self.listWidgetContact.addItem(f'{i}')

    # @login_required
    def add_contact(self):
        """Метод добавления клиента в список контактов"""
        name = self.lineEditContact.text()
        self.client.user_interface.add_contact(name)

    # @login_required
    def del_contact(self):
        """Метод удаления клиента из списока контактов"""
        name = self.lineEditContact.text()
        self.client.user_interface.delete_contact(name)

    # @login_required
    def enter_massege(self):
        """Метод отправки сообщения"""
        text = self.lineEditMesssag.text()
        self.client.user_interface.create_message(text, self.room_id_now)

    # @login_required
    def get_message(self, item):
        """Метод получения истории переписки, id переписки и вызов метода listen_massage"""
        user_name = item.text()
        try:
            self.stop_listen()
        except AttributeError:
            pass
        answer = self.client.get_massage_history(user_name)
        self.room_id_now = answer[1]
        massage_l = answer[0]
        self.listWidgetMessage.clear()
        if len(massage_l) != 0:
            for i in massage_l:
                self.listWidgetMessage.addItem(f'{i}')
        self.listen_massage()

    def listen_massage(self):
        """Метод запуска потока слушающего новые сообщения"""
        self.tread_massage = SlowTask(self.client, self.listWidgetMessage, self.room_id_now)
        self.tread_massage.start()

    def stop_listen(self):
        """Метод остановки потока слушающего новые сообщения"""
        self.tread_massage.terminate()

    def closeEvent(self, event):
        """Метод остановки приложения"""
        self.client.user_interface.close_client()


def main():
    """Функция запуска графического приложения"""
    app = QtWidgets.QApplication(sys.argv)
    window = ExampleApp()
    window.show()
    app.exec_()


if __name__ == '__main__':
    main()

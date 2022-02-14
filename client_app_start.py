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


def login_required(func):
    def decor(self, *args, **kwargs):
        config = load_config('config.yaml')
        s = socket(AF_INET, SOCK_STREAM)
        try:
            s.connect(('127.0.0.1', 8888))
        except ConnectionRefusedError:
            print('400: Bad Request')
        message_dict = {
            "action": "check_authenticate",
            "time": time.time(),
            "user_login": self.client.name
        }
        post_data(s, message_dict, config)
        answer = get_data(s, config)
        s.close()
        if answer['alert'] is True:
            return func(self, *args, **kwargs)
        elif answer['alert'] is False:
            print('login error')
        else:
            print('massage error')
    return decor


class SlowTask(QThread):

    def __init__(self, client, list_widget, room_id):
        super().__init__()
        self.client = client
        self.list_widget = list_widget
        self.room_id = room_id
        self.time = 0.1

    def run(self):
        while True:
            massage = self.client.receiver.m
            if massage != 'COD_NONE_MASSAGE':
                if massage['to'] == self.room_id and self.time != massage['time']:
                    self.list_widget.addItem(f'{massage["from"]}: {massage["message"]}')
                    self.time = massage['time']


class ExampleApp(QtWidgets.QMainWindow, client_app.Ui_MainForm):
    def __init__(self):
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
        while True:
            login_text, ok_login = QInputDialog.getText(self, 'Вход', 'Введите имя:')
            if ok_login == True:
                password_text, ok_password = QInputDialog.getText(self, 'Вход', 'Введите пароль:')
                if ok_password == True:
                    hashed_password = hashlib.sha512(password_text.encode('utf-8') + self.salt.encode('utf-8')).hexdigest()
                    answer = self.client.logging_user(login_text, hashed_password)
                    if answer[0] == True:
                        QMessageBox.information(self, 'Вход', answer[1]['alert'], QMessageBox.Yes)
                        break
                    else:
                        QMessageBox.information(self, 'Вход', answer[1]['error'], QMessageBox.Yes)


    @login_required
    def get_contact(self):
        self.listWidgetContact.clear()
        contact_l = self.client.get_contact()
        if len(contact_l) != 0:
            for i in contact_l:
                self.listWidgetContact.addItem(f'{i}')

    @login_required
    def add_contact(self):
        name = self.lineEditContact.text()
        self.client.user_interface.add_contact(name)

    @login_required
    def del_contact(self):
        name = self.lineEditContact.text()
        self.client.user_interface.delete_contact(name)

    @login_required
    def enter_massege(self):
        text = self.lineEditMesssag.text()
        self.client.user_interface.create_message(text, self.room_id_now)

    @login_required
    def get_message(self, item):
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
        self.tread_massage = SlowTask(self.client, self.listWidgetMessage, self.room_id_now)
        self.tread_massage.start()

    def stop_listen(self):
        self.tread_massage.terminate()

    def closeEvent(self, event):
        self.client.user_interface.close_client()


def main():
    app = QtWidgets.QApplication(sys.argv)
    window = ExampleApp()
    window.show()
    app.exec_()


if __name__ == '__main__':
    main()
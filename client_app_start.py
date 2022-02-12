import sys
import os, sqlite3, logging, threading
import time
from datetime import datetime
import subprocess
from PyQt5 import QtWidgets
from PyQt5.QtCore import QThread
from PyQt5.QtWidgets import QInputDialog, QMessageBox
from PyQt5 import QtCore

from client import Client
import client_app
from utils import *


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
                    answer = self.client.logging_user(login_text, password_text)
                    if answer[0] == True:
                        QMessageBox.information(self, 'Вход', answer[1]['alert'], QMessageBox.Yes)
                        break
                    else:
                        QMessageBox.information(self, 'Вход', answer[1]['error'], QMessageBox.Yes)

    def get_contact(self):
        self.listWidgetContact.clear()
        contact_l = self.client.get_contact()
        if len(contact_l) != 0:
            for i in contact_l:
                self.listWidgetContact.addItem(f'{i}')

    def add_contact(self):
        name = self.lineEditContact.text()
        self.client.user_interface.add_contact(name)

    def del_contact(self):
        name = self.lineEditContact.text()
        self.client.user_interface.delete_contact(name)

    def enter_massege(self):
        text = self.lineEditMesssag.text()
        self.client.user_interface.create_message(text, self.room_id_now)

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
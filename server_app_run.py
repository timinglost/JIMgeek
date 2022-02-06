import sys
import os, sqlite3
from datetime import datetime
import subprocess

from PyQt5 import QtWidgets

import server_app

class ExampleApp(QtWidgets.QMainWindow, server_app.Ui_Form):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.show_users()
        self.update_button.clicked.connect(self.show_users)
        self.contact_list.itemClicked.connect(self.onClicked)
        self.run_server.clicked.connect(self.start_server)

    def onClicked(self, item):
        self.s_list.clear()
        id_user = int((item.text()).split()[1])
        connect = sqlite3.connect('messenger.db')
        cursor = connect.cursor()
        cursor.execute(f"SELECT time_connect, ip_addr name FROM user_history WHERE id_user = '{id_user}'")
        result = cursor.fetchall()
        connect.close()
        if len(result) != 0:
            for i in result:
                data_time = datetime.utcfromtimestamp(i[0]).strftime('%Y-%m-%d %H:%M:%S')
                self.s_list.addItem(f'time: {data_time} ip: {i[1]}')

    def show_users(self):
        self.contact_list.clear()
        connect = sqlite3.connect('messenger.db')
        cursor = connect.cursor()
        cursor.execute("SELECT id, name FROM users")
        result = cursor.fetchall()
        connect.close()

        for i in result:
            self.contact_list.addItem(f'id: {i[0]} name: {i[1]}')

    def start_server(self):
        adrr = self.lineEditAddres.text()
        port = self.lineEditPort.text()
        subprocess.Popen(['python', 'server.py', '-a', f'{adrr}', '-p', f'{port}'], creationflags=subprocess.CREATE_NEW_CONSOLE)


def main():
    app = QtWidgets.QApplication(sys.argv)
    window = ExampleApp()
    window.show()
    app.exec_()

if __name__ == '__main__':
    main()
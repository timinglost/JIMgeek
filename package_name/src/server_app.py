# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'server_app.ui'
#
# Created by: PyQt5 UI code generator 5.15.4
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_Form(object):
    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.resize(500, 500)
        Form.setMaximumSize(QtCore.QSize(500, 500))
        Form.setSizeIncrement(QtCore.QSize(500, 500))
        self.run_server = QtWidgets.QPushButton(Form)
        self.run_server.setGeometry(QtCore.QRect(10, 10, 87, 23))
        self.run_server.setObjectName("run_server")
        self.label_client_list = QtWidgets.QLabel(Form)
        self.label_client_list.setGeometry(QtCore.QRect(270, 80, 87, 13))
        self.label_client_list.setObjectName("label_client_list")
        self.update_button = QtWidgets.QPushButton(Form)
        self.update_button.setGeometry(QtCore.QRect(400, 70, 75, 23))
        self.update_button.setObjectName("update_button")
        self.label_s = QtWidgets.QLabel(Form)
        self.label_s.setGeometry(QtCore.QRect(10, 80, 105, 13))
        self.label_s.setObjectName("label_s")
        self.contact_list = QtWidgets.QListWidget(Form)
        self.contact_list.setGeometry(QtCore.QRect(270, 100, 221, 381))
        self.contact_list.setObjectName("contact_list")
        self.s_list = QtWidgets.QListWidget(Form)
        self.s_list.setGeometry(QtCore.QRect(10, 100, 241, 381))
        self.s_list.setObjectName("s_list")
        self.lineEditAddres = QtWidgets.QLineEdit(Form)
        self.lineEditAddres.setGeometry(QtCore.QRect(100, 10, 113, 20))
        self.lineEditAddres.setText("")
        self.lineEditAddres.setObjectName("lineEditAddres")
        self.lineEditPort = QtWidgets.QLineEdit(Form)
        self.lineEditPort.setGeometry(QtCore.QRect(230, 10, 113, 20))
        self.lineEditPort.setObjectName("lineEditPort")
        self.labelAdres = QtWidgets.QLabel(Form)
        self.labelAdres.setGeometry(QtCore.QRect(130, 30, 47, 13))
        self.labelAdres.setObjectName("labelAdres")
        self.labelPort = QtWidgets.QLabel(Form)
        self.labelPort.setGeometry(QtCore.QRect(270, 30, 47, 13))
        self.labelPort.setObjectName("labelPort")

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        _translate = QtCore.QCoreApplication.translate
        Form.setWindowTitle(_translate("Form", "Form"))
        self.run_server.setText(_translate("Form", "Запуск сервера"))
        self.label_client_list.setText(_translate("Form", "Список клиентов"))
        self.update_button.setText(_translate("Form", "Обновить"))
        self.label_s.setText(_translate("Form", "Статистика клиента"))
        self.lineEditPort.setText(_translate("Form", "8888"))
        self.labelAdres.setText(_translate("Form", "Адресс"))
        self.labelPort.setText(_translate("Form", "Порт"))
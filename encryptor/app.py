import sys
import os
from encryptor import constants
from encryptor.send import sender
from encryptor.receive import receiver
from PyQt5.QtWidgets import (
    QApplication,
    QLabel,
    QLineEdit,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QComboBox,
    QDialog
)


class App(QMainWindow):
    def __init__(self, sender):
        super(App, self).__init__()
        self.sender = sender
        self.title = "Encryptor"
        self.left = 100
        self.top = 100
        self.width = 400
        self.height = 200
        self.init_UI()

    def init_UI(self):
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)

        self.label = QLabel(self)
        self.label.setText("Type your message")
        self.label.setFixedWidth(200)
        self.label.move(20, 10)

        # Create a textbox.
        self.textbox = QLineEdit(self)
        self.textbox.move(20, 40)
        self.textbox.resize(280, 40)

         # Create a dropdown list and change handler
        self.combobox = QComboBox(self)
        self.combobox.addItems(["ECB", "CBC", "CFB", "OFB"])
        self.combobox.move(40, 100)
        print(self.combobox.currentText())
        self.combobox.currentIndexChanged.connect(self.mode_change)

        # Create a button and click handler.
        self.button = QPushButton("Send", self)
        self.button.move(200, 100)
        self.button.clicked.connect(self.on_click)
        self.show()

    def mode_change(self):
        print ("selection changed ", self.combobox.currentText())

    def on_click(self):
        self.textbox_value = self.textbox.text()

        self.sender.encrypt_message(self.textbox_value.encode("utf-8"), self.combobox.currentText())
        QMessageBox.information(
            self,
            "Message",
            "Succesfully sent message: " + self.textbox_value,
            QMessageBox.Ok,
            QMessageBox.Ok,
        )
        self.textbox.setText("")

class App2(QMainWindow):
    def __init__(self, receiver):
        super(App2, self).__init__()
        self.title = "Decryptor"
        self.left = 600
        self.top = 100
        self.width = 400
        self.height = 200
        self.receiver = receiver
        self.init_UI()

    def init_UI(self):
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)

        self.passtxt = QLineEdit(self)
        self.passtxt.setEchoMode(QLineEdit.Password)
        self.passtxt.move(20, 40)

        self.label = QLabel(self)
        if os.path.exists(constants.RECEIVE_PRIVATE_KEY) and os.path.exists(
            os.path.abspath(constants.RECEIVE_PUBLIC_KEY)
        ):
            self.label.setText("Type your password for the private key access")
        else:
            self.label.setText("Type your password for the creation of private key")
        self.label.setFixedWidth(400)
        self.label.move(20, 10)

        # Create a button and click handler.
        self.button = QPushButton("OK", self)
        self.button.move(200, 100)
        self.button.clicked.connect(self.on_click)
        self.show()

    def on_click(self):
        QMessageBox.information(
            self,
            "Password",
            "Your password: " + self.passtxt.text(),
            QMessageBox.Ok,
            QMessageBox.Ok,
        )

        if os.path.exists(constants.RECEIVE_PRIVATE_KEY) and os.path.exists(
            os.path.abspath(constants.RECEIVE_PUBLIC_KEY)
        ):
            self.private_key = self.receiver.get_privkey(self.passtxt.text())
            self.receiver.decrypt_message(self.private_key)
        else:
            self.receiver.create_keys(self.passtxt.text())
            print("Keys created succesfully")

        self.passtxt.setText("")

def run():
    qt_app = QApplication(sys.argv)

    obj_sender = sender.Sender()
    obj_receiver = receiver.Receiver()

    app = App(obj_sender)
    app2 = App2(obj_receiver)

    sys.exit(qt_app.exec_())

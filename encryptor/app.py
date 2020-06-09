import sys
from encryptor.send import sender
from encryptor.receive import receiver
from PyQt5.QtWidgets import (
    QApplication,
    QLabel,
    QLineEdit,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QComboBox
)


class App(QMainWindow):
    def __init__(self):
        super(App, self).__init__()
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
        textbox_value = self.textbox.text()

        sender.encrypt_message(textbox_value.encode("utf-8"), self.combobox.currentText())
        QMessageBox.information(
            self,
            "Message",
            "Succesfully sent message: " + textbox_value,
            QMessageBox.Ok,
            QMessageBox.Ok,
        )
        self.textbox.setText("")
        receiver.decrypt_message(self.combobox.currentText())


def run():
    qt_app = QApplication(sys.argv)
    app = App()

    sender.create_keys()
    receiver.create_keys()
    sys.exit(qt_app.exec_())

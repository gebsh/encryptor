from PyQt5.QtWidgets import QWidget, QVBoxLayout, QPlainTextEdit, QPushButton
from PyQt5.QtCore import pyqtSignal, pyqtSlot


class SendBox(QWidget):
    """Box that allows to send messages to the server."""

    send = pyqtSignal(str)

    def __init__(self) -> None:
        super().__init__()

        layout = QVBoxLayout()
        send_button = QPushButton("Send message")
        self._textarea = QPlainTextEdit()

        send_button.clicked.connect(self._send_message)
        layout.addWidget(self._textarea)
        layout.addWidget(send_button)
        self.setLayout(layout)

    @pyqtSlot()
    def _send_message(self) -> None:
        message = self._textarea.toPlainText()

        self.send.emit(message)

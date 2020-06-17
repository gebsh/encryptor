from PyQt5.QtWidgets import QWidget, QVBoxLayout, QPlainTextEdit, QPushButton, QFileDialog, QHBoxLayout
from PyQt5.QtCore import pyqtSignal, pyqtSlot


class SendBox(QWidget):
    """Box that allows to send messages to the server."""

    send_message = pyqtSignal(str)
    send_file = pyqtSignal(str)

    def __init__(self) -> None:
        super().__init__()

        layout = QVBoxLayout()
        buttons_widget = QWidget()
        buttons_layout = QHBoxLayout()
        self._file_button = QPushButton("Send file")
        message_button = QPushButton("Send message")
        self._textarea = QPlainTextEdit()

        self._file_button.clicked.connect(self._send_file)
        message_button.clicked.connect(self._send_message)
        buttons_layout.addWidget(self._file_button)
        buttons_layout.addWidget(message_button)
        buttons_widget.setLayout(buttons_layout)
        layout.addWidget(self._textarea)
        layout.addWidget(buttons_widget)
        self.setLayout(layout)

    @pyqtSlot()
    def _send_message(self) -> None:
        message = self._textarea.toPlainText()

        self.send_message.emit(message)

    @pyqtSlot()
    def _send_file(self) -> None:
        dialog = QFileDialog()
        dialog.setFileMode(QFileDialog.ExistingFile)

        if dialog.exec_():
            filepath = dialog.selectedFiles()[0]

            self.send_file.emit(filepath)

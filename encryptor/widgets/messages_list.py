from PyQt5.QtWidgets import (
    QWidget,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QPushButton,
    QHBoxLayout,
)
from PyQt5.QtCore import pyqtSignal, pyqtSlot
from encryptor.network.message import Message


class MessageItem(QWidget):
    """A single message on a list."""

    decrypt = pyqtSignal(Message)

    def __init__(self, message: Message) -> None:
        super().__init__()

        self._message = message
        layout = QHBoxLayout()
        decrypt_button = QPushButton("Decrypt", self)

        layout.addWidget(QLabel("New message"))
        layout.addWidget(decrypt_button)
        decrypt_button.clicked.connect(lambda: self._decrypt())
        self.setLayout(layout)

    @pyqtSlot()
    def _decrypt(self) -> None:
        self.decrypt.emit(self._message)

class MessagesList(QListWidget):
    """List of received messages."""

    decrypt = pyqtSignal(Message)

    @pyqtSlot(Message)
    def new_message(self, message: Message) -> None:
        """Add a message to the list."""

        list_item = QListWidgetItem()
        message_item = MessageItem(message)

        list_item.setSizeHint(message_item.sizeHint())
        message_item.decrypt.connect(self.decrypt.emit)
        self.addItem(list_item)
        self.setItemWidget(list_item, message_item)

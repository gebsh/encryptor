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
from Crypto.PublicKey import RSA


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
    ask_for_privkey = pyqtSignal()

    def __init__(self) -> None:
        super().__init__()

        self._privkey: Optional[RSA.RsaKey] = None

    @pyqtSlot(Message)
    def new_message(self, message: Message) -> None:
        """Add a message to the list."""

        list_item = QListWidgetItem()
        message_item = MessageItem(message)

        list_item.setSizeHint(message_item.sizeHint())
        message_item.decrypt.connect(self.decrypt.emit)
        self.addItem(list_item)
        self.setItemWidget(list_item, message_item)

    @pyqtSlot(Message)
    def decrypt_message(self, message: Message) -> None:
        """Decrypts a message from the list."""

        if self._privkey == None:
            self.ask_for_privkey.emit()

        print(self._privkey)
        decrypted_message_content = decrypt(
            message.content, message.headers.mode, self._privkey
        )

        if message.headers.content_type == ContentType.FILE:
            decrypted_message = Message.of(
                decrypted_message_content,
                ContentType.FILE,
                filename=message.headers.filename,
            )
            print(f"Decrypted file: {decrypted_message.headers.filename}")
            decrypted_message.write_to_file(self._keys_dir)
        else:
            print(f"Decrypted message: {decrypted_message_content.decode('utf-8')}")


    def set_privkey(self, privkey: RSA.RsaKey) -> None:
        self._privkey = privkey

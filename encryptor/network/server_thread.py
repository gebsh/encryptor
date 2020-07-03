import socket
import traceback
from pathlib import Path
from Crypto.PublicKey import RSA
from PyQt5.QtCore import QThread, pyqtSignal, pyqtSlot
from encryptor.widgets.auth_dialogs import AuthDialog
from encryptor.encryption.keys import get_private_key
from encryptor.encryption.crypto import decrypt
from .connection import Address, ConnectionClosed
from .message import Message, MessageReader, ContentType


class ServerThread(QThread):
    """A thread that is responsible for handling incoming connections and messages."""

    handshake = pyqtSignal(Address)
    pubkey = pyqtSignal(RSA.RsaKey)
    new_message = pyqtSignal(Message)
    disconnect = pyqtSignal()

    def __init__(self, addr: Address, keys_dir: Path) -> None:
        super().__init__()

        self.addr = addr
        self._socket = socket.socket()
        self._keys_dir = keys_dir

        self._socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    def __del__(self) -> None:
        try:
            self._socket.shutdown(socket.SHUT_RDWR)
        except OSError:
            pass
        finally:
            self._socket.close()

    @pyqtSlot()
    def run(self) -> None:
        """Run the server."""

        self._socket.bind((self.addr.host, self.addr.port))
        self._socket.listen()

        while True:
            conn = self._socket.accept()[0]
            reader = MessageReader(conn, self._keys_dir)

            print(f"New connection from {reader.endpoint_addr}")

            try:
                ret_addr = reader.read_handshake()
                self.handshake.emit(ret_addr)

                pubkey = reader.read_pubkey()
                self.pubkey.emit(pubkey)

                while True:
                    message = reader.read(self._keys_dir)
                    self.new_message.emit(message)
            except Exception as e:
                reader.close()

                if isinstance(e, ConnectionClosed):
                    print(f"Closed connection with {reader.endpoint_addr}")
                else:
                    traceback.print_exc()

                # Remove the reference for the sake of garbage collector's sanity.
                reader = None  # type: ignore

                self.disconnect.emit()
                break

    @pyqtSlot(Message)
    def decrypt(self, message: Message) -> None:
        """Decrypt read message."""

        dialog = AuthDialog()

        if dialog.exec_():
            passphrase = dialog.passphrase.text()
            privkey = get_private_key(self._keys_dir, passphrase)
        else:
            return

        decrypted_message_content = decrypt(
            message.content, message.headers.encryption_mode, privkey
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

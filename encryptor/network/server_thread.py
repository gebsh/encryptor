import socket
import traceback
from pathlib import Path
from Crypto.PublicKey import RSA
from PyQt5.QtCore import QThread, pyqtSignal, pyqtSlot
from encryptor.widgets.auth_dialogs import AuthDialog
from encryptor.encryption.keys import get_private_key
from encryptor.encryption.crypto import decrypt
from .connection import Address, ConnectionClosed
from .message import Message, MessageReader, ContentType, JSONMessageContent


class ServerThread(QThread):
    """A thread that is responsible for handling incoming connections and messages."""

    handshake = pyqtSignal(Address)
    pubkey = pyqtSignal(RSA.RsaKey)
    new_message = pyqtSignal(Message)
    disconnect = pyqtSignal()
    ask_for_dir = pyqtSignal(Message)
    part_received = pyqtSignal(int)
    file_upload_progress = pyqtSignal(int)

    def __init__(self, addr: Address) -> None:
        super().__init__()

        self.addr = addr
        self._socket = socket.socket()

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
            reader = MessageReader(conn)

            print(f"New connection from {reader.endpoint_addr}")

            try:
                ret_addr = reader.read_handshake()
                self.handshake.emit(ret_addr)

                pubkey = reader.read_pubkey()
                self.pubkey.emit(pubkey)

                while True:

                    message = reader.read()
                    message_type = message.headers.content_type

                    if message_type == ContentType.JSON:
                        part_number = JSONMessageContent.from_message(message).part_number
                        self.file_upload_progress.emit(part_number)
                    else:
                        if message_type == ContentType.FILE:
                            if message.headers.part_number is not None:
                                reader.read_part_of_file(message)
                                self.part_received.emit(message.headers.part_number)
                                if message.headers.part_number == message.headers.number_of_parts:
                                    message.content = reader._data_in_progress
                                    reader._data_in_progress = None
                                    print(f"Saving encrypted file: {message.headers.filename}")
                                    self.ask_for_dir.emit(message)
                                    self.new_message.emit(message)
                        else:
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

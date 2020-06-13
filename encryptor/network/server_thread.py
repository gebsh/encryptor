import socket
import traceback
from Crypto.PublicKey import RSA
from PyQt5.QtCore import QThread, pyqtSignal, pyqtSlot
from .connection import Address
from .exceptions import ConnectionClosed
from .message import Message, MessageReader


class ServerThread(QThread):
    """A thread that is responsible for handling incoming connections and messages."""

    handshake = pyqtSignal(Address)
    pubkey = pyqtSignal(RSA.RsaKey)
    new_message = pyqtSignal(Message)
    disconnect = pyqtSignal()

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

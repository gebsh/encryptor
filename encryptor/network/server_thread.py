import socket
import traceback
from typing import cast, Optional
from PyQt5.QtCore import QThread, pyqtSignal, pyqtSlot
from .message import ContentType, Message, MessageReader, JSONMessageContent
from .exceptions import ConnectionClosed


class ServerThread(QThread):
    """A thread that is responsible for handling incoming connections and messages."""

    handshake = pyqtSignal(tuple)

    def __init__(self, host: str, port: int) -> None:
        super().__init__()

        self._host = host
        self._port = port
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

        self._socket.bind((self._host, self._port))
        self._socket.listen()

        while True:
            conn, addr = self._socket.accept()
            reader = MessageReader(conn)

            print(f"New connection from {addr[0]}:{addr[1]}")

            try:
                handshake_content = JSONMessageContent.from_message(
                    reader.read(content_type=ContentType.JSON)
                )

                self.handshake.emit(
                    (handshake_content.server_host, handshake_content.server_port)
                )
            except Exception as e:
                if isinstance(e, ConnectionClosed):
                    print(f"Closing connection to {addr[0]}:{addr[1]}")
                else:
                    traceback.print_exc()

                conn.shutdown(socket.SHUT_RDWR)
                conn.close()
                break

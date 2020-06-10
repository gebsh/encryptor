import socket
import selectors
import types
from typing import cast
from PyQt5.QtCore import QObject, QThread, pyqtSignal, pyqtSlot
from encryptor import constants
from encryptor.encryption.message import Message
from encryptor.encryption.crypto import decrypt
from .frames import IFrame, DFrame


class ServerSignals(QObject):
    """Signals available from a running server thread."""

    new_message = pyqtSignal(Message)
    new_file = pyqtSignal(bytes)


class ServerWorker(QThread):
    """Worker thread responsible for receiving data from other clients."""

    def __init__(self, host: str, port: int) -> None:
        super(ServerWorker, self).__init__()

        self._host = host
        self._port = port
        self._selector = selectors.DefaultSelector()
        self._socket = socket.socket()
        self.signals = ServerSignals()

    def __del__(self) -> None:
        self._selector.close()

    @property
    def address(self) -> str:
        """An andress of the server."""

        return f"{self._host}:{self._port}"

    @pyqtSlot()
    def run(self) -> None:
        """Listen for any incoming data."""

        self._socket.bind((self._host, self._port))
        self._socket.listen()
        self._socket.setblocking(False)
        self._selector.register(self._socket, selectors.EVENT_READ, data=None)

        print(f"ServerWorker listens on {self.address}")

        while True:
            events = self._selector.select(timeout=None)

            for key, _ in events:
                if key.data is None:
                    self._accept_socket(cast(socket.socket, key.fileobj))
                else:
                    self._serve_socket(key)

    def _accept_socket(self, sock: socket.socket) -> None:
        connection, address = sock.accept()
        data = types.SimpleNamespace(address=f"{address[0]}:{address[1]}")

        connection.setblocking(False)
        self._selector.register(connection, selectors.EVENT_READ, data=data)
        print(f"New connection from {data.address}")

    def _serve_socket(self, key: selectors.SelectorKey) -> None:
        sock = cast(socket.socket, key.fileobj)
        sock_data = key.data
        info_frame_bytes = sock.recv(IFrame.frame_size)

        if info_frame_bytes == b"":
            print(f"Closing connection to {sock_data.address}")
            self._selector.unregister(sock)
            sock.close()
        else:
            info_frame = IFrame.from_bytes(info_frame_bytes)
            data = bytearray()
            length = info_frame.data_length

            while length > 0:
                if length < constants.BUFFER_SIZE:
                    data.extend(sock.recv(length))
                    length = 0
                else:
                    data.extend(sock.recv(constants.BUFFER_SIZE))
                    length -= constants.BUFFER_SIZE

            message = Message(data.decode(DFrame.encoding), sock_data.address)

            print(f"Received data from {sock_data.address}: {message.content:.256}")

            self.signals.new_message.emit(message)

import socket
import traceback
from typing import Optional
from PyQt5.QtCore import QObject, pyqtSignal, pyqtSlot
from encryptor import constants
from encryptor.encryption.mode import EncryptionMode
from encryptor.encryption.crypto import encrypt
from encryptor.network.connection import Connection
from encryptor.network.message import (
    ContentType,
    JSONContentType,
    Message,
    JSONMessageContent,
)
from .frames import IFrame, DFrame


class ClientSignals(QObject):
    """Signals available from a running client thread."""

    connection = pyqtSignal(str)
    disconnection = pyqtSignal()


class ClientWorker(QObject):
    """Worker responsible for sending data to another client."""

    def __init__(
        self, server_host: str, server_port: int, mode: EncryptionMode
    ) -> None:
        super().__init__()

        self._server_host = server_host
        self._server_port = server_port
        self._mode = mode
        self._socket: Optional[socket.socket] = None
        self._connection: Optional[Connection] = None
        self.signals = ClientSignals()

    def __del__(self) -> None:
        if self._socket is not None:
            self._socket.close()

    @pyqtSlot(str)
    def connect(self, address: str) -> None:
        """Connect to a server at a specified address."""

        addr, *rest = address.split(":")

        if len(rest) == 1:
            port = int(rest[0])
        else:
            port = constants.DEFAULT_SERVER_PORT

        self._addr = f"{addr}:{port}"

        try:
            self._socket = socket.socket()
            self._socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self._socket.connect((addr, port))
            self._socket.sendall(
                Message.of(
                    JSONMessageContent(
                        content_type=JSONContentType.HANDSHAKE,
                        server_host=self._server_host,
                        server_port=self._server_port,
                    ).to_bytes(),
                    ContentType.JSON,
                ).to_bytes()
            )
            self.signals.connection.emit(self._addr)
            print(f"Connected to the server {self._addr}")
        except socket.error:
            self._addr = None
            self._socket = None

            print(f"Could not connect to the {self._addr}")
            traceback.print_exc()

    @pyqtSlot()
    def disconnect(self) -> None:
        """Disconnect from the server."""

        if self._socket is not None:
            self._socket.close()
            self.signals.disconnection.emit()
            print(f"Disconnected from the server {self._addr}")

    @pyqtSlot(EncryptionMode)
    def change_mode(self, mode: EncryptionMode) -> None:
        """Change the encryption mode."""

        self._mode = mode

        print(f"Changed encryption mode to {self._mode}")

    @pyqtSlot(str)
    def send_message(self, message: str) -> None:
        """Send a message to the server."""

        if self._socket is not None:
            data = message.encode(DFrame.encoding)

            print(f"Sending a message to the {self._addr}")
            self._socket.sendall(IFrame(len(data), self._mode).to_bytes())
            self._socket.sendall(data)

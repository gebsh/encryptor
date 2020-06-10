import socket
import traceback
from typing import Optional
from PyQt5.QtCore import QObject, pyqtSignal, pyqtSlot
from encryptor import constants
from .frames import IFrame


class ClientSignals(QObject):
    """Signals available from a running client thread."""

    connection = pyqtSignal(str)
    disconnection = pyqtSignal()


class ClientWorker(QObject):
    """Worker responsible for sending data to another client."""

    def __init__(self) -> None:
        super(ClientWorker, self).__init__()

        self._socket: Optional[socket.socket] = None
        self._addr: Optional[str] = None
        self.signals = ClientSignals()

    def __del__(self) -> None:
        if self._socket is not None:
            self._socket.close()

    @pyqtSlot(str)
    def connect(self, address: str) -> None:
        """Connect to a specified address."""

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
            self.signals.connection.emit(self._addr)
        except socket.error:
            self._addr = None
            self._socket = None

            print(f"Could not connect to the {self._addr}")
            traceback.print_exc()

    @pyqtSlot()
    def disconnect(self) -> None:
        """Disconnect from the currently connected address."""

        if self._socket is not None:
            self._socket.close()
            self.signals.disconnection.emit()

    @pyqtSlot(bytes)
    def send(self, data: bytes) -> None:
        """Send data to another client."""

        if self._socket is not None:
            print(f"Sending a message to the {self._addr}")
            self._socket.sendall(IFrame(len(data)).to_bytes())
            self._socket.sendall(data)

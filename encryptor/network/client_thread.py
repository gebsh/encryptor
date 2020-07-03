import socket
from typing import Optional
from pathlib import Path
from Crypto.PublicKey import RSA
from PyQt5.QtCore import QObject, pyqtSignal, pyqtSlot
from encryptor.encryption.mode import EncryptionMode
from encryptor.encryption.crypto import encrypt
from .connection import Address
from .message import ContentType, Message, MessageWriter


class ClientWorker(QObject):
    """Worker responsible for sending data to another client."""

    connection = pyqtSignal(Address)
    disconnection = pyqtSignal()

    def __init__(
        self, server_addr: Address, mode: EncryptionMode, pubkey: RSA.RsaKey
    ) -> None:
        super().__init__()

        self._server_addr = server_addr
        self._mode = mode
        self._pubkey = pubkey
        self._writer: Optional[MessageWriter] = None

    def __del__(self) -> None:
        self.disconnect()

    @pyqtSlot(Address)
    def connect(self, addr: Address) -> None:
        """Connect to a server at a specified address."""

        sock = socket.socket()

        try:
            print(f"Connecting to the {addr}")
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            sock.connect((addr.host, addr.port))

            self._writer = MessageWriter(sock)

            self._writer.write_handshake(self._server_addr)
        except OSError:
            print(f"Could not connect to the {addr}")
            self.disconnect()

    @pyqtSlot()
    def disconnect(self) -> None:
        """Disconnect from the server."""

        if self._writer is not None:
            self._writer.close()
            print(f"Disconnected from the {self._writer.endpoint_addr}")

            self._writer = None
            self.disconnection.emit()

    @pyqtSlot(Address)
    def handshake(self, addr: Address) -> None:
        """Handshake with a specified address."""

        if self._writer is not None:
            if self._writer.endpoint_addr == addr:
                self._writer.write_pubkey(self._pubkey)
            else:
                raise RuntimeError(
                    f"Handshake requested with {addr} but the client is already connected to {self._writer.endpoint_addr}"
                )
        else:
            self.connect(addr)

    @pyqtSlot(RSA.RsaKey)
    def rec_pubkey(self, pubkey: RSA.RsaKey) -> None:
        """Register a receipent's pubkey."""

        if self._writer is not None:
            self._writer.update_endpoint_pubkey(pubkey)

            if not self._writer.connected:
                self._writer.write_pubkey(self._pubkey)

            if self._writer.connected:
                self.connection.emit(self._writer.endpoint_addr)
        else:
            raise RuntimeError(
                "Cannot register a receipent's pubkey, writer does not exist"
            )

    @pyqtSlot(EncryptionMode)
    def change_mode(self, mode: EncryptionMode) -> None:
        """Change the encryption mode."""

        self._mode = mode

        print(f"Changed encryption mode to {self._mode}")

    @pyqtSlot(str)
    def send_message(self, message: str) -> None:
        """Send a message to the server."""

        if self._writer is not None:
            # TODO: Don't hardcode encoding here.
            encrypted_message = encrypt(
                message.encode("utf-8"), self._mode, self._writer._endpoint_pubkey
            )
            self._writer.write(
                Message.of(
                    encrypted_message, ContentType.BINARY, encryption_mode=self._mode
                )
            )
        else:
            raise RuntimeError("Cannot send a message, writer does not exist")

    @pyqtSlot(str)
    def send_file(self, filepath: str) -> None:
        """Send a file to the server."""

        path = Path(filepath)

        if self._writer is not None:
            data = encrypt(path.read_bytes(), self._mode, self._writer._endpoint_pubkey)

            print(f"Sending a file {filepath} to the {self._writer.endpoint_addr}")
            self._writer.write(
                Message.of(data, ContentType.FILE, mode=self._mode, filename=path.name)
            )

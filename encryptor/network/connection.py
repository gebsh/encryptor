import socket
from typing import cast, NoReturn, Optional, Tuple
from PyQt5.QtCore import QObject, pyqtSignal
from .message import Message, MessageReader, MessageWriter


class ConnectionAddr:
    """Addresses of a connection."""

    def __init__(
        self, sender_addr: Tuple[str, int], receiver_addr: Tuple[str, int]
    ) -> None:
        self.sender_host = sender_addr[0]
        self.sender_port = sender_addr[1]
        self.receiver_host = receiver_addr[0]
        self.receiver_port = receiver_addr[1]

    def __repr__(self) -> str:
        return f"{self.from_addr()} -> {self.to_addr()}"

    def __str__(self) -> str:
        return self.__repr__()

    def from_addr(self) -> str:
        """Address of the sender."""

        return f"{self.sender_host}:{self.sender_port}"

    def to_addr(self) -> str:
        """Address of the receiver."""

        return f"{self.receiver_host}:{self.receiver_port}"


class Connection:
    """Partial one-way connection."""

    def __init__(
        self,
        /,
        reader: Optional[MessageReader] = None,
        writer: Optional[MessageWriter] = None,
    ) -> None:
        assert (reader is None and writer is not None) or (
            reader is not None and writer is None
        ), "Either a reader or a writer must be specified"

        self._reader = reader
        self._writer = writer

    def upgrade(
        self,
        /,
        reader: Optional[MessageReader] = None,
        writer: Optional[MessageWriter] = None,
    ) -> "DuplexConnection":
        """Upgrade to a two-way duplex connection."""

        if self._reader is None:
            assert (
                reader is not None
            ), "Cannot upgrade the writer connection without a reader"

            return DuplexConnection(reader, cast(MessageWriter, self._writer))

        assert (
            writer is not None
        ), "Cannot upgrade the reader connection without a writer"

        return DuplexConnection(self._reader, writer)

    # def read(self) -> NoReturn:
    # """Read incoming messages."""

    # while True:
    #     message = Message.read(self._read_sock)

    #     print(f"Received a new message from {self._read_addr.from_addr}: {message}")
    #     self.new_message.emit(message)


class DuplexConnection(QObject):
    """Connection between two applications."""

    new_message = pyqtSignal(Message)

    def __init__(self, reader: MessageReader, writer: MessageWriter) -> None:
        super().__init__()

        self._read_addr = ConnectionAddr(
            reader.sock.getsockname(), reader.sock.getpeername()
        )
        self._write_addr = ConnectionAddr(
            writer.sock.getsockname(), writer.sock.getpeername()
        )

import json
import socket
import struct
import sys
import os
from pathlib import Path
from types import SimpleNamespace
from typing import Literal, Optional, Union
from Crypto.PublicKey import RSA
from encryptor.constants import BUFFER_SIZE, METAHEADER_LEN
from encryptor.encryption.mode import EncryptionMode
from encryptor.utils.json import json_encode, json_decode, json_serializable
from encryptor.utils.serializable_enum import SerializableEnum
from .connection import Address, ConnectionClosed


class ContentType(SerializableEnum):
    """A type of a message content."""

    JSON = "json"
    BINARY = "binary"
    FILE = "file"


class JSONContentType(SerializableEnum):
    """A type of a JSON message content."""

    HANDSHAKE = "handshake"
    PUBKEY = "pubkey"
    FILE_PROGRESS = "progress"


@json_serializable
class MessageHeaders(SimpleNamespace):
    """A header sent between applications."""

    ENCODING = "utf-8"
    REQUIRED_HEADERS = (
        "byteorder",
        "content_length",
        "content_type",
        "content_encoding",
    )
    byteorder: Union[Literal["big"], Literal["little"]]
    content_length: int
    content_type: ContentType
    content_encoding: str
    mode: EncryptionMode
    filename: str
    part_number: int
    number_of_parts: int

    @staticmethod
    def to_json(header: "MessageHeaders") -> str:
        """Convert message headers to JSON."""

        return json_encode(header.__dict__)

    @staticmethod
    def from_json(s: str) -> "MessageHeaders":
        """Convert JSON to message headers."""

        headers = json_decode(s)

        if not isinstance(headers, dict):
            raise TypeError(
                f"Cannot convert {headers.__class__.__name__} to headers dictionary"
            )

        for header in MessageHeaders.REQUIRED_HEADERS:
            if header not in headers:
                raise TypeError(f"Missing a required header {header}")

        return MessageHeaders(**headers)


class Message:
    """Message sent between applications."""

    def __init__(self, headers: MessageHeaders, content: bytes) -> None:
        self.headers = headers
        self.content = content

    def __repr__(self) -> str:
        return f"Message({repr({'headers': self.headers, 'content': self.content})})"

    def __str__(self) -> str:
        ellipsis = "..." if self.headers.content_length > 64 else ""

        return f"Message(len: {self.headers.content_length}) {{ {self.content!r:.64}{ellipsis} }}"

    def to_bytes(self) -> bytes:
        """Convert the message to bytes."""

        headers = json_encode(self.headers).encode(MessageHeaders.ENCODING)
        metaheader = struct.pack(">Q", len(headers))

        return metaheader + headers + self.content

    @staticmethod
    def of(
        content: bytes,
        content_type: ContentType,
        mode: Optional[EncryptionMode] = None,
        filename: Optional[str] = None,
        part_number: Optional[int] = None,
        number_of_parts: Optional[int] = None,
        content_encoding: str = "utf-8",
    ) -> "Message":
        """Create a new message with a given content and its type and encoding."""

        return Message(
            MessageHeaders(
                byteorder=sys.byteorder,
                content_length=len(content),
                content_type=content_type,
                content_encoding=content_encoding,
                mode=mode,
                filename=filename,
                part_number=part_number,
                number_of_parts=number_of_parts,
            ),
            content,
        )

    def write_to_file(self, file_path: Path) -> None:
        """Writing bytes to file"""

        print("pisanie bajtow")

        if file_path.exists():
            if self.headers.part_number is None or self.headers.part_number < 2:
                os.remove(file_path)
                file_path.write_bytes(self.content)
            else:
                existing_bytes = file_path.read_bytes()
                file_path.write_bytes(existing_bytes + self.content)
        else:
            file_path.write_bytes(self.content)

class JSONMessageContent(SimpleNamespace):
    """Content of a JSON message sent between applications."""

    ENCODING = "utf-8"
    REQUIRED_FIELDS = ("content_type",)
    content_type: JSONContentType

    def to_bytes(self) -> bytes:
        """Convert the content to bytes."""

        return json.dumps(
            {**self.__dict__, "type": self.content_type},
            default=str,
            ensure_ascii=False,
        ).encode(JSONMessageContent.ENCODING)

    @staticmethod
    def from_message(message: Message) -> "JSONMessageContent":
        """Extract JSON content from a message."""

        content_type = message.headers.content_type

        if content_type != ContentType.JSON:
            raise TypeError(
                f"Cannot extract JSON content from a message with declared content type as {content_type}"
            )

        data = json_decode(message.content.decode(JSONMessageContent.ENCODING))

        if not isinstance(data, dict):
            raise TypeError(
                f"Cannot convert {data!r} to JSON content, value is not a dictionary"
            )

        for field in JSONMessageContent.REQUIRED_FIELDS:
            if field not in data:
                raise ValueError(f"Missing a required field {field}")

        return JSONMessageContent(**data)


class MessageReader:
    """Reads messages from an endpoint."""

    def __init__(self, sock: socket.socket) -> None:
        self.endpoint_addr = Address(*sock.getpeername())
        self._sock = sock
        self._buffer = b""
        self._headers_len: Optional[int] = None
        self._headers: Optional[MessageHeaders] = None
        self._content: Optional[bytes] = None
        self._request_reading = True
        self._closed = False
        self._data_in_progress: Optional[bytes] = None


    def __del__(self) -> None:
        self.close()

    def close(self) -> None:
        """Close the reader and free used resources."""

        if not self._closed:
            print(f"Closing the reader from {self.endpoint_addr}")

            try:
                self._sock.shutdown(socket.SHUT_RDWR)
            except OSError:
                pass
            finally:
                self._sock.close()

            self._closed = True

    def read_handshake(self) -> Address:
        """Read a handshake from the endpoint."""

        handshake_content = JSONMessageContent.from_message(
            self.read(content_type=ContentType.JSON)
        )

        return Address(handshake_content.ret_host, handshake_content.ret_port)

    def read_part_of_file(self, message: Message) -> None:
        """Read and rememeber part of a large file from the endpoint."""

        if self._data_in_progress is not None:
            self._data_in_progress += message.content
        else:
            self._data_in_progress = message.content

    def read_pubkey(self) -> RSA.RsaKey:
        """Read a pubkey from the endpoint."""

        pubkey_message = self.read(content_type=ContentType.BINARY)

        return RSA.import_key(pubkey_message.content)

    def read(
        self,
#        keys_dir: Optional[Path] = None,
        content_type: Optional[ContentType] = None,
    ) -> Message:
        """Read a single message."""

        message: Optional[Message] = None

        while message is None:
            message = self.try_read()

        message_type = message.headers.content_type

        if content_type is None or message_type == content_type:
            print(f"New message from {self.endpoint_addr}: {message}")

            return message

        raise TypeError(f"Expected content type {content_type} but got {message_type}")

    def try_read(self) -> Optional[Message]:
        """Try to read a single message."""

        if self._request_reading:
            data = self._sock.recv(BUFFER_SIZE)

            if data == b"":
                raise ConnectionClosed()

            self._buffer += data
            self._request_reading = False

        if self._headers_len is None:
            self._process_metaheader()

        if self._headers_len is not None and self._headers is None:
            self._process_headers(self._headers_len)

        if self._headers is not None and self._content is None:
            self._process_content(self._headers)

            if self._content is not None:
                headers = self._headers  # type: ignore
                content = self._content
                self._headers_len = None
                self._headers = None
                self._content = None

                return Message(headers, content)

        return None

    def _process_metaheader(self) -> None:
        if len(self._buffer) >= METAHEADER_LEN:
            self._headers_len = struct.unpack(">Q", self._buffer[:METAHEADER_LEN])[0]
            self._buffer = self._buffer[METAHEADER_LEN:]
        else:
            self._request_reading = True

    def _process_headers(self, headers_len: int) -> None:
        if len(self._buffer) >= headers_len:
            self._headers = json_decode(
                self._buffer[:headers_len].decode(MessageHeaders.ENCODING)
            )
            self._buffer = self._buffer[headers_len:]
        else:
            self._request_reading = True

    def _process_content(self, headers: MessageHeaders) -> None:
        if len(self._buffer) >= headers.content_length:
            self._content = self._buffer[: headers.content_length]
            self._buffer = self._buffer[headers.content_length :]

            if self._buffer == b"":
                self._request_reading = True
        else:
            self._request_reading = True


class MessageWriter:
    """Writes messages to an endpoint."""

    def __init__(self, sock: socket.socket) -> None:
        self.endpoint_addr = Address(*sock.getpeername())
        self._endpoint_pubkey: Optional[RSA.RsaKey] = None
        self._connected = False
        self._closed = False
        self._sent_pubkey = False
        self._sock = sock
        self._file_in_progress_path: Optional[Path] = None
        self._data_in_progress: Optional[bytes] = None
        self._number_of_parts: Optional[int] = None

    def __del__(self) -> None:
        self.close()

    @property
    def connected(self) -> bool:
        """Determine whether the writer is ready to send messages."""

        return self._endpoint_pubkey is not None and self._connected

    def close(self) -> None:
        """Close the writer and free used resources."""

        if not self._closed:
            print(f"Closing the writer to {self.endpoint_addr}")

            try:
                self._sock.shutdown(socket.SHUT_RDWR)
            except OSError:
                pass
            finally:
                self._sock.close()

            self._closed = True

    def update_endpoint_pubkey(self, pubkey: RSA.RsaKey) -> None:
        """Update pubkey of the endpoint."""

        self._endpoint_pubkey = pubkey

        if self._sent_pubkey:
            self._connected = True

            print(f"Established connection to {self.endpoint_addr}")

    def write_handshake(self, ret_address: Address) -> None:
        """Write a handshake to the endpoint."""

        print(f"Sending a handshake to {self.endpoint_addr}")
        self._sock.sendall(
            Message.of(
                JSONMessageContent(
                    content_type=JSONContentType.HANDSHAKE,
                    ret_host=ret_address.host,
                    ret_port=ret_address.port,
                ).to_bytes(),
                ContentType.JSON,
            ).to_bytes()
        )

    def write_pubkey(self, pubkey: RSA.RsaKey) -> None:
        """Write a pubkey to the endpoint."""

        print(f"Sending a pubkey to {self.endpoint_addr}")
        self._sock.sendall(
            Message.of(pubkey.export_key(), ContentType.BINARY).to_bytes()
        )

        self._sent_pubkey = True

        if self._endpoint_pubkey is not None:
            self._connected = True

            print(f"Established connection to {self.endpoint_addr}")

    def write_upload_progress(self, part_number: int) -> None:
        """Write information about receiving part of the file to the endpoint."""

        print(f"Received part {part_number} of the file")

        self._sock.sendall(
            Message.of(
                JSONMessageContent(
                    content_type=JSONContentType.FILE_PROGRESS,
                    part_number=part_number,
                ).to_bytes(),
                ContentType.JSON,
            ).to_bytes()
        )


    def write(self, message: Message) -> None:
        """Write a single message to the endpoint."""

        if message.headers.number_of_parts is not None and message.headers.number_of_parts == message.headers.part_number:
            self._data_in_progress = None
            self._file_in_progress_path = None
            self._number_of_parts = None

        assert (
            self.connected
        ), "Cannot write a message without an established connection"

        print(f"Sending a message {message} to {self.endpoint_addr}")
        self._sock.sendall(message.to_bytes())

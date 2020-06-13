import io
import json
import socket
import struct
import sys
from enum import Enum
from types import SimpleNamespace
from typing import cast, Any, List, Literal, Optional, Union
from Crypto.PublicKey import RSA
from encryptor.constants import BUFFER_SIZE, METAHEADER_LEN
from .connection import Address
from .exceptions import ConnectionClosed


class ContentType(Enum):
    """A type of a message content."""

    JSON = "json"
    BINARY = "binary"

    def __str__(self) -> str:  # pylint: disable=invalid-str-returned
        return cast(str, self.value)

    @classmethod
    def values(cls) -> List[str]:
        """Get list of types values."""

        return list(map(lambda t: t.value, cls))  # type: ignore


class JSONContentType(Enum):
    """A type of a JSON message content."""

    HANDSHAKE = "handshake"
    PUBKEY = "pubkey"

    def __str__(self) -> str:  # pylint: disable=invalid-str-returned
        return cast(str, self.value)

    @classmethod
    def values(cls) -> List[str]:
        """Get list of types values."""

        return list(map(lambda t: t.value, cls))  # type: ignore


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

    @staticmethod
    def from_json(data: Any) -> "MessageHeaders":
        """Convert JSON data to message headers."""

        if not isinstance(data, dict):
            raise ValueError(
                f"Cannot convert {data!r} to headers, value is not a dictionary"
            )

        for header in MessageHeaders.REQUIRED_HEADERS:
            if header not in data:
                raise ValueError(f"Missing a required header {header}")

        data["content_type"] = ContentType(data["content_type"])

        return MessageHeaders(**data)

    @staticmethod
    def to_json(header: "MessageHeaders") -> str:
        """Convert message headers to JSON data."""

        return json.dumps(header.__dict__, default=str, ensure_ascii=False)


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

        headers = MessageHeaders.to_json(self.headers).encode(MessageHeaders.ENCODING)
        metaheader = struct.pack(">Q", len(headers))

        return metaheader + headers + self.content

    @staticmethod
    def of(
        content: bytes, content_type: ContentType, content_encoding: str = "utf-8"
    ) -> "Message":
        """Create a new message with a given content and its type and encoding."""

        return Message(
            MessageHeaders(
                byteorder=sys.byteorder,
                content_length=len(content),
                content_type=content_type,
                content_encoding=content_encoding,
            ),
            content,
        )


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
            raise ValueError(
                f"Cannot extract JSON content from a message with declared content type as {content_type}"
            )

        data = _decode_json(message.content, JSONMessageContent.ENCODING)

        if not isinstance(data, dict):
            raise ValueError(
                f"Cannot convert {data!r} to JSON content, value is not a dictionary"
            )

        for field in JSONMessageContent.REQUIRED_FIELDS:
            if field not in data:
                raise ValueError(f"Missing a required field {field}")

        data["content_type"] = JSONContentType(data["content_type"])

        return JSONMessageContent(**data)


class MessageReader:
    """Reads messages from an endpoint."""

    def __init__(self, sock: socket.socket, keys_dir: str) -> None:
        self.endpoint_addr = Address(*sock.getpeername())
        self._sock = sock
        self._buffer = b""
        self._headers_len: Optional[int] = None
        self._headers: Optional[MessageHeaders] = None
        self._content: Optional[bytes] = None
        self._request_reading = True
        self._closed = False
        self._keys_dir = keys_dir

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

    def read_pubkey(self) -> RSA.RsaKey:
        """Read a pubkey from the endpoint."""

        pubkey_message = self.read(content_type=ContentType.BINARY)

        return RSA.import_key(pubkey_message.content)

    def read(self, content_type: Optional[ContentType] = None) -> Message:
        """Read a single message."""

        message: Optional[Message] = None

        while message is None:
            message = self.try_read()

        message_type = message.headers.content_type

        if content_type is None or message_type == content_type:
            print(f"New message from {self.endpoint_addr}: {message}")

            return message

        raise ValueError(f"Expected content type {content_type} but got {message_type}")

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
            self._headers = MessageHeaders.from_json(
                _decode_json(self._buffer[:headers_len], MessageHeaders.ENCODING)
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

    def write(self, message: Message) -> None:
        """Write a single message to the endpoint."""

        assert (
            self.connected
        ), "Cannot write a message without an established connection"

        # TODO: Add encryption here.
        print(f"Sending a message {message} to {self.endpoint_addr}")
        self._sock.sendall(message.to_bytes())


def _decode_json(data: bytes, encoding: str) -> Any:
    try:
        json_text = io.TextIOWrapper(io.BytesIO(data), encoding=encoding, newline="")
        json_data = json.load(json_text)
    finally:
        json_text.close()

    return json_data

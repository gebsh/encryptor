from typing import Any


class MessageHeader:
    """A header sent between applications."""

    REQUIRED_HEADERS = (
        "byteorder",
        "content-length",
        "content-type",
        "content-encoding",
    )

    def __init__(
        self,
        byteorder: str,
        content_type: str,
        content_encoding: str,
        content_length: int,
    ) -> None:
        self.byteorder = byteorder
        self.content_type = content_type
        self.content_encoding = content_encoding
        self.content_length = content_length

    @staticmethod
    def from_json(data: Any) -> "MessageHeader":
        """Convert JSON data to headers."""

        if not isinstance(data, dict):
            raise ValueError(
                f"Cannot convert {data!r} to headers, value is not a dictionary"
            )

        for header in MessageHeader.REQUIRED_HEADERS:
            if header not in data:
                raise ValueError(f"Missing required header {header}")

        return MessageHeader(**data)

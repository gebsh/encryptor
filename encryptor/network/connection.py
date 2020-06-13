from typing import Any, Optional


class ConnectionClosed(Exception):
    """Socket connection closed."""


class Address:
    """Address of an endpoint."""

    def __init__(self, host: str, port: int) -> None:
        self.host = host
        self.port = port

    def __repr__(self) -> str:
        return f"{self.host}:{self.port}"

    def __str__(self) -> str:
        return self.__repr__()

    def __eq__(self, value: Any) -> bool:
        if isinstance(value, Address):
            return self.host == value.host and self.port == value.port

        return False

    def __ne__(self, value: Any) -> bool:
        return not self.__eq__(value)

    @staticmethod
    def from_str(addr: str, default_port: Optional[int] = None) -> "Address":
        """Create a new address from its string representation."""

        host, *rest = addr.split(":")

        if len(rest) == 1:
            return Address(host, int(rest[0]))

        if default_port is not None:
            return Address(host, default_port)

        raise ValueError(
            "Given string does not contain a port and no default port was specified"
        )

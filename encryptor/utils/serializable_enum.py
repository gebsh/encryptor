from enum import Enum
from .json import json_serializable


@json_serializable
class SerializableEnum(Enum):
    """JSON serializable enumeration."""

    @classmethod
    def to_json(cls, enum_member: "SerializableEnum") -> str:
        """Encode to JSON."""

        return str(enum_member.value)

    @classmethod
    def from_json(cls, s: str) -> "SerializableEnum":
        """Decode from JSON."""

        return cls(s)

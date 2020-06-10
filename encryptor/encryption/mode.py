from enum import Enum


class EncryptionMode(Enum):
    """Mode of encryption."""

    ECB = "ECB"
    CBC = "CBC"
    CFB = "CFB"
    OFB = "OFB"

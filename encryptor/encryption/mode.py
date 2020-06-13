from encryptor.utils.serializable_enum import SerializableEnum


class EncryptionMode(SerializableEnum):
    """Mode of encryption."""

    ECB = "ECB"
    CBC = "CBC"
    CFB = "CFB"
    OFB = "OFB"

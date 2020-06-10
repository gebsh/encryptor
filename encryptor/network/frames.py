from encryptor import constants
from encryptor.encryption.mode import EncryptionMode


class IFrame:
    """Frame with data information."""

    encoding = "ascii"
    frame_size = constants.BUFFER_SIZE
    data_length_len = 64
    mode_len = 3
    filler_len = frame_size - data_length_len - mode_len

    def __init__(self, data_len: int, mode: EncryptionMode) -> None:
        self.data_length = data_len
        self.mode = mode

    @staticmethod
    def from_bytes(data: bytes) -> "IFrame":
        """Convert a bytes sequence to the frame."""

        s = data.decode(IFrame.encoding)
        data_length = int(s[: IFrame.data_length_len])
        mode = EncryptionMode(
            s[IFrame.data_length_len : IFrame.data_length_len + IFrame.mode_len]
        )

        return IFrame(data_length, mode)

    def to_bytes(self) -> bytes:
        """Convert the frame to bytes sequence."""

        data_length_region = f"{self.data_length:064}".encode(IFrame.encoding)
        mode_region: bytes = self.mode.value.encode(IFrame.encoding)
        filler_region = bytes(IFrame.filler_len)

        return data_length_region + mode_region + filler_region


class DFrame:
    """Frame with data."""

    encoding = "utf-8"

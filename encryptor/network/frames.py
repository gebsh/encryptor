from encryptor import constants


class IFrame:
    """Frame with data information."""

    encoding = "ascii"
    frame_size = constants.BUFFER_SIZE
    data_length_len = 64
    filler_len = frame_size - data_length_len

    def __init__(self, data_len: int) -> None:
        self.data_length = data_len

    @staticmethod
    def from_bytes(data: bytes) -> "IFrame":
        """Convert a bytes sequence to the frame."""

        s = data.decode(IFrame.encoding)
        data_length = int(s[: IFrame.data_length_len])

        return IFrame(data_length)

    def to_bytes(self) -> bytes:
        """Convert the frame to bytes sequence."""

        data_length_region = f"{self.data_length:064}".encode(IFrame.encoding)
        filler_region = bytes(IFrame.filler_len)

        return data_length_region + filler_region

import socket
from PyQt5.QtCore import QRunnable, QThread, pyqtSlot


def host_ip() -> str:
    """Get an IP address of the host."""

    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    ip: str

    try:
        s.connect(("10.255.255.255", 1))
        ip = s.getsockname()[0]
    except Exception:
        ip = "127.0.0.1"
    finally:
        s.close()

    return ip


class ServerWorker(QThread):
    """Worker thread that is responsible for receiving data from other clients."""

    def __init__(self, host: str, port: int) -> None:
        super(ServerWorker, self).__init__()

        self._host = host
        self._port = port
        self._socket = socket.socket()

    def __del__(self) -> None:
        self._socket.close()

    @pyqtSlot()
    def run(self) -> None:
        """Listen for any incoming data."""

        self._socket.bind((self._host, self._port))
        self._socket.listen()

        print("ServerWorker listens on {}:{}".format(self._host, self._port))

        connection, address = self._socket.accept()

        with connection:
            print("{} connected".format(address))

            while True:
                data = connection.recv(1024)

                if not data:
                    break

                print("Received data {!r}".format(data))


class SendWorker(QRunnable):
    """Worker that is responsible for sending data to another client."""

    def __init__(self, data: bytes) -> None:
        super(SendWorker, self).__init__()

        self._data = data
        self._socket = socket.socket()

    @pyqtSlot()
    def run(self) -> None:
        """Send data to another client."""

        self._socket.connect(("127.0.0.1", 4000))
        self._socket.sendall(self._data)

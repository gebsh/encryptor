import sys
from typing import Optional
from PyQt5.QtGui import QCloseEvent
from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5.QtCore import QSize, QThread
from encryptor.widgets.menu_bar import MenuBar
from encryptor.widgets.status_bar import StatusBar
from encryptor.widgets.send_box import SendBox
from encryptor.network.client_thread import ClientWorker
from encryptor.network.server_thread import ServerWorker


class MainWindow(QMainWindow):
    """Main window of the application."""

    def __init__(self, port: int) -> None:
        super(MainWindow, self).__init__()

        self._receiver_ip: Optional[str] = None
        self._client_thread = QThread()
        self._client_worker = ClientWorker()
        self._server_worker = ServerWorker("127.0.0.1", port)

        self._init_gui()
        self._init_client()
        self._init_server()
        self.show()

    def closeEvent(self, event: QCloseEvent) -> None:
        """Handle close event."""

        self._server_worker.quit()
        event.accept()

    def _init_gui(self) -> None:
        self._menu_bar = MenuBar()
        self._status_bar = StatusBar(self._server_worker.address)
        self._send_box = SendBox()
        self._menu_bar.connection.connect(self._client_worker.connect)
        self._menu_bar.disconnection.connect(self._client_worker.disconnect)
        self._send_box.send.connect(self._client_worker.send)
        self._client_worker.signals.connection.connect(
            self._status_bar.update_server_address
        )
        self._client_worker.signals.disconnection.connect(
            lambda: self._status_bar.update_server_ip(None)
        )

        self.setWindowTitle("Encryptor")
        self.setMinimumSize(QSize(640, 360))
        self.setMenuBar(self._menu_bar)
        self.setStatusBar(self._status_bar)
        self.setCentralWidget(self._send_box)

    def _init_client(self) -> None:
        self._client_worker.moveToThread(self._client_thread)
        self._client_thread.start()

    def _init_server(self) -> None:
        self._server_worker.start()


def run(port: int):
    """Run the application."""

    qt_app = QApplication(sys.argv)
    window = MainWindow(port)

    sys.exit(qt_app.exec_())

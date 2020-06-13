import sys
from typing import Optional
from PyQt5.QtGui import QCloseEvent
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QHBoxLayout
from PyQt5.QtCore import QSize, QThread
from encryptor.encryption.mode import EncryptionMode
from encryptor.encryption.keys import keys_exist, create_keys
from encryptor.widgets.menu_bar import MenuBar
from encryptor.widgets.status_bar import StatusBar
from encryptor.widgets.send_box import SendBox
from encryptor.widgets.auth_dialogs import NewKeysDialog
from encryptor.widgets.messages_list import MessagesList
from encryptor.network.client_thread import ClientWorker
from encryptor.network.server_thread import ServerThread


class MainWindow(QMainWindow):
    """Main window of the application."""

    def __init__(self, port: int, keys_dir: str) -> None:
        super(MainWindow, self).__init__()

        self._receiver_ip: Optional[str] = None
        self._client_thread = QThread()
        self._client_worker = ClientWorker("127.0.0.1", port, EncryptionMode.ECB)
        self._server_worker = ServerThread("127.0.0.1", port)

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
        self._status_bar = StatusBar("self._server_worker.address")
        self._send_box = SendBox()
        self._messages_list = MessagesList()
        central_widget = QWidget()
        central_layout = QHBoxLayout()

        self._menu_bar.connection.connect(self._client_worker.connect)
        self._menu_bar.disconnection.connect(self._client_worker.disconnect)
        self._status_bar.mode_change.connect(self._client_worker.change_mode)
        self._send_box.send.connect(self._client_worker.send_message)
        self._client_worker.signals.connection.connect(
            self._status_bar.update_server_address
        )
        self._client_worker.signals.disconnection.connect(
            lambda: self._status_bar.update_server_address(None)
        )
        # self._server_worker.signals.new_message.connect(self._messages_list.new_message)

        central_widget.setLayout(central_layout)
        central_layout.addWidget(self._send_box)
        central_layout.addWidget(self._messages_list)
        self.setWindowTitle("Encryptor")
        self.setMinimumSize(QSize(960, 540))
        self.setMenuBar(self._menu_bar)
        self.setStatusBar(self._status_bar)
        self.setCentralWidget(central_widget)

    def _init_client(self) -> None:
        self._client_worker.moveToThread(self._client_thread)
        self._client_thread.start()

    def _init_server(self) -> None:
        self._server_worker.start()


def run(port: int, keys_dir: str) -> None:
    """Run the application."""

    qt_app = QApplication(sys.argv)

    if not keys_exist(keys_dir):
        dialog = NewKeysDialog()

        if dialog.exec_():
            passphrase = dialog.passphrase.text()

            if passphrase != "":
                create_keys(passphrase, keys_dir)

                window = MainWindow(port, keys_dir)

                sys.exit(qt_app.exec_())
    else:
        window = MainWindow(port, keys_dir)

        sys.exit(qt_app.exec_())

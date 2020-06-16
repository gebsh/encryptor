import signal
import sys
from Crypto.PublicKey import RSA
from pathlib import Path
from PyQt5.QtGui import QCloseEvent
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QHBoxLayout
from PyQt5.QtCore import QSize, QThread, QTimer, pyqtSlot
from encryptor.encryption.mode import EncryptionMode
from encryptor.encryption.keys import keys_exist, create_keys, get_public_key, get_private_key
from encryptor.widgets.menu_bar import MenuBar
from encryptor.widgets.status_bar import StatusBar
from encryptor.widgets.send_box import SendBox
from encryptor.widgets.auth_dialogs import NewKeysDialog, AuthDialog
from encryptor.widgets.messages_list import MessagesList
from encryptor.network.connection import Address
from encryptor.network.client_thread import ClientWorker
from encryptor.network.server_thread import ServerThread
from encryptor.network.message import Message


class MainWindow(QMainWindow):
    """Main window of the application."""

    def __init__(self, port: int, keys_dir: Path) -> None:
        super().__init__()

        self._server_thread = ServerThread(Address("127.0.0.1", port))
        self._client_thread = QThread()
        self._client_worker = ClientWorker(
            Address("127.0.0.1", port), EncryptionMode.ECB, get_public_key(keys_dir)
        )
        self._keys_dir = keys_dir

        self._init_gui()
        self._init_client()
        self._init_server()
        self.show()

    def closeEvent(self, event: QCloseEvent) -> None:
        """Handle close event."""

        self._server_thread.quit()
        self._client_thread.quit()
        event.accept()

    def _init_gui(self) -> None:
        self._menu_bar = MenuBar()
        self._status_bar = StatusBar(self._server_thread.addr)
        self._send_box = SendBox()
        self._messages_list = MessagesList()
        central_widget = QWidget()
        central_layout = QHBoxLayout()

        self._menu_bar.connection.connect(self._client_worker.connect)
        self._menu_bar.disconnection.connect(self._client_worker.disconnect)
        self._status_bar.mode_change.connect(self._client_worker.change_mode)
        self._send_box.send_message.connect(self._client_worker.send_message)
        self._send_box.send_file.connect(self._client_worker.send_file)
        self._client_worker.connection.connect(self._status_bar.update_server_addr)
        self._client_worker.disconnection.connect(
            lambda: self._status_bar.update_server_addr(None)
        )
        self._server_thread.handshake.connect(self._client_worker.handshake)
        self._server_thread.pubkey.connect(self._client_worker.rec_pubkey)
        self._server_thread.disconnect.connect(self._client_worker.disconnect)
        self._server_thread.new_message.connect(self._messages_list.new_message)
        self._messages_list.decrypt.connect(self._messages_list.decrypt_message)
        self._messages_list.ask_for_privkey.connect(self.authorize)
        self._server_thread.ask_for_dir.connect(self.create_file_path)
        self._messages_list.ask_for_dir.connect(self.create_file_path)
        self._server_thread.part_received.connect(self._client_worker.file_upload_progress)
        self._server_thread.file_upload_progress.connect(self.send_next_part)

        central_widget.setLayout(central_layout)
        central_layout.addWidget(self._send_box)
        central_layout.addWidget(self._messages_list)
        self.setWindowTitle("Encryptor")
        self.setMinimumSize(QSize(600, 400))
        self.setMenuBar(self._menu_bar)
        self.setStatusBar(self._status_bar)
        self.setCentralWidget(central_widget)

    @pyqtSlot(Message)
    def authorize(self, message: Message) -> None:
        dialog = AuthDialog()

        if dialog.exec_():
            passphrase = dialog.passphrase.text()
            privkey = get_private_key(self._keys_dir, passphrase)
        # TODO handle wrong password
        self._messages_list.set_privkey(privkey, message)

    @pyqtSlot(Message)
    def create_file_path(self, message: Message) -> None:

        files_dir: Path = self._keys_dir / "files"
        files_dir.mkdir(exist_ok=True)
        file_path: Path = files_dir / message.headers.filename
        message.write_to_file(file_path)

    @pyqtSlot(int)
    def send_next_part(self, part_number: int) -> None:

        part_number += 1
        # TODO progressbar
        self._client_worker.send_part_of_file(part_number)

    def _init_client(self) -> None:
        self._client_worker.moveToThread(self._client_thread)
        self._client_thread.start()

    def _init_server(self) -> None:
        self._server_thread.start()


def run(port: int, keys_dir: Path) -> None:
    """Run the application."""

    app = QApplication(sys.argv)
    timer = QTimer()

    signal.signal(signal.SIGINT, lambda *_: app.quit())

    # Using a timer here allows Python's interpreter to run from time to time and handle
    # signals.
    timer.start(500)
    timer.timeout.connect(lambda: None)

    if not keys_exist(keys_dir):
        dialog = NewKeysDialog()

        if dialog.exec_():
            passphrase = dialog.passphrase.text()

            if passphrase != "":
                create_keys(keys_dir, passphrase)
            else:
                return
        else:
            return

    MainWindow(port, keys_dir)
    sys.exit(app.exec_())

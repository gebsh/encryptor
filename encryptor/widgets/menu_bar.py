from PyQt5.QtWidgets import (
    QAction,
    QMenuBar,
    QDialog,
    QLineEdit,
    QLabel,
    QDialogButtonBox,
    QVBoxLayout,
)
from PyQt5.QtCore import pyqtSignal, pyqtSlot
from encryptor.constants import DEFAULT_SERVER_PORT
from encryptor.network.connection import Address


class ConnectDialog(QDialog):
    """A dialog to connect to the server."""

    def __init__(self):
        super().__init__()

        self.textbox = QLineEdit(self)
        textbox_label = QLabel("Enter an address of the server")
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        layout = QVBoxLayout()

        self.setWindowTitle("New connection")
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(textbox_label)
        layout.addWidget(self.textbox)
        layout.addWidget(button_box)
        self.setLayout(layout)


class MenuBar(QMenuBar):
    """Menu bar of the application."""

    connection = pyqtSignal(Address)
    disconnection = pyqtSignal()

    def __init__(self) -> None:
        super().__init__()

        self._connection_menu = self.addMenu("Connection")
        connect_action = QAction("Connect", self)
        disconnect_action = QAction("Disconnect", self)

        connect_action.setShortcut("Ctrl+N")
        connect_action.setStatusTip("Connect to the server")
        connect_action.triggered.connect(self._open_connect_dialog)
        disconnect_action.setShortcut("Ctrl+D")
        disconnect_action.setStatusTip("Disconnect from the server")
        disconnect_action.triggered.connect(self.disconnection.emit)
        self._connection_menu.addActions([connect_action, disconnect_action])

    @pyqtSlot()
    def _open_connect_dialog(self) -> None:
        dialog = ConnectDialog()

        if dialog.exec_():
            self.connection.emit(
                Address.from_str(
                    dialog.textbox.text(), default_port=DEFAULT_SERVER_PORT
                )
            )

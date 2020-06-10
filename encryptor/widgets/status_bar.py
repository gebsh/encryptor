from typing import Optional
from PyQt5.QtWidgets import QLabel, QStatusBar, QComboBox
from PyQt5.QtCore import pyqtSignal, pyqtSlot
from encryptor.encryption.mode import EncryptionMode


class StatusBar(QStatusBar):
    """Status bar of the application."""

    mode_change = pyqtSignal(EncryptionMode)

    def __init__(self, client_address: str) -> None:
        super(StatusBar, self).__init__()

        self._client_address = QLabel(f"Your IP: {client_address}")
        self._server_address = QLabel()
        self._combobox = QComboBox()

        self._server_address.setVisible(False)
        self._combobox.addItems(
            [
                EncryptionMode.ECB.value,
                EncryptionMode.CBC.value,
                EncryptionMode.CFB.value,
                EncryptionMode.OFB.value,
            ]
        )
        self._combobox.currentIndexChanged.connect(
            lambda mode_index: self.mode_change.emit(
                EncryptionMode(self._combobox.itemText(mode_index))
            )
        )
        self.addWidget(self._combobox)
        self.addPermanentWidget(self._client_address)
        self.addPermanentWidget(self._server_address)

    @pyqtSlot(str)
    def update_server_address(self, address: Optional[str]) -> None:
        """Update an address of the connected server."""

        if address is None:
            self._server_address.setVisible(False)
        else:
            self._server_address.setText(f"Connected to: {address}")
            self._server_address.setVisible(True)

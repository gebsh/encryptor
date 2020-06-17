from typing import Optional
from PyQt5.QtWidgets import QLabel, QStatusBar, QComboBox, QProgressBar
from PyQt5.QtCore import pyqtSignal, pyqtSlot
from encryptor.encryption.mode import EncryptionMode
from encryptor.network.connection import Address


class StatusBar(QStatusBar):
    """Status bar of the application."""

    mode_change = pyqtSignal(EncryptionMode)

    def __init__(self, my_addr: Address) -> None:
        super().__init__()

        self._client_address = QLabel(f"Your IP: {my_addr}")
        self._server_address = QLabel()
        self._combobox = QComboBox()
        self._progress_bar = QProgressBar()


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
        self.addWidget(self._progress_bar)
        self.addPermanentWidget(self._client_address)
        self.addPermanentWidget(self._server_address)

    @pyqtSlot(Address)
    def update_server_addr(self, addr: Optional[Address]) -> None:
        """Update an address of the connected server."""

        if addr is None:
            self._server_address.setVisible(False)
        else:
            self._server_address.setText(f"Connected to: {addr}")
            self._server_address.setVisible(True)

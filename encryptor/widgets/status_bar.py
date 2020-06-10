from typing import Optional
from PyQt5.QtWidgets import QLabel, QStatusBar
from PyQt5.QtCore import pyqtSlot


class StatusBar(QStatusBar):
    """Status bar of the application."""

    def __init__(self, client_address: str) -> None:
        super(StatusBar, self).__init__()

        self._client_address = QLabel(f"Your IP: {client_address}")
        self._server_address = QLabel()

        self._server_address.setVisible(False)
        self.addPermanentWidget(self._client_address)
        self.addPermanentWidget(self._server_address)

    @pyqtSlot()
    @pyqtSlot(str)
    def update_server_address(self, address: Optional[str]) -> None:
        """Update an address of the connected server."""

        if address is None:
            self._server_address.setVisible(False)
        else:
            self._server_address.setText(f"Connected to: {address}")
            self._server_address.setVisible(True)

from PyQt5.QtWidgets import QDialog, QDialogButtonBox, QLineEdit, QLabel, QVBoxLayout


class AuthDialog(QDialog):
    """Dialog to authorize user decryption request."""

    def __init__(self) -> None:
        super().__init__()

        self.passphrase = QLineEdit(self)
        self.passphrase.setEchoMode(QLineEdit.Password)
        passphrase_label = QLabel("Enter a passphrase of you private key")
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        layout = QVBoxLayout()

        self.setWindowTitle("Enter key passphrase")
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(passphrase_label)
        layout.addWidget(self.passphrase)
        layout.addWidget(button_box)
        self.setLayout(layout)


class NewKeysDialog(QDialog):
    """Dialog to authorize creation of new user keys."""

    def __init__(self) -> None:
        super().__init__()

        self.passphrase = QLineEdit(self)
        self.passphrase.setEchoMode(QLineEdit.Password)
        passphrase_label = QLabel(
            "It looks like you haven't created your public and private keys yet. Enter a passphrase of your new private key"
        )
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        layout = QVBoxLayout()

        self.setWindowTitle("Enter key passphrase")
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(passphrase_label)
        layout.addWidget(self.passphrase)
        layout.addWidget(button_box)
        self.setLayout(layout)

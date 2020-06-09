from PyQt5.QtWidgets import QDialog, QDialogButtonBox, QVBoxLayout, QLabel, QLineEdit


class ReceiverDialog(QDialog):
    """A dialog to choose a receiver."""

    def __init__(self):
        super(ReceiverDialog, self).__init__()
        self.setWindowTitle("New receiver")

        self.textbox = QLineEdit(self)
        textbox_label = QLabel("Enter an IP")
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        layout = QVBoxLayout()

        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(textbox_label)
        layout.addWidget(self.textbox)
        layout.addWidget(button_box)
        self.setLayout(layout)

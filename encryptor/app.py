import sys
from typing import Optional
from PyQt5.QtGui import QCloseEvent
from PyQt5.QtWidgets import (
    QAction,
    QApplication,
    QLabel,
    QMainWindow,
    QPushButton,
    QPlainTextEdit,
    QVBoxLayout,
    QWidget,
)
from PyQt5.QtCore import QSize, QThreadPool
from encryptor.widgets.dialogs import ReceiverDialog
from encryptor.network.workers import host_ip, ServerWorker, SendWorker


class MainWindow(QMainWindow):
    """Main window of the application."""

    def __init__(self, port: int) -> None:
        super(MainWindow, self).__init__()

        self._host_ip: str = host_ip()
        self._receiver_ip: Optional[str] = None
        self._server_worker = ServerWorker("127.0.0.1", port)
        self._send_threadpool = QThreadPool()

        self.setWindowTitle("Encryptor")
        self.setMinimumSize(QSize(640, 360))
        self._create_menu()
        self._create_status_bar()
        self._create_content()
        self._server_worker.start()
        self.show()

    def closeEvent(self, event: QCloseEvent) -> None:
        """Handle close event."""

        self._server_worker.quit()
        event.accept()

    def _create_status_bar(self) -> None:
        self.receiver_ip_label = QLabel()
        host_ip_label = QLabel("Your IP: {}".format(self._host_ip))
        status_bar = self.statusBar()

        self.receiver_ip_label.setVisible(False)
        status_bar.addPermanentWidget(host_ip_label)
        status_bar.addPermanentWidget(self.receiver_ip_label)

    def _create_menu(self) -> None:
        menu = self.menuBar()
        connection_menu = menu.addMenu("Connection")
        choose_receiver_action = QAction("Choose receiver", self)

        choose_receiver_action.setShortcut("Ctrl+R")
        choose_receiver_action.setStatusTip("Receiver choice")
        choose_receiver_action.triggered.connect(self._handle_receiver_choice)
        connection_menu.addAction(choose_receiver_action)

    def _create_content(self) -> None:
        layout = QVBoxLayout()
        widget = QWidget()
        self.textarea = QPlainTextEdit()
        self.send_button = QPushButton("Send message")

        self.send_button.clicked.connect(self._handle_message_sending)
        layout.addWidget(self.textarea)
        layout.addWidget(self.send_button)
        widget.setLayout(layout)
        self.setCentralWidget(widget)

    def _handle_receiver_choice(self) -> None:
        dialog = ReceiverDialog()

        if dialog.exec_():
            self._update_receiver_ip(dialog.textbox.text())

    def _handle_message_sending(self) -> None:
        worker = SendWorker(self.textarea.toPlainText().encode("utf-8"))

        self._send_threadpool.start(worker)

    def _update_receiver_ip(self, ip: Optional[str]) -> None:
        if ip is None or ip == "":
            self._receiver_ip = None
            self.receiver_ip_label.setVisible(False)
        else:
            self._receiver_ip = ip
            self.receiver_ip_label.setText("Receiver's IP: {}".format(ip))
            self.receiver_ip_label.setVisible(True)


def run(port: int):
    """Run the application."""

    qt_app = QApplication(sys.argv)
    window = MainWindow(port)

    sys.exit(qt_app.exec_())

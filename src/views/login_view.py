from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox
)
from PyQt6.QtCore import Qt, pyqtSignal

class LoginView(QWidget):
    login_successful = pyqtSignal(dict)

    def __init__(self, auth_controller):
        super().__init__()
        self.auth_controller = auth_controller
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Đăng Nhập - Quiz Examination System")
        self.setFixedSize(400, 280)

        layout = QVBoxLayout()
        layout.setSpacing(12)

        title = QLabel("HỆ THỐNG THI TRẮC NGHIỆM")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("font-size: 16px; font-weight: bold; margin-bottom: 10px;")
        layout.addWidget(title)

        self.txt_username = QLineEdit()
        self.txt_username.setPlaceholderText("Tên đăng nhập (Username)")
        layout.addWidget(self.txt_username)

        self.txt_password = QLineEdit()
        self.txt_password.setPlaceholderText("Mật khẩu (Password)")
        self.txt_password.setEchoMode(QLineEdit.EchoMode.Password)
        layout.addWidget(self.txt_password)

        self.btn_login = QPushButton("Đăng Nhập")
        self.btn_login.setStyleSheet("padding: 8px; font-weight: bold; background-color: #2563eb; color: white;")
        self.btn_login.clicked.connect(self.handle_login)
        layout.addWidget(self.btn_login)

        self.setLayout(layout)

    def handle_login(self):
        username = self.txt_username.text().strip()
        password = self.txt_password.text()
        result = self.auth_controller.login(username, password)

        if result["success"]:
            QMessageBox.information(self, "Thành công", result["message"])
            self.login_successful.emit(result["user"])
        else:
            QMessageBox.warning(self, "Lỗi đăng nhập", result["message"])

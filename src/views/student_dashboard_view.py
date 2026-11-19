from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QHeaderView, QAbstractItemView,
    QMessageBox, QFrame
)
from PyQt6.QtCore import Qt


class StudentDashboardView(QWidget):
    """SCR-01: Màn hình Dashboard dành cho Sinh viên."""

    def __init__(self, user=None, controller=None, on_start_quiz=None, on_logout=None):
        super().__init__()
        self.user = user or {"id": 3, "full_name": "Phan Gia Hưng", "email": "hung.pg@student.edu.vn"}
        self.controller = controller
        self.on_start_quiz = on_start_quiz
        self.on_logout = on_logout
        self.quizzes = []
        self._init_ui()
        self.load_quizzes()

    def _init_ui(self):
        self.setWindowTitle("Quiz Examination System - Student Dashboard")
        self.resize(960, 600)
        self.setStyleSheet("""
            QWidget { background-color: #f4f6f9; font-family: 'Segoe UI', Arial; font-size: 14px; color: #1e293b; }
            QFrame#Header { background-color: #1e3a8a; border-radius: 8px; padding: 12px; }
            QLabel#HeaderTitle { color: white; font-size: 18px; font-weight: bold; }
            QLabel#UserInfo { color: #dbeafe; font-size: 13px; }
            QPushButton#PrimaryBtn { background-color: #2563eb; color: white; border-radius: 6px; padding: 8px 16px; font-weight: bold; }
            QPushButton#PrimaryBtn:hover { background-color: #1d4ed8; }
            QPushButton#DangerBtn { background-color: #dc2626; color: white; border-radius: 6px; padding: 8px 14px; font-weight: bold; }
            QPushButton#DangerBtn:hover { background-color: #b91c1c; }
            QTableWidget { background-color: white; border: 1px solid #cbd5e1; border-radius: 6px; gridline-color: #e2e8f0; }
            QHeaderView::section { background-color: #e2e8f0; padding: 8px; font-weight: bold; border: none; }
        """)

        layout = QVBoxLayout(self)
        layout.setSpacing(16)
        layout.setContentsMargins(20, 20, 20, 20)

        # Header
        header = QFrame()
        header.setObjectName("Header")
        h_layout = QHBoxLayout(header)

        title_box = QVBoxLayout()
        lbl_title = QLabel("HỆ THỐNG THI TRẮC NGHIỆM TRỰC TUYẾN")
        lbl_title.setObjectName("HeaderTitle")
        lbl_user = QLabel(f"Sinh viên: {self.user.get('full_name')} ({self.user.get('email')})")
        lbl_user.setObjectName("UserInfo")
        title_box.addWidget(lbl_title)
        title_box.addWidget(lbl_user)

        btn_refresh = QPushButton("Làm mới")
        btn_refresh.setObjectName("PrimaryBtn")
        btn_refresh.clicked.connect(self.load_quizzes)

        btn_logout = QPushButton("Đăng xuất")
        btn_logout.setObjectName("DangerBtn")
        btn_logout.clicked.connect(self._handle_logout)

        h_layout.addLayout(title_box)
        h_layout.addStretch()
        h_layout.addWidget(btn_refresh)
        h_layout.addWidget(btn_logout)
        layout.addWidget(header)

        # Section Title
        lbl_sec = QLabel("Danh sách Bài thi đang mở (Published Quizzes)")
        lbl_sec.setStyleSheet("font-size: 16px; font-weight: bold; color: #0f172a;")
        layout.addWidget(lbl_sec)

        # Quiz Table
        self.table = QTableWidget(0, 6)
        self.table.setHorizontalHeaderLabels([
            "Mã đề", "Tên bài thi", "Mô tả", "Thời gian (phút)", "Điểm đạt", "Thao tác"
        ])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.verticalHeader().setDefaultSectionSize(44)
        layout.addWidget(self.table)

    def load_quizzes(self):
        """Lấy danh sách đề thi đã công bố từ controller hoặc dữ liệu mẫu."""
        if self.controller and hasattr(self.controller, "get_published_quizzes"):
            raw_quizzes = self.controller.get_published_quizzes()
        else:
            raw_quizzes = [
                {"id": 1, "title": "Software Engineering - Chapter 3 Design", "description": "Kiểm tra kiến trúc MVC & UML", "duration_minutes": 15, "pass_score": 5.0, "is_published": 1},
                {"id": 2, "title": "Database Systems - Normalization & SQL", "description": "Chuẩn hóa 1NF, 2NF, 3NF và truy vấn", "duration_minutes": 20, "pass_score": 5.0, "is_published": 1},
                {"id": 3, "title": "Draft Quiz (Ẩn)", "description": "Đề nháp chưa công bố", "duration_minutes": 30, "pass_score": 5.0, "is_published": 0},
            ]

        # Chỉ hiển thị đề thi đã Publish
        self.quizzes = [
            q for q in raw_quizzes
            if (q.get("is_published", 1) if isinstance(q, dict) else getattr(q, "is_published", 1))
        ]

        self.table.setRowCount(len(self.quizzes))
        for row, q in enumerate(self.quizzes):
            q_id = q["id"] if isinstance(q, dict) else q.id
            title = q["title"] if isinstance(q, dict) else q.title
            desc = q.get("description", "") if isinstance(q, dict) else getattr(q, "description", "")
            duration = q.get("duration_minutes", 15) if isinstance(q, dict) else getattr(q, "duration_minutes", 15)
            pass_score = q.get("pass_score", 5.0) if isinstance(q, dict) else getattr(q, "pass_score", 5.0)

            self.table.setItem(row, 0, QTableWidgetItem(str(q_id)))
            self.table.setItem(row, 1, QTableWidgetItem(str(title)))
            self.table.setItem(row, 2, QTableWidgetItem(str(desc)))
            self.table.setItem(row, 3, QTableWidgetItem(f"{duration} phút"))
            self.table.setItem(row, 4, QTableWidgetItem(f"{pass_score} / 10"))

            btn_start = QPushButton("Bắt đầu làm bài")
            btn_start.setObjectName("PrimaryBtn")
            btn_start.clicked.connect(lambda checked, quiz=q: self._start_quiz(quiz))
            self.table.setCellWidget(row, 5, btn_start)

    def _start_quiz(self, quiz):
        title = quiz["title"] if isinstance(quiz, dict) else quiz.title
        reply = QMessageBox.question(
            self, "Xác nhận làm bài",
            f"Bạn có chắc muốn bắt đầu bài thi:\n'{title}'?\nĐồng hồ sẽ bắt đầu đếm ngược ngay lập tức.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            if self.on_start_quiz:
                self.on_start_quiz(quiz)
            else:
                QMessageBox.information(self, "Thông báo", f"Chuyển sang màn hình làm bài: {title}")

    def _handle_logout(self):
        if self.on_logout:
            self.on_logout()
        else:
            self.close()


if __name__ == "__main__":
    import sys
    from PyQt6.QtWidgets import QApplication
    app = QApplication(sys.argv)
    win = StudentDashboardView()
    win.show()
    sys.exit(app.exec())
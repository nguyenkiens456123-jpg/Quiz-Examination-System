from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QHeaderView, QAbstractItemView, QFrame
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor


class ResultView(QWidget):
    """SCR-03: Màn hình hiển thị Kết quả thi & Chi tiết từng câu ĐÚNG/SAI."""

    def __init__(self, result_data=None, on_back_dashboard=None, on_logout=None):
        super().__init__()
        self.result_data = result_data or {
            "quiz_title": "Software Engineering - Chapter 3 Design",
            "score": 6.67,
            "correct_count": 2,
            "total_questions": 3,
            "passed": True,
            "details": [
                {"question": "Trong kiến trúc MVC, thành phần nào hiển thị giao diện?", "chosen": "View", "correct": "View", "is_correct": True},
                {"question": "Chuẩn 3NF loại bỏ hiện tượng nào?", "chosen": "Phụ thuộc hàm bắc cầu vào khóa chính", "correct": "Phụ thuộc hàm bắc cầu vào khóa chính", "is_correct": True},
                {"question": "Auto-Save lưu sau mỗi bao lâu?", "chosen": "5 giây", "correct": "10 giây", "is_correct": False},
            ],
        }
        self.on_back_dashboard = on_back_dashboard
        self.on_logout = on_logout
        self._init_ui()

    def _init_ui(self):
        self.setWindowTitle("Quiz Examination System - Kết quả bài thi")
        self.resize(960, 620)
        self.setStyleSheet("""
            QWidget { background-color: #f4f6f9; font-family: 'Segoe UI', Arial; font-size: 14px; color: #0f172a; }
            QFrame#SummaryCard { background-color: white; border: 1px solid #cbd5e1; border-radius: 10px; padding: 18px; }
            QPushButton#PrimaryBtn { background-color: #2563eb; color: white; border-radius: 6px; padding: 10px 18px; font-weight: bold; }
            QPushButton#PrimaryBtn:hover { background-color: #1d4ed8; }
            QPushButton#DangerBtn { background-color: #dc2626; color: white; border-radius: 6px; padding: 10px 18px; font-weight: bold; }
            QTableWidget { background-color: white; border: 1px solid #cbd5e1; border-radius: 6px; }
            QHeaderView::section { background-color: #e2e8f0; padding: 8px; font-weight: bold; border: none; }
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(16)

        # Summary Card
        card = QFrame()
        card.setObjectName("SummaryCard")
        c_layout = QHBoxLayout(card)

        info_col = QVBoxLayout()
        lbl_title = QLabel(f"KẾT QUẢ BÀI THI: {self.result_data.get('quiz_title', '')}")
        lbl_title.setStyleSheet("font-size: 17px; font-weight: bold; color: #1e3a8a;")

        score = self.result_data.get("score", 0.0)
        correct = self.result_data.get("correct_count", 0)
        total = self.result_data.get("total_questions", 0)
        lbl_score = QLabel(f"Điểm số: {score} / 10.0   |   Số câu đúng: {correct} / {total}")
        lbl_score.setStyleSheet("font-size: 16px; font-weight: bold; margin-top: 6px;")

        info_col.addWidget(lbl_title)
        info_col.addWidget(lbl_score)

        passed = self.result_data.get("passed", False)
        lbl_badge = QLabel("PASS" if passed else "FAIL")
        lbl_badge.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl_badge.setFixedSize(120, 48)
        badge_bg = "#16a34a" if passed else "#dc2626"
        lbl_badge.setStyleSheet(
            f"background-color: {badge_bg}; color: white; font-size: 20px; font-weight: bold; border-radius: 8px;"
        )

        c_layout.addLayout(info_col)
        c_layout.addStretch()
        c_layout.addWidget(lbl_badge)
        layout.addWidget(card)

        # Review Table
        lbl_detail = QLabel("Chi tiết bài làm")
        lbl_detail.setStyleSheet("font-size: 15px; font-weight: bold;")
        layout.addWidget(lbl_detail)

        details = self.result_data.get("details", [])
        table = QTableWidget(len(details), 4)
        table.setHorizontalHeaderLabels(["Câu hỏi", "Đáp án bạn chọn", "Đáp án đúng", "Kết quả"])
        table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        table.verticalHeader().setDefaultSectionSize(42)

        for row, item in enumerate(details):
            table.setItem(row, 0, QTableWidgetItem(str(item.get("question", ""))))
            table.setItem(row, 1, QTableWidgetItem(str(item.get("chosen", ""))))
            table.setItem(row, 2, QTableWidgetItem(str(item.get("correct", ""))))

            is_right = item.get("is_correct", False)
            status_item = QTableWidgetItem("ĐÚNG" if is_right else "SAI")
            status_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            status_item.setForeground(QColor("#15803d" if is_right else "#b91c1c"))
            table.setItem(row, 3, status_item)

        layout.addWidget(table)

        # Bottom Actions
        btn_row = QHBoxLayout()
        btn_back = QPushButton("← Quay về Trang chủ")
        btn_back.setObjectName("PrimaryBtn")
        btn_back.clicked.connect(lambda: self.on_back_dashboard() if self.on_back_dashboard else self.close())

        btn_logout = QPushButton("Đăng xuất")
        btn_logout.setObjectName("DangerBtn")
        btn_logout.clicked.connect(lambda: self.on_logout() if self.on_logout else self.close())

        btn_row.addWidget(btn_back)
        btn_row.addStretch()
        btn_row.addWidget(btn_logout)
        layout.addLayout(btn_row)


if __name__ == "__main__":
    import sys
    from PyQt6.QtWidgets import QApplication
    app = QApplication(sys.argv)
    win = ResultView()
    win.show()
    sys.exit(app.exec())
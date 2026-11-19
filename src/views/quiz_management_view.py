import csv
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QLineEdit, QSpinBox, QDoubleSpinBox, QCheckBox, QTableWidget,
    QTableWidgetItem, QHeaderView, QAbstractItemView, QTabWidget,
    QFrame, QMessageBox, QFileDialog
)
from PyQt6.QtCore import Qt
from src.views.question_bank_view import QuestionBankView


class QuizManagementView(QWidget):
    """SCR-05: Giao diện Quản lý Đề thi, Ngân hàng Câu hỏi & Thống kê Bảng điểm."""

    def __init__(self, user=None, quiz_controller=None, grading_controller=None, on_logout=None):
        super().__init__()
        self.user = user or {"id": 2, "full_name": "Nguyễn Sỹ Kiên", "role": "Teacher"}
        self.quiz_controller = quiz_controller
        self.grading_controller = grading_controller
        self.on_logout = on_logout

        self.quizzes = [
            {"id": 1, "title": "Software Engineering - Chapter 3 Design", "duration_minutes": 15, "pass_score": 5.0, "is_published": True},
            {"id": 2, "title": "Database Systems - Normalization & SQL", "duration_minutes": 20, "pass_score": 5.0, "is_published": True},
        ]
        self.attempts = [
            {"attempt_id": 1, "student_name": "Phan Gia Hưng", "quiz_title": "Software Engineering - Chapter 3 Design", "score": 8.5, "passed": True},
            {"attempt_id": 2, "student_name": "Trần Minh Anh", "quiz_title": "Database Systems - Normalization & SQL", "score": 4.0, "passed": False},
        ]
        self._init_ui()
        self._refresh_quiz_table()
        self._refresh_gradebook()

    def _init_ui(self):
        self.setWindowTitle("Quiz Examination System - Quản trị Giảng viên / Admin")
        self.resize(1040, 660)
        self.setStyleSheet("""
            QWidget { background-color: #f1f5f9; font-family: 'Segoe UI', Arial; font-size: 14px; color: #0f172a; }
            QFrame#TopBar { background-color: #1e293b; border-radius: 8px; padding: 12px 16px; }
            QFrame#FormCard, QFrame#KpiCard { background-color: white; border: 1px solid #cbd5e1; border-radius: 8px; padding: 14px; }
            QPushButton#PrimaryBtn { background-color: #2563eb; color: white; border-radius: 6px; padding: 8px 16px; font-weight: bold; }
            QPushButton#SuccessBtn { background-color: #16a34a; color: white; border-radius: 6px; padding: 8px 16px; font-weight: bold; }
            QPushButton#DangerBtn { background-color: #dc2626; color: white; border-radius: 6px; padding: 8px 14px; font-weight: bold; }
            QLineEdit, QSpinBox, QDoubleSpinBox { background-color: white; border: 1px solid #cbd5e1; border-radius: 5px; padding: 6px; }
            QTableWidget { background-color: white; border: 1px solid #cbd5e1; border-radius: 6px; }
            QHeaderView::section { background-color: #e2e8f0; padding: 8px; font-weight: bold; border: none; }
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(18, 18, 18, 18)
        layout.setSpacing(14)

        # Header Bar
        top_bar = QFrame()
        top_bar.setObjectName("TopBar")
        top_layout = QHBoxLayout(top_bar)
        lbl_title = QLabel(f"BẢNG ĐIỀU KHIỂN QUẢN TRỊ ({self.user.get('role')}: {self.user.get('full_name')})")
        lbl_title.setStyleSheet("color: white; font-size: 16px; font-weight: bold;")

        btn_logout = QPushButton("Đăng xuất")
        btn_logout.setObjectName("DangerBtn")
        btn_logout.clicked.connect(lambda: self.on_logout() if self.on_logout else self.close())

        top_layout.addWidget(lbl_title)
        top_layout.addStretch()
        top_layout.addWidget(btn_logout)
        layout.addWidget(top_bar)

        # Tabs
        self.tabs = QTabWidget()
        self.tabs.addTab(self._build_quiz_tab(), "SCR-05: Quản lý Đề thi")
        self.tabs.addTab(QuestionBankView(self.quiz_controller), "SCR-04: Ngân hàng Câu hỏi")
        self.tabs.addTab(self._build_gradebook_tab(), "Bảng điểm & Thống kê")
        layout.addWidget(self.tabs)

    def _build_quiz_tab(self):
        tab = QWidget()
        v_layout = QVBoxLayout(tab)
        v_layout.setSpacing(12)

        # Form Tạo đề thi
        form_card = QFrame()
        form_card.setObjectName("FormCard")
        f_layout = QHBoxLayout(form_card)

        self.txt_quiz_title = QLineEdit()
        self.txt_quiz_title.setPlaceholderText("Nhập tên đề thi mới...")

        self.spin_duration = QSpinBox()
        self.spin_duration.setRange(1, 180)
        self.spin_duration.setValue(15)
        self.spin_duration.setSuffix(" phút")

        self.spin_pass = QDoubleSpinBox()
        self.spin_pass.setRange(1.0, 10.0)
        self.spin_pass.setValue(5.0)
        self.spin_pass.setSingleStep(0.5)

        self.chk_publish = QCheckBox("Công bố (Publish)")
        self.chk_publish.setChecked(True)

        btn_save_quiz = QPushButton("Lưu bài thi")
        btn_save_quiz.setObjectName("SuccessBtn")
        btn_save_quiz.clicked.connect(self._create_quiz)

        f_layout.addWidget(QLabel("Tên đề:"))
        f_layout.addWidget(self.txt_quiz_title, 3)
        f_layout.addWidget(QLabel("Thời gian:"))
        f_layout.addWidget(self.spin_duration)
        f_layout.addWidget(QLabel("Điểm đạt:"))
        f_layout.addWidget(self.spin_pass)
        f_layout.addWidget(self.chk_publish)
        f_layout.addWidget(btn_save_quiz)
        v_layout.addWidget(form_card)

        # Bảng danh sách đề thi
        self.quiz_table = QTableWidget(0, 5)
        self.quiz_table.setHorizontalHeaderLabels(["ID", "Tên bài thi", "Thời gian", "Điểm đạt", "Trạng thái"])
        self.quiz_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.quiz_table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        v_layout.addWidget(self.quiz_table)
        return tab

    def _build_gradebook_tab(self):
        tab = QWidget()
        v_layout = QVBoxLayout(tab)
        v_layout.setSpacing(12)

        # 4 Thẻ KPI
        kpi_row = QHBoxLayout()
        self.lbl_kpi_total = self._make_kpi_card(kpi_row, "Tổng lượt làm bài", "0")
        self.lbl_kpi_avg = self._make_kpi_card(kpi_row, "Điểm trung bình", "0.0")
        self.lbl_kpi_pass_rate = self._make_kpi_card(kpi_row, "Tỷ lệ Đạt (Pass)", "0%")
        self.lbl_kpi_max = self._make_kpi_card(kpi_row, "Điểm cao nhất", "0.0")
        v_layout.addLayout(kpi_row)

        # Export CSV Button
        action_bar = QHBoxLayout()
        action_bar.addStretch()
        btn_export = QPushButton("Xuất Bảng điểm (.CSV)")
        btn_export.setObjectName("PrimaryBtn")
        btn_export.clicked.connect(self._export_csv)
        action_bar.addWidget(btn_export)
        v_layout.addLayout(action_bar)

        # Bảng điểm chi tiết
        self.grade_table = QTableWidget(0, 5)
        self.grade_table.setHorizontalHeaderLabels(["Mã lượt thi", "Sinh viên", "Bài thi", "Điểm số", "Kết quả"])
        self.grade_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.grade_table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        v_layout.addWidget(self.grade_table)
        return tab

    def _make_kpi_card(self, parent_layout, title, value):
        card = QFrame()
        card.setObjectName("KpiCard")
        c_layout = QVBoxLayout(card)
        lbl_t = QLabel(title)
        lbl_t.setStyleSheet("color: #64748b; font-size: 13px;")
        lbl_v = QLabel(value)
        lbl_v.setStyleSheet("color: #1e3a8a; font-size: 22px; font-weight: bold;")
        c_layout.addWidget(lbl_t)
        c_layout.addWidget(lbl_v)
        parent_layout.addWidget(card)
        return lbl_v

    def _create_quiz(self):
        title = self.txt_quiz_title.text().strip()
        if not title:
            QMessageBox.warning(self, "Thiếu thông tin", "Vui lòng nhập tên bài thi!")
            return
        new_quiz = {
            "id": max((q["id"] for q in self.quizzes), default=0) + 1,
            "title": title,
            "duration_minutes": self.spin_duration.value(),
            "pass_score": self.spin_pass.value(),
            "is_published": self.chk_publish.isChecked(),
        }
        if self.quiz_controller and hasattr(self.quiz_controller, "create_quiz"):
            self.quiz_controller.create_quiz(new_quiz)
        self.quizzes.append(new_quiz)
        self.txt_quiz_title.clear()
        self._refresh_quiz_table()
        QMessageBox.information(self, "Thành công", f"Đã lưu bài thi: {title}")

    def _refresh_quiz_table(self):
        self.quiz_table.setRowCount(len(self.quizzes))
        for row, q in enumerate(self.quizzes):
            self.quiz_table.setItem(row, 0, QTableWidgetItem(str(q["id"])))
            self.quiz_table.setItem(row, 1, QTableWidgetItem(q["title"]))
            self.quiz_table.setItem(row, 2, QTableWidgetItem(f"{q['duration_minutes']} phút"))
            self.quiz_table.setItem(row, 3, QTableWidgetItem(f"{q['pass_score']} / 10"))
            self.quiz_table.setItem(row, 4, QTableWidgetItem("Đã công bố" if q["is_published"] else "Bản nháp"))

    def _refresh_gradebook(self):
        total = len(self.attempts)
        scores = [a["score"] for a in self.attempts]
        avg_score = round(sum(scores) / total, 2) if total else 0.0
        pass_count = sum(1 for a in self.attempts if a["passed"])
        pass_rate = round((pass_count / total) * 100, 1) if total else 0.0
        max_score = max(scores) if scores else 0.0

        self.lbl_kpi_total.setText(str(total))
        self.lbl_kpi_avg.setText(str(avg_score))
        self.lbl_kpi_pass_rate.setText(f"{pass_rate}%")
        self.lbl_kpi_max.setText(str(max_score))

        self.grade_table.setRowCount(total)
        for row, a in enumerate(self.attempts):
            self.grade_table.setItem(row, 0, QTableWidgetItem(str(a["attempt_id"])))
            self.grade_table.setItem(row, 1, QTableWidgetItem(a["student_name"]))
            self.grade_table.setItem(row, 2, QTableWidgetItem(a["quiz_title"]))
            self.grade_table.setItem(row, 3, QTableWidgetItem(str(a["score"])))
            self.grade_table.setItem(row, 4, QTableWidgetItem("PASS" if a["passed"] else "FAIL"))

    def _export_csv(self):
        file_path, _ = QFileDialog.getSaveFileName(self, "Lưu Bảng điểm CSV", "gradebook_report.csv", "CSV Files (*.csv)")
        if not file_path:
            return
        with open(file_path, mode="w", newline="", encoding="utf-8-sig") as f:
            writer = csv.writer(f)
            writer.writerow(["Attempt ID", "Student Name", "Quiz Title", "Score", "Status"])
            for a in self.attempts:
                writer.writerow([a["attempt_id"], a["student_name"], a["quiz_title"], a["score"], "PASS" if a["passed"] else "FAIL"])
        QMessageBox.information(self, "Xuất file thành công", f"Đã lưu bảng điểm tại:\n{file_path}")


if __name__ == "__main__":
    import sys
    from PyQt6.QtWidgets import QApplication
    app = QApplication(sys.argv)
    win = QuizManagementView()
    win.show()
    sys.exit(app.exec())
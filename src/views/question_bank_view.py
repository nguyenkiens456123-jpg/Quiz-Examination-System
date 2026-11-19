from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QComboBox, QLineEdit, QTableWidget, QTableWidgetItem,
    QHeaderView, QAbstractItemView, QDialog, QFormLayout, QMessageBox
)
from PyQt6.QtCore import Qt


class QuestionDialog(QDialog):
    """Hộp thoại Thêm / Sửa câu hỏi với 4 đáp án A, B, C, D."""

    def __init__(self, parent=None, question_data=None):
        super().__init__(parent)
        self.question_data = question_data
        self.setWindowTitle("Sửa câu hỏi" if question_data else "Thêm câu hỏi mới")
        self.resize(520, 340)
        self._init_ui()

    def _init_ui(self):
        layout = QFormLayout(self)
        self.txt_content = QLineEdit()
        self.txt_a = QLineEdit()
        self.txt_b = QLineEdit()
        self.txt_c = QLineEdit()
        self.txt_d = QLineEdit()
        self.cb_correct = QComboBox()
        self.cb_correct.addItems(["A", "B", "C", "D"])

        if self.question_data:
            self.txt_content.setText(self.question_data.get("content", ""))
            opts = self.question_data.get("options", [])
            fields = [self.txt_a, self.txt_b, self.txt_c, self.txt_d]
            for idx, opt in enumerate(opts[:4]):
                fields[idx].setText(opt.get("content", ""))
                if opt.get("is_correct"):
                    self.cb_correct.setCurrentIndex(idx)

        layout.addRow("Nội dung câu hỏi:", self.txt_content)
        layout.addRow("Đáp án A:", self.txt_a)
        layout.addRow("Đáp án B:", self.txt_b)
        layout.addRow("Đáp án C:", self.txt_c)
        layout.addRow("Đáp án D:", self.txt_d)
        layout.addRow("Đáp án đúng:", self.cb_correct)

        btn_box = QHBoxLayout()
        btn_save = QPushButton("Lưu câu hỏi")
        btn_save.setStyleSheet("background-color: #2563eb; color: white; padding: 8px 16px; border-radius: 5px; font-weight: bold;")
        btn_save.clicked.connect(self._validate_and_accept)

        btn_cancel = QPushButton("Hủy")
        btn_cancel.clicked.connect(self.reject)

        btn_box.addStretch()
        btn_box.addWidget(btn_save)
        btn_box.addWidget(btn_cancel)
        layout.addRow(btn_box)

    def _validate_and_accept(self):
        if not self.txt_content.text().strip():
            QMessageBox.warning(self, "Thiếu thông tin", "Vui lòng nhập nội dung câu hỏi!")
            return
        if not all([self.txt_a.text().strip(), self.txt_b.text().strip(), self.txt_c.text().strip(), self.txt_d.text().strip()]):
            QMessageBox.warning(self, "Thiếu thông tin", "Vui lòng nhập đầy đủ cả 4 đáp án A, B, C, D!")
            return
        self.accept()

    def get_data(self):
        correct_idx = self.cb_correct.currentIndex()
        texts = [self.txt_a.text().strip(), self.txt_b.text().strip(), self.txt_c.text().strip(), self.txt_d.text().strip()]
        return {
            "content": self.txt_content.text().strip(),
            "options": [{"content": t, "is_correct": (i == correct_idx)} for i, t in enumerate(texts)],
        }


class QuestionBankView(QWidget):
    """SCR-04: Màn hình Quản lý Ngân hàng Câu hỏi (Thêm, Sửa, Xóa, Tìm kiếm)."""

    def __init__(self, quiz_controller=None):
        super().__init__()
        self.quiz_controller = quiz_controller
        self.questions_cache = [
            {
                "id": 101, "quiz_id": 1, "content": "Trong kiến trúc MVC, thành phần nào hiển thị giao diện?",
                "options": [
                    {"content": "Model", "is_correct": False},
                    {"content": "View", "is_correct": True},
                    {"content": "Controller", "is_correct": False},
                    {"content": "Database", "is_correct": False},
                ],
            },
            {
                "id": 102, "quiz_id": 1, "content": "Chuẩn 3NF loại bỏ hiện tượng nào?",
                "options": [
                    {"content": "Khóa chính trùng lặp", "is_correct": False},
                    {"content": "Phụ thuộc hàm bắc cầu", "is_correct": True},
                    {"content": "Thiếu khóa ngoại", "is_correct": False},
                    {"content": "Dữ liệu kiểu chuỗi", "is_correct": False},
                ],
            },
        ]
        self._init_ui()
        self.refresh_table()

    def _init_ui(self):
        self.setWindowTitle("SCR-04: Quản lý Ngân hàng Câu hỏi")
        self.resize(960, 580)
        self.setStyleSheet("""
            QWidget { background-color: #f8fafc; font-family: 'Segoe UI', Arial; font-size: 14px; }
            QPushButton#AddBtn { background-color: #16a34a; color: white; padding: 8px 14px; border-radius: 6px; font-weight: bold; }
            QPushButton#EditBtn { background-color: #2563eb; color: white; padding: 6px 12px; border-radius: 5px; }
            QPushButton#DelBtn { background-color: #dc2626; color: white; padding: 6px 12px; border-radius: 5px; }
            QLineEdit, QComboBox { background-color: white; border: 1px solid #cbd5e1; border-radius: 6px; padding: 6px 10px; }
            QTableWidget { background-color: white; border: 1px solid #cbd5e1; border-radius: 6px; }
            QHeaderView::section { background-color: #e2e8f0; padding: 8px; font-weight: bold; border: none; }
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        # Toolbar
        top_bar = QHBoxLayout()
        self.cb_quiz = QComboBox()
        self.cb_quiz.addItem("Software Engineering - Chapter 3 Design", 1)
        self.cb_quiz.addItem("Database Systems - Normalization & SQL", 2)
        self.cb_quiz.currentIndexChanged.connect(self.refresh_table)

        self.txt_search = QLineEdit()
        self.txt_search.setPlaceholderText("Tìm kiếm nội dung câu hỏi...")
        self.txt_search.textChanged.connect(self.refresh_table)

        btn_add = QPushButton("+ Thêm câu hỏi")
        btn_add.setObjectName("AddBtn")
        btn_add.clicked.connect(self._add_question)

        top_bar.addWidget(QLabel("Đề thi:"))
        top_bar.addWidget(self.cb_quiz, 2)
        top_bar.addWidget(self.txt_search, 3)
        top_bar.addWidget(btn_add)
        layout.addLayout(top_bar)

        # Table
        self.table = QTableWidget(0, 5)
        self.table.setHorizontalHeaderLabels(["ID", "Nội dung câu hỏi", "4 Lựa chọn", "Đáp án đúng", "Thao tác"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.verticalHeader().setDefaultSectionSize(44)
        layout.addWidget(self.table)

    def refresh_table(self):
        keyword = self.txt_search.text().strip().lower()
        filtered = [q for q in self.questions_cache if keyword in q["content"].lower()]

        self.table.setRowCount(len(filtered))
        labels = ["A", "B", "C", "D"]
        for row, q in enumerate(filtered):
            opts_str = " | ".join(f"{labels[i]}: {o['content']}" for i, o in enumerate(q["options"]))
            correct_lbl = next((labels[i] for i, o in enumerate(q["options"]) if o.get("is_correct")), "-")

            self.table.setItem(row, 0, QTableWidgetItem(str(q["id"])))
            self.table.setItem(row, 1, QTableWidgetItem(q["content"]))
            self.table.setItem(row, 2, QTableWidgetItem(opts_str))
            self.table.setItem(row, 3, QTableWidgetItem(correct_lbl))

            action_widget = QWidget()
            a_layout = QHBoxLayout(action_widget)
            a_layout.setContentsMargins(4, 2, 4, 2)

            btn_edit = QPushButton("Sửa")
            btn_edit.setObjectName("EditBtn")
            btn_edit.clicked.connect(lambda checked, item=q: self._edit_question(item))

            btn_del = QPushButton("Xóa")
            btn_del.setObjectName("DelBtn")
            btn_del.clicked.connect(lambda checked, q_id=q["id"]: self._delete_question(q_id))

            a_layout.addWidget(btn_edit)
            a_layout.addWidget(btn_del)
            self.table.setCellWidget(row, 4, action_widget)

    def _add_question(self):
        dlg = QuestionDialog(self)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            data = dlg.get_data()
            new_id = max((q["id"] for q in self.questions_cache), default=100) + 1
            data["id"] = new_id
            data["quiz_id"] = self.cb_quiz.currentData()
            if self.quiz_controller and hasattr(self.quiz_controller, "add_question"):
                self.quiz_controller.add_question(data)
            self.questions_cache.append(data)
            self.refresh_table()

    def _edit_question(self, question_item):
        dlg = QuestionDialog(self, question_item)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            updated = dlg.get_data()
            question_item["content"] = updated["content"]
            question_item["options"] = updated["options"]
            if self.quiz_controller and hasattr(self.quiz_controller, "update_question"):
                self.quiz_controller.update_question(question_item["id"], updated)
            self.refresh_table()

    def _delete_question(self, q_id):
        reply = QMessageBox.question(
            self, "Xác nhận xóa", f"Bạn có chắc muốn xóa câu hỏi ID {q_id}?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            if self.quiz_controller and hasattr(self.quiz_controller, "delete_question"):
                self.quiz_controller.delete_question(q_id)
            self.questions_cache = [q for q in self.questions_cache if q["id"] != q_id]
            self.refresh_table()


if __name__ == "__main__":
    import sys
    from PyQt6.QtWidgets import QApplication
    app = QApplication(sys.argv)
    win = QuestionBankView()
    win.show()
    sys.exit(app.exec())
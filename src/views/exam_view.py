from datetime import datetime
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QRadioButton, QButtonGroup, QGridLayout, QFrame, QMessageBox
)
from PyQt6.QtCore import Qt, QTimer


class ExamView(QWidget):
    """SCR-02: Màn hình Làm bài thi trắc nghiệm (Countdown + Question Palette + Auto-Save 10s)."""

    def __init__(self, user=None, quiz=None, questions=None, controller=None, on_submit_success=None):
        super().__init__()
        self.user = user or {"id": 3, "full_name": "Phan Gia Hưng"}
        self.quiz = quiz or {"id": 1, "title": "Software Engineering - Chapter 3 Design", "duration_minutes": 15, "pass_score": 5.0}
        self.controller = controller
        self.on_submit_success = on_submit_success

        self.questions = questions or self._load_questions()
        self.current_index = 0
        self.selected_answers = {}  # {question_id: option_id}
        self.palette_buttons = []

        duration_mins = self.quiz["duration_minutes"] if isinstance(self.quiz, dict) else getattr(self.quiz, "duration_minutes", 15)
        self.remaining_seconds = int(duration_mins) * 60

        self._init_ui()
        self._display_question(0)
        self._start_timers()

    def _load_questions(self):
        q_id = self.quiz["id"] if isinstance(self.quiz, dict) else self.quiz.id
        if self.controller and hasattr(self.controller, "get_questions_by_quiz"):
            return self.controller.get_questions_by_quiz(q_id)
        return [
            {
                "id": 101,
                "content": "Trong kiến trúc MVC, thành phần nào chịu trách nhiệm hiển thị giao diện người dùng?",
                "options": [
                    {"id": 1, "content": "Model", "is_correct": False},
                    {"id": 2, "content": "View", "is_correct": True},
                    {"id": 3, "content": "Controller", "is_correct": False},
                    {"id": 4, "content": "Database", "is_correct": False},
                ],
            },
            {
                "id": 102,
                "content": "Chuẩn 3NF trong cơ sở dữ liệu quan hệ nhằm loại bỏ hiện tượng nào?",
                "options": [
                    {"id": 5, "content": "Khóa chính trùng lặp", "is_correct": False},
                    {"id": 6, "content": "Phụ thuộc hàm bắc cầu vào khóa chính", "is_correct": True},
                    {"id": 7, "content": "Thiếu khóa ngoại", "is_correct": False},
                    {"id": 8, "content": "Dữ liệu kiểu chuỗi", "is_correct": False},
                ],
            },
            {
                "id": 103,
                "content": "Tính năng Auto-Save của hệ thống thực hiện lưu nháp bài làm sau mỗi bao lâu?",
                "options": [
                    {"id": 9, "content": "5 giây", "is_correct": False},
                    {"id": 10, "content": "10 giây", "is_correct": True},
                    {"id": 11, "content": "30 giây", "is_correct": False},
                    {"id": 12, "content": "60 giây", "is_correct": False},
                ],
            },
        ]

    def _init_ui(self):
        self.setWindowTitle("Quiz Examination System - Làm bài thi")
        self.resize(1024, 640)
        self.setStyleSheet("""
            QWidget { background-color: #f8fafc; font-family: 'Segoe UI', Arial; font-size: 14px; color: #0f172a; }
            QFrame#TopBar { background-color: #0f172a; border-radius: 8px; padding: 10px 16px; }
            QLabel#QuizTitle { color: white; font-size: 16px; font-weight: bold; }
            QLabel#TimerLabel { color: #fbbf24; font-size: 18px; font-weight: bold; }
            QLabel#AutoSaveLabel { color: #4ade80; font-size: 12px; }
            QFrame#Card { background-color: white; border: 1px solid #cbd5e1; border-radius: 8px; padding: 16px; }
            QRadioButton { padding: 10px; border: 1px solid #e2e8f0; border-radius: 6px; margin-bottom: 8px; background: #f8fafc; }
            QRadioButton:hover { background-color: #eff6ff; border-color: #93c5fd; }
            QPushButton#NavBtn { background-color: #e2e8f0; color: #1e293b; border-radius: 6px; padding: 8px 18px; font-weight: bold; }
            QPushButton#NavBtn:hover { background-color: #cbd5e1; }
            QPushButton#SubmitBtn { background-color: #16a34a; color: white; border-radius: 6px; padding: 10px 22px; font-weight: bold; font-size: 15px; }
            QPushButton#SubmitBtn:hover { background-color: #15803d; }
        """)

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)

        # Top Bar
        top_bar = QFrame()
        top_bar.setObjectName("TopBar")
        top_layout = QHBoxLayout(top_bar)

        quiz_title = self.quiz["title"] if isinstance(self.quiz, dict) else self.quiz.title
        lbl_quiz = QLabel(f"Bài thi: {quiz_title}")
        lbl_quiz.setObjectName("QuizTitle")

        self.lbl_autosave = QLabel("Auto-save: Sẵn sàng")
        self.lbl_autosave.setObjectName("AutoSaveLabel")

        self.lbl_timer = QLabel("Thời gian còn lại: 15:00")
        self.lbl_timer.setObjectName("TimerLabel")

        top_layout.addWidget(lbl_quiz)
        top_layout.addStretch()
        top_layout.addWidget(self.lbl_autosave)
        top_layout.addSpacing(20)
        top_layout.addWidget(self.lbl_timer)
        main_layout.addWidget(top_bar)

        # Body: Left Palette + Right Question Area
        body_layout = QHBoxLayout()
        body_layout.setSpacing(16)

        # Left Palette
        left_card = QFrame()
        left_card.setObjectName("Card")
        left_card.setFixedWidth(250)
        left_layout = QVBoxLayout(left_card)
        lbl_pal = QLabel("Bảng câu hỏi")
        lbl_pal.setStyleSheet("font-weight: bold; font-size: 15px;")
        left_layout.addWidget(lbl_pal)

        grid = QGridLayout()
        grid.setSpacing(8)
        for idx in range(len(self.questions)):
            btn = QPushButton(str(idx + 1))
            btn.setFixedSize(42, 42)
            btn.clicked.connect(lambda checked, i=idx: self._display_question(i))
            self.palette_buttons.append(btn)
            grid.addWidget(btn, idx // 4, idx % 4)
        left_layout.addLayout(grid)
        left_layout.addStretch()

        lbl_legend = QLabel("🟩 Đã trả lời   ⬜ Chưa trả lời")
        lbl_legend.setStyleSheet("font-size: 12px; color: #475569;")
        left_layout.addWidget(lbl_legend)
        body_layout.addWidget(left_card)

        # Right Question Content
        right_card = QFrame()
        right_card.setObjectName("Card")
        right_layout = QVBoxLayout(right_card)

        self.lbl_q_number = QLabel("Câu hỏi 1")
        self.lbl_q_number.setStyleSheet("font-weight: bold; color: #2563eb; font-size: 15px;")
        self.lbl_q_content = QLabel("")
        self.lbl_q_content.setWordWrap(True)
        self.lbl_q_content.setStyleSheet("font-size: 16px; font-weight: 500; margin: 10px 0;")

        right_layout.addWidget(self.lbl_q_number)
        right_layout.addWidget(self.lbl_q_content)

        self.option_group = QButtonGroup(self)
        self.option_group.setExclusive(True)
        self.radio_buttons = []
        for i in range(4):
            rb = QRadioButton("")
            self.option_group.addButton(rb, i)
            self.radio_buttons.append(rb)
            right_layout.addWidget(rb)
        self.option_group.idClicked.connect(self._on_option_selected)

        right_layout.addStretch()

        # Navigation & Submit Buttons
        nav_layout = QHBoxLayout()
        self.btn_prev = QPushButton("← Câu trước")
        self.btn_prev.setObjectName("NavBtn")
        self.btn_prev.clicked.connect(lambda: self._display_question(self.current_index - 1))

        self.btn_next = QPushButton("Câu tiếp theo →")
        self.btn_next.setObjectName("NavBtn")
        self.btn_next.clicked.connect(lambda: self._display_question(self.current_index + 1))

        self.btn_submit = QPushButton("NỘP BÀI THI")
        self.btn_submit.setObjectName("SubmitBtn")
        self.btn_submit.clicked.connect(self._confirm_submit)

        nav_layout.addWidget(self.btn_prev)
        nav_layout.addWidget(self.btn_next)
        nav_layout.addStretch()
        nav_layout.addWidget(self.btn_submit)
        right_layout.addLayout(nav_layout)

        body_layout.addWidget(right_card)
        main_layout.addLayout(body_layout)

    def _display_question(self, index):
        if not self.questions or index < 0 or index >= len(self.questions):
            return
        self.current_index = index
        q = self.questions[index]
        q_id = q["id"] if isinstance(q, dict) else q.id
        content = q["content"] if isinstance(q, dict) else q.content
        options = q["options"] if isinstance(q, dict) else q.options

        self.lbl_q_number.setText(f"Câu hỏi {index + 1} / {len(self.questions)}")
        self.lbl_q_content.setText(content)

        self.option_group.setExclusive(False)
        for rb in self.radio_buttons:
            rb.setChecked(False)
            rb.hide()
        self.option_group.setExclusive(True)

        labels = ["A", "B", "C", "D"]
        saved_opt_id = self.selected_answers.get(q_id)
        for idx, opt in enumerate(options[:4]):
            opt_id = opt["id"] if isinstance(opt, dict) else opt.id
            opt_text = opt["content"] if isinstance(opt, dict) else opt.content
            rb = self.radio_buttons[idx]
            rb.setText(f"{labels[idx]}. {opt_text}")
            rb.setProperty("option_id", opt_id)
            rb.show()
            if saved_opt_id == opt_id:
                rb.setChecked(True)

        self.btn_prev.setEnabled(index > 0)
        self.btn_next.setEnabled(index < len(self.questions) - 1)
        self._update_palette_styles()

    def _on_option_selected(self, btn_id):
        q = self.questions[self.current_index]
        q_id = q["id"] if isinstance(q, dict) else q.id
        opt_id = self.radio_buttons[btn_id].property("option_id")
        self.selected_answers[q_id] = opt_id
        self._update_palette_styles()

    def _update_palette_styles(self):
        for idx, btn in enumerate(self.palette_buttons):
            q = self.questions[idx]
            q_id = q["id"] if isinstance(q, dict) else q.id
            answered = q_id in self.selected_answers
            is_current = idx == self.current_index

            bg = "#22c55e" if answered else "#ffffff"
            fg = "#ffffff" if answered else "#1e293b"
            border = "2px solid #2563eb" if is_current else "1px solid #cbd5e1"
            btn.setStyleSheet(f"background-color: {bg}; color: {fg}; border: {border}; border-radius: 6px; font-weight: bold;")

    def _start_timers(self):
        self.countdown_timer = QTimer(self)
        self.countdown_timer.timeout.connect(self._tick_countdown)
        self.countdown_timer.start(1000)

        self.autosave_timer = QTimer(self)
        self.autosave_timer.timeout.connect(self._auto_save)
        self.autosave_timer.start(10000)  # Mỗi 10 giây

    def _tick_countdown(self):
        self.remaining_seconds -= 1
        mins, secs = divmod(max(0, self.remaining_seconds), 60)
        self.lbl_timer.setText(f"Thời gian còn lại: {mins:02d}:{secs:02d}")
        if self.remaining_seconds <= 60:
            self.lbl_timer.setStyleSheet("color: #ef4444; font-size: 18px; font-weight: bold;")
        if self.remaining_seconds <= 0:
            self._stop_timers()
            QMessageBox.warning(self, "Hết giờ", "Đã hết thời gian làm bài! Hệ thống tự động nộp bài.")
            self._submit_exam()

    def _auto_save(self):
        if self.controller and hasattr(self.controller, "auto_save_answers"):
            quiz_id = self.quiz["id"] if isinstance(self.quiz, dict) else self.quiz.id
            self.controller.auto_save_answers(self.user["id"], quiz_id, self.selected_answers)
        now_str = datetime.now().strftime("%H:%M:%S")
        self.lbl_autosave.setText(f"Auto-save: Đã lưu nháp lúc {now_str}")

    def _confirm_submit(self):
        unanswered = len(self.questions) - len(self.selected_answers)
        msg = "Bạn có chắc chắn muốn nộp bài thi?"
        if unanswered > 0:
            msg = f"Bạn còn {unanswered} câu chưa trả lời. Bạn vẫn muốn nộp bài chứ?"
        reply = QMessageBox.question(
            self, "Xác nhận nộp bài", msg,
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            self._stop_timers()
            self._submit_exam()

    def _stop_timers(self):
        if hasattr(self, "countdown_timer"):
            self.countdown_timer.stop()
        if hasattr(self, "autosave_timer"):
            self.autosave_timer.stop()

    def _submit_exam(self):
        quiz_id = self.quiz["id"] if isinstance(self.quiz, dict) else self.quiz.id
        if self.controller and hasattr(self.controller, "submit_exam"):
            result = self.controller.submit_exam(self.user["id"], quiz_id, self.selected_answers)
        else:
            # Tính điểm dự phòng khi chạy độc lập
            correct = 0
            details = []
            for q in self.questions:
                q_id = q["id"]
                chosen_id = self.selected_answers.get(q_id)
                correct_opt = next((o for o in q["options"] if o.get("is_correct")), None)
                chosen_opt = next((o for o in q["options"] if o["id"] == chosen_id), None)
                is_right = chosen_opt is not None and chosen_opt.get("is_correct", False)
                if is_right:
                    correct += 1
                details.append({
                    "question": q["content"],
                    "chosen": chosen_opt["content"] if chosen_opt else "Chưa chọn",
                    "correct": correct_opt["content"] if correct_opt else "",
                    "is_correct": is_right,
                })
            total = len(self.questions)
            score = round((correct / total) * 10, 2) if total else 0.0
            pass_score = self.quiz.get("pass_score", 5.0)
            result = {
                "quiz_title": self.quiz.get("title", ""),
                "score": score,
                "correct_count": correct,
                "total_questions": total,
                "passed": score >= pass_score,
                "details": details,
            }

        if self.on_submit_success:
            self.on_submit_success(result)
        else:
            QMessageBox.information(
                self, "Kết quả bài thi",
                f"Điểm số: {result['score']} / 10\nTrạng thái: {'PASS' if result['passed'] else 'FAIL'}"
            )


if __name__ == "__main__":
    import sys
    from PyQt6.QtWidgets import QApplication
    app = QApplication(sys.argv)
    win = ExamView()
    win.show()
    sys.exit(app.exec())
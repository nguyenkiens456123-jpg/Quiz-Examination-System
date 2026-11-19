import sys
from typing import Dict, List, Optional
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QColor, QFont
from PyQt6.QtWidgets import (
    QApplication,
    QButtonGroup,
    QCheckBox,
    QComboBox,
    QDialog,
    QFileDialog,
    QFormLayout,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QHeaderView,
    QInputDialog,
    QLabel,
    QLineEdit,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QRadioButton,
    QScrollArea,
    QSpinBox,
    QDoubleSpinBox,
    QStackedWidget,
    QTabWidget,
    QTableWidget,
    QTableWidgetItem,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from src.controllers.auth_controller import AuthController
from src.controllers.exam_controller import ExamController
from src.controllers.quiz_controller import QuizController
from src.database.db_init import DatabaseManager
from src.models.entities import Attempt, Quiz, User

APP_STYLESHEET = """
QMainWindow, QWidget {
    background-color: #F6F7FB;
    color: #1E293B;
    font-family: 'Segoe UI', Arial, sans-serif;
    font-size: 13px;
}
QFrame#Card {
    background-color: #FFFFFF;
    border: 1px solid #E2E8F0;
    border-radius: 12px;
}
QFrame#HeaderBar {
    background-color: #FFFFFF;
    border-bottom: 1px solid #E2E8F0;
}
QPushButton#PrimaryBtn {
    background-color: #4F46E5;
    color: #FFFFFF;
    border: none;
    border-radius: 8px;
    padding: 9px 16px;
    font-weight: 600;
}
QPushButton#PrimaryBtn:hover {
    background-color: #4338CA;
}
QPushButton#DangerBtn {
    background-color: #EF4444;
    color: #FFFFFF;
    border: none;
    border-radius: 8px;
    padding: 9px 16px;
    font-weight: 600;
}
QPushButton#DangerBtn:hover {
    background-color: #DC2626;
}
QPushButton#SecondaryBtn {
    background-color: #FFFFFF;
    color: #334155;
    border: 1px solid #CBD5E1;
    border-radius: 8px;
    padding: 8px 14px;
    font-weight: 600;
}
QPushButton#SecondaryBtn:hover {
    background-color: #F1F5F9;
}
QPushButton#DisabledBtn {
    background-color: #E2E8F0;
    color: #64748B;
    border: none;
    border-radius: 8px;
    padding: 9px 16px;
    font-weight: 600;
}
QLineEdit, QComboBox, QSpinBox, QDoubleSpinBox, QTextEdit {
    background-color: #FFFFFF;
    border: 1px solid #CBD5E1;
    border-radius: 8px;
    padding: 7px 10px;
}
QLineEdit:focus, QComboBox:focus, QTextEdit:focus {
    border: 1.5px solid #4F46E5;
}
QTableWidget {
    background-color: #FFFFFF;
    border: 1px solid #E2E8F0;
    border-radius: 8px;
    gridline-color: #F1F5F9;
}
QHeaderView::section {
    background-color: #F8FAFC;
    color: #475569;
    font-weight: 600;
    padding: 8px;
    border: none;
    border-bottom: 1px solid #E2E8F0;
}
"""


class QuestionEditorDialog(QDialog):
    """Dialog for UC-07 (+ Add New / Edit Question)."""

    def __init__(self, subjects: List[str], parent=None, question=None):
        super().__init__(parent)
        self.setWindowTitle("Question Bank Editor" if not question else f"Edit Question Q_{question.questionID:03d}")
        self.setMinimumWidth(520)

        layout = QVBoxLayout(self)
        form = QFormLayout()

        self.subject_cb = QComboBox()
        self.subject_cb.setEditable(True)
        self.subject_cb.addItems(subjects)

        self.topic_input = QLineEdit()
        self.topic_input.setPlaceholderText("e.g., UML Modeling, SDLC, SQL...")

        self.content_input = QTextEdit()
        self.content_input.setMaximumHeight(80)
        self.content_input.setPlaceholderText("Enter question text...")

        self.opt_inputs = [QLineEdit() for _ in range(4)]
        for i, inp in enumerate(self.opt_inputs):
            inp.setPlaceholderText(f"Option {chr(65 + i)} text...")

        self.correct_cb = QComboBox()
        self.correct_cb.addItems(["Option A", "Option B", "Option C", "Option D"])

        self.expl_input = QLineEdit()
        self.expl_input.setPlaceholderText("Detailed explanation shown after exam...")

        if question:
            self.subject_cb.setCurrentText(question.subject)
            self.topic_input.setText(question.topic)
            self.content_input.setPlainText(question.content)
            self.expl_input.setText(question.explanation)
            for idx, opt in enumerate(question.options[:4]):
                self.opt_inputs[idx].setText(opt.optionText)
                if opt.isCorrect:
                    self.correct_cb.setCurrentIndex(idx)

        form.addRow("Subject:", self.subject_cb)
        form.addRow("Topic:", self.topic_input)
        form.addRow("Question Text:", self.content_input)
        for i, inp in enumerate(self.opt_inputs):
            form.addRow(f"Option {chr(65 + i)}:", inp)
        form.addRow("Correct Answer:", self.correct_cb)
        form.addRow("Feedback / Explanation:", self.expl_input)
        layout.addLayout(form)

        btn_row = QHBoxLayout()
        cancel_btn = QPushButton("Cancel")
        cancel_btn.setObjectName("SecondaryBtn")
        cancel_btn.clicked.connect(self.reject)

        save_btn = QPushButton("Save Question")
        save_btn.setObjectName("PrimaryBtn")
        save_btn.clicked.connect(self.accept)

        btn_row.addStretch()
        btn_row.addWidget(cancel_btn)
        btn_row.addWidget(save_btn)
        layout.addLayout(btn_row)

    def get_data(self):
        return {
            "subject": self.subject_cb.currentText().strip() or "General",
            "topic": self.topic_input.text().strip() or "General",
            "content": self.content_input.toPlainText().strip(),
            "options": [inp.text().strip() for inp in self.opt_inputs],
            "correct_index": self.correct_cb.currentIndex(),
            "explanation": self.expl_input.text().strip(),
        }


class LoginView(QWidget):
    """UC-01 & FR-ST-01: Login & Student Registration Screen."""

    def __init__(self, auth_ctrl: AuthController, on_login_success):
        super().__init__()
        self.auth_ctrl = auth_ctrl
        self.on_login_success = on_login_success

        outer = QVBoxLayout(self)
        outer.setAlignment(Qt.AlignmentFlag.AlignCenter)

        card = QFrame()
        card.setObjectName("Card")
        card.setFixedWidth(430)
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(32, 32, 32, 32)
        card_layout.setSpacing(14)

        badge = QLabel("Q  QUIZ EXAMINATION SYSTEM")
        badge.setStyleSheet("color: #4F46E5; font-weight: 700; font-size: 13px;")
        card_layout.addWidget(badge)

        title = QLabel("Welcome Back")
        title.setStyleSheet("font-size: 22px; font-weight: 700; color: #0F172A;")
        card_layout.addWidget(title)

        sub = QLabel("Sign in with your Student, Teacher, or Admin credentials.")
        sub.setStyleSheet("color: #64748B;")
        card_layout.addWidget(sub)

        self.tabs = QTabWidget()

        # Login Tab
        login_tab = QWidget()
        l_form = QVBoxLayout(login_tab)
        l_form.setSpacing(10)
        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("Email or ID (e.g., student01@uth.edu.vn)")
        self.email_input.setText("student01@uth.edu.vn")

        self.pass_input = QLineEdit()
        self.pass_input.setPlaceholderText("Password")
        self.pass_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.pass_input.setText("123456")

        login_btn = QPushButton("Log In")
        login_btn.setObjectName("PrimaryBtn")
        login_btn.clicked.connect(self.handle_login)

        hint = QLabel("Demo accounts (pw: 123456):\n• Student: student01@uth.edu.vn\n• Teacher: teacher@uth.edu.vn\n• Admin: admin@uth.edu.vn")
        hint.setStyleSheet("color: #64748B; font-size: 11px; background: #F8FAFC; padding: 8px; border-radius: 6px;")

        l_form.addWidget(QLabel("Email / Username:"))
        l_form.addWidget(self.email_input)
        l_form.addWidget(QLabel("Password:"))
        l_form.addWidget(self.pass_input)
        l_form.addWidget(login_btn)
        l_form.addWidget(hint)

        # Register Tab (FR-ST-01)
        reg_tab = QWidget()
        r_form = QVBoxLayout(reg_tab)
        r_form.setSpacing(10)
        self.reg_name = QLineEdit()
        self.reg_name.setPlaceholderText("Full Name (e.g., Nguyen Van B)")
        self.reg_email = QLineEdit()
        self.reg_email.setPlaceholderText("Email Address (e.g., sv02@uth.edu.vn)")
        self.reg_pass = QLineEdit()
        self.reg_pass.setPlaceholderText("Password (min 6 chars)")
        self.reg_pass.setEchoMode(QLineEdit.EchoMode.Password)

        reg_btn = QPushButton("Create Student Account")
        reg_btn.setObjectName("PrimaryBtn")
        reg_btn.clicked.connect(self.handle_register)

        r_form.addWidget(QLabel("Full Name:"))
        r_form.addWidget(self.reg_name)
        r_form.addWidget(QLabel("Email Address:"))
        r_form.addWidget(self.reg_email)
        r_form.addWidget(QLabel("Password:"))
        r_form.addWidget(self.reg_pass)
        r_form.addWidget(reg_btn)

        self.tabs.addTab(login_tab, "Sign In")
        self.tabs.addTab(reg_tab, "Register (Student)")
        card_layout.addWidget(self.tabs)
        outer.addWidget(card)

    def handle_login(self):
        ok, msg, user = self.auth_ctrl.login(self.email_input.text(), self.pass_input.text())
        if not ok:
            QMessageBox.warning(self, "Authentication Error", msg)
            return
        self.on_login_success(user)

    def handle_register(self):
        ok, msg = self.auth_ctrl.register_student(
            self.reg_name.text(), self.reg_email.text(), self.reg_pass.text()
        )
        if ok:
            QMessageBox.information(self, "Registration Successful", msg)
            self.email_input.setText(self.reg_email.text().strip())
            self.tabs.setCurrentIndex(0)
        else:
            QMessageBox.warning(self, "Registration Error", msg)


class StudentDashboardView(QWidget):
    """SCR-01: Student Quiz Dashboard (UC-02)."""

    def __init__(self, quiz_ctrl: QuizController, on_start_quiz, on_view_result, on_logout):
        super().__init__()
        self.quiz_ctrl = quiz_ctrl
        self.on_start_quiz = on_start_quiz
        self.on_view_result = on_view_result
        self.on_logout = on_logout
        self.current_user: Optional[User] = None
        self.current_filter = "All"

        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # Header Navigation Bar
        header = QFrame()
        header.setObjectName("HeaderBar")
        h_layout = QHBoxLayout(header)
        h_layout.setContentsMargins(24, 12, 24, 12)

        brand = QLabel("Q  QUIZ SYSTEM")
        brand.setStyleSheet("font-size: 16px; font-weight: 800; color: #4F46E5;")

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search by title, keyword, course...")
        self.search_input.setFixedWidth(340)
        self.search_input.textChanged.connect(self.refresh_quizzes)

        self.filter_btns: Dict[str, QPushButton] = {}
        filter_box = QHBoxLayout()
        for label in ["All", "Active", "Completed"]:
            btn = QPushButton(label)
            btn.setObjectName("SecondaryBtn")
            btn.clicked.connect(lambda _, f=label: self.set_filter(f))
            self.filter_btns[label] = btn
            filter_box.addWidget(btn)

        self.user_label = QLabel("User: Student")
        self.user_label.setStyleSheet("font-weight: 600; color: #334155;")

        logout_btn = QPushButton("Logout")
        logout_btn.setObjectName("SecondaryBtn")
        logout_btn.clicked.connect(self.on_logout)

        h_layout.addWidget(brand)
        h_layout.addSpacing(20)
        h_layout.addWidget(self.search_input)
        h_layout.addStretch()
        h_layout.addLayout(filter_box)
        h_layout.addSpacing(20)
        h_layout.addWidget(self.user_label)
        h_layout.addWidget(logout_btn)
        root.addWidget(header)

        # Body Area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        body = QWidget()
        self.body_layout = QVBoxLayout(body)
        self.body_layout.setContentsMargins(32, 24, 32, 24)
        self.body_layout.setSpacing(16)

        title_row = QHBoxLayout()
        title_col = QVBoxLayout()
        sub_lbl = QLabel("YOUR LEARNING, IN PROGRESS")
        sub_lbl.setStyleSheet("color: #4F46E5; font-size: 11px; font-weight: 700;")
        main_lbl = QLabel("List of available exams")
        main_lbl.setStyleSheet("font-size: 24px; font-weight: 700; color: #0F172A;")
        title_col.addWidget(sub_lbl)
        title_col.addWidget(main_lbl)

        self.count_badge = QLabel("0 quizzes available")
        self.count_badge.setStyleSheet("background: #EEF2FF; color: #4F46E5; padding: 6px 12px; border-radius: 12px; font-weight: 600;")

        title_row.addLayout(title_col)
        title_row.addStretch()
        title_row.addWidget(self.count_badge)
        self.body_layout.addLayout(title_row)

        self.grid_container = QWidget()
        self.grid_layout = QGridLayout(self.grid_container)
        self.grid_layout.setSpacing(18)
        self.body_layout.addWidget(self.grid_container)
        self.body_layout.addStretch()

        scroll.setWidget(body)
        root.addWidget(scroll)

    def load_user(self, user: User):
        self.current_user = user
        self.user_label.setText(f"STUDENT PORTAL  |  User: {user.fullname} ({user.username})")
        self.set_filter("All")

    def set_filter(self, filter_name: str):
        self.current_filter = filter_name
        for name, btn in self.filter_btns.items():
            if name == filter_name:
                btn.setStyleSheet("background-color: #EEF2FF; color: #4F46E5; border: 1px solid #4F46E5; border-radius: 8px; padding: 8px 14px; font-weight: 700;")
            else:
                btn.setStyleSheet("")
                btn.setObjectName("SecondaryBtn")
        self.refresh_quizzes()

    def refresh_quizzes(self):
        if not self.current_user:
            return
        while self.grid_layout.count():
            item = self.grid_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        quizzes = self.quiz_ctrl.get_student_quizzes(
            self.current_user.userID, self.search_input.text(), self.current_filter
        )
        self.count_badge.setText(f"{len(quizzes)} quizzes available")

        if not quizzes:
            empty_lbl = QLabel("No available quizzes found matching your criteria.")
            empty_lbl.setStyleSheet("color: #64748B; font-size: 14px; padding: 30px;")
            self.grid_layout.addWidget(empty_lbl, 0, 0)
            return

        for idx, q in enumerate(quizzes):
            card = QFrame()
            card.setObjectName("Card")
            c_lay = QVBoxLayout(card)
            c_lay.setContentsMargins(20, 20, 20, 20)
            c_lay.setSpacing(10)

            top = QHBoxLayout()
            status_pill = QLabel(f"● {q['status']}" if q["status"] == "Active" else "✓ Completed")
            if q["status"] == "Active":
                status_pill.setStyleSheet("background: #EEF2FF; color: #4F46E5; padding: 4px 10px; border-radius: 10px; font-size: 11px; font-weight: 600;")
            else:
                status_pill.setStyleSheet("background: #DCFCE7; color: #16A34A; padding: 4px 10px; border-radius: 10px; font-size: 11px; font-weight: 600;")
            top.addStretch()
            top.addWidget(status_pill)
            c_lay.addLayout(top)

            subj = QLabel(f"Subject: {q['subject']}")
            subj.setStyleSheet("color: #64748B; font-size: 12px;")
            c_lay.addWidget(subj)

            title = QLabel(f"Topic: {q['title']}")
            title.setStyleSheet("font-size: 17px; font-weight: 700; color: #0F172A;")
            title.setWordWrap(True)
            c_lay.addWidget(title)

            meta = QLabel(
                f"Duration:  <b>{q['durationMins']} Mins</b><br>"
                f"Questions:  <b>{q['questionCount']} Multiple Choice</b><br>"
                f"Pass Score:  <b>{int(q['passScore'])}%</b>"
            )
            meta.setStyleSheet("color: #475569; line-height: 1.5; margin-top: 6px; margin-bottom: 6px;")
            c_lay.addWidget(meta)

            if q["status"] == "Active":
                action_btn = QPushButton("START QUIZ  →")
                action_btn.setObjectName("PrimaryBtn")
                action_btn.clicked.connect(lambda _, item=q: self.on_start_quiz(item))
                c_lay.addWidget(action_btn)
            else:
                btn_row = QHBoxLayout()
                done_btn = QPushButton("COMPLETED  ✓")
                done_btn.setObjectName("DisabledBtn")
                done_btn.setEnabled(False)

                rev_btn = QPushButton("View Breakdown")
                rev_btn.setObjectName("SecondaryBtn")
                rev_btn.clicked.connect(lambda _, aid=q["lastAttemptID"]: self.on_view_result(aid))
                btn_row.addWidget(done_btn)
                btn_row.addWidget(rev_btn)
                c_lay.addLayout(btn_row)

            self.grid_layout.addWidget(card, idx // 3, idx % 3)


class ExamAttemptView(QWidget):
    """SCR-02: Real-Time Exam Attempt & Timer Interface (UC-03, UC-04, UC-05)."""

    def __init__(self, exam_ctrl: ExamController, on_exam_finished):
        super().__init__()
        self.exam_ctrl = exam_ctrl
        self.on_exam_finished = on_exam_finished

        self.attempt: Optional[Attempt] = None
        self.quiz: Optional[Quiz] = None
        self.current_q_idx: int = 0
        self.remaining_seconds: int = 0
        self.selected_map: Dict[int, Optional[int]] = {}
        self.flagged_map: Dict[int, bool] = {}
        self.grid_buttons: List[QPushButton] = []

        self.countdown_timer = QTimer(self)
        self.countdown_timer.timeout.connect(self._tick_second)

        self.autosave_timer = QTimer(self)
        self.autosave_timer.timeout.connect(self._trigger_autosave)

        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)

        # Top Persistent Banner
        header = QFrame()
        header.setObjectName("HeaderBar")
        h_lay = QHBoxLayout(header)
        h_lay.setContentsMargins(24, 12, 24, 12)

        self.exam_title_lbl = QLabel("Midterm Exam")
        self.exam_title_lbl.setStyleSheet("font-size: 17px; font-weight: 700; color: #0F172A;")

        self.autosave_lbl = QLabel("● Auto-saved 10s ago")
        self.autosave_lbl.setStyleSheet("color: #16A34A; font-weight: 600;")

        self.timer_lbl = QLabel("TIME REMAINING: 45:00")
        self.timer_lbl.setStyleSheet("background: #EEF2FF; color: #DC2626; font-size: 16px; font-weight: 800; padding: 8px 14px; border-radius: 8px;")

        h_lay.addWidget(self.exam_title_lbl)
        h_lay.addStretch()
        h_lay.addWidget(self.autosave_lbl)
        h_lay.addSpacing(20)
        h_lay.addWidget(self.timer_lbl)
        root.addWidget(header)

        # Main Workspace (Left Question Card + Right Question Grid)
        workspace = QHBoxLayout()
        workspace.setContentsMargins(28, 24, 28, 24)
        workspace.setSpacing(20)

        # Left Question Panel
        q_card = QFrame()
        q_card.setObjectName("Card")
        q_lay = QVBoxLayout(q_card)
        q_lay.setContentsMargins(28, 24, 28, 24)
        q_lay.setSpacing(16)

        q_top = QHBoxLayout()
        self.q_counter_lbl = QLabel("Question 1 of 10")
        self.q_counter_lbl.setStyleSheet("font-weight: 700; color: #475569;")

        self.flag_btn = QPushButton("⚑ Flag for Review")
        self.flag_btn.setObjectName("SecondaryBtn")
        self.flag_btn.clicked.connect(self.toggle_current_flag)

        q_top.addWidget(self.q_counter_lbl)
        q_top.addStretch()
        q_top.addWidget(self.flag_btn)
        q_lay.addLayout(q_top)

        self.q_text_lbl = QLabel("Question content goes here?")
        self.q_text_lbl.setStyleSheet("font-size: 18px; font-weight: 700; color: #0F172A;")
        self.q_text_lbl.setWordWrap(True)
        q_lay.addWidget(self.q_text_lbl)

        self.option_group = QButtonGroup(self)
        self.option_radios: List[QRadioButton] = []
        for idx in range(4):
            rb = QRadioButton(f"Option {chr(65 + idx)}")
            rb.setStyleSheet("padding: 12px; border: 1px solid #E2E8F0; border-radius: 8px; font-size: 14px;")
            rb.clicked.connect(lambda _, i=idx: self.select_option_index(i))
            self.option_group.addButton(rb, idx)
            self.option_radios.append(rb)
            q_lay.addWidget(rb)

        q_lay.addStretch()

        nav_row = QHBoxLayout()
        self.prev_btn = QPushButton("←  Previous Question")
        self.prev_btn.setObjectName("SecondaryBtn")
        self.prev_btn.clicked.connect(lambda: self.go_to_question(self.current_q_idx - 1))

        self.nav_mid_lbl = QLabel("1 / 10")
        self.nav_mid_lbl.setStyleSheet("color: #64748B; font-weight: 600;")

        self.next_btn = QPushButton("Next Question  →")
        self.next_btn.setObjectName("PrimaryBtn")
        self.next_btn.clicked.connect(lambda: self.go_to_question(self.current_q_idx + 1))

        nav_row.addWidget(self.prev_btn)
        nav_row.addStretch()
        nav_row.addWidget(self.nav_mid_lbl)
        nav_row.addStretch()
        nav_row.addWidget(self.next_btn)
        q_lay.addLayout(nav_row)

        # Right Question Grid Sidebar
        side_card = QFrame()
        side_card.setObjectName("Card")
        side_card.setFixedWidth(290)
        s_lay = QVBoxLayout(side_card)
        s_lay.setContentsMargins(20, 20, 20, 20)
        s_lay.setSpacing(12)

        s_title = QLabel("QUESTION GRID")
        s_title.setStyleSheet("font-weight: 800; color: #0F172A;")
        s_sub = QLabel("Jump to any question")
        s_sub.setStyleSheet("color: #64748B; font-size: 12px;")
        s_lay.addWidget(s_title)
        s_lay.addWidget(s_sub)

        self.grid_widget = QWidget()
        self.q_grid_layout = QGridLayout(self.grid_widget)
        self.q_grid_layout.setSpacing(8)
        s_lay.addWidget(self.grid_widget)

        legend = QLabel("🟦 Answered    🟨 Flagged for review\n⬜ Unanswered  🔲 Current question")
        legend.setStyleSheet("color: #64748B; font-size: 11px; margin-top: 8px;")
        s_lay.addWidget(legend)
        s_lay.addStretch()

        submit_btn = QPushButton("SUBMIT QUIZ")
        submit_btn.setObjectName("DangerBtn")
        submit_btn.clicked.connect(self.confirm_manual_submit)
        s_lay.addWidget(submit_btn)

        workspace.addWidget(q_card, 3)
        workspace.addWidget(side_card, 1)
        root.addLayout(workspace)

    def start_session(self, attempt: Attempt, quiz: Quiz):
        self.attempt = attempt
        self.quiz = quiz
        self.current_q_idx = 0
        self.remaining_seconds = quiz.durationMins * 60
        self.selected_map = {q.questionID: None for q in quiz.questions}
        self.flagged_map = {q.questionID: False for q in quiz.questions}

        self.exam_title_lbl.setText(f"{quiz.title} - {quiz.subject}")
        self.autosave_lbl.setText("● Auto-saved 10s ago")
        self._build_question_grid()
        self.go_to_question(0)

        self._update_timer_display()
        self.countdown_timer.start(1000)
        self.autosave_timer.start(10000)  # UC-05: Every 10 seconds

    def _build_question_grid(self):
        while self.q_grid_layout.count():
            item = self.q_grid_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        self.grid_buttons.clear()

        if not self.quiz:
            return
        for idx, _ in enumerate(self.quiz.questions):
            btn = QPushButton(f"{idx + 1:02d}")
            btn.setFixedSize(46, 42)
            btn.clicked.connect(lambda _, i=idx: self.go_to_question(i))
            self.grid_buttons.append(btn)
            self.q_grid_layout.addWidget(btn, idx // 4, idx % 4)

    def _refresh_grid_colors(self):
        if not self.quiz:
            return
        for idx, q in enumerate(self.quiz.questions):
            btn = self.grid_buttons[idx]
            is_curr = (idx == self.current_q_idx)
            is_flag = self.flagged_map.get(q.questionID, False)
            is_ans = self.selected_map.get(q.questionID) is not None

            border = "2px solid #4F46E5" if is_curr else "1px solid #CBD5E1"
            if is_flag:
                bg, fg = "#FEF3C7", "#D97706"
            elif is_ans:
                bg, fg = "#EEF2FF", "#4F46E5"
            else:
                bg, fg = "#FFFFFF", "#475569"

            btn.setStyleSheet(f"background-color: {bg}; color: {fg}; border: {border}; border-radius: 8px; font-weight: 700;")

    def go_to_question(self, idx: int):
        if not self.quiz or idx < 0 or idx >= len(self.quiz.questions):
            return
        self.current_q_idx = idx
        total = len(self.quiz.questions)
        q = self.quiz.questions[idx]

        self.q_counter_lbl.setText(f"Question {idx + 1} of {total}  ({q.points} Point)")
        self.nav_mid_lbl.setText(f"{idx + 1} / {total}")
        self.q_text_lbl.setText(q.content)
        self.prev_btn.setEnabled(idx > 0)
        self.next_btn.setEnabled(idx < total - 1)

        if self.flagged_map.get(q.questionID, False):
            self.flag_btn.setText("⚑ Flagged (Click to Unflag)")
            self.flag_btn.setStyleSheet("background: #FEF3C7; color: #D97706; border: 1px solid #F59E0B; border-radius: 8px; padding: 8px 14px; font-weight: 700;")
        else:
            self.flag_btn.setText("⚑ Flag for Review")
            self.flag_btn.setStyleSheet("")
            self.flag_btn.setObjectName("SecondaryBtn")

        self.option_group.setExclusive(False)
        selected_opt_id = self.selected_map.get(q.questionID)
        for i, rb in enumerate(self.option_radios):
            if i < len(q.options):
                opt = q.options[i]
                rb.setVisible(True)
                rb.setText(f"{chr(65 + i)}.  {opt.optionText}")
                rb.setChecked(opt.optionID == selected_opt_id)
            else:
                rb.setVisible(False)
        self.option_group.setExclusive(True)
        self._refresh_grid_colors()

    def select_option_index(self, opt_idx: int):
        if not self.quiz or not self.attempt:
            return
        q = self.quiz.questions[self.current_q_idx]
        if opt_idx < len(q.options):
            opt_id = q.options[opt_idx].optionID
            self.selected_map[q.questionID] = opt_id
            self.exam_ctrl.save_selection(self.attempt.attemptID, q.questionID, opt_id)
            self._refresh_grid_colors()

    def toggle_current_flag(self):
        if not self.quiz or not self.attempt:
            return
        q = self.quiz.questions[self.current_q_idx]
        new_state = self.exam_ctrl.toggle_flag(self.attempt.attemptID, q.questionID)
        self.flagged_map[q.questionID] = new_state
        self.go_to_question(self.current_q_idx)

    def _trigger_autosave(self):
        if not self.attempt:
            return
        ok, status_text = self.exam_ctrl.auto_save_progress(
            self.attempt.attemptID, self.selected_map, self.flagged_map
        )
        self.autosave_lbl.setText(f"● {status_text}")
        self.autosave_lbl.setStyleSheet("color: #16A34A; font-weight: 600;" if ok else "color: #DC2626; font-weight: 600;")

    def _update_timer_display(self):
        mins, secs = divmod(max(0, self.remaining_seconds), 60)
        self.timer_lbl.setText(f"TIME REMAINING: {mins:02d}:{secs:02d}")

    def _tick_second(self):
        self.remaining_seconds -= 1
        self._update_timer_display()
        if self.remaining_seconds <= 0:
            self.countdown_timer.stop()
            self.autosave_timer.stop()
            QMessageBox.information(self, "Time Expired", "Time is up! Your exam has been automatically submitted.")
            self._finalize_submission()

    def confirm_manual_submit(self):
        reply = QMessageBox.question(
            self,
            "Confirm Submission",
            "Are you sure you want to submit your quiz?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if reply == QMessageBox.StandardButton.Yes:
            self.countdown_timer.stop()
            self.autosave_timer.stop()
            self._finalize_submission()

    def _finalize_submission(self):
        if not self.attempt:
            return
        self.exam_ctrl.auto_save_progress(self.attempt.attemptID, self.selected_map, self.flagged_map)
        _, result_data = self.exam_ctrl.submit_and_grade(self.attempt.attemptID)
        self.on_exam_finished(result_data)


class ResultBreakdownView(QWidget):
    """SCR-03: Quiz Result & Breakdown View (UC-06)."""

    def __init__(self, on_back_dashboard):
        super().__init__()
        self.on_back_dashboard = on_back_dashboard

        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)

        header = QFrame()
        header.setObjectName("HeaderBar")
        h_lay = QHBoxLayout(header)
        h_lay.setContentsMargins(24, 12, 24, 12)
        brand = QLabel("Q  QUIZ SYSTEM   |   Quiz Results & Breakdown")
        brand.setStyleSheet("font-size: 16px; font-weight: 800; color: #4F46E5;")
        h_lay.addWidget(brand)
        h_lay.addStretch()
        root.addWidget(header)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        body = QWidget()
        self.b_lay = QVBoxLayout(body)
        self.b_lay.setContentsMargins(32, 24, 32, 24)
        self.b_lay.setSpacing(18)

        # Summary Banner Card
        summary_card = QFrame()
        summary_card.setObjectName("Card")
        s_lay = QHBoxLayout(summary_card)
        s_lay.setContentsMargins(24, 24, 24, 24)

        self.score_lbl = QLabel("9.0 / 10")
        self.score_lbl.setStyleSheet("font-size: 32px; font-weight: 800; color: #4F46E5;")

        self.correct_lbl = QLabel("18 / 20 Correct")
        self.correct_lbl.setStyleSheet("font-size: 20px; font-weight: 700;")

        self.time_lbl = QLabel("32:45 Elapsed")
        self.time_lbl.setStyleSheet("font-size: 20px; font-weight: 700;")

        self.status_badge = QLabel("✓ PASSED")
        self.status_badge.setStyleSheet("background: #DCFCE7; color: #16A34A; padding: 8px 16px; border-radius: 12px; font-size: 15px; font-weight: 800;")

        back_btn = QPushButton("←  Return to Dashboard")
        back_btn.setObjectName("PrimaryBtn")
        back_btn.clicked.connect(self.on_back_dashboard)

        s_lay.addWidget(self.score_lbl)
        s_lay.addSpacing(30)
        s_lay.addWidget(self.correct_lbl)
        s_lay.addSpacing(30)
        s_lay.addWidget(self.time_lbl)
        s_lay.addStretch()
        s_lay.addWidget(self.status_badge)
        s_lay.addSpacing(16)
        s_lay.addWidget(back_btn)
        self.b_lay.addWidget(summary_card)

        self.items_container = QVBoxLayout()
        self.items_container.setSpacing(12)
        self.b_lay.addLayout(self.items_container)
        self.b_lay.addStretch()

        scroll.setWidget(body)
        root.addWidget(scroll)

    def display_result(self, data: Dict):
        while self.items_container.count():
            item = self.items_container.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        self.score_lbl.setText(f"{data.get('totalScore', 0)} / 10")
        self.correct_lbl.setText(f"{data.get('correctCount', 0)} / {data.get('totalQuestions', 0)} Correct")
        self.time_lbl.setText(f"{data.get('timeElapsed', '00:00')} Elapsed")

        if data.get("isPassed"):
            self.status_badge.setText("✓ PASSED")
            self.status_badge.setStyleSheet("background: #DCFCE7; color: #16A34A; padding: 8px 16px; border-radius: 12px; font-size: 15px; font-weight: 800;")
        else:
            self.status_badge.setText("✕ FAILED")
            self.status_badge.setStyleSheet("background: #FEE2E2; color: #DC2626; padding: 8px 16px; border-radius: 12px; font-size: 15px; font-weight: 800;")

        # Exception Flow A1 of UC-06: Review Rules check
        if not data.get("reviewRules", True):
            msg = QLabel("Detailed answer key review is disabled by the instructor.")
            msg.setStyleSheet("background: #FEF3C7; color: #92400E; padding: 16px; border-radius: 8px; font-weight: 600;")
            self.items_container.addWidget(msg)
            return

        for idx, item in enumerate(data.get("items", []), start=1):
            card = QFrame()
            card.setObjectName("Card")
            c_lay = QVBoxLayout(card)
            c_lay.setContentsMargins(20, 16, 20, 16)
            c_lay.setSpacing(8)

            tag = "✓ Correct" if item["isCorrect"] else "✕ Incorrect"
            tag_color = "#16A34A" if item["isCorrect"] else "#DC2626"
            head = QLabel(f"<b>Question {idx}</b>   <span style='color:{tag_color}; font-weight:700;'>{tag}</span>")
            q_txt = QLabel(item["content"])
            q_txt.setStyleSheet("font-size: 15px; font-weight: 700;")
            q_txt.setWordWrap(True)

            ans_lbl = QLabel(f"Your Answer: <b>{item['selectedText']}</b>   |   Correct Answer: <b>{item['correctText']}</b>")
            fb_lbl = QLabel(f"ℹ Feedback: {item['explanation']}")
            fb_lbl.setStyleSheet("color: #475569; background: #F8FAFC; padding: 8px; border-radius: 6px;")
            fb_lbl.setWordWrap(True)

            c_lay.addWidget(head)
            c_lay.addWidget(q_txt)
            c_lay.addWidget(ans_lbl)
            c_lay.addWidget(fb_lbl)
            self.items_container.addWidget(card)


class AdminTeacherPortalView(QWidget):
    """SCR-04 (Question Bank) + SCR-05 (Quiz Builder) + UC-10 (Gradebook) + UC-11 (Users & Roles)."""

    def __init__(self, auth_ctrl: AuthController, quiz_ctrl: QuizController, on_logout):
        super().__init__()
        self.auth_ctrl = auth_ctrl
        self.quiz_ctrl = quiz_ctrl
        self.on_logout = on_logout
        self.current_user: Optional[User] = None
        self.loaded_questions = []

        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)

        # Top Header
        header = QFrame()
        header.setObjectName("HeaderBar")
        h_lay = QHBoxLayout(header)
        h_lay.setContentsMargins(24, 12, 24, 12)
        brand = QLabel("Q  QUIZ SYSTEM   |   ADMIN & TEACHER WORKSPACE")
        brand.setStyleSheet("font-size: 16px; font-weight: 800; color: #4F46E5;")

        self.user_lbl = QLabel("User: Teacher")
        self.user_lbl.setStyleSheet("font-weight: 600;")

        logout_btn = QPushButton("Logout")
        logout_btn.setObjectName("SecondaryBtn")
        logout_btn.clicked.connect(self.on_logout)

        h_lay.addWidget(brand)
        h_lay.addStretch()
        h_lay.addWidget(self.user_lbl)
        h_lay.addSpacing(12)
        h_lay.addWidget(logout_btn)
        root.addWidget(header)

        self.tabs = QTabWidget()
        self.tabs.setStyleSheet("QTabBar::tab { padding: 10px 18px; font-weight: 600; }")

        self.tabs.addTab(self._build_scr04_question_bank(), "SCR-04: Question Bank (UC-07)")
        self.tabs.addTab(self._build_scr05_quiz_builder(), "SCR-05: Quiz Builder & Rules (UC-08/09)")
        self.tabs.addTab(self._build_uc10_gradebook(), "Gradebook & Analytics (UC-10)")
        self.user_mgmt_tab = self._build_uc11_users()
        self.tabs.addTab(self.user_mgmt_tab, "Manage Users & Roles (UC-11)")

        self.tabs.currentChanged.connect(self._on_tab_changed)
        root.addWidget(self.tabs)

    def load_user(self, user: User):
        self.current_user = user
        self.user_lbl.setText(f"User: {user.fullname} ({user.role.upper()})")
        # RBAC: Admin inherits Teacher rights + User Management; Teacher hides UC-11 tab
        is_admin = (user.role == "admin")
        self.tabs.setTabVisible(3, is_admin)
        self.refresh_question_bank()
        self.refresh_builder_questions()
        self.refresh_gradebook_quizzes()
        if is_admin:
            self.refresh_users_table()

    def _on_tab_changed(self, idx: int):
        if idx == 0:
            self.refresh_question_bank()
        elif idx == 1:
            self.refresh_builder_questions()
        elif idx == 2:
            self.refresh_gradebook_quizzes()
        elif idx == 3:
            self.refresh_users_table()

    # ---------------- SCR-04: Question Bank ----------------
    def _build_scr04_question_bank(self) -> QWidget:
        w = QWidget()
        lay = QVBoxLayout(w)
        lay.setContentsMargins(24, 20, 24, 20)
        lay.setSpacing(14)

        bar = QHBoxLayout()
        self.qb_search = QLineEdit()
        self.qb_search.setPlaceholderText("Search Question...")
        self.qb_search.textChanged.connect(self.refresh_question_bank)

        self.qb_subject_cb = QComboBox()
        self.qb_subject_cb.addItem("All")
        self.qb_subject_cb.addItems(self.quiz_ctrl.get_subjects())
        self.qb_subject_cb.currentTextChanged.connect(self.refresh_question_bank)

        add_btn = QPushButton("+ Add New")
        add_btn.setObjectName("PrimaryBtn")
        add_btn.clicked.connect(self.handle_add_question)

        edit_btn = QPushButton("Edit Selected")
        edit_btn.setObjectName("SecondaryBtn")
        edit_btn.clicked.connect(self.handle_edit_question)

        imp_btn = QPushButton("Import Excel / CSV")
        imp_btn.setObjectName("SecondaryBtn")
        imp_btn.clicked.connect(self.handle_import_excel)

        del_btn = QPushButton("Delete")
        del_btn.setObjectName("DangerBtn")
        del_btn.clicked.connect(self.handle_delete_questions)

        bar.addWidget(self.qb_search, 2)
        bar.addWidget(QLabel("Subject:"))
        bar.addWidget(self.qb_subject_cb, 1)
        bar.addWidget(add_btn)
        bar.addWidget(edit_btn)
        bar.addWidget(imp_btn)
        bar.addWidget(del_btn)
        lay.addLayout(bar)

        self.qb_table = QTableWidget(0, 7)
        self.qb_table.setHorizontalHeaderLabels(
            ["ID", "Question Text", "Option A", "Option B", "Option C", "Option D", "Correct Answer"]
        )
        self.qb_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.qb_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        lay.addWidget(self.qb_table)
        return w

    def refresh_question_bank(self):
        subj = self.qb_subject_cb.currentText()
        kw = self.qb_search.text()
        self.loaded_questions = self.quiz_ctrl.list_questions(subj, kw)
        self.qb_table.setRowCount(len(self.loaded_questions))

        for r_idx, q in enumerate(self.loaded_questions):
            id_item = QTableWidgetItem(f"Q_{q.questionID:03d}")
            id_item.setData(Qt.ItemDataRole.UserRole, q.questionID)
            self.qb_table.setItem(r_idx, 0, id_item)
            self.qb_table.setItem(r_idx, 1, QTableWidgetItem(q.content))

            correct_label = ""
            for c_idx in range(4):
                if c_idx < len(q.options):
                    opt = q.options[c_idx]
                    self.qb_table.setItem(r_idx, 2 + c_idx, QTableWidgetItem(opt.optionText))
                    if opt.isCorrect:
                        correct_label = f"Option {chr(65 + c_idx)}"
                else:
                    self.qb_table.setItem(r_idx, 2 + c_idx, QTableWidgetItem(""))
            self.qb_table.setItem(r_idx, 6, QTableWidgetItem(correct_label))

    def handle_add_question(self):
        dlg = QuestionEditorDialog(self.quiz_ctrl.get_subjects(), self)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            d = dlg.get_data()
            ok, msg = self.quiz_ctrl.add_question(
                d["subject"], d["topic"], d["content"], d["options"], d["correct_index"], 1.0, d["explanation"]
            )
            if ok:
                self.refresh_question_bank()
                self.refresh_builder_questions()
            else:
                QMessageBox.warning(self, "Validation Error", msg)

    def handle_edit_question(self):
        row = self.qb_table.currentRow()
        if row < 0 or row >= len(self.loaded_questions):
            QMessageBox.information(self, "Select Question", "Please select a question row to edit.")
            return
        q = self.loaded_questions[row]
        dlg = QuestionEditorDialog(self.quiz_ctrl.get_subjects(), self, question=q)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            d = dlg.get_data()
            ok, msg = self.quiz_ctrl.update_question(
                q.questionID, d["subject"], d["topic"], d["content"], d["options"], d["correct_index"], d["explanation"]
            )
            if ok:
                self.refresh_question_bank()
            else:
                QMessageBox.warning(self, "Error", msg)

    def handle_delete_questions(self):
        rows = {idx.row() for idx in self.qb_table.selectedIndexes()}
        if not rows:
            QMessageBox.information(self, "Delete", "Select at least one row to delete.")
            return
        qids = [self.qb_table.item(r, 0).data(Qt.ItemDataRole.UserRole) for r in rows]
        ok, msg = self.quiz_ctrl.delete_questions(qids)
        if ok:
            self.refresh_question_bank()
            self.refresh_builder_questions()

    def handle_import_excel(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "Import Questions", "", "Excel or CSV Files (*.xlsx *.csv)"
        )
        if not path:
            return
        ok, msg = self.quiz_ctrl.import_questions_from_file(path)
        QMessageBox.information(self, "Import Result", msg)
        if ok:
            self.refresh_question_bank()
            self.refresh_builder_questions()

    # ---------------- SCR-05: Quiz Builder & Rules ----------------
    def _build_scr05_quiz_builder(self) -> QWidget:
        w = QWidget()
        main_lay = QHBoxLayout(w)
        main_lay.setContentsMargins(24, 20, 24, 20)
        main_lay.setSpacing(20)

        # Left Panel: Quiz Details + Advanced Configuration
        left_card = QFrame()
        left_card.setObjectName("Card")
        l_lay = QVBoxLayout(left_card)
        l_lay.setContentsMargins(20, 20, 20, 20)
        l_lay.setSpacing(12)

        l_lay.addWidget(QLabel("<b>Quiz Details</b>"))
        self.qb_title = QLineEdit()
        self.qb_title.setPlaceholderText("e.g., Software Design — Practice Quiz")

        self.qb_subject = QComboBox()
        self.qb_subject.setEditable(True)
        self.qb_subject.addItems(self.quiz_ctrl.get_subjects())

        row_num = QHBoxLayout()
        self.qb_duration = QSpinBox()
        self.qb_duration.setRange(1, 300)
        self.qb_duration.setValue(45)

        self.qb_pass = QDoubleSpinBox()
        self.qb_pass.setRange(0, 100)
        self.qb_pass.setValue(70.0)

        row_num.addWidget(QLabel("Time Limit (min):"))
        row_num.addWidget(self.qb_duration)
        row_num.addWidget(QLabel("Passing Score %:"))
        row_num.addWidget(self.qb_pass)

        self.qb_class = QComboBox()
        self.qb_class.setEditable(True)
        self.qb_class.addItems(["Software Design · Class SE-01", "Database Systems · Class DB-02", "OOP C++ · Class CS-01"])

        self.qb_code = QLineEdit()
        self.qb_code.setPlaceholderText("Optional Access Code (e.g., SSD2026)")

        l_lay.addWidget(QLabel("Title:"))
        l_lay.addWidget(self.qb_title)
        l_lay.addWidget(QLabel("Subject:"))
        l_lay.addWidget(self.qb_subject)
        l_lay.addLayout(row_num)
        l_lay.addWidget(QLabel("Class Assignment:"))
        l_lay.addWidget(self.qb_class)
        l_lay.addWidget(QLabel("Access Code:"))
        l_lay.addWidget(self.qb_code)

        l_lay.addSpacing(8)
        l_lay.addWidget(QLabel("<b>Advanced Configuration (UC-09)</b>"))
        self.chk_shuffle_q = QCheckBox("Shuffle Question Order (Randomize question sequence)")
        self.chk_shuffle_o = QCheckBox("Shuffle Options (Randomize answer choices A-D)")
        self.chk_review = QCheckBox("Review Rules (Show answers and feedback after submission)")
        self.chk_review.setChecked(True)

        l_lay.addWidget(self.chk_shuffle_q)
        l_lay.addWidget(self.chk_shuffle_o)
        l_lay.addWidget(self.chk_review)
        l_lay.addStretch()

        btn_row = QHBoxLayout()
        draft_btn = QPushButton("Save Draft")
        draft_btn.setObjectName("SecondaryBtn")
        draft_btn.clicked.connect(lambda: self.handle_save_quiz(False))

        pub_btn = QPushButton("Publish Quiz")
        pub_btn.setObjectName("PrimaryBtn")
        pub_btn.clicked.connect(lambda: self.handle_save_quiz(True))

        btn_row.addWidget(draft_btn)
        btn_row.addWidget(pub_btn)
        l_lay.addLayout(btn_row)

        # Right Panel: Question Selector Panel
        right_card = QFrame()
        right_card.setObjectName("Card")
        r_lay = QVBoxLayout(right_card)
        r_lay.setContentsMargins(20, 20, 20, 20)
        r_lay.setSpacing(10)

        top_r = QHBoxLayout()
        top_r.addWidget(QLabel("<b>Question Selector Panel</b>"))
        self.attached_badge = QLabel("0 attached")
        self.attached_badge.setStyleSheet("background: #EEF2FF; color: #4F46E5; padding: 4px 10px; border-radius: 10px; font-weight: 700;")
        top_r.addStretch()
        top_r.addWidget(self.attached_badge)
        r_lay.addLayout(top_r)

        self.builder_q_table = QTableWidget(0, 3)
        self.builder_q_table.setHorizontalHeaderLabels(["Attach", "ID", "Question Text"])
        self.builder_q_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        self.builder_q_table.itemChanged.connect(self._update_attached_count)
        r_lay.addWidget(self.builder_q_table)

        main_lay.addWidget(left_card, 2)
        main_lay.addWidget(right_card, 3)
        return w

    def refresh_builder_questions(self):
        questions = self.quiz_ctrl.list_questions("All", "")
        self.builder_q_table.blockSignals(True)
        self.builder_q_table.setRowCount(len(questions))
        for idx, q in enumerate(questions):
            chk_item = QTableWidgetItem()
            chk_item.setFlags(Qt.ItemFlag.ItemIsUserCheckable | Qt.ItemFlag.ItemIsEnabled)
            chk_item.setCheckState(Qt.CheckState.Unchecked)
            chk_item.setData(Qt.ItemDataRole.UserRole, q.questionID)

            self.builder_q_table.setItem(idx, 0, chk_item)
            self.builder_q_table.setItem(idx, 1, QTableWidgetItem(f"Q_{q.questionID:03d}"))
            self.builder_q_table.setItem(idx, 2, QTableWidgetItem(f"[{q.subject}] {q.content}"))
        self.builder_q_table.blockSignals(False)
        self._update_attached_count()

    def _get_selected_builder_qids(self) -> List[int]:
        qids = []
        for r in range(self.builder_q_table.rowCount()):
            item = self.builder_q_table.item(r, 0)
            if item and item.checkState() == Qt.CheckState.Checked:
                qids.append(item.data(Qt.ItemDataRole.UserRole))
        return qids

    def _update_attached_count(self):
        cnt = len(self._get_selected_builder_qids())
        self.attached_badge.setText(f"{cnt} attached")

    def handle_save_quiz(self, is_published: bool):
        if not self.current_user:
            return
        qids = self._get_selected_builder_qids()
        ok, msg, _ = self.quiz_ctrl.create_and_configure_quiz(
            title=self.qb_title.text(),
            subject=self.qb_subject.currentText(),
            duration_mins=self.qb_duration.value(),
            pass_score=self.qb_pass.value(),
            class_assignment=self.qb_class.currentText(),
            access_code=self.qb_code.text(),
            shuffle_questions=self.chk_shuffle_q.isChecked(),
            shuffle_options=self.chk_shuffle_o.isChecked(),
            review_rules=self.chk_review.isChecked(),
            is_published=is_published,
            question_ids=qids,
            created_by=self.current_user.userID,
        )
        if ok:
            QMessageBox.information(self, "Quiz Saved", msg)
            self.qb_title.clear()
            self.qb_code.clear()
            self.refresh_builder_questions()
        else:
            QMessageBox.warning(self, "Missing Required Information", msg)

    # ---------------- UC-10: Gradebook & Analytics ----------------
    def _build_uc10_gradebook(self) -> QWidget:
        w = QWidget()
        lay = QVBoxLayout(w)
        lay.setContentsMargins(24, 20, 24, 20)
        lay.setSpacing(14)

        top = QHBoxLayout()
        self.gb_quiz_cb = QComboBox()
        self.gb_quiz_cb.currentIndexChanged.connect(self.refresh_gradebook_data)

        exp_btn = QPushButton("Export CSV Report")
        exp_btn.setObjectName("PrimaryBtn")
        exp_btn.clicked.connect(self.handle_export_csv)

        top.addWidget(QLabel("Select Quiz:"))
        top.addWidget(self.gb_quiz_cb, 2)
        top.addStretch()
        top.addWidget(exp_btn)
        lay.addLayout(top)

        self.gb_stats_lbl = QLabel("Average: 0.0  |  Highest: 0.0  |  Lowest: 0.0  |  Pass Rate: 0%")
        self.gb_stats_lbl.setStyleSheet("background: #EEF2FF; color: #1E293B; padding: 12px; border-radius: 8px; font-weight: 700;")
        lay.addWidget(self.gb_stats_lbl)

        self.gb_table = QTableWidget(0, 6)
        self.gb_table.setHorizontalHeaderLabels(["Attempt ID", "Student ID", "Full Name", "Email", "Score (/10)", "Status"])
        self.gb_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        lay.addWidget(self.gb_table)
        return w

    def refresh_gradebook_quizzes(self):
        self.gb_quiz_cb.blockSignals(True)
        self.gb_quiz_cb.clear()
        for q in self.quiz_ctrl.list_all_quizzes():
            self.gb_quiz_cb.addItem(f"{q['title']} ({q['subject']})", q["quizID"])
        self.gb_quiz_cb.blockSignals(False)
        self.refresh_gradebook_data()

    def refresh_gradebook_data(self):
        quiz_id = self.gb_quiz_cb.currentData()
        if not quiz_id:
            return
        records, stats = self.quiz_ctrl.get_gradebook_and_analytics(quiz_id)
        self.gb_stats_lbl.setText(
            f"Submissions: {stats['count']}   |   Average Score: {stats['avgScore']}/10   |   "
            f"Highest: {stats['maxScore']}   |   Lowest: {stats['minScore']}   |   Pass Rate: {stats['passRate']}%"
        )
        self.gb_table.setRowCount(len(records))
        for idx, r in enumerate(records):
            self.gb_table.setItem(idx, 0, QTableWidgetItem(str(r["attemptID"])))
            self.gb_table.setItem(idx, 1, QTableWidgetItem(r["username"]))
            self.gb_table.setItem(idx, 2, QTableWidgetItem(r["full_name"]))
            self.gb_table.setItem(idx, 3, QTableWidgetItem(r["email"]))
            self.gb_table.setItem(idx, 4, QTableWidgetItem(str(r["totalScore"])))
            self.gb_table.setItem(idx, 5, QTableWidgetItem("PASSED" if r["isPassed"] else "FAILED"))

    def handle_export_csv(self):
        quiz_id = self.gb_quiz_cb.currentData()
        if not quiz_id:
            return
        path, _ = QFileDialog.getSaveFileName(self, "Save Gradebook CSV", "gradebook_report.csv", "CSV Files (*.csv)")
        if not path:
            return
        ok, msg = self.quiz_ctrl.export_gradebook_csv(quiz_id, path)
        QMessageBox.information(self, "CSV Export", msg)

    # ---------------- UC-11: Manage Users & Roles ----------------
    def _build_uc11_users(self) -> QWidget:
        w = QWidget()
        lay = QVBoxLayout(w)
        lay.setContentsMargins(24, 20, 24, 20)
        lay.setSpacing(14)

        form_bar = QHBoxLayout()
        self.u_username = QLineEdit()
        self.u_username.setPlaceholderText("Username / ID")
        self.u_fullname = QLineEdit()
        self.u_fullname.setPlaceholderText("Full Name")
        self.u_email = QLineEdit()
        self.u_email.setPlaceholderText("Email")
        self.u_pass = QLineEdit()
        self.u_pass.setPlaceholderText("Initial Password")
        self.u_role = QComboBox()
        self.u_role.addItems(["student", "teacher", "admin"])

        add_u_btn = QPushButton("+ Add User")
        add_u_btn.setObjectName("PrimaryBtn")
        add_u_btn.clicked.connect(self.handle_admin_add_user)

        toggle_lock_btn = QPushButton("Lock / Unlock Selected")
        toggle_lock_btn.setObjectName("DangerBtn")
        toggle_lock_btn.clicked.connect(self.handle_toggle_user_lock)

        form_bar.addWidget(self.u_username)
        form_bar.addWidget(self.u_fullname)
        form_bar.addWidget(self.u_email)
        form_bar.addWidget(self.u_pass)
        form_bar.addWidget(self.u_role)
        form_bar.addWidget(add_u_btn)
        form_bar.addWidget(toggle_lock_btn)
        lay.addLayout(form_bar)

        self.users_table = QTableWidget(0, 6)
        self.users_table.setHorizontalHeaderLabels(["ID", "Username", "Full Name", "Email", "Role", "Status"])
        self.users_table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.Stretch)
        self.users_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        lay.addWidget(self.users_table)
        return w

    def refresh_users_table(self):
        users = self.auth_ctrl.list_users()
        self.users_table.setRowCount(len(users))
        for idx, u in enumerate(users):
            id_item = QTableWidgetItem(str(u.userID))
            id_item.setData(Qt.ItemDataRole.UserRole, u)
            self.users_table.setItem(idx, 0, id_item)
            self.users_table.setItem(idx, 1, QTableWidgetItem(u.username))
            self.users_table.setItem(idx, 2, QTableWidgetItem(u.fullname))
            self.users_table.setItem(idx, 3, QTableWidgetItem(u.email))
            self.users_table.setItem(idx, 4, QTableWidgetItem(u.role))
            self.users_table.setItem(idx, 5, QTableWidgetItem(u.status))

    def handle_admin_add_user(self):
        ok, msg = self.auth_ctrl.admin_create_user(
            self.u_username.text(), self.u_fullname.text(), self.u_email.text(), self.u_pass.text(), self.u_role.currentText()
        )
        if ok:
            self.u_username.clear()
            self.u_fullname.clear()
            self.u_email.clear()
            self.u_pass.clear()
            self.refresh_users_table()
        else:
            QMessageBox.warning(self, "Error", msg)

    def handle_toggle_user_lock(self):
        row = self.users_table.currentRow()
        if row < 0:
            return
        user_obj: User = self.users_table.item(row, 0).data(Qt.ItemDataRole.UserRole)
        new_status = "locked" if user_obj.status == "active" else "active"
        self.auth_ctrl.admin_update_role_and_status(user_obj.userID, user_obj.role, new_status)
        self.refresh_users_table()


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Quiz Examination System — Group 10")
        self.resize(1280, 820)

        self.db = DatabaseManager()
        self.auth_ctrl = AuthController(self.db)
        self.quiz_ctrl = QuizController(self.db)
        self.exam_ctrl = ExamController(self.db)

        self.stack = QStackedWidget()
        self.setCentralWidget(self.stack)

        self.login_view = LoginView(self.auth_ctrl, self.handle_login_success)
        self.student_dash = StudentDashboardView(
            self.quiz_ctrl, self.handle_start_quiz, self.handle_view_result, self.handle_logout
        )
        self.exam_view = ExamAttemptView(self.exam_ctrl, self.handle_exam_finished)
        self.result_view = ResultBreakdownView(self.return_to_dashboard)
        self.admin_portal = AdminTeacherPortalView(self.auth_ctrl, self.quiz_ctrl, self.handle_logout)

        self.stack.addWidget(self.login_view)     # 0
        self.stack.addWidget(self.student_dash)   # 1
        self.stack.addWidget(self.exam_view)      # 2
        self.stack.addWidget(self.result_view)    # 3
        self.stack.addWidget(self.admin_portal)   # 4

        self.stack.setCurrentIndex(0)

    def handle_login_success(self, user: User):
        # UC-01 Main Flow Step 4 routing
        if user.role == "student":
            self.student_dash.load_user(user)
            self.stack.setCurrentIndex(1)
        else:
            self.admin_portal.load_user(user)
            self.stack.setCurrentIndex(4)

    def handle_start_quiz(self, quiz_card_data: Dict):
        if not self.auth_ctrl.current_user:
            return
        passcode = ""
        if quiz_card_data.get("accessCode"):
            text, ok = QInputDialog.getText(
                self,
                "Exam Access Code Required",
                f"Enter room passcode for '{quiz_card_data['title']}':",
                QLineEdit.EchoMode.Password,
            )
            if not ok:
                return
            passcode = text

        ok, msg, attempt, quiz = self.exam_ctrl.start_quiz_attempt(
            self.auth_ctrl.current_user.userID, quiz_card_data["quizID"], passcode
        )
        if not ok or not attempt or not quiz:
            QMessageBox.warning(self, "Cannot Start Quiz", msg)
            return

        self.exam_view.start_session(attempt, quiz)
        self.stack.setCurrentIndex(2)

    def handle_exam_finished(self, result_data: Dict):
        self.result_view.display_result(result_data)
        self.stack.setCurrentIndex(3)

    def handle_view_result(self, attempt_id: int):
        if not attempt_id:
            return
        data = self.exam_ctrl.get_attempt_breakdown(attempt_id)
        self.result_view.display_result(data)
        self.stack.setCurrentIndex(3)

    def return_to_dashboard(self):
        if self.auth_ctrl.current_user:
            self.student_dash.load_user(self.auth_ctrl.current_user)
            self.stack.setCurrentIndex(1)

    def handle_logout(self):
        self.auth_ctrl.logout()
        self.stack.setCurrentIndex(0)


def launch_app():
    app = QApplication(sys.argv)
    app.setStyleSheet(APP_STYLESHEET)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
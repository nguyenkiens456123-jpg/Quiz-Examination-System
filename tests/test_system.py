import gc
import pytest

from src.controllers.auth_controller import AuthController
from src.controllers.exam_controller import ExamController
from src.controllers.quiz_controller import QuizController
from src.database.db_init import DatabaseManager
from src.models.entities import Question


@pytest.fixture
def temp_system(tmp_path):
    db_file = tmp_path / "test_quiz.db"
    db = DatabaseManager(db_path=str(db_file))
    auth = AuthController(db)
    quiz_ctrl = QuizController(db)
    exam_ctrl = ExamController(db)
    yield db, auth, quiz_ctrl, exam_ctrl
    gc.collect()


def test_tc01_valid_student_login(temp_system):
    _, auth, _, _ = temp_system
    ok, msg, user = auth.login("student01@uth.edu.vn", "123456")
    assert ok is True
    assert user is not None
    assert user.role == "student"


def test_tc02_invalid_login_credentials(temp_system):
    _, auth, _, _ = temp_system
    ok, msg, user = auth.login("student01@uth.edu.vn", "wrongpass")
    assert ok is False
    assert msg == "Invalid username or password"
    assert user is None


def test_tc03_locked_account_login_blocked(temp_system):
    _, auth, _, _ = temp_system
    ok, msg, user = auth.login("locked@uth.edu.vn", "123456")
    assert ok is False
    assert "suspended" in msg


def test_tc04_student_registration_and_duplicate_check(temp_system):
    _, auth, _, _ = temp_system
    ok, _ = auth.register_student("Pham Van D", "newstudent@uth.edu.vn", "secret123")
    assert ok is True
    ok_dup, msg_dup = auth.register_student("Pham Van D", "newstudent@uth.edu.vn", "secret123")
    assert ok_dup is False
    assert "exists" in msg_dup


def test_tc05_dashboard_search_and_filter(temp_system):
    _, _, quiz_ctrl, _ = temp_system
    all_q = quiz_ctrl.get_student_quizzes(user_id=1, keyword="", status_filter="All")
    assert len(all_q) == 3

    completed_q = quiz_ctrl.get_student_quizzes(user_id=1, keyword="", status_filter="Completed")
    assert len(completed_q) == 1
    assert completed_q[0]["title"] == "Basic Quiz"

    search_q = quiz_ctrl.get_student_quizzes(user_id=1, keyword="Midterm", status_filter="Active")
    assert len(search_q) == 1
    assert search_q[0]["quizID"] == 1


def test_tc06_start_quiz_passcode_validation(temp_system):
    _, _, _, exam_ctrl = temp_system
    # Quiz 1 requires passcode "SSD2026"
    ok_bad, msg_bad, _, _ = exam_ctrl.start_quiz_attempt(user_id=1, quiz_id=1, entered_passcode="WRONG")
    assert ok_bad is False
    assert "Invalid exam access code" in msg_bad

    ok_good, _, attempt, quiz = exam_ctrl.start_quiz_attempt(user_id=1, quiz_id=1, entered_passcode="SSD2026")
    assert ok_good is True
    assert attempt is not None
    assert len(quiz.questions) == 6


def test_tc07_prevent_retaking_completed_quiz(temp_system):
    _, _, _, exam_ctrl = temp_system
    # Quiz 3 is already completed by user 1 in seed data
    ok, msg, _, _ = exam_ctrl.start_quiz_attempt(user_id=1, quiz_id=3)
    assert ok is False
    assert "already completed" in msg


def test_tc08_flag_question_and_autosave_progress(temp_system):
    _, _, _, exam_ctrl = temp_system
    _, _, attempt, quiz = exam_ctrl.start_quiz_attempt(user_id=1, quiz_id=1, entered_passcode="SSD2026")
    q1 = quiz.questions[0]
    flagged = exam_ctrl.toggle_flag(attempt.attemptID, q1.questionID)
    assert flagged is True

    ok_save, status_txt = exam_ctrl.auto_save_progress(
        attempt.attemptID,
        {q1.questionID: q1.options[1].optionID},
        {q1.questionID: True},
    )
    assert ok_save is True
    assert status_txt == "Auto-saved 10s ago"


def test_tc09_auto_grading_pass_outcome(temp_system):
    _, _, _, exam_ctrl = temp_system
    _, _, attempt, quiz = exam_ctrl.start_quiz_attempt(user_id=1, quiz_id=1, entered_passcode="SSD2026")
    # Answer all 6 questions correctly
    for q in quiz.questions:
        correct_opt = next(o for o in q.options if o.isCorrect)
        exam_ctrl.save_selection(attempt.attemptID, q.questionID, correct_opt.optionID)

    ok, result = exam_ctrl.submit_and_grade(attempt.attemptID)
    assert ok is True
    assert result["totalScore"] == 10.0
    assert result["isPassed"] is True


def test_tc10_auto_grading_fail_outcome(temp_system):
    _, _, _, exam_ctrl = temp_system
    _, _, attempt, quiz = exam_ctrl.start_quiz_attempt(user_id=2, quiz_id=1, entered_passcode="SSD2026")
    # Answer all 6 questions incorrectly
    for q in quiz.questions:
        wrong_opt = next(o for o in q.options if not o.isCorrect)
        exam_ctrl.save_selection(attempt.attemptID, q.questionID, wrong_opt.optionID)

    ok, result = exam_ctrl.submit_and_grade(attempt.attemptID)
    assert ok is True
    assert result["totalScore"] == 0.0
    assert result["isPassed"] is False


def test_tc11_question_bank_crud_and_validation(temp_system):
    _, _, quiz_ctrl, _ = temp_system
    q_invalid = Question(1, "SE", "Test", "", 1.0)
    assert q_invalid.validateQuestion() is False

    ok, _ = quiz_ctrl.add_question(
        "Software Specification & Design",
        "Testing",
        "What is Black-box testing?",
        ["Testing internal code", "Testing functionality without knowing internal code", "Unit testing", "Code review"],
        1,
        1.0,
        "Black-box testing evaluates I/O behavior.",
    )
    assert ok is True
    questions = quiz_ctrl.list_questions("Software Specification & Design", "Black-box")
    assert len(questions) == 1

    ok_del, _ = quiz_ctrl.delete_questions([questions[0].questionID])
    assert ok_del is True


def test_tc12_create_quiz_with_advanced_rules_and_review_disabled(temp_system):
    _, _, quiz_ctrl, exam_ctrl = temp_system
    qs = quiz_ctrl.list_questions("All", "")[:2]
    qids = [q.questionID for q in qs]

    ok, _, _ = quiz_ctrl.create_and_configure_quiz(
        title="Custom No-Review Quiz",
        subject="Software Specification & Design",
        duration_mins=15,
        pass_score=50.0,
        class_assignment="Class SE-01",
        access_code="TEST99",
        shuffle_questions=True,
        shuffle_options=True,
        review_rules=False,
        is_published=True,
        question_ids=qids,
        created_by=3,
    )
    assert ok is True

    quizzes = quiz_ctrl.get_student_quizzes(user_id=2, keyword="Custom No-Review", status_filter="Active")
    assert len(quizzes) == 1
    new_quiz_id = quizzes[0]["quizID"]

    _, _, att, _ = exam_ctrl.start_quiz_attempt(user_id=2, quiz_id=new_quiz_id, entered_passcode="TEST99")
    _, res = exam_ctrl.submit_and_grade(att.attemptID)
    assert res["reviewRules"] is False


def test_tc13_create_quiz_missing_required_fields_rejected(temp_system):
    _, _, quiz_ctrl, _ = temp_system
    ok, msg, _ = quiz_ctrl.create_and_configure_quiz(
        title="",
        subject="SE",
        duration_mins=30,
        pass_score=50.0,
        class_assignment="SE-01",
        access_code="",
        shuffle_questions=False,
        shuffle_options=False,
        review_rules=True,
        is_published=True,
        question_ids=[],
        created_by=3,
    )
    assert ok is False
    assert "Title is required" in msg


def test_tc14_gradebook_analytics_and_csv_export(temp_system, tmp_path):
    _, _, quiz_ctrl, _ = temp_system
    records, stats = quiz_ctrl.get_gradebook_and_analytics(quiz_id=3)
    assert len(records) == 1
    assert stats["avgScore"] == 10.0
    assert stats["passRate"] == 100.0

    csv_path = tmp_path / "gradebook_export.csv"
    ok, _ = quiz_ctrl.export_gradebook_csv(quiz_id=3, file_path=str(csv_path))
    assert ok is True
    content = csv_path.read_text(encoding="utf-8-sig")
    assert "Nguyen Van A" in content


def test_tc15_admin_manage_users_and_roles(temp_system):
    _, auth, _, _ = temp_system
    ok, _ = auth.admin_create_user("TC-02", "New Teacher", "teacher2@uth.edu.vn", "123456", "teacher")
    assert ok is True
    users = auth.list_users("teacher2@uth.edu.vn")
    assert len(users) == 1
    auth.admin_update_role_and_status(users[0].userID, "admin", "locked")
    updated = auth.list_users("teacher2@uth.edu.vn")[0]
    assert updated.role == "admin"
    assert updated.status == "locked"
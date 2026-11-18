"""
exam_controller.py  -  Quiz Taking & Attempt Module (nhánh feat/exam-autosave)
Phụ trách: Trần Lê Đăng Khôi
Use case: UC-03 (Bắt đầu / tiếp tục làm bài), UC-04 (Trả lời & đếm ngược),
          UC-05 (Auto-Save mỗi 10 giây + Nộp bài)

!!! Tên bảng/cột bên dưới là GIẢ ĐỊNH theo Class Diagram stage 1-2.
    Sau khi Duy push db_init.py, đối chiếu lại các câu SQL (xem mục SCHEMA ở cuối file).
"""
import sqlite3
import threading
from contextlib import closing
from datetime import datetime, timedelta, timezone
from typing import Callable, Dict, List, Optional

AUTOSAVE_INTERVAL_SEC = 10

STATUS_IN_PROGRESS = "IN_PROGRESS"
STATUS_SUBMITTED = "SUBMITTED"


class ExamError(Exception):
    """Lỗi nghiệp vụ khi làm bài (hết giờ, attempt không tồn tại, ...)."""


class ExamController:
    def __init__(self, db_path: str,
                 now_func: Optional[Callable[[], datetime]] = None,
                 grader: Optional[Callable[[int], object]] = None):
        """
        db_path  : đường dẫn file SQLite (do db_init.py của Duy tạo)
        now_func : hàm trả về thời gian hiện tại (để unit test giả lập đồng hồ)
        grader   : hàm chấm điểm của Duy, vd GradingController().grade_attempt
                   -> được gọi sau khi nộp bài (nếu truyền vào)
        """
        self.db_path = db_path
        self._now = now_func or (lambda: datetime.now(timezone.utc))
        self._grader = grader
        # Đáp án đã chọn nhưng CHƯA ghi DB: {attempt_id: {question_id: option_id}}
        self._pending: Dict[int, Dict[int, int]] = {}
        self._lock = threading.Lock()

    # ------------------------------------------------------------------ DB
    def _connect(self) -> sqlite3.Connection:
        # Mỗi lần gọi mở 1 connection riêng -> an toàn khi Auto-Save chạy ở thread khác
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON")
        return conn

    def _get_attempt(self, conn, attempt_id: int) -> sqlite3.Row:
        row = conn.execute(
            'SELECT a.*, q.duration_minutes FROM ATTEMPT a '
            'JOIN QUIZ q ON q.quiz_id = a.quiz_id WHERE a.attempt_id = ?',
            (attempt_id,)).fetchone()
        if row is None:
            raise ExamError(f"Attempt {attempt_id} không tồn tại")
        return row

    # ------------------------------------------------- UC-03: bắt đầu làm bài
    def start_attempt(self, user_id: int, quiz_id: int) -> int:
        """Tạo lượt thi mới. Nếu SV đang có lượt chưa nộp & còn giờ -> tiếp tục lượt đó."""
        with closing(self._connect()) as conn:
            quiz = conn.execute("SELECT * FROM QUIZ WHERE quiz_id = ?", (quiz_id,)).fetchone()
            if quiz is None:
                raise ExamError("Đề thi không tồn tại")

            old = conn.execute(
                "SELECT attempt_id FROM ATTEMPT WHERE user_id=? AND quiz_id=? AND status=?",
                (user_id, quiz_id, STATUS_IN_PROGRESS)).fetchone()
            if old is not None:
                if self.get_remaining_seconds(old["attempt_id"]) > 0:
                    return old["attempt_id"]          # tiếp tục bài đang làm dở
                self.submit_attempt(old["attempt_id"], auto_submit=True)  # hết giờ -> nộp

            cur = conn.execute(
                "INSERT INTO ATTEMPT (user_id, quiz_id, start_time, status) VALUES (?,?,?,?)",
                (user_id, quiz_id, self._now().isoformat(), STATUS_IN_PROGRESS))
            conn.commit()
            return cur.lastrowid

    def get_questions(self, attempt_id: int) -> List[dict]:
        """Danh sách câu hỏi + đáp án (KHÔNG trả is_correct cho phía giao diện)."""
        with closing(self._connect()) as conn:
            att = self._get_attempt(conn, attempt_id)
            questions = conn.execute(
                "SELECT question_id, content FROM QUESTION WHERE quiz_id=? ORDER BY question_id",
                (att["quiz_id"],)).fetchall()
            result = []
            for q in questions:
                opts = conn.execute(
                    'SELECT option_id, content FROM "OPTION" WHERE question_id=? ORDER BY option_id',
                    (q["question_id"],)).fetchall()
                result.append({
                    "question_id": q["question_id"],
                    "content": q["content"],
                    "options": [{"option_id": o["option_id"], "content": o["content"]} for o in opts],
                })
            return result

    # ------------------------------------------- UC-04: đếm ngược & trả lời
    def get_remaining_seconds(self, attempt_id: int) -> int:
        """Thời gian còn lại (giây). Tính từ start_time trong DB -> tắt app mở lại vẫn đúng."""
        with closing(self._connect()) as conn:
            att = self._get_attempt(conn, attempt_id)
        if att["status"] == STATUS_SUBMITTED:
            return 0
        start = datetime.fromisoformat(att["start_time"])
        deadline = start + timedelta(minutes=att["duration_minutes"])
        return max(0, int((deadline - self._now()).total_seconds()))

    def is_expired(self, attempt_id: int) -> bool:
        return self.get_remaining_seconds(attempt_id) <= 0

    def save_answer(self, attempt_id: int, question_id: int, option_id: int) -> None:
        """Gọi mỗi khi SV bấm chọn đáp án. Chỉ lưu vào bộ nhớ, Auto-Save sẽ ghi DB."""
        if self.is_expired(attempt_id):
            raise ExamError("Đã hết thời gian làm bài")
        with self._lock:
            self._pending.setdefault(attempt_id, {})[question_id] = option_id

    def get_saved_answers(self, attempt_id: int) -> Dict[int, int]:
        """Đáp án đã chọn (DB + chưa flush) -> dùng để khôi phục giao diện khi mở lại bài."""
        with closing(self._connect()) as conn:
            rows = conn.execute(
                "SELECT question_id, selected_option_id FROM ATTEMPT_DETAIL WHERE attempt_id=?",
                (attempt_id,)).fetchall()
        answers = {r["question_id"]: r["selected_option_id"] for r in rows}
        with self._lock:
            answers.update(self._pending.get(attempt_id, {}))
        return answers

    # ------------------------------------------------- UC-05: Auto-Save, nộp
    def autosave(self, attempt_id: int) -> int:
        """Ghi các đáp án đang chờ xuống DB. Trả về số câu đã lưu. Gọi mỗi 10 giây."""
        with self._lock:
            pending = dict(self._pending.get(attempt_id, {}))
        if not pending:
            return 0
        with closing(self._connect()) as conn:
            for qid, oid in pending.items():
                cur = conn.execute(
                    "UPDATE ATTEMPT_DETAIL SET selected_option_id=? WHERE attempt_id=? AND question_id=?",
                    (oid, attempt_id, qid))
                if cur.rowcount == 0:
                    conn.execute(
                        "INSERT INTO ATTEMPT_DETAIL (attempt_id, question_id, selected_option_id) "
                        "VALUES (?,?,?)", (attempt_id, qid, oid))
            conn.commit()
        with self._lock:
            buf = self._pending.get(attempt_id, {})
            for qid, oid in pending.items():
                if buf.get(qid) == oid:      # không xoá nếu SV vừa đổi đáp án trong lúc ghi
                    del buf[qid]
        return len(pending)

    def submit_attempt(self, attempt_id: int, auto_submit: bool = False) -> dict:
        """Nộp bài (SV bấm nộp hoặc hết giờ). Gọi nhiều lần vẫn an toàn."""
        with closing(self._connect()) as conn:
            att = self._get_attempt(conn, attempt_id)
        if att["status"] == STATUS_SUBMITTED:
            return {"attempt_id": attempt_id, "status": STATUS_SUBMITTED, "already_submitted": True}

        self.autosave(attempt_id)            # đảm bảo không mất câu nào
        end = self._now()
        deadline = datetime.fromisoformat(att["start_time"]) + timedelta(minutes=att["duration_minutes"])
        end = min(end, deadline)             # nộp trễ vẫn tính tối đa đến hạn
        with closing(self._connect()) as conn:
            conn.execute("UPDATE ATTEMPT SET status=?, end_time=? WHERE attempt_id=?",
                         (STATUS_SUBMITTED, end.isoformat(), attempt_id))
            conn.commit()
        with self._lock:
            self._pending.pop(attempt_id, None)

        result = {"attempt_id": attempt_id, "status": STATUS_SUBMITTED,
                  "auto_submit": auto_submit, "already_submitted": False}
        if self._grader is not None:         # gọi hàm chấm điểm của Duy
            result["grade"] = self._grader(attempt_id)
        return result


class AutoSaver:
    """
    Chạy nền: cứ mỗi `interval` giây gọi controller.autosave(); khi hết giờ gọi on_timeout().
    Dùng khi chạy console / test. Với PyQt6 có thể dùng QTimer thay thế (xem cuối file).
    """

    def __init__(self, controller: ExamController, attempt_id: int,
                 interval: float = AUTOSAVE_INTERVAL_SEC,
                 on_timeout: Optional[Callable[[], None]] = None):
        self.controller = controller
        self.attempt_id = attempt_id
        self.interval = interval
        self.on_timeout = on_timeout
        self._stop = threading.Event()
        self._thread: Optional[threading.Thread] = None

    def start(self) -> None:
        self._stop.clear()
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()

    def stop(self) -> None:
        self._stop.set()
        if self._thread:
            self._thread.join(timeout=self.interval + 1)

    def _run(self) -> None:
        while not self._stop.wait(self.interval):      # ngủ `interval` giây hoặc bị stop
            self.controller.autosave(self.attempt_id)
            if self.controller.is_expired(self.attempt_id):
                self.controller.submit_attempt(self.attempt_id, auto_submit=True)
                if self.on_timeout:
                    self.on_timeout()
                break


# ---------------------------------------------------------------- SCHEMA giả định
# ATTEMPT(attempt_id PK, user_id, quiz_id, start_time TEXT, end_time TEXT, status TEXT, score REAL)
# ATTEMPT_DETAIL(detail_id PK, attempt_id, question_id, selected_option_id, is_correct)
# QUIZ(quiz_id PK, title, duration_minutes INT)
# QUESTION(question_id PK, quiz_id, content)
# "OPTION"(option_id PK, question_id, content, is_correct)
#
# ---------------------------------------------------------------- Gợi ý cho View (PyQt6)
# self.timer_save = QTimer(self); self.timer_save.timeout.connect(lambda: ctrl.autosave(aid))
# self.timer_save.start(10_000)                      # Auto-Save 10 giây
# self.timer_clock = QTimer(self); self.timer_clock.timeout.connect(self.refresh_clock)
# self.timer_clock.start(1_000)   # refresh_clock: ctrl.get_remaining_seconds(aid); =0 -> ctrl.submit_attempt(aid, True)

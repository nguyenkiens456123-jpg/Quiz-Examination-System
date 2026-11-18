import sqlite3
import time
from datetime import datetime, timedelta, timezone

import pytest

from src.controllers.exam_controller import (
    AutoSaver, ExamController, ExamError, STATUS_IN_PROGRESS, STATUS_SUBMITTED)

SCHEMA = """
CREATE TABLE QUIZ (quiz_id INTEGER PRIMARY KEY, title TEXT, duration_minutes INTEGER);
CREATE TABLE QUESTION (question_id INTEGER PRIMARY KEY, quiz_id INTEGER, content TEXT);
CREATE TABLE "OPTION" (option_id INTEGER PRIMARY KEY, question_id INTEGER, content TEXT, is_correct INTEGER);
CREATE TABLE ATTEMPT (attempt_id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER, quiz_id INTEGER,
                      start_time TEXT, end_time TEXT, status TEXT, score REAL);
CREATE TABLE ATTEMPT_DETAIL (detail_id INTEGER PRIMARY KEY AUTOINCREMENT, attempt_id INTEGER,
                             question_id INTEGER, selected_option_id INTEGER, is_correct INTEGER);
INSERT INTO QUIZ VALUES (1, 'Demo quiz', 30);
INSERT INTO QUESTION VALUES (1, 1, 'Q1'), (2, 1, 'Q2');
INSERT INTO "OPTION" VALUES (1,1,'A',1),(2,1,'B',0),(3,2,'C',0),(4,2,'D',1);
"""


class FakeClock:
    def __init__(self):
        self.t = datetime(2026, 11, 20, 8, 0, 0, tzinfo=timezone.utc)

    def __call__(self):
        return self.t

    def advance(self, seconds):
        self.t += timedelta(seconds=seconds)


@pytest.fixture
def env(tmp_path):
    db = str(tmp_path / "test.db")
    conn = sqlite3.connect(db)
    conn.executescript(SCHEMA)
    conn.commit()
    conn.close()
    clock = FakeClock()
    return ExamController(db, now_func=clock), clock, db


def count_details(db, attempt_id):
    conn = sqlite3.connect(db)
    n = conn.execute("SELECT COUNT(*) FROM ATTEMPT_DETAIL WHERE attempt_id=?", (attempt_id,)).fetchone()[0]
    conn.close()
    return n


def test_TC01_start_attempt_creates_in_progress(env):
    ctrl, _, db = env
    aid = ctrl.start_attempt(user_id=3, quiz_id=1)
    status = sqlite3.connect(db).execute("SELECT status FROM ATTEMPT WHERE attempt_id=?", (aid,)).fetchone()[0]
    assert status == STATUS_IN_PROGRESS


def test_TC02_start_attempt_invalid_quiz(env):
    ctrl, _, _ = env
    with pytest.raises(ExamError):
        ctrl.start_attempt(3, 999)


def test_TC03_resume_existing_attempt(env):
    ctrl, clock, _ = env
    a1 = ctrl.start_attempt(3, 1)
    clock.advance(60)
    assert ctrl.start_attempt(3, 1) == a1


def test_TC04_get_questions_hides_correct_flag(env):
    ctrl, _, _ = env
    qs = ctrl.get_questions(ctrl.start_attempt(3, 1))
    assert len(qs) == 2 and len(qs[0]["options"]) == 2
    assert "is_correct" not in qs[0]["options"][0]


def test_TC05_countdown(env):
    ctrl, clock, _ = env
    aid = ctrl.start_attempt(3, 1)
    assert ctrl.get_remaining_seconds(aid) == 30 * 60
    clock.advance(600)
    assert ctrl.get_remaining_seconds(aid) == 20 * 60
    clock.advance(99999)
    assert ctrl.get_remaining_seconds(aid) == 0


def test_TC06_answer_not_in_db_before_autosave(env):
    ctrl, _, db = env
    aid = ctrl.start_attempt(3, 1)
    ctrl.save_answer(aid, 1, 1)
    assert count_details(db, aid) == 0
    assert ctrl.get_saved_answers(aid) == {1: 1}


def test_TC07_autosave_persists(env):
    ctrl, _, db = env
    aid = ctrl.start_attempt(3, 1)
    ctrl.save_answer(aid, 1, 1)
    ctrl.save_answer(aid, 2, 4)
    assert ctrl.autosave(aid) == 2
    assert count_details(db, aid) == 2
    assert ctrl.autosave(aid) == 0          # không còn gì để lưu


def test_TC08_change_answer_overwrites(env):
    ctrl, _, db = env
    aid = ctrl.start_attempt(3, 1)
    ctrl.save_answer(aid, 1, 1)
    ctrl.autosave(aid)
    ctrl.save_answer(aid, 1, 2)
    ctrl.autosave(aid)
    assert count_details(db, aid) == 1
    assert ctrl.get_saved_answers(aid) == {1: 2}


def test_TC09_save_after_expired_rejected(env):
    ctrl, clock, _ = env
    aid = ctrl.start_attempt(3, 1)
    clock.advance(31 * 60)
    with pytest.raises(ExamError):
        ctrl.save_answer(aid, 1, 1)


def test_TC10_submit_flushes_pending(env):
    ctrl, _, db = env
    aid = ctrl.start_attempt(3, 1)
    ctrl.save_answer(aid, 1, 1)
    res = ctrl.submit_attempt(aid)
    assert res["status"] == STATUS_SUBMITTED
    assert count_details(db, aid) == 1


def test_TC11_submit_idempotent(env):
    ctrl, _, _ = env
    aid = ctrl.start_attempt(3, 1)
    ctrl.submit_attempt(aid)
    assert ctrl.submit_attempt(aid)["already_submitted"] is True


def test_TC12_late_submit_end_time_capped(env):
    ctrl, clock, db = env
    aid = ctrl.start_attempt(3, 1)
    clock.advance(40 * 60)
    ctrl.submit_attempt(aid, auto_submit=True)
    end = sqlite3.connect(db).execute("SELECT end_time FROM ATTEMPT WHERE attempt_id=?", (aid,)).fetchone()[0]
    assert datetime.fromisoformat(end) == datetime(2026, 11, 20, 8, 30, tzinfo=timezone.utc)


def test_TC13_grader_called_on_submit(tmp_path):
    db = str(tmp_path / "g.db")
    conn = sqlite3.connect(db); conn.executescript(SCHEMA); conn.commit(); conn.close()
    called = []
    ctrl = ExamController(db, grader=lambda aid: called.append(aid) or 10.0)
    aid = ctrl.start_attempt(3, 1)
    assert ctrl.submit_attempt(aid)["grade"] == 10.0
    assert called == [aid]


def test_TC14_autosaver_background_thread(env):
    ctrl, _, db = env
    aid = ctrl.start_attempt(3, 1)
    ctrl.save_answer(aid, 1, 1)
    saver = AutoSaver(ctrl, aid, interval=0.05)
    saver.start()
    time.sleep(0.3)
    saver.stop()
    assert count_details(db, aid) == 1

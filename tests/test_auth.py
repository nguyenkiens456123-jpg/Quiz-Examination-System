import os
import sqlite3
import pytest
from src.controllers.auth_controller import AuthController

TEST_DB = "tests/test_quiz.db"

@pytest.fixture
def auth_ctrl():
    if os.path.exists(TEST_DB):
        os.remove(TEST_DB)
    conn = sqlite3.connect(TEST_DB)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE USER (
            user_id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            full_name TEXT,
            role TEXT NOT NULL,
            status TEXT DEFAULT 'ACTIVE'
        )
    ''')
    ctrl = AuthController(db_path=TEST_DB)
    hashed = ctrl.hash_password("123456")
    cursor.execute("INSERT INTO USER (username, password_hash, full_name, role, status) VALUES (?, ?, ?, ?, ?)",
                   ("kien_admin", hashed, "Nguyen Sy Kien", "ADMIN", "ACTIVE"))
    cursor.execute("INSERT INTO USER (username, password_hash, full_name, role, status) VALUES (?, ?, ?, ?, ?)",
                   ("locked_user", hashed, "Locked User", "STUDENT", "LOCKED"))
    conn.commit()
    conn.close()

    yield ctrl

    if os.path.exists(TEST_DB):
        os.remove(TEST_DB)

def test_login_success(auth_ctrl):
    res = auth_ctrl.login("kien_admin", "123456")
    assert res["success"] is True
    assert res["user"]["role"] == "ADMIN"

def test_login_wrong_password(auth_ctrl):
    res = auth_ctrl.login("kien_admin", "sai_mat_khau")
    assert res["success"] is False

def test_login_locked_account(auth_ctrl):
    res = auth_ctrl.login("locked_user", "123456")
    assert res["success"] is False
    assert "bị khóa" in res["message"]

import sqlite3
import bcrypt
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "database", "quiz_system.db")

class AuthController:
    def __init__(self, db_path=DB_PATH):
        self.db_path = db_path
        self.current_user = None

    def _get_connection(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def hash_password(self, plain_password: str) -> str:
        salt = bcrypt.gensalt()
        return bcrypt.hashpw(plain_password.encode('utf-8'), salt).decode('utf-8')

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        try:
            return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))
        except ValueError:
            return False

    def login(self, username: str, password: str) -> dict:
        if not username or not password:
            return {"success": False, "message": "Vui lòng nhập đầy đủ tài khoản và mật khẩu.", "user": None}

        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM USER WHERE username = ?", (username,))
        user = cursor.fetchone()
        conn.close()

        if not user:
            return {"success": False, "message": "Tài khoản không tồn tại.", "user": None}

        if user["status"] != "ACTIVE":
            return {"success": False, "message": "Tài khoản đã bị khóa. Liên hệ Admin.", "user": None}

        if not self.verify_password(password, user["password_hash"]):
            return {"success": False, "message": "Mật khẩu không chính xác.", "user": None}

        self.current_user = dict(user)
        return {"success": True, "message": "Đăng nhập thành công!", "user": self.current_user}

    def logout(self):
        self.current_user = None

    def has_permission(self, required_roles: list) -> bool:
        if not self.current_user:
            return False
        return self.current_user.get("role") in required_roles

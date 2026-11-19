from typing import List, Optional, Tuple
import bcrypt
from src.database.db_init import DatabaseManager
from src.models.entities import User


class AuthController:
    def __init__(self, db: DatabaseManager):
        self.db = db
        self.current_user: Optional[User] = None

    def login(self, identifier: str, password: str) -> Tuple[bool, str, Optional[User]]:
        """UC-01: Log in / Authenticate with BCrypt verification and account status check."""
        identifier = (identifier or "").strip()
        if not identifier or not password:
            return False, "Please enter both email/username and password.", None

        with self.db.get_connection() as conn:
            cur = conn.cursor()
            cur.execute(
                "SELECT * FROM USER WHERE email = ? OR username = ?;",
                (identifier, identifier),
            )
            row = cur.fetchone()

        if not row:
            return False, "Invalid username or password", None

        user = User(
            user_id=row["userID"],
            username=row["username"],
            password_hash=row["password"],
            fullname=row["full_name"],
            email=row["email"],
            role=row["role"],
            status=row["status"],
        )

        # Exception Flow A2 of UC-01
        if user.status != "active":
            return False, "Your account has been suspended. Please contact Admin.", None

        # Main Flow + Exception Flow A1 of UC-01
        if not user.login(password):
            return False, "Invalid username or password", None

        self.current_user = user
        return True, "Login successful", user

    def logout(self) -> None:
        if self.current_user:
            self.current_user.logout()
            self.current_user = None

    def register_student(self, full_name: str, email: str, password: str, username: Optional[str] = None) -> Tuple[bool, str]:
        """FR-ST-01: Student registration."""
        full_name = (full_name or "").strip()
        email = (email or "").strip().lower()
        if not full_name or not email or not password:
            return False, "Full Name, Email, and Password are required."
        if "@" not in email:
            return False, "Invalid email format."
        if len(password) < 6:
            return False, "Password must be at least 6 characters."

        uname = (username or email.split("@")[0]).strip()
        pw_hash = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

        try:
            with self.db.get_connection() as conn:
                conn.execute(
                    "INSERT INTO USER (username, full_name, email, password, role, status) VALUES (?, ?, ?, ?, 'student', 'active');",
                    (uname, full_name, email, pw_hash),
                )
                conn.commit()
            return True, "Account registered successfully!"
        except Exception as exc:
            if "UNIQUE" in str(exc).upper():
                return False, "Username or Email already exists."
            return False, f"Database error: {exc}"

    def list_users(self, keyword: str = "") -> List[User]:
        """UC-11: List and search all users."""
        kw = f"%{(keyword or '').strip()}%"
        with self.db.get_connection() as conn:
            cur = conn.cursor()
            cur.execute(
                """SELECT * FROM USER
                   WHERE username LIKE ? OR full_name LIKE ? OR email LIKE ? OR role LIKE ?
                   ORDER BY userID ASC;""",
                (kw, kw, kw, kw),
            )
            rows = cur.fetchall()
        return [
            User(r["userID"], r["username"], r["password"], r["full_name"], r["email"], r["role"], r["status"])
            for r in rows
        ]

    def admin_create_user(self, username: str, full_name: str, email: str, password: str, role: str) -> Tuple[bool, str]:
        """UC-11: Administrator creates user account and assigns role."""
        username = (username or "").strip()
        full_name = (full_name or "").strip()
        email = (email or "").strip().lower()
        role = (role or "student").lower()
        if not username or not full_name or not email or not password:
            return False, "All user fields are required."
        if role not in ("student", "teacher", "admin"):
            return False, "Role must be student, teacher, or admin."

        pw_hash = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
        try:
            with self.db.get_connection() as conn:
                conn.execute(
                    "INSERT INTO USER (username, full_name, email, password, role, status) VALUES (?, ?, ?, ?, ?, 'active');",
                    (username, full_name, email, pw_hash, role),
                )
                conn.commit()
            return True, f"User '{username}' created successfully."
        except Exception as exc:
            if "UNIQUE" in str(exc).upper():
                return False, "Duplicate account: Username or Email already exists."
            return False, str(exc)

    def admin_update_role_and_status(self, user_id: int, role: str, status: str) -> Tuple[bool, str]:
        """UC-11: Update RBAC role and lock/unlock account."""
        role = role.lower()
        status = status.lower()
        if role not in ("student", "teacher", "admin"):
            return False, "Invalid role."
        if status not in ("active", "locked"):
            return False, "Invalid status."
        with self.db.get_connection() as conn:
            conn.execute(
                "UPDATE USER SET role = ?, status = ? WHERE userID = ?;",
                (role, status, user_id),
            )
            conn.commit()
        return True, "User role and status updated."
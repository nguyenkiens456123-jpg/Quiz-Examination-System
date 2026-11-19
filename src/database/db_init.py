import os
import sqlite3
from datetime import datetime, timedelta
import bcrypt

DEFAULT_DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "quiz_system.db")


class DatabaseManager:
    def __init__(self, db_path: str = DEFAULT_DB_PATH):
        self.db_path = db_path
        self.init_schema()
        self.seed_data()

    def get_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON;")
        return conn

    def init_schema(self) -> None:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            # 6.1 USER
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS USER (
                    userID INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    full_name TEXT NOT NULL,
                    email TEXT UNIQUE NOT NULL,
                    password TEXT NOT NULL,
                    role TEXT NOT NULL CHECK(role IN ('student', 'teacher', 'admin')),
                    status TEXT NOT NULL DEFAULT 'active' CHECK(status IN ('active', 'locked'))
                );
            """)
            # 6.2 QUIZ
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS QUIZ (
                    quizID INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    subject TEXT NOT NULL DEFAULT 'Software Specification & Design',
                    durationMins INTEGER NOT NULL,
                    passScore REAL NOT NULL,
                    classAssignment TEXT DEFAULT 'Class SE-01',
                    accessCode TEXT DEFAULT '',
                    shuffleQuestions INTEGER NOT NULL DEFAULT 0,
                    shuffleOptions INTEGER NOT NULL DEFAULT 0,
                    reviewRules INTEGER NOT NULL DEFAULT 1,
                    isPublished INTEGER NOT NULL DEFAULT 0,
                    created_by INTEGER,
                    FOREIGN KEY (created_by) REFERENCES USER(userID) ON DELETE SET NULL
                );
            """)
            # 6.3 QUESTION
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS QUESTION (
                    questionID INTEGER PRIMARY KEY AUTOINCREMENT,
                    quizID INTEGER,
                    subject TEXT NOT NULL,
                    topic TEXT NOT NULL,
                    content TEXT NOT NULL,
                    points REAL NOT NULL DEFAULT 1.0,
                    explanation TEXT DEFAULT '',
                    FOREIGN KEY (quizID) REFERENCES QUIZ(quizID) ON DELETE SET NULL
                );
            """)
            # Junction table to allow reusing Question Bank items across multiple quizzes
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS QUIZ_QUESTION (
                    quizID INTEGER NOT NULL,
                    questionID INTEGER NOT NULL,
                    PRIMARY KEY (quizID, questionID),
                    FOREIGN KEY (quizID) REFERENCES QUIZ(quizID) ON DELETE CASCADE,
                    FOREIGN KEY (questionID) REFERENCES QUESTION(questionID) ON DELETE CASCADE
                );
            """)
            # 6.4 OPTION
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS OPTION (
                    optionID INTEGER PRIMARY KEY AUTOINCREMENT,
                    questionID INTEGER NOT NULL,
                    option_text TEXT NOT NULL,
                    is_correct INTEGER NOT NULL DEFAULT 0,
                    FOREIGN KEY (questionID) REFERENCES QUESTION(questionID) ON DELETE CASCADE
                );
            """)
            # 6.5 ATTEMPT
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS ATTEMPT (
                    attemptID INTEGER PRIMARY KEY AUTOINCREMENT,
                    userID INTEGER NOT NULL,
                    quizID INTEGER NOT NULL,
                    startTime TEXT NOT NULL,
                    submitTime TEXT,
                    totalScore REAL DEFAULT 0.0,
                    isPassed INTEGER DEFAULT 0,
                    status TEXT NOT NULL DEFAULT 'In_Progress',
                    FOREIGN KEY (userID) REFERENCES USER(userID) ON DELETE CASCADE,
                    FOREIGN KEY (quizID) REFERENCES QUIZ(quizID) ON DELETE CASCADE
                );
            """)
            # 6.6 ATTEMPT_DETAIL
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS ATTEMPT_DETAIL (
                    detailID INTEGER PRIMARY KEY AUTOINCREMENT,
                    attemptID INTEGER NOT NULL,
                    questionID INTEGER NOT NULL,
                    selectedOptionID INTEGER,
                    isFlagged INTEGER NOT NULL DEFAULT 0,
                    isCorrect INTEGER NOT NULL DEFAULT 0,
                    UNIQUE(attemptID, questionID),
                    FOREIGN KEY (attemptID) REFERENCES ATTEMPT(attemptID) ON DELETE CASCADE,
                    FOREIGN KEY (questionID) REFERENCES QUESTION(questionID) ON DELETE CASCADE,
                    FOREIGN KEY (selectedOptionID) REFERENCES OPTION(optionID) ON DELETE SET NULL
                );
            """)
            conn.commit()

    def seed_data(self) -> None:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM USER;")
            if cursor.fetchone()[0] > 0:
                return

            pw_hash = bcrypt.hashpw(b"123456", bcrypt.gensalt()).decode("utf-8")

            users = [
                ("ST-01", "Nguyen Van A", "student01@uth.edu.vn", pw_hash, "student", "active"),
                ("ST-02", "Tran Thi B", "student02@uth.edu.vn", pw_hash, "student", "active"),
                ("TC-01", "Le Minh C (Teacher)", "teacher@uth.edu.vn", pw_hash, "teacher", "active"),
                ("AD-01", "System Administrator", "admin@uth.edu.vn", pw_hash, "admin", "active"),
                ("ST-LOCK", "Locked Student", "locked@uth.edu.vn", pw_hash, "student", "locked"),
            ]
            cursor.executemany(
                "INSERT INTO USER (username, full_name, email, password, role, status) VALUES (?, ?, ?, ?, ?, ?);",
                users,
            )

            # 3 Quizzes matching Figure 7.1 (SCR-01)
            quizzes = [
                ("Midterm Exam 2026", "Software Specification & Design", 45, 70.0, "Software Design · Class SE-01", "SSD2026", 0, 0, 1, 1, 3),
                ("SQL Final Examination", "Relational Database System", 60, 60.0, "Database Systems · Class DB-02", "", 1, 1, 1, 1, 3),
                ("Basic Quiz", "OOP C++", 30, 80.0, "OOP C++ · Class CS-01", "", 0, 0, 1, 1, 3),
            ]
            cursor.executemany(
                """INSERT INTO QUIZ (title, subject, durationMins, passScore, classAssignment, accessCode,
                   shuffleQuestions, shuffleOptions, reviewRules, isPublished, created_by)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);""",
                quizzes,
            )

            # Sample Question Bank matching Figure 7.2, 7.3, 7.4, 7.5
            questions_data = [
                (
                    1, "Software Specification & Design", "SDLC Basics",
                    "What does SDLC stand for?", 1.0,
                    "SDLC stands for Software Development Life Cycle, the structured process for building software.",
                    [("Software Design Life Cycle", 0), ("Software Development Life Cycle", 1), ("System Data Logic Control", 0), ("System Design Level Check", 0)],
                ),
                (
                    1, "Software Specification & Design", "Process Models",
                    "Which model is sequential?", 1.0,
                    "The Waterfall model follows a strict linear and sequential phase-by-phase flow.",
                    [("Agile", 0), ("Scrum", 0), ("Waterfall", 1), ("Spiral", 0)],
                ),
                (
                    1, "Software Specification & Design", "Architecture",
                    "What does 'M' mean in MVC?", 1.0,
                    "MVC stands for Model-View-Controller, where 'M' represents Model (data and business logic).",
                    [("Module", 0), ("Method", 0), ("Model", 1), ("Modifier", 0)],
                ),
                (
                    1, "Software Specification & Design", "UML Modeling",
                    "Which UML diagram models interactions over time?", 1.0,
                    "A Sequence Diagram models object interactions arranged in time sequence.",
                    [("Class diagram", 0), ("Sequence diagram", 1), ("Use Case diagram", 0), ("Component diagram", 0)],
                ),
                (
                    1, "Software Specification & Design", "DFD Modeling",
                    "What is the primary purpose of a Data Flow Diagram (DFD)?", 1.0,
                    "A DFD illustrates how data enters, moves through, is processed, and is stored inside a system.",
                    [("To show the system architecture", 0), ("To show the user interface", 0), ("To show how data moves through system", 1), ("To show hardware components", 0)],
                ),
                (
                    1, "Software Specification & Design", "Requirements Engineering",
                    "What does a functional requirement describe?", 1.0,
                    "Functional requirements define what specific behavior or function the system must perform.",
                    [("How fast the system loads", 0), ("A specific behavior or function the system must perform.", 1), ("The server hardware specification", 0), ("The color palette of the UI", 0)],
                ),
                (
                    2, "Relational Database System", "SQL Constraints",
                    "Which SQL constraint uniquely identifies each record in a table?", 1.0,
                    "PRIMARY KEY uniquely identifies each row and implicitly enforces NOT NULL and UNIQUE.",
                    [("FOREIGN KEY", 0), ("PRIMARY KEY", 1), ("CHECK", 0), ("DEFAULT", 0)],
                ),
                (
                    2, "Relational Database System", "Normalization",
                    "Which normal form eliminates transitive dependencies?", 1.0,
                    "Third Normal Form (3NF) requires 2NF and removes transitive dependencies on the primary key.",
                    [("1NF", 0), ("2NF", 0), ("3NF", 1), ("UNF", 0)],
                ),
                (
                    3, "OOP C++", "OOP Pillars",
                    "Which OOP principle hides internal object state using private attributes?", 1.0,
                    "Encapsulation bundles data and methods while restricting direct external access.",
                    [("Polymorphism", 0), ("Inheritance", 0), ("Encapsulation", 1), ("Overloading", 0)],
                ),
                (
                    3, "OOP C++", "C++ Memory",
                    "Which operator dynamically allocates memory on the heap in C++?", 1.0,
                    "The 'new' operator allocates memory dynamically on the free store (heap).",
                    [("malloc", 0), ("alloc", 0), ("new", 1), ("create", 0)],
                ),
            ]

            for quiz_id, subj, topic, content, pts, expl, opts in questions_data:
                cursor.execute(
                    """INSERT INTO QUESTION (quizID, subject, topic, content, points, explanation)
                       VALUES (?, ?, ?, ?, ?, ?);""",
                    (quiz_id, subj, topic, content, pts, expl),
                )
                q_id = cursor.lastrowid
                cursor.execute("INSERT INTO QUIZ_QUESTION (quizID, questionID) VALUES (?, ?);", (quiz_id, q_id))
                for opt_text, is_corr in opts:
                    cursor.execute(
                        "INSERT INTO OPTION (questionID, option_text, is_correct) VALUES (?, ?, ?);",
                        (q_id, opt_text, is_corr),
                    )

            # Seed 1 completed attempt for ST-01 on Quiz 3 ("Basic Quiz") so SCR-01 shows "Completed" card
            start_dt = (datetime.now() - timedelta(minutes=20)).isoformat()
            sub_dt = datetime.now().isoformat()
            cursor.execute(
                """INSERT INTO ATTEMPT (userID, quizID, startTime, submitTime, totalScore, isPassed, status)
                   VALUES (1, 3, ?, ?, 10.0, 1, 'Submitted');""",
                (start_dt, sub_dt),
            )
            att_id = cursor.lastrowid
            cursor.execute("SELECT questionID FROM QUIZ_QUESTION WHERE quizID = 3;")
            for row in cursor.fetchall():
                qid = row["questionID"]
                cursor.execute("SELECT optionID FROM OPTION WHERE questionID = ? AND is_correct = 1;", (qid,))
                corr_opt = cursor.fetchone()["optionID"]
                cursor.execute(
                    """INSERT INTO ATTEMPT_DETAIL (attemptID, questionID, selectedOptionID, isFlagged, isCorrect)
                       VALUES (?, ?, ?, 0, 1);""",
                    (att_id, qid, corr_opt),
                )

            conn.commit()
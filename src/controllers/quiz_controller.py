import csv
from typing import Dict, List, Optional, Tuple
import openpyxl
from src.database.db_init import DatabaseManager
from src.models.entities import Option, Question, Quiz


class QuizController:
    def __init__(self, db: DatabaseManager):
        self.db = db

    def get_subjects(self) -> List[str]:
        with self.db.get_connection() as conn:
            cur = conn.cursor()
            cur.execute("SELECT DISTINCT subject FROM QUESTION ORDER BY subject ASC;")
            subjects = [r["subject"] for r in cur.fetchall()]
        if "Software Specification & Design" not in subjects:
            subjects.insert(0, "Software Specification & Design")
        return subjects

    def get_student_quizzes(self, user_id: int, keyword: str = "", status_filter: str = "All") -> List[Dict]:
        """UC-02: View Dashboard & Search Quizzes with Active / Completed status."""
        kw = (keyword or "").strip().lower()
        with self.db.get_connection() as conn:
            cur = conn.cursor()
            cur.execute("SELECT * FROM QUIZ WHERE isPublished = 1 ORDER BY quizID ASC;")
            quiz_rows = cur.fetchall()

            results = []
            for q in quiz_rows:
                qid = q["quizID"]
                cur.execute("SELECT COUNT(*) FROM QUIZ_QUESTION WHERE quizID = ?;", (qid,))
                q_count = cur.fetchone()[0]

                cur.execute(
                    """SELECT attemptID, totalScore, isPassed FROM ATTEMPT
                       WHERE userID = ? AND quizID = ? AND status = 'Submitted'
                       ORDER BY attemptID DESC LIMIT 1;""",
                    (user_id, qid),
                )
                att = cur.fetchone()
                is_completed = att is not None
                state = "Completed" if is_completed else "Active"

                if status_filter != "All" and state != status_filter:
                    continue
                if kw and (kw not in q["title"].lower() and kw not in q["subject"].lower() and kw not in (q["classAssignment"] or "").lower()):
                    continue

                results.append({
                    "quizID": qid,
                    "title": q["title"],
                    "subject": q["subject"],
                    "durationMins": q["durationMins"],
                    "passScore": q["passScore"],
                    "classAssignment": q["classAssignment"],
                    "accessCode": q["accessCode"],
                    "questionCount": q_count,
                    "status": state,
                    "lastAttemptID": att["attemptID"] if att else None,
                    "lastScore": att["totalScore"] if att else None,
                })
        return results

    def list_questions(self, subject: str = "All", keyword: str = "") -> List[Question]:
        """UC-07: Search & filter Question Bank."""
        kw = f"%{(keyword or '').strip()}%"
        with self.db.get_connection() as conn:
            cur = conn.cursor()
            if subject and subject != "All":
                cur.execute(
                    """SELECT * FROM QUESTION
                       WHERE subject = ? AND (content LIKE ? OR topic LIKE ?)
                       ORDER BY questionID ASC;""",
                    (subject, kw, kw),
                )
            else:
                cur.execute(
                    """SELECT * FROM QUESTION
                       WHERE content LIKE ? OR topic LIKE ? OR subject LIKE ?
                       ORDER BY questionID ASC;""",
                    (kw, kw, kw),
                )
            q_rows = cur.fetchall()

            questions: List[Question] = []
            for r in q_rows:
                cur.execute("SELECT * FROM OPTION WHERE questionID = ? ORDER BY optionID ASC;", (r["questionID"],))
                opts = [
                    Option(o["optionID"], o["questionID"], o["option_text"], bool(o["is_correct"]))
                    for o in cur.fetchall()
                ]
                questions.append(
                    Question(
                        question_id=r["questionID"],
                        subject=r["subject"],
                        topic=r["topic"],
                        content=r["content"],
                        points=r["points"],
                        explanation=r["explanation"] or "",
                        options=opts,
                    )
                )
        return questions

    def add_question(
        self,
        subject: str,
        topic: str,
        content: str,
        options_list: List[str],
        correct_index: int,
        points: float = 1.0,
        explanation: str = "",
    ) -> Tuple[bool, str]:
        """UC-07: Add a new question with 4 choices and correct answer key."""
        content = (content or "").strip()
        if not content:
            return False, "Question content cannot be empty."
        cleaned_opts = [o.strip() for o in options_list if o and o.strip()]
        if len(cleaned_opts) < 2:
            return False, "At least 2 non-empty options are required."
        if correct_index < 0 or correct_index >= len(cleaned_opts):
            return False, "Please select a valid correct option."

        q_obj = Question(0, subject or "General", topic or "General", content, points, explanation)
        for idx, text in enumerate(cleaned_opts):
            q_obj.addOption(Option(idx + 1, 0, text, idx == correct_index))
        if not q_obj.validateQuestion():
            return False, "Question validation failed."

        with self.db.get_connection() as conn:
            cur = conn.cursor()
            cur.execute(
                """INSERT INTO QUESTION (subject, topic, content, points, explanation)
                   VALUES (?, ?, ?, ?, ?);""",
                (q_obj.subject, q_obj.topic, q_obj.content, q_obj.points, q_obj.explanation),
            )
            qid = cur.lastrowid
            for idx, text in enumerate(cleaned_opts):
                cur.execute(
                    "INSERT INTO OPTION (questionID, option_text, is_correct) VALUES (?, ?, ?);",
                    (qid, text, 1 if idx == correct_index else 0),
                )
            conn.commit()
        return True, f"Question Q_{qid:03d} added successfully."

    def update_question(
        self,
        question_id: int,
        subject: str,
        topic: str,
        content: str,
        options_list: List[str],
        correct_index: int,
        explanation: str = "",
    ) -> Tuple[bool, str]:
        """UC-07: Edit existing question."""
        if not content.strip() or len([o for o in options_list if o.strip()]) < 2:
            return False, "Question content and at least 2 options are required."
        with self.db.get_connection() as conn:
            cur = conn.cursor()
            cur.execute(
                "UPDATE QUESTION SET subject = ?, topic = ?, content = ?, explanation = ? WHERE questionID = ?;",
                (subject.strip(), topic.strip(), content.strip(), explanation.strip(), question_id),
            )
            cur.execute("DELETE FROM OPTION WHERE questionID = ?;", (question_id,))
            for idx, text in enumerate(options_list):
                if text.strip():
                    cur.execute(
                        "INSERT INTO OPTION (questionID, option_text, is_correct) VALUES (?, ?, ?);",
                        (question_id, text.strip(), 1 if idx == correct_index else 0),
                    )
            conn.commit()
        return True, f"Question Q_{question_id:03d} updated."

    def delete_questions(self, question_ids: List[int]) -> Tuple[bool, str]:
        """UC-07: Batch delete questions."""
        if not question_ids:
            return False, "No questions selected."
        with self.db.get_connection() as conn:
            for qid in question_ids:
                conn.execute("DELETE FROM QUESTION WHERE questionID = ?;", (qid,))
            conn.commit()
        return True, f"Deleted {len(question_ids)} question(s)."

    def import_questions_from_file(self, file_path: str) -> Tuple[bool, str]:
        """UC-07 & NFR-07: Import questions from Excel (.xlsx) or UTF-8 CSV."""
        imported = 0
        try:
            rows = []
            if file_path.lower().endswith(".xlsx"):
                wb = openpyxl.load_workbook(file_path, data_only=True)
                sheet = wb.active
                for idx, r in enumerate(sheet.iter_rows(values_only=True)):
                    if idx == 0:
                        continue
                    rows.append(list(r))
            else:
                with open(file_path, mode="r", encoding="utf-8-sig") as f:
                    reader = csv.reader(f)
                    next(reader, None)
                    rows = list(reader)

            letter_map = {"A": 0, "B": 1, "C": 2, "D": 3}
            for r in rows:
                if not r or len(r) < 7 or not r[2]:
                    continue
                subj = str(r[0] or "General").strip()
                topic = str(r[1] or "Imported").strip()
                content = str(r[2]).strip()
                opts = [str(r[3] or "").strip(), str(r[4] or "").strip(), str(r[5] or "").strip(), str(r[6] or "").strip()]
                corr_raw = str(r[7] if len(r) > 7 else "A").strip().upper()
                corr_idx = letter_map.get(corr_raw[-1:] if corr_raw else "A", 0)
                expl = str(r[8]).strip() if len(r) > 8 and r[8] else ""
                ok, _ = self.add_question(subj, topic, content, opts, corr_idx, 1.0, expl)
                if ok:
                    imported += 1
            return True, f"Successfully imported {imported} question(s)."
        except Exception as exc:
            return False, f"Import failed: {exc}"

    def create_and_configure_quiz(
        self,
        title: str,
        subject: str,
        duration_mins: int,
        pass_score: float,
        class_assignment: str,
        access_code: str,
        shuffle_questions: bool,
        shuffle_options: bool,
        review_rules: bool,
        is_published: bool,
        question_ids: List[int],
        created_by: int,
    ) -> Tuple[bool, str, Optional[Quiz]]:
        """UC-08 & UC-09: Create & Configure Quiz + Advanced Rules."""
        title = (title or "").strip()
        if not title:
            return False, "Quiz Title is required.", None
        if duration_mins <= 0:
            return False, "Time Limit must be greater than 0 minutes.", None
        if pass_score < 0 or pass_score > 100:
            return False, "Passing Score must be between 0 and 100%.", None
        if not question_ids:
            return False, "Please attach at least 1 question from the Question Bank.", None

        quiz_obj = Quiz(
            quiz_id=0,
            title=title,
            duration_mins=duration_mins,
            pass_score=pass_score,
            class_assignment=class_assignment or "Class SE-01",
            access_code=(access_code or "").strip(),
            shuffle_questions=shuffle_questions,
            shuffle_options=shuffle_options,
            review_rules=review_rules,
            is_published=is_published,
            subject=subject or "Software Specification & Design",
        )
        quiz_obj.configureRules(shuffle_questions, shuffle_options, review_rules)
        if is_published:
            quiz_obj.publishQuiz()

        with self.db.get_connection() as conn:
            cur = conn.cursor()
            cur.execute(
                """INSERT INTO QUIZ (title, subject, durationMins, passScore, classAssignment, accessCode,
                   shuffleQuestions, shuffleOptions, reviewRules, isPublished, created_by)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);""",
                (
                    quiz_obj.title,
                    quiz_obj.subject,
                    quiz_obj.durationMins,
                    quiz_obj.passScore,
                    quiz_obj.classAssignment,
                    quiz_obj.accessCode,
                    int(quiz_obj.shuffleQuestions),
                    int(quiz_obj.shuffleOptions),
                    int(quiz_obj.reviewRules),
                    int(quiz_obj.isPublished),
                    created_by,
                ),
            )
            new_qid = cur.lastrowid
            for question_id in question_ids:
                cur.execute(
                    "INSERT OR IGNORE INTO QUIZ_QUESTION (quizID, questionID) VALUES (?, ?);",
                    (new_qid, question_id),
                )
            conn.commit()

        status_text = "published" if is_published else "saved as draft"
        return True, f"Quiz '{title}' {status_text} with {len(question_ids)} question(s).", quiz_obj

    def list_all_quizzes(self) -> List[Dict]:
        with self.db.get_connection() as conn:
            cur = conn.cursor()
            cur.execute("SELECT * FROM QUIZ ORDER BY quizID ASC;")
            return [dict(r) for r in cur.fetchall()]

    def get_gradebook_and_analytics(self, quiz_id: int) -> Tuple[List[Dict], Dict]:
        """UC-10: View Gradebook & Analytics."""
        with self.db.get_connection() as conn:
            cur = conn.cursor()
            cur.execute(
                """SELECT a.attemptID, u.username, u.full_name, u.email, a.startTime, a.submitTime,
                          a.totalScore, a.isPassed
                   FROM ATTEMPT a
                   JOIN USER u ON a.userID = u.userID
                   WHERE a.quizID = ? AND a.status = 'Submitted'
                   ORDER BY a.totalScore DESC, a.attemptID ASC;""",
                (quiz_id,),
            )
            rows = [dict(r) for r in cur.fetchall()]

        if not rows:
            return [], {
                "count": 0,
                "avgScore": 0.0,
                "maxScore": 0.0,
                "minScore": 0.0,
                "passRate": 0.0,
            }

        scores = [r["totalScore"] for r in rows]
        passed_count = sum(1 for r in rows if r["isPassed"])
        stats = {
            "count": len(rows),
            "avgScore": round(sum(scores) / len(scores), 2),
            "maxScore": max(scores),
            "minScore": min(scores),
            "passRate": round((passed_count / len(rows)) * 100.0, 1),
        }
        return rows, stats

    def export_gradebook_csv(self, quiz_id: int, file_path: str) -> Tuple[bool, str]:
        """FR-AD-05 & NFR-07: Export UTF-8 CSV gradebook report."""
        records, stats = self.get_gradebook_and_analytics(quiz_id)
        if not records:
            return False, "No results available for the selected quiz."
        try:
            with open(file_path, mode="w", newline="", encoding="utf-8-sig") as f:
                writer = csv.writer(f)
                writer.writerow(["Attempt ID", "Student ID", "Full Name", "Email", "Score (/10)", "Status", "Submitted At"])
                for r in records:
                    writer.writerow([
                        r["attemptID"],
                        r["username"],
                        r["full_name"],
                        r["email"],
                        r["totalScore"],
                        "PASSED" if r["isPassed"] else "FAILED",
                        r["submitTime"] or "",
                    ])
                writer.writerow([])
                writer.writerow(["Summary", f"Total: {stats['count']}", f"Avg: {stats['avgScore']}", f"Max: {stats['maxScore']}", f"Min: {stats['minScore']}", f"Pass Rate: {stats['passRate']}%"])
            return True, f"Exported {len(records)} result(s) to CSV."
        except Exception as exc:
            return False, f"CSV export failed: {exc}"
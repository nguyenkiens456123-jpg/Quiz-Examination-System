import random
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from src.database.db_init import DatabaseManager
from src.models.entities import Attempt, AttemptDetail, Option, Question, Quiz


class ExamController:
    def __init__(self, db: DatabaseManager):
        self.db = db

    def load_quiz_with_questions(self, quiz_id: int) -> Optional[Quiz]:
        with self.db.get_connection() as conn:
            cur = conn.cursor()
            cur.execute("SELECT * FROM QUIZ WHERE quizID = ?;", (quiz_id,))
            q_row = cur.fetchone()
            if not q_row:
                return None

            cur.execute(
                """SELECT q.* FROM QUESTION q
                   JOIN QUIZ_QUESTION qq ON q.questionID = qq.questionID
                   WHERE qq.quizID = ?
                   ORDER BY q.questionID ASC;""",
                (quiz_id,),
            )
            question_rows = cur.fetchall()

            questions: List[Question] = []
            for qr in question_rows:
                cur.execute("SELECT * FROM OPTION WHERE questionID = ? ORDER BY optionID ASC;", (qr["questionID"],))
                opts = [
                    Option(o["optionID"], o["questionID"], o["option_text"], bool(o["is_correct"]))
                    for o in cur.fetchall()
                ]
                if q_row["shuffleOptions"]:
                    random.shuffle(opts)
                questions.append(
                    Question(
                        question_id=qr["questionID"],
                        subject=qr["subject"],
                        topic=qr["topic"],
                        content=qr["content"],
                        points=qr["points"],
                        explanation=qr["explanation"] or "",
                        options=opts,
                    )
                )

            if q_row["shuffleQuestions"]:
                random.shuffle(questions)

            return Quiz(
                quiz_id=q_row["quizID"],
                title=q_row["title"],
                duration_mins=q_row["durationMins"],
                pass_score=q_row["passScore"],
                class_assignment=q_row["classAssignment"] or "",
                access_code=q_row["accessCode"] or "",
                shuffle_questions=bool(q_row["shuffleQuestions"]),
                shuffle_options=bool(q_row["shuffleOptions"]),
                review_rules=bool(q_row["reviewRules"]),
                is_published=bool(q_row["isPublished"]),
                subject=q_row["subject"],
                questions=questions,
            )

    def start_quiz_attempt(self, user_id: int, quiz_id: int, entered_passcode: str = "") -> Tuple[bool, str, Optional[Attempt], Optional[Quiz]]:
        """DFD 6.1 & UC-03: Validate passcode/eligibility & initialize Attempt."""
        quiz = self.load_quiz_with_questions(quiz_id)
        if not quiz or not quiz.isPublished:
            return False, "Quiz is not available.", None, None

        if quiz.accessCode and quiz.accessCode.strip() != (entered_passcode or "").strip():
            return False, "Invalid exam access code. Please try again.", None, None

        with self.db.get_connection() as conn:
            cur = conn.cursor()
            cur.execute(
                "SELECT attemptID FROM ATTEMPT WHERE userID = ? AND quizID = ? AND status = 'Submitted';",
                (user_id, quiz_id),
            )
            if cur.fetchone():
                return False, "You have already completed this quiz.", None, None

            attempt = Attempt(0, user_id, quiz_id)
            attempt.startAttempt()
            cur.execute(
                """INSERT INTO ATTEMPT (userID, quizID, startTime, status)
                   VALUES (?, ?, ?, 'In_Progress');""",
                (user_id, quiz_id, attempt.startTime.isoformat()),
            )
            att_id = cur.lastrowid

            details: List[AttemptDetail] = []
            for q in quiz.questions:
                cur.execute(
                    """INSERT INTO ATTEMPT_DETAIL (attemptID, questionID, selectedOptionID, isFlagged, isCorrect)
                       VALUES (?, ?, NULL, 0, 0);""",
                    (att_id, q.questionID),
                )
                details.append(AttemptDetail(cur.lastrowid, att_id, q.questionID))
            conn.commit()

        final_attempt = Attempt(att_id, user_id, quiz_id, attempt.startTime)
        final_attempt.details.extend(details)
        return True, "Attempt started.", final_attempt, quiz

    def save_selection(self, attempt_id: int, question_id: int, selected_option_id: Optional[int]) -> None:
        """UC-04: Record answer choice."""
        with self.db.get_connection() as conn:
            conn.execute(
                """UPDATE ATTEMPT_DETAIL
                   SET selectedOptionID = ?
                   WHERE attemptID = ? AND questionID = ?;""",
                (selected_option_id, attempt_id, question_id),
            )
            conn.commit()

    def toggle_flag(self, attempt_id: int, question_id: int) -> bool:
        """UC-04: Toggle Flag for Review state."""
        with self.db.get_connection() as conn:
            cur = conn.cursor()
            cur.execute(
                "SELECT isFlagged FROM ATTEMPT_DETAIL WHERE attemptID = ? AND questionID = ?;",
                (attempt_id, question_id),
            )
            row = cur.fetchone()
            new_flag = 0 if (row and row["isFlagged"]) else 1
            cur.execute(
                "UPDATE ATTEMPT_DETAIL SET isFlagged = ? WHERE attemptID = ? AND questionID = ?;",
                (new_flag, attempt_id, question_id),
            )
            conn.commit()
        return bool(new_flag)

    def auto_save_progress(self, attempt_id: int, answers_map: Dict[int, Optional[int]], flags_map: Dict[int, bool]) -> Tuple[bool, str]:
        """DFD 6.3 & UC-05: Periodic 10-second Auto-Save persistence."""
        try:
            with self.db.get_connection() as conn:
                for qid, opt_id in answers_map.items():
                    flagged = 1 if flags_map.get(qid, False) else 0
                    conn.execute(
                        """UPDATE ATTEMPT_DETAIL
                           SET selectedOptionID = ?, isFlagged = ?
                           WHERE attemptID = ? AND questionID = ?;""",
                        (opt_id, flagged, attempt_id, qid),
                    )
                conn.commit()
            return True, "Auto-saved 10s ago"
        except Exception:
            return False, "Connection lost. Retrying..."

    def submit_and_grade(self, attempt_id: int) -> Tuple[bool, Dict]:
        """DFD 6.4, 6.5 & UC-03: Lock attempt, compute score, and write result."""
        with self.db.get_connection() as conn:
            cur = conn.cursor()
            cur.execute("SELECT * FROM ATTEMPT WHERE attemptID = ?;", (attempt_id,))
            att_row = cur.fetchone()
            if not att_row:
                return False, {}

            quiz = self.load_quiz_with_questions(att_row["quizID"])
            if not quiz:
                return False, {}

            attempt = Attempt(
                attempt_id=att_row["attemptID"],
                user_id=att_row["userID"],
                quiz_id=att_row["quizID"],
                start_time=datetime.fromisoformat(att_row["startTime"]),
            )

            cur.execute("SELECT * FROM ATTEMPT_DETAIL WHERE attemptID = ?;", (attempt_id,))
            for d in cur.fetchall():
                attempt.details.append(
                    AttemptDetail(
                        detail_id=d["detailID"],
                        attempt_id=d["attemptID"],
                        question_id=d["questionID"],
                        selected_option_id=d["selectedOptionID"],
                        is_flagged=bool(d["isFlagged"]),
                        is_correct=bool(d["isCorrect"]),
                    )
                )

            final_score = attempt.submitAttempt(quiz.questions, quiz.passScore)

            for d in attempt.details:
                cur.execute(
                    "UPDATE ATTEMPT_DETAIL SET isCorrect = ? WHERE detailID = ?;",
                    (1 if d.isCorrect else 0, d.detailID),
                )

            cur.execute(
                """UPDATE ATTEMPT
                   SET submitTime = ?, totalScore = ?, isPassed = ?, status = 'Submitted'
                   WHERE attemptID = ?;""",
                (attempt.submitTime.isoformat(), final_score, 1 if attempt.isPassed else 0, attempt_id),
            )
            conn.commit()

        return True, self.get_attempt_breakdown(attempt_id)

    def get_attempt_breakdown(self, attempt_id: int) -> Dict:
        """UC-06: Result & Itemized Breakdown View respecting quiz.reviewRules."""
        with self.db.get_connection() as conn:
            cur = conn.cursor()
            cur.execute(
                """SELECT a.*, q.title, q.durationMins, q.passScore, q.reviewRules
                   FROM ATTEMPT a JOIN QUIZ q ON a.quizID = q.quizID
                   WHERE a.attemptID = ?;""",
                (attempt_id,),
            )
            row = cur.fetchone()
            if not row:
                return {}

            start_dt = datetime.fromisoformat(row["startTime"])
            sub_dt = datetime.fromisoformat(row["submitTime"]) if row["submitTime"] else datetime.now()
            elapsed_secs = max(1, int((sub_dt - start_dt).total_seconds()))
            mins, secs = divmod(elapsed_secs, 60)

            cur.execute(
                """SELECT ad.*, q.content, q.points, q.explanation
                   FROM ATTEMPT_DETAIL ad JOIN QUESTION q ON ad.questionID = q.questionID
                   WHERE ad.attemptID = ?
                   ORDER BY ad.detailID ASC;""",
                (attempt_id,),
            )
            detail_rows = cur.fetchall()

            breakdown_items = []
            correct_count = 0
            for dr in detail_rows:
                cur.execute("SELECT * FROM OPTION WHERE questionID = ? ORDER BY optionID ASC;", (dr["questionID"],))
                opts = cur.fetchall()
                selected_text = "Not answered"
                correct_text = ""
                for idx, o in enumerate(opts):
                    prefix = chr(65 + idx)
                    if o["optionID"] == dr["selectedOptionID"]:
                        selected_text = f"{prefix}. {o['option_text']}"
                    if o["is_correct"]:
                        correct_text = f"{prefix}. {o['option_text']}"

                if dr["isCorrect"]:
                    correct_count += 1

                breakdown_items.append({
                    "questionID": dr["questionID"],
                    "content": dr["content"],
                    "selectedText": selected_text,
                    "correctText": correct_text,
                    "isCorrect": bool(dr["isCorrect"]),
                    "explanation": dr["explanation"] or "No additional feedback.",
                })

        return {
            "attemptID": attempt_id,
            "quizTitle": row["title"],
            "totalScore": row["totalScore"],
            "passScore": row["passScore"],
            "isPassed": bool(row["isPassed"]),
            "correctCount": correct_count,
            "totalQuestions": len(breakdown_items),
            "timeElapsed": f"{mins:02d}:{secs:02d}",
            "durationMins": row["durationMins"],
            "reviewRules": bool(row["reviewRules"]),
            "items": breakdown_items,
        }
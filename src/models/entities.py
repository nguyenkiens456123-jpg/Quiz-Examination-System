from datetime import datetime
from typing import List, Optional
import bcrypt


class Option:
    def __init__(self, option_id: int, question_id: int, option_text: str, is_correct: bool = False):
        self.__optionID: int = option_id
        self.__questionID: int = question_id
        self.__optionText: str = option_text
        self.__isCorrect: bool = bool(is_correct)

    @property
    def optionID(self) -> int:
        return self.__optionID

    @property
    def questionID(self) -> int:
        return self.__questionID

    @property
    def optionText(self) -> str:
        return self.__optionText

    @property
    def isCorrect(self) -> bool:
        return self.__isCorrect

    def getOptionDetails(self) -> str:
        status = " [CORRECT]" if self.__isCorrect else ""
        return f"Option #{self.__optionID}: {self.__optionText}{status}"


class Question:
    def __init__(
        self,
        question_id: int,
        subject: str,
        topic: str,
        content: str,
        points: float = 1.0,
        explanation: str = "",
        options: Optional[List[Option]] = None,
    ):
        self.__questionID: int = question_id
        self.__subject: str = subject
        self.__topic: str = topic
        self.__content: str = content
        self.__points: float = float(points)
        self.__explanation: str = explanation
        self.__options: List[Option] = options if options is not None else []

    @property
    def questionID(self) -> int:
        return self.__questionID

    @property
    def subject(self) -> str:
        return self.__subject

    @property
    def topic(self) -> str:
        return self.__topic

    @property
    def content(self) -> str:
        return self.__content

    @property
    def points(self) -> float:
        return self.__points

    @property
    def explanation(self) -> str:
        return self.__explanation

    @property
    def options(self) -> List[Option]:
        return self.__options

    def addOption(self, option: Option) -> None:
        self.__options.append(option)

    def validateQuestion(self) -> bool:
        if not self.__content or not self.__content.strip():
            return False
        if len(self.__options) < 2:
            return False
        return any(opt.isCorrect for opt in self.__options)


class User:
    def __init__(
        self,
        user_id: int,
        username: str,
        password_hash: str,
        fullname: str,
        email: str,
        role: str = "student",
        status: str = "active",
    ):
        self.__userID: int = user_id
        self.__username: str = username
        self.__password: str = password_hash
        self.__fullname: str = fullname
        self.__email: str = email
        self.__role: str = role.lower()
        self.__status: str = status.lower()
        self.__is_authenticated: bool = False

    @property
    def userID(self) -> int:
        return self.__userID

    @property
    def username(self) -> str:
        return self.__username

    @property
    def fullname(self) -> str:
        return self.__fullname

    @property
    def email(self) -> str:
        return self.__email

    @property
    def role(self) -> str:
        return self.__role

    @property
    def status(self) -> str:
        return self.__status

    def login(self, plain_password: str) -> bool:
        if self.__status != "active":
            return False
        try:
            valid = bcrypt.checkpw(plain_password.encode("utf-8"), self.__password.encode("utf-8"))
        except Exception:
            valid = (plain_password == self.__password)
        self.__is_authenticated = valid
        return valid

    def logout(self) -> None:
        self.__is_authenticated = False

    def updateProfile(self, fullname: str, email: str) -> None:
        if fullname.strip():
            self.__fullname = fullname.strip()
        if email.strip():
            self.__email = email.strip()


class Quiz:
    def __init__(
        self,
        quiz_id: int,
        title: str,
        duration_mins: int,
        pass_score: float,
        class_assignment: str = "Class SE-01",
        access_code: str = "",
        shuffle_questions: bool = False,
        shuffle_options: bool = False,
        review_rules: bool = True,
        is_published: bool = False,
        subject: str = "Software Specification & Design",
        questions: Optional[List[Question]] = None,
    ):
        self.__quizID: int = quiz_id
        self.__title: str = title
        self.__durationMins: int = int(duration_mins)
        self.__passScore: float = float(pass_score)
        self.__classAssignment: str = class_assignment
        self.__accessCode: str = access_code or ""
        self.__shuffleQuestions: bool = bool(shuffle_questions)
        self.__shuffleOptions: bool = bool(shuffle_options)
        self.__reviewRules: bool = bool(review_rules)
        self.__isPublished: bool = bool(is_published)
        self.__subject: str = subject
        self.__questions: List[Question] = questions if questions is not None else []

    @property
    def quizID(self) -> int:
        return self.__quizID

    @property
    def title(self) -> str:
        return self.__title

    @property
    def durationMins(self) -> int:
        return self.__durationMins

    @property
    def passScore(self) -> float:
        return self.__passScore

    @property
    def classAssignment(self) -> str:
        return self.__classAssignment

    @property
    def accessCode(self) -> str:
        return self.__accessCode

    @property
    def shuffleQuestions(self) -> bool:
        return self.__shuffleQuestions

    @property
    def shuffleOptions(self) -> bool:
        return self.__shuffleOptions

    @property
    def reviewRules(self) -> bool:
        return self.__reviewRules

    @property
    def isPublished(self) -> bool:
        return self.__isPublished

    @property
    def subject(self) -> str:
        return self.__subject

    @property
    def questions(self) -> List[Question]:
        return self.__questions

    def createQuiz(self, title: str, duration_mins: int, pass_score: float) -> None:
        self.__title = title
        self.__durationMins = duration_mins
        self.__passScore = pass_score

    def publishQuiz(self) -> None:
        self.__isPublished = True

    def assignClass(self, class_name: str) -> None:
        self.__classAssignment = class_name

    def configureRules(self, shuffle_q: bool, shuffle_o: bool, review_rules: bool) -> None:
        self.__shuffleQuestions = bool(shuffle_q)
        self.__shuffleOptions = bool(shuffle_o)
        self.__reviewRules = bool(review_rules)


class AttemptDetail:
    def __init__(
        self,
        detail_id: int,
        attempt_id: int,
        question_id: int,
        selected_option_id: Optional[int] = None,
        is_flagged: bool = False,
        is_correct: bool = False,
    ):
        self.__detailID: int = detail_id
        self.__attemptID: int = attempt_id
        self.__questionID: int = question_id
        self.__selectedOptionID: Optional[int] = selected_option_id
        self.__isFlagged: bool = bool(is_flagged)
        self.__isCorrect: bool = bool(is_correct)

    @property
    def detailID(self) -> int:
        return self.__detailID

    @property
    def attemptID(self) -> int:
        return self.__attemptID

    @property
    def questionID(self) -> int:
        return self.__questionID

    @property
    def selectedOptionID(self) -> Optional[int]:
        return self.__selectedOptionID

    @property
    def isFlagged(self) -> bool:
        return self.__isFlagged

    @property
    def isCorrect(self) -> bool:
        return self.__isCorrect

    def saveSelection(self, option_id: Optional[int], is_correct: bool = False) -> None:
        self.__selectedOptionID = option_id
        self.__isCorrect = bool(is_correct)

    def toggleFlag(self) -> bool:
        self.__isFlagged = not self.__isFlagged
        return self.__isFlagged


class Attempt:
    def __init__(
        self,
        attempt_id: int,
        user_id: int,
        quiz_id: int,
        start_time: Optional[datetime] = None,
        submit_time: Optional[datetime] = None,
        total_score: float = 0.0,
        is_passed: bool = False,
        status: str = "In_Progress",
    ):
        self.__attemptID: int = attempt_id
        self.__userID: int = user_id
        self.__quizID: int = quiz_id
        self.__startTime: datetime = start_time or datetime.now()
        self.__submitTime: Optional[datetime] = submit_time
        self.__totalScore: float = float(total_score)
        self.__isPassed: bool = bool(is_passed)
        self.__status: str = status
        self.__details: List[AttemptDetail] = []

    @property
    def attemptID(self) -> int:
        return self.__attemptID

    @property
    def userID(self) -> int:
        return self.__userID

    @property
    def quizID(self) -> int:
        return self.__quizID

    @property
    def startTime(self) -> datetime:
        return self.__startTime

    @property
    def submitTime(self) -> Optional[datetime]:
        return self.__submitTime

    @property
    def totalScore(self) -> float:
        return self.__totalScore

    @property
    def isPassed(self) -> bool:
        return self.__isPassed

    @property
    def status(self) -> str:
        return self.__status

    @property
    def details(self) -> List[AttemptDetail]:
        return self.__details

    def startAttempt(self) -> None:
        self.__startTime = datetime.now()
        self.__status = "In_Progress"

    def autoSave(self) -> str:
        return f"Auto-saved at {datetime.now().strftime('%H:%M:%S')}"

    def submitAttempt(self, questions: List[Question], pass_score_percent: float) -> float:
        self.__submitTime = datetime.now()
        self.__status = "Submitted"
        return self.calculateScore(questions, pass_score_percent)

    def calculateScore(self, questions: List[Question], pass_score_percent: float) -> float:
        total_max_points = sum(q.points for q in questions)
        if total_max_points <= 0:
            self.__totalScore = 0.0
            self.__isPassed = False
            return 0.0

        earned_points = 0.0
        detail_map = {d.questionID: d for d in self.__details}
        for q in questions:
            detail = detail_map.get(q.questionID)
            if detail and detail.selectedOptionID is not None:
                correct_opt_ids = {o.optionID for o in q.options if o.isCorrect}
                is_right = detail.selectedOptionID in correct_opt_ids
                detail.saveSelection(detail.selectedOptionID, is_right)
                if is_right:
                    earned_points += q.points

        percentage = (earned_points / total_max_points) * 100.0
        self.__totalScore = round((earned_points / total_max_points) * 10.0, 2)
        self.__isPassed = percentage >= pass_score_percent
        return self.__totalScore
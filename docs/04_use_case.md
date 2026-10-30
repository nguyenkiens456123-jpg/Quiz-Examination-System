# Use Case Specification

## 1. Use Case Diagram

![Use Case Diagram](<Task 4 User Case.png>)

---

## 2. Detailed Use Case Specifications

### 2.1. Student Module

#### 2.1.1. Use case Register / Log in (UC-ST-01)
* **Actor(s):** Student
* **Summary:** This use case allows a student to register a new account and to log in to access the student features.

**Main flow:**
1. The use case starts when the Student selects the Register function.
2. The system displays the registration form (full name, e-mail, password).
3. The Student fills in the form and submits it.
4. The system validates the data (required fields, e-mail format, unique e-mail, password policy).
5. The system creates the account with role Student and stores the hashed password.
6. The system displays a success message and redirects to the Login page.
7. The Student enters e-mail and password and submits the login form.
8. The system verifies the credentials against the stored password hash.
9. The system creates a session and redirects the Student to the Quiz Dashboard.

* **Alternative flows:**
  * **Invalid data:** the system highlights the wrong fields and returns to step 3.
  * **E-mail already registered:** the system shows the message "E-mail is already in use" and returns to step 3.
  * **Wrong e-mail or password:** the system shows a generic error message and the Student re-enters the credentials.
* **Special requirements:** Passwords are stored as salted hashes and are never stored in plain text; the e-mail address must be unique; the login error message does not reveal whether the e-mail or the password is wrong.
* **System state before:** For registration, the e-mail is not yet registered. For login, the Student has an existing account.
* **System state after:** A new Student account exists (registration), and/or the Student is authenticated with an active session (login).
* **Extension points:** None.

#### 2.1.2. Use case View quiz dashboard (UC-ST-02)
* **Actor(s):** Student
* **Summary:** This use case allows a Student to see the list of quizzes that are available to take.

**Main flow:**
1. The use case starts when the Student logs in successfully or selects Dashboard.
2. The system retrieves all quizzes whose availability status is Available.
3. The system displays each quiz with its title, category, duration (minutes) and total number of questions.
4. The Student selects a quiz and chooses Start; the system executes use case Attempt quiz with timer.

* **Alternative flows:**
  * **No quiz available:** the system displays the message "No quizzes are available at the moment".
  * **Search/Filter:** The Student filters or searches quizzes by title or category (if implemented): the system refreshes the list with the matching quizzes.
* **Special requirements:** Only quizzes that are Available and contain at least one question are displayed.
* **System state before:** The Student is logged in.
* **System state after:** The list of available quizzes is displayed; no data is changed.
* **Extension points:** None.

#### 2.1.3. Use case Attempt quiz with timer (UC-ST-03)
* **Actor(s):** Student
* **Summary:** This use case allows a Student to start a quiz attempt with a real-time countdown timer.

**Main flow:**
1. The use case starts when the Student selects Start on a quiz.
2. The system displays the quiz information (duration, number of questions) and asks for confirmation.
3. The Student confirms.
4. The system creates an attempt with status In Progress, records the start time and computes the end time (start time + duration).
5. The system displays the first question and the countdown timer, whose remaining time is calculated from the server clock.
6. The system executes use case Answer and navigate questions while the Student is working.
7. When the Student submits or the timer reaches zero, the system executes use case Auto-submit and score.

* **Alternative flows:**
  * **Cancel confirmation:** The Student cancels at the confirmation step: the system returns to the Quiz Dashboard and no attempt is created.
  * **Page reload or connection lost:** when the Student returns, the system resumes the attempt with the correct remaining time and the previously saved answers.
  * **Quiz unavailable:** The quiz was set to unavailable: the system refuses to start a new attempt; an attempt already in progress may be completed.
* **Special requirements:** The remaining time is always derived from the server timestamps, so refreshing the page or changing the device clock does not change it. The maximum number of attempts per quiz is a configurable rule.
* **System state before:** The Student is logged in and the selected quiz is Available.
* **System state after:** An attempt with status In Progress exists, with its start time and end time recorded.
* **Extension points:** Includes use case Answer and navigate questions.

#### 2.1.4. Use case Answer and navigate questions (UC-ST-04)
* **Actor(s):** Student
* **Summary:** This use case allows a Student to select answers and to move freely between the questions before submitting the quiz.

**Main flow:**
1. The use case starts when the system displays a question of an attempt that is In Progress.
2. The system shows the question text and the options A, B, C and D.
3. The Student selects one option; the system saves the selection immediately.
4. The Student moves to another question with Previous/Next or by selecting a number in the question list.
5. The system shows the status of each question (answered / not answered).
6. The Student repeats steps 3 to 5 until ready, then selects Submit.

* **Alternative flows:**
  * **Change answer:** The Student changes an answer: the system replaces the previous selection.
  * **Clear answer:** The Student clears an answer (if supported): the question becomes not answered.
  * **Unanswered warning:** The Student submits while some questions are unanswered: the system shows a warning; if the Student confirms, the flow continues with use case Auto-submit and score.
  * **Network error:** Saving an answer fails because of a network error: the system shows a warning and retries saving.
* **Special requirements:** Each question accepts exactly one selected option; answers are saved on every change; the correct answers are never sent to the browser before submission.
* **System state before:** The attempt is In Progress and the time has not expired.
* **System state after:** The selected answers are stored in the attempt.
* **Extension points:** None.

#### 2.1.5. Use case Auto-submit and score (UC-ST-05)
* **Actor(s):** Student, Timer (system)
* **Summary:** This use case records the Student's choices, evaluates them against the answer key, calculates the total score and automatically submits the quiz when the countdown timer expires.

**Main flow:**
1. The use case starts when the Student selects Submit and confirms.
2. The system closes the attempt so that answers can no longer be changed.
3. The system loads the Student's answers and the correct options of every question.
4. For each question the system decides whether the answer is correct.
5. The system calculates the number of correct answers and the total score, and compares it with the passing score of the quiz.
6. The system stores the result, sets the attempt status to Submitted and displays the result (use case View result and history).

* **Alternative flows:**
  * **Timeout:** when the countdown timer reaches zero, the system submits the attempt automatically with the saved answers and continues from step 3.
  * **Unanswered question:** counted as incorrect and scores 0.
  * **Duplicate submission:** Duplicate submission (double click, or manual submit at the same moment as the timeout): the system processes only the first one and ignores the others.
* **Special requirements:** Score = (number of correct answers / total number of questions) x maximum score; the attempt passes if the score is greater than or equal to the passing score; grading is idempotent and a submitted attempt is never re-graded.
* **System state before:** The attempt is In Progress.
* **System state after:** The attempt is Submitted and its score and pass/fail result are stored.
* **Extension points:** Extends use case Attempt quiz with timer when the time expires (automatic submission).

#### 2.1.6. Use case View result and history (UC-ST-06)
* **Actor(s):** Student
* **Summary:** This use case allows a Student to view the result of a quiz and the history of his/her attempts, including a performance breakdown.

**Main flow:**
1. The use case starts when an attempt has been graded, or when the Student selects My history.
2. The system displays the instant feedback: score, number of correct and incorrect answers, and the Pass/Fail result.
3. The Student selects My history.
4. The system lists the Student's past attempts with quiz title, date and time, score and result.
5. The Student selects an attempt to view its performance breakdown.
6. The system displays the breakdown: correct, incorrect and unanswered questions, the percentage score, the time spent, and the result of each question (the correct answers are shown if the quiz policy allows).

* **Alternative flows:**
  * **No history:** the system displays the message "You have not taken any quiz yet".
  * **Filter history:** The Student filters the history by quiz or date range: the system shows only the matching attempts.
  * **Multiple attempts:** The Student has several attempts of the same quiz: the system shows them in chronological order so the progress can be compared.
* **Special requirements:** A Student can only view his/her own results. Whether correct answers appear in the breakdown is configurable.
* **System state before:** The Student is logged in; at least one submitted attempt exists (for the history part).
* **System state after:** No data is changed.
* **Extension points:** None.

---

### 2.2. Admin / Teacher Module

#### 2.2.1. Use case Admin login (UC-AD-01)
* **Actor(s):** Admin / Teacher
* **Summary:** This use case allows an administrator or teacher to log in with privileged credentials; the system enforces role-based access control.

**Main flow:**
1. The use case starts when the Admin/Teacher selects the Login function.
2. The system displays the login form.
3. The user enters e-mail and password and submits.
4. The system verifies the credentials against the stored password hash.
5. The system checks that the account role is Admin or Teacher.
6. The system creates a session and redirects the user to the administration dashboard.

* **Alternative flows:**
  * **Wrong credentials:** the system shows a generic error message.
  * **Account locked/deactivated:** the system shows the message that the account cannot be used.
  * **Student role attempted:** The user has the role Student: the system redirects the user to the Student dashboard instead.
  * **Unauthorized access:** A user without sufficient privileges opens an administration URL: the system returns "403 Forbidden" or redirects to the login page.
* **Special requirements:** Authorization is checked on the server for every administrative function (not only hidden in the interface); Admin/Teacher accounts cannot be created by self-registration; all traffic uses HTTPS.
* **System state before:** The Admin/Teacher account exists and is active.
* **System state after:** The user is authenticated and an administrative session is created.
* **Extension points:** None. All other administrative use cases require this use case to have been completed.

#### 2.2.2. Use case Manage quizzes (UC-AD-02)
* **Actor(s):** Admin / Teacher
* **Summary:** This use case allows an Admin/Teacher to create, update and delete quizzes and to configure their title, time limit, passing score and availability status.

**Main flow:**
1. The use case starts when the Admin/Teacher
2. The system displays the list of quizzes.
3. The Admin/Teacher selects Create quiz.
4. The system displays the quiz form (title, category, duration in minutes, passing score, availability status).
5. The Admin/Teacher fills in the form and submits it.
6. The system validates the data, saves the quiz and displays it in the list.

* **Alternative flows:**
  * **Update:** the Admin/Teacher selects a quiz, edits the form and saves; the system validates and updates the quiz.
  * **Delete:** the Admin/Teacher selects Delete and confirms; the system deletes the quiz (see Special requirements for quizzes that already have attempts).
  * **Availability:** the Admin/Teacher switches the status between Available and Unavailable; the system updates the visibility of the quiz for students.
  * **Invalid data:** (empty title, duration less than or equal to 0, passing score outside the scoring scale): the system highlights the wrong fields and returns to step 5.
* **Special requirements:** Duration must be greater than 0 and the passing score must lie within the scoring scale. A quiz without questions cannot be set to Available. A quiz that already has attempts cannot be physically deleted (soft delete or refusal) so that the score history is preserved. Editing a quiz does not affect attempts that are in progress.
* **System state before:** The Admin/Teacher is logged in.
* **System state after:** The quiz is created, updated or deleted.
* **Extension points:** None.

#### 2.2.3. Use case Manage question bank (UC-AD-03)
* **Actor(s):** Admin / Teacher
* **Summary:** This use case allows an Admin/Teacher to add, edit and remove multiple-choice questions, their options (A, B, C, D) and the correct answer.

**Main flow:**
1. The use case starts when the Admin/Teacher selects a quiz and chooses Manage questions.
2. The system displays the questions of the quiz.
3. The Admin/Teacher selects Add question.
4. The system displays the question form (question text, options A, B, C, D, correct answer).
5. The Admin/Teacher fills in the form, designates the correct answer and submits it.
6. The system validates the data, saves the question and displays it in the list.

* **Alternative flows:**
  * **Edit:** the Admin/Teacher selects a question, changes the text, the options or the correct answer and saves.
  * **Remove:** the Admin/Teacher selects Delete and confirms; the system removes the question from the quiz.
  * **Missing fields:** Missing question text or option: the system highlights the missing fields and returns to step 5.
  * **No correct answer:** No correct answer designated: the system refuses to save and asks the Admin/Teacher to select one.
  * **Duplicate options:** the system shows a warning.
* **Special requirements:** Each question has exactly four options and exactly one correct answer. Editing or deleting a question must not change the score of attempts that were already submitted (snapshot or soft delete).
* **System state before:** The Admin/Teacher is logged in and the quiz exists.
* **System state after:** The question bank of the quiz is updated.
* **Extension points:** None.

#### 2.2.4. Use case Manage users (UC-AD-04)
* **Actor(s):** Admin / Teacher
* **Summary:** This use case allows an Admin/Teacher to view and manage student user accounts.

**Main flow:**
1. The use case starts when the Admin/Teacher selects Manage users.
2. The system displays the searchable, paginated list of student accounts (full name, e-mail, status).
3. The Admin/Teacher selects a student.
4. The system displays the student's profile and account status.
5. The Admin/Teacher edits the profile (full name, e-mail) and saves.
6. The system validates the data, updates the account and displays a success message.

* **Alternative flows:**
  * **Lock/unlock or deactivate:** the Admin/Teacher changes the account status and confirms; the system updates the status, and a locked or deactivated student can no longer log in.
  * **E-mail conflict/invalid:** E-mail already used by another account or invalid format: the system shows an error and returns to step 5.
  * **Reset credentials:** the Admin/Teacher selects Reset password; the system automatically resets the student's password to a default password (e.g., `123456`) and displays a success message.
* **Special requirements:** The Admin/Teacher can never see an original password. Deactivating an account keeps the student's attempt history.
* **System state before:** The Admin/Teacher is logged in and the student account exists.
* **System state after:** The student account (profile, credentials or status) is updated.
* **Extension points:** None.

#### 2.2.5. Use case View reports (UC-AD-05)
* **Actor(s):** Admin / Teacher
* **Summary:** This use case allows an Admin/Teacher to generate statistical reports on student scores and quiz completion rates.

**Main flow:**
1. The use case starts when the Admin/Teacher selects Reports.
2. The system displays the list of quizzes and the optional filters (date range, student).
3. The Admin/Teacher selects a quiz (and the filters).
4. The system aggregates the submitted attempts and the assigned students.
5. The system displays the score statistics: number of attempts, average, highest and lowest score, pass rate, and the score of each student.
6. The system displays the completion statistics: number of students who completed the quiz, number who have not taken it, and the completion rate (completed / total students).

* **Alternative flows:**
  * **No attempt:** No attempt for the selected quiz: the system displays the message "No data available" and a completion rate of 0%.
  * **Export:** Export (if implemented): the Admin/Teacher selects Export; the system generates a CSV/Excel file of the report for download.
  * **All quizzes summary:** The Admin/Teacher selects all quizzes: the system displays a summary table with one row per quiz.
* **Special requirements:** Only attempts with status Submitted are counted as completed. Completion rate = (students with at least one submitted attempt / total registered students) x 100%. Reports are available only to the roles Admin and Teacher.
* **System state before:** The Admin/Teacher is logged in; quizzes and submitted attempts exist.
* **System state after:** The report is displayed (and exported if requested); no data is changed.
* **Extension points:** None.

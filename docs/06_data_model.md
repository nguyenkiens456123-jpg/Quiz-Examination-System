# 6. Data Model (Relational Database Schema)
### 1. Table `User`
Stores user account information and role/permission information within the system.

| Column Name | Data Type | Constraints | Description |
| :--- | :--- | :--- | :--- |
| **userId** | INT | PRIMARY KEY, AUTO_INCREMENT | User identifier |
| username | VARCHAR(50) | NOT NULL, UNIQUE | Username |
| password | VARCHAR(255) | NOT NULL | Password (hash-encrypted) |
| fullName | VARCHAR(100) | NOT NULL | Full name |
| email | VARCHAR(100) | NOT NULL, UNIQUE | Email adress |
| role | VARCHAR(20) | NOT NULL | Role (Ex: Student, Teacher, Admin) |

---

### 2. Table `Quizz`
Store exam configuration information.

| Column Name | Data Type | Constraints | Description |
| :--- | :--- | :--- | :--- |
| **quizId** | INT | PRIMARY KEY, AUTO_INCREMENT | Exam code |
| title | VARCHAR(150) | NOT NULL | Exam title |
| description | TEXT | NULL | Detailed description of the exam |
| durationMinutes | INT | NOT NULL | The time allotted for the test is in minutes |
| passingScore | FLOAT | NOT NULL | Minimum passing score |
| isPublished | BOOLEAN | NOT NULL, DEFAULT FALSE | Publication status (Open / Draft) |

---

### 3. Table `Question`
Store a list of questions belonging to the exams.

| Column Name | Data Type | Constraints | Description |
| :--- | :--- | :--- | :--- |
| **questionId** | INT | PRIMARY KEY, AUTO_INCREMENT | Question identifier |
| **quizId** | INT | FOREIGN KEY (Quizzes.quizId) | Foreign key linked to the exam |
| content | TEXT | NOT NULL | Question content |
| questionType | VARCHAR(50) | NOT NULL | Question type |
| points | FLOAT | NOT NULL | Points for the question |

---

### 4. Table `Option`
Store the options (answers) for each question.

| Column Name | Data Type | Constraints | Description |
| :--- | :--- | :--- | :--- |
| **optionId** | INT | PRIMARY KEY, AUTO_INCREMENT | Option identifier |
| **questionId** | INT | FOREIGN KEY (Questions.questionId) | Foreign key linked to the question |
| content | TEXT | NOT NULL | Answer content (A, B, C, D...) |
| isCorrect | BOOLEAN | NOT NULL, DEFAULT FALSE | Identify the correct answer (True/False) |

---

### 5. Table `Attempt`
Stores historical information about the times candidates have taken the test.

| Column Name | Data Type | Constraints | Description |
| :--- | :--- | :--- | :--- |
| **attemptId** | INT | PRIMARY KEY, AUTO_INCREMENT | Exam attempt identifier |
| **userId** | INT | FOREIGN KEY (Users.userId) | Foreign keys linked to the test-taker |
| **quizId** | INT | FOREIGN KEY (Quizzes.quizId) | The foreign key linked to the exam was created. |
| startTime | DATETIME | NOT NULL | The time to start the test |
| endTime | DATETIME | NULL | Submission/End Date |
| totalScore | FLOAT | NULL | Total score achieved in the round |

---

### 6. Table `AttemptDetail`
Store detailed information about the answers chosen by the test-taker for each question in each round of the exam.

| Column Name | Data Type | Constraints | Description |
| :--- | :--- | :--- | :--- |
| **attemptDetailId** | INT | PRIMARY KEY, AUTO_INCREMENT | Answer details identifier |
| **attemptId** | INT | FOREIGN KEY (Attempts.attemptId) | Foreign key linked to exam turn |
| **questionId** | INT | FOREIGN KEY (Questions.questionId) | Foreign key linked to the question |
| **selectedOptionId** | INT | FOREIGN KEY (Options.optionId) | Foreign key linking to the candidate's chosen answer. |
| isCorrect | BOOLEAN | NOT NULL | Evaluate the student's answer as true or false|

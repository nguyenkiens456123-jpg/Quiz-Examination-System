# 6. Data Model (Relational Database Schema)

This document maps the structural Class Diagram into relational database tables, defining Primary Keys (PK), Foreign Keys (FK), data types, and nullability constraints in Third Normal Form (3NF).

---

## 1. Table Definitions

### Table 1: `users`
Stores user account credentials, profile information, and access control roles.

| Field Name | Data Type | Constraints | Description |
| :--- | :--- | :--- | :--- |
| `user_id` | INT | PK, AUTO_INCREMENT | Unique identifier for each user |
| `username` | VARCHAR(50) | NOT NULL, UNIQUE | User login username |
| `full_name` | VARCHAR(100) | NOT NULL | User's full name |
| `email` | VARCHAR(100) | NOT NULL, UNIQUE | User's email address |
| `password_hash` | VARCHAR(255) | NOT NULL | BCrypt hashed password |
| `role` | ENUM('Student','Teacher','Admin') | NOT NULL | User role permission level |
| `status` | ENUM('Active','Locked') | DEFAULT 'Active' | Account status flag |

---

### Table 2: `quizzes`
Stores test configurations, time limits, passing scores, and publication status.

| Field Name | Data Type | Constraints | Description |
| :--- | :--- | :--- | :--- |
| `quiz_id` | INT | PK, AUTO_INCREMENT | Unique quiz identifier |
| `title` | VARCHAR(200) | NOT NULL | Quiz title |
| `description` | TEXT | NULL | Detailed quiz instructions |
| `duration_mins` | INT | NOT NULL | Examination duration limit in minutes |
| `pass_score` | DECIMAL(4,2) | NOT NULL | Minimum passing score threshold |
| `created_by` | INT | FK -> users(user_id) | ID of the teacher who created the quiz |
| `is_published` | BOOLEAN | DEFAULT FALSE | Visibility flag for students |

---

### Table 3: `questions`
Holds individual test questions linked to specific quizzes.

| Field Name | Data Type | Constraints | Description |
| :--- | :--- | :--- | :--- |
| `question_id` | INT | PK, AUTO_INCREMENT | Unique question identifier |
| `quiz_id` | INT | FK -> quizzes(quiz_id) | Parent quiz ID |
| `content` | TEXT | NOT NULL | Question text body |
| `points` | DECIMAL(4,2) | DEFAULT 1.00 | Score points allocated to this question |

---

### Table 4: `options`
Stores answer choices for questions and marks correct answers.

| Field Name | Data Type | Constraints | Description |
| :--- | :--- | :--- | :--- |
| `option_id` | INT | PK, AUTO_INCREMENT | Unique choice option identifier |
| `question_id` | INT | FK -> questions(question_id) | Parent question ID |
| `option_text` | TEXT | NOT NULL | Text content of the option |
| `is_correct` | BOOLEAN | DEFAULT FALSE | Flag indicating if option is correct key |

---

### Table 5: `attempts`
Tracks individual student exam sessions, start/submit timestamps, and final scores.

| Field Name | Data Type | Constraints | Description |
| :--- | :--- | :--- | :--- |
| `attempt_id` | INT | PK, AUTO_INCREMENT | Unique exam attempt identifier |
| `user_id` | INT | FK -> users(user_id) | ID of the student taking the exam |
| `quiz_id` | INT | FK -> quizzes(quiz_id) | ID of the attempted quiz |
| `start_time` | DATETIME | NOT NULL | Timestamp when exam session started |
| `submit_time` | DATETIME | NULL | Timestamp when exam was submitted |
| `total_score` | DECIMAL(4,2) | NULL | Final calculated score |
| `status` | ENUM('In_Progress','Submitted','Timed_Out') | DEFAULT 'In_Progress' | Current attempt status |

---

### Table 6: `attempt_details`
Records individual selected options and correctness per question for each attempt.

| Field Name | Data Type | Constraints | Description |
| :--- | :--- | :--- | :--- |
| `detail_id` | INT | PK, AUTO_INCREMENT | Unique selection record identifier |
| `attempt_id` | INT | FK -> attempts(attempt_id) | Parent attempt ID |
| `question_id` | INT | FK -> questions(question_id) | Question ID answered |
| `selected_option_id` | INT | FK -> options(option_id) | Option ID chosen by student |
| `is_correct` | BOOLEAN | NULL | Correctness evaluation flag |

---


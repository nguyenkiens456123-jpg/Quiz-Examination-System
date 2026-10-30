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

## 2. SQL DDL Definition Script

```sql
CREATE DATABASE IF NOT EXISTS quiz_examination_system;
USE quiz_examination_system;

CREATE TABLE users (
    user_id INT PRIMARY KEY AUTO_INCREMENT,
    username VARCHAR(50) NOT NULL UNIQUE,
    full_name VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role ENUM('Student','Teacher','Admin') NOT NULL,
    status ENUM('Active','Locked') DEFAULT 'Active'
);

CREATE TABLE quizzes (
    quiz_id INT PRIMARY KEY AUTO_INCREMENT,
    title VARCHAR(200) NOT NULL,
    description TEXT NULL,
    duration_mins INT NOT NULL,
    pass_score DECIMAL(4,2) NOT NULL,
    created_by INT NOT NULL,
    is_published BOOLEAN DEFAULT FALSE,
    FOREIGN KEY (created_by) REFERENCES users(user_id)
);

CREATE TABLE questions (
    question_id INT PRIMARY KEY AUTO_INCREMENT,
    quiz_id INT NOT NULL,
    content TEXT NOT NULL,
    points DECIMAL(4,2) DEFAULT 1.00,
    FOREIGN KEY (quiz_id) REFERENCES quizzes(quiz_id) ON DELETE CASCADE
);

CREATE TABLE options (
    option_id INT PRIMARY KEY AUTO_INCREMENT,
    question_id INT NOT NULL,
    option_text TEXT NOT NULL,
    is_correct BOOLEAN DEFAULT FALSE,
    FOREIGN KEY (question_id) REFERENCES questions(question_id) ON DELETE CASCADE
);

CREATE TABLE attempts (
    attempt_id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT NOT NULL,
    quiz_id INT NOT NULL,
    start_time DATETIME NOT NULL,
    submit_time DATETIME NULL,
    total_score DECIMAL(4,2) NULL,
    status ENUM('In_Progress','Submitted','Timed_Out') DEFAULT 'In_Progress',
    FOREIGN KEY (user_id) REFERENCES users(user_id),
    FOREIGN KEY (quiz_id) REFERENCES quizzes(quiz_id) ON DELETE CASCADE
);

CREATE TABLE attempt_details (
    detail_id INT PRIMARY KEY AUTO_INCREMENT,
    attempt_id INT NOT NULL,
    question_id INT NOT NULL,
    selected_option_id INT NULL,
    is_correct BOOLEAN NULL,
    FOREIGN KEY (attempt_id) REFERENCES attempts(attempt_id) ON DELETE CASCADE,
    FOREIGN KEY (question_id) REFERENCES questions(question_id) ON DELETE CASCADE,
    FOREIGN KEY (selected_option_id) REFERENCES options(option_id) ON DELETE SET NULL
);

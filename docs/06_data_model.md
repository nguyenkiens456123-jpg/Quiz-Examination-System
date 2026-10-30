# 6. Data Model (Relational Database Schema)
-- 1. Khởi tạo Database
CREATE DATABASE IF NOT EXISTS quiz_examination_system;
USE quiz_examination_system;

-- 2. Bảng users
CREATE TABLE users (
    user_id INT PRIMARY KEY AUTO_INCREMENT,
    username VARCHAR(50) NOT NULL UNIQUE,
    full_name VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role ENUM('Student','Teacher','Admin') NOT NULL,
    status ENUM('Active','Locked') DEFAULT 'Active'
);

-- 3. Bảng quizzes
CREATE TABLE quizzes (
    quiz_id INT PRIMARY KEY AUTO_INCREMENT,
    title VARCHAR(200) NOT NULL,
    description TEXT NULL,
    duration_mins INT NOT NULL,
    pass_score DECIMAL(4,2) NOT NULL,
    created_by INT NOT NULL,
    is_published BOOLEAN DEFAULT FALSE,
    CONSTRAINT fk_quizzes_created_by 
        FOREIGN KEY (created_by) REFERENCES users(user_id)
);

-- 4. Bảng questions
CREATE TABLE questions (
    question_id INT PRIMARY KEY AUTO_INCREMENT,
    quiz_id INT NOT NULL,
    content TEXT NOT NULL,
    points DECIMAL(4,2) DEFAULT 1.00,
    CONSTRAINT fk_questions_quiz 
        FOREIGN KEY (quiz_id) REFERENCES quizzes(quiz_id) 
        ON DELETE CASCADE
);

-- 5. Bảng options
CREATE TABLE options (
    option_id INT PRIMARY KEY AUTO_INCREMENT,
    question_id INT NOT NULL,
    option_text TEXT NOT NULL,
    is_correct BOOLEAN DEFAULT FALSE,
    CONSTRAINT fk_options_question 
        FOREIGN KEY (question_id) REFERENCES questions(question_id) 
        ON DELETE CASCADE
);

-- 6. Bảng attempts
CREATE TABLE attempts (
    attempt_id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT NOT NULL,
    quiz_id INT NOT NULL,
    start_time DATETIME NOT NULL,
    submit_time DATETIME NULL,
    total_score DECIMAL(4,2) NULL,
    status ENUM('In_Progress','Submitted','Timed_Out') DEFAULT 'In_Progress',
    CONSTRAINT fk_attempts_user 
        FOREIGN KEY (user_id) REFERENCES users(user_id),
    CONSTRAINT fk_attempts_quiz 
        FOREIGN KEY (quiz_id) REFERENCES quizzes(quiz_id) 
        ON DELETE CASCADE
);

-- 7. Bảng attempt_details
CREATE TABLE attempt_details (
    detail_id INT PRIMARY KEY AUTO_INCREMENT,
    attempt_id INT NOT NULL,
    question_id INT NOT NULL,
    selected_option_id INT NULL,
    is_correct BOOLEAN NULL,
    CONSTRAINT fk_details_attempt 
        FOREIGN KEY (attempt_id) REFERENCES attempts(attempt_id) 
        ON DELETE CASCADE,
    CONSTRAINT fk_details_question 
        FOREIGN KEY (question_id) REFERENCES questions(question_id) 
        ON DELETE CASCADE,
    CONSTRAINT fk_details_option 
        FOREIGN KEY (selectedOption_id) REFERENCES options(option_id) 
        ON DELETE SET NULL
);

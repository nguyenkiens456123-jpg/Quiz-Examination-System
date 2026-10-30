# 6. Data Model (Relational Database Schema)
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

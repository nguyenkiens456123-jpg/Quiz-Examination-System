# 6. Data Model (Relational Database Schema)
-- 1. Table Users
CREATE TABLE Users (
    userId INT PRIMARY KEY AUTO_INCREMENT,
    username VARCHAR(50) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL,
    fullName VARCHAR(100) NOT NULL,
    email VARCHAR(100) NOT NULL UNIQUE,
    role VARCHAR(20) NOT NULL
);

-- 2. Table Quizzes
CREATE TABLE Quizzes (
    quizId INT PRIMARY KEY AUTO_INCREMENT,
    title VARCHAR(150) NOT NULL,
    description TEXT NULL,
    durationMinutes INT NOT NULL,
    passingScore FLOAT NOT NULL,
    isPublished BOOLEAN NOT NULL DEFAULT FALSE
);

-- 3. Table Questions
CREATE TABLE Questions (
    questionId INT PRIMARY KEY AUTO_INCREMENT,
    quizId INT NOT NULL,
    content TEXT NOT NULL,
    questionType VARCHAR(50) NOT NULL,
    points FLOAT NOT NULL,
    FOREIGN KEY (quizId) REFERENCES Quizzes(quizId)
);

-- 4. Table Options
CREATE TABLE Options (
    optionId INT PRIMARY KEY AUTO_INCREMENT,
    questionId INT NOT NULL,
    content TEXT NOT NULL,
    isCorrect BOOLEAN NOT NULL DEFAULT FALSE,
    FOREIGN KEY (questionId) REFERENCES Questions(questionId)
);

-- 5. Table Attempts
CREATE TABLE Attempts (
    attemptId INT PRIMARY KEY AUTO_INCREMENT,
    userId INT NOT NULL,
    quizId INT NOT NULL,
    startTime DATETIME NOT NULL,
    endTime DATETIME NULL,
    totalScore FLOAT NULL,
    FOREIGN KEY (userId) REFERENCES Users(userId),
    FOREIGN KEY (quizId) REFERENCES Quizzes(quizId)
);

-- 6. Table AttemptDetails
CREATE TABLE AttemptDetails (
    attemptDetailId INT PRIMARY KEY AUTO_INCREMENT,
    attemptId INT NOT NULL,
    questionId INT NOT NULL,
    selectedOptionId INT NOT NULL,
    isCorrect BOOLEAN NOT NULL,
    FOREIGN KEY (attemptId) REFERENCES Attempts(attemptId),
    FOREIGN KEY (questionId) REFERENCES Questions(questionId),
    FOREIGN KEY (selectedOptionId) REFERENCES Options(optionId)
);

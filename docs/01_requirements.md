# 1. FUNCTIONAL AND NON-FUNCTIONAL REQUIREMENTS

## 1.1. Functional Requirements (FR)

### 1.1.1. Student Module
 **FR-ST-01 (Account Registration & Authentication):** The system shall allow students to register a new account by providing their full name, email, and password, and securely log in to access student features.
  **FR-ST-02 (Quiz Dashboard):** The system shall display a customized dashboard showing available quizzes, including quiz title, category, duration, and total number of questions.
 **FR-ST-03 (Quiz Attempt & Timer):** The system shall allow students to start a quiz attempt with a synchronized real-time countdown timer that automatically tracks remaining time.
 **FR-ST-04 (Question Navigation & Selection):** The system shall present multiple-choice questions one by one or in a list, allowing students to select option answers and navigate between questions freely before submitting.
 **FR-ST-05 (Auto-Submission & Scoring):** The system shall automatically record user choices, evaluate submitted answers against the answer key, calculate total scores, and auto-submit the quiz when the countdown timer expires.
 **FR-ST-06 (Result & History Viewing):** The system shall display instant score feedback upon completion and allow students to view their historical attempt records.

### 1.1.2. Admin / Teacher Module
 **FR-AD-01 (Administrative Authentication):** The system shall enforce role-based access control, requiring administrators/teachers to log in with privileged credentials.
 **FR-AD-02 (Quiz Management):** The system shall allow admins to create, update, and delete quizzes, configuring details such as title, time limit (duration in minutes), passing score, and availability status.
 **FR-AD-03 (Question Bank Management):** The system shall allow admins to manage question banks by adding, editing, or removing multiple-choice questions, option choices (A, B, C, D), and designating the correct answer key.
 **FR-AD-04 (User Management):** The system shall allow admins to view, edit student profiles, and reset student credentials if required.
 **FR-AD-05 (Gradebook & Reports):** The system shall generate summary statistics and score reports for completed quizzes across all student accounts.

## 1.2. Non-functional Requirements (NFR)

 **NFR-01 (Usability):** The application interface must be clean, responsive, and compatible across standard web browsers on both desktop computers and mobile devices[cite: 7].
 **NFR-02 (Performance):** The system must process and record quiz submissions within 2 seconds under normal network conditions and support up to 500 concurrent students taking exams simultaneously[cite: 7].
 **NFR-03 (Security):** All user passwords must be securely hashed before storage in the database. The application must sanitize input fields to prevent common web vulnerabilities such as SQL Injection and Cross-Site Scripting (XSS)[cite: 7].
 **NFR-04 (Reliability & Availability):** The system database must maintain data integrity during unexpected session terminations, auto-saving active student selections locally or temporarily on the server.

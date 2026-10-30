# 5. Class Diagram & Entity Descriptions

This document outlines the structural Class Diagram for the Quiz Examination System, identifying core domain entities, their attributes, methods, relationships, and method behaviors.

---

## 1. Class Details (Attributes and Methods)

### **User**
Base class for system users; holds authentication credentials and account roles.
* **Attributes:**
  * `- userId: int`
  * `- username: String`
  * `- password: String`
  * `- fullName: String`
  * `- email: String`
  * `- role: String`
* **Methods:**
  * `+ login(): boolean`
  * `+ logout(): void`

### **Quiz**
Manages test configuration, duration, passing criteria, and publication status.
* **Attributes:**
  * `- quizId: int`
  * `- title: String`
  * `- description: String`
  * `- durationMinutes: int`
  * `- passingScore: float`
  * `- isPublished: boolean`
* **Methods:**
  * `+ createQuiz(): void`
  * `+ publishQuiz(): void`

### **Question**
Holds question content, types, points, and belongs to a specific quiz.
* **Attributes:**
  * `- questionId: int`
  * `- quizId: int`
  * `- content: String`
  * `- questionType: String`
  * `- points: float`
* **Methods:**
  * `+ addQuestion(): void`
  * `+ validateQuestion(): boolean`

### **Option**
Stores choices/answers for a specific question and indicates whether it is correct.
* **Attributes:**
  * `- optionId: int`
  * `- questionId: int`
  * `- content: String`
  * `- isCorrect: boolean`
* **Methods:**
  * `+ getOptionDetails(): String`

### **Attempt**
Tracks user examination sessions, timing, and total scores.
* **Attributes:**
  * `- attemptId: int`
  * `- userId: int`
  * `- quizId: int`
  * `- startTime: DateTime`
  * `- endTime: DateTime`
  * `- totalScore: float`
* **Methods:**
  * `+ startAttempt(): void`
  * `+ submitAttempt(): void`
  * `+ calculateScore(): float`

### **AttemptDetail**
Stores individual answers selected by the user for each question during an examination attempt.
* **Attributes:**
  * `- attemptDetailId: int`
  * `- attemptId: int`
  * `- questionId: int`
  * `- selectedOptionId: int`
  * `- isCorrect: boolean`
* **Methods:**
  * `+ saveAnswer(): void`

---

## 2. Relationships Mapping

| Class 1 | Multiplicity | Class 2 | Meaning |
| :--- | :--- | :--- | :--- |
| **User** | 1 .. 0..\* | **Attempt** | A user can make many attempts or not do it. |
| **Quiz** | 1 .. 0..\* | **Attempt** | A quiz can have many attempts or not. |
| **Quiz** | 1 .. 1..\* | **Question** | A quiz contains questions. |
| **Question** | 1 .. 1..\* | **Option** | Composition: a question has 1 or more options. |
| **Attempt** | 1 .. 1..\* | **AttemptDetail** | An attempt consists of many attempt details. |
| **Question** | 1 .. 0..\* | **AttemptDetail** | Question referenced in attempt details. |
| **Option** | 0..1 .. 0..\* | **AttemptDetail** | Option chosen in attempt details. |

---

## 3. Behavior of Main Methods

| Method | Behavior |
| :--- | :--- |
| **User.login(username, password)** | Verifies credentials, counts failed login attempts, creates a session; throws an error when the account is locked. |
| **User.logout()** | Terminates the active user session and clears authentication tokens. |
| **Quiz.createQuiz()** | Validates the configuration parameters and creates a new Quiz with a draft status. |
| **Quiz.publishQuiz()** | Checks if the quiz contains questions and valid criteria, then changes its status to published. |
| **Question.validateQuestion()** | Verifies that the question content and its associated options are correctly configured. |
| **Option.getOptionDetails()** | Retrieves the content and correctness status of a specific option choice. |
| **Attempt.startAttempt()** | Checks quiz availability and remaining attempts, then creates a new Attempt record with a start timestamp. |
| **Attempt.submitAttempt()** | Sets the attempt status to submitted, triggers score calculation, and saves the final results. |
| **Attempt.calculateScore()** | Evaluates student answers against correct options, sums up the points, and returns the total score. |
| **AttemptDetail.saveAnswer()** | Creates or updates the selected option answer for a specific question within the attempt. |

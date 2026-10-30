# 5. Class Diagram & Entity Descriptions


![Use Case Diagram](<Task5.drawio.png>)


This section documents the object-oriented Class Diagram, detailing entity attributes, access modifiers, methods, structural relationships, and method behaviors based on the updated domain model.

---

## I. Structural Relationships

| Class 1 | Multiplicity | Class 2 | Relationship Description |
| :--- | :--- | :--- | :--- |
| `User` | 1 | `0...*` | `Attempt` | A user can initiate multiple exam attempts. |
| `User` | 1 | `0...*` | `Quiz` | A user (Teacher/Admin) can create multiple quizzes. |
| `Quiz` | 1 | `0...*` | `Attempt` | A quiz can have multiple exam attempts. |
| `Quiz` | 1 | `1...*` | `Question` | A quiz contains one or more questions. |
| `Question` | 1 | `1...*` | `Option` | A question has one or more answer options. |
| `Attempt` | 1 | `1...*` | `AttemptDetail` | An attempt consists of multiple detailed responses. |
| `Question` | 1 | `0...*` | `AttemptDetail` | A question is referenced in multiple attempt details. |
| `Option` | `0...1` | `0...*` | `AttemptDetail` | An option can be selected in attempt details. |

---

## II. Class Details (Attributes & Methods)

### 1. User
Base class representing system accounts (Students, Teachers, Admins).
* **Attributes:**
  * `- userID: Int`
  * `- username: String`
  * `- password: String`
  * `- fullname: String`
  * `- email: String`
  * `- role: String`
* **Methods:**
  * `+ login(): Boolean`
  * `+ logout(): Void`
  * `+ updateProfile(): Void`

### 2. Quiz
Manages quiz configuration, duration settings, passing score thresholds, and publication.
* **Attributes:**
  * `- quizID: Int`
  * `- title: String`
  * `- durationMins: Int`
  * `- passScore: Float`
  * `- isPublished: Boolean`
* **Methods:**
  * `+ createQuiz(): Void`
  * `+ publishQuiz(): Void`
  * `+ assignClass(): Void`

### 3. Question
Holds question content, assigned points, and parent quiz reference.
* **Attributes:**
  * `- questionID: Int`
  * `- quizID: Int`
  * `- content: String`
  * `- points: Float`
* **Methods:**
  * `+ addOption(): Void`
  * `+ validateQuestion(): Void`

### 4. Option
Stores choice content and correct flags associated with a specific question.
* **Attributes:**
  * `- optionID: Int`
  * `- questionID: Int`
  * `- optionText: String`
  * `- isCorrect: Boolean`
* **Methods:**
  * `+ getOptionDetails(): String`

### 5. Attempt
Tracks individual student exam sessions, timers, and total score calculations.
* **Attributes:**
  * `- attemptID: Int`
  * `- userID: Int`
  * `- quizID: Int`
  * `- startTime: DateTime`
  * `- submitTime: DateTime`
  * `- totalScore: Float`
* **Methods:**
  * `+ startAttempt(): Void`
  * `+ autoSave(): Void`
  * `+ submitAttempt(): Void`
  * `+ calculateScore(): Float`

### 6. AttemptDetail
Records the selected option and correctness flag for each question answered during an attempt.
* **Attributes:**
  * `- detailID: Int`
  * `- attemptID: Int`
  * `- questionID: Int`
  * `- selectedOptionID: Int`
  * `- isCorrect: Boolean`
* **Methods:**
  * `+ saveSelection(): Void`

---

## III. Behavior of Main Methods

| Method | Detailed Behavior Description |
| :--- | :--- |
| `User.login()` | Validates user credentials, creates a session token, and grants role-based access upon successful authentication. |
| `User.logout()` | Invalidates the active session token and clears user authentication state. |
| `User.updateProfile()` | Updates account information such as full name or password. |
| `Quiz.createQuiz()` | Validates configuration parameters and initializes a new quiz in draft status. |
| `Quiz.publishQuiz()` | Verifies that the quiz contains valid questions and toggles its availability for students (`isPublished = true`). |
| `Quiz.assignClass()` | Links a published quiz to specific student classes or groups. |
| `Question.addOption()` | Appends a new choice option to the target question. |
| `Question.validateQuestion()` | Ensures the question contains valid content, assigned points, and at least one correct option key. |
| `Option.getOptionDetails()` | Returns the option text and its correctness indicator. |
| `Attempt.startAttempt()` | Verifies quiz availability, creates an active attempt session, and records `startTime`. |
| `Attempt.autoSave()` | Periodically saves the student's selected choices to prevent data loss. |
| `Attempt.submitAttempt()` | Sets `submitTime`, locks further editing, and triggers final score calculation. |
| `Attempt.calculateScore()` | Compares selected options against correct keys, sums up earned points, and returns `totalScore`. |
| `AttemptDetail.saveSelection()` | Records or updates the student's selected option (`selectedOptionID`) for a specific question. |

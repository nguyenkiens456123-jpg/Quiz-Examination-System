# Use Case Specification

## 1. Use Case Diagram

![Use Case Diagram](<Use case (1).png>)

---

# 4. Use Case Diagram & Detailed Specifications

## 4.1. Actor Definitions

- **Guest:** Unauthenticated visitor capable only of registration and basic login actions.
- **Student:** Authenticated learner enrolled in classes who browses quizzes, executes attempts, selects choices, and views transcripts.
- **Teacher:** Academic instructor who manages question repositories, configures quizzes, schedules exams, and analyzes gradebooks.
- **Admin:** System administrator possessing global permissions for user account management, role assignment, and platform configuration.

---

## 4.2. Student Module Use Cases

### UC-ST-01: Register / Log in
- **Actor(s):** Guest, Student
- **Summary:** Allows a guest to register a new account or an existing student to log in.
- **Main Flow:**
  1. User selects Register or Login.
  2. System displays input form (Full Name, Email, Password).
  3. User submits credentials.
  4. System validates input, hashes password, and creates account or generates JWT session token.
  5. System redirects user to the Quiz Dashboard.
- **Alternative Flows:**
  - *Invalid Input / Email in use / Wrong Password:* System displays generic error message and prompts re-entry.

### UC-ST-02: View quiz dashboard
- **Actor(s):** Student
- **Summary:** Displays the list of available quizzes assigned to the student.
- **Main Flow:**
  1. Student navigates to Dashboard upon logging in.
  2. System retrieves and displays active quizzes (Title, Subject, Duration, Total Questions).
  3. Student selects a quiz to start.
- **Alternative Flows:**
  - *No Quiz Available:* System displays "No quizzes available at the moment".
  - *Search/Filter:* Student filters list by keyword or subject.

### UC-ST-03: Attempt quiz with timer
- **Actor(s):** Student
- **Summary:** Starts a quiz testing session with a real-time server-synchronized countdown timer.
- **Main Flow:**
  1. Student selects "Start Attempt" on a quiz.
  2. System creates a new attempt record with status `In Progress` and sets end time.
  3. System renders the exam UI, Question Grid, and initiates the countdown timer.
  4. Student works through questions (executes `Answer & navigate`).
  5. System triggers `Auto-submit & score` when student submits or timer reaches 00:00:00.
- **Alternative Flows:**
  - *Network Drop / Refresh:* System resumes the attempt with correct remaining time based on Server clock.

### UC-ST-04: Answer & navigate *(Included in UC-ST-03)*
- **Actor(s):** Student
- **Summary:** Allows students to select options and move freely across questions during an active attempt.
- **Main Flow:**
  1. System displays question text and choices A, B, C, D.
  2. Student selects an option; system automatically background-saves choices every 10 seconds.
  3. Student navigates between questions via Next/Prev buttons or the Question Grid palette.
- **Alternative Flows:**
  - *Change Answer:* Overwrites previous selection.- *Network Error:* Displays warning banner and retries background sync.

### UC-ST-05: Auto-submit & score
- **Actor(s):** Student, System Timer
- **Summary:** Locks the attempt, compares student choices against correct answer keys, and calculates total score.
- **Main Flow:**
  1. Triggered by student clicking "Submit" or countdown timer reaching 00:00:00.
  2. System locks attempt inputs to prevent further changes.
  3. System compares student choices with correct keys, computes score, and sets status to `Submitted`.
  4. System updates results in database and redirects to Result View.
- **Alternative Flows:**
  - *Timeout:* Automatically submits all currently saved answers.
  - *Unanswered Questions:* Assigned 0 points without negative penalty.

### UC-ST-06: View result & history
- **Actor(s):** Student
- **Summary:** Displays instant score feedback and historical attempt transcripts.
- **Main Flow:**
  1. System displays total score, Pass/Fail status, and correct/wrong breakdown.
  2. Student opens "My History" to view chronological list of past attempts.
  3. Student selects an attempt to view question-by-question breakdown (if quiz policy permits).

---

## 4.3. Admin & Teacher Module Use Cases

### UC-AD-01: Admin login
- **Actor(s):** Teacher, Admin
- **Summary:** Authenticates privileged users with role-based administrative access control.
- **Main Flow:**
  1. User enters administrative credentials on Admin Login form.
  2. System verifies credentials and checks role (`Teacher` or `Admin`).
  3. System grants session and redirects user to Admin Portal.
- **Alternative Flows:**
  - *Locked / Deactivated Account:* System displays "Account disabled" notification.

### UC-AD-02: Manage quizzes
- **Actor(s):** Teacher, Admin
- **Summary:** Create, update, publish, or delete quizzes and configure operational settings.
- **Main Flow:**
  1. User opens Quiz Manager and selects "Create Quiz".
  2. User enters parameters: Title, Subject, Duration (mins), Passing Score (%), and Status.
  3. System validates data and saves quiz configuration.
- **Alternative Flows:**
  - *Delete Quiz:* Soft-deletes or archives quiz if past attempts already exist.

### UC-AD-03: Manage question bank
- **Actor(s):** Teacher, Admin
- **Summary:** Authors, updates, and removes multiple-choice questions and option keys.
- **Main Flow:**
  1. User selects a quiz and clicks "Manage Questions".
  2. User inputs Question text, choices (A, B, C, D), point weights, and designates the correct answer key.
  3. System validates and updates the Question Bank repository.
- **Alternative Flows:**
  - *Missing Correct Key:* System prompts user to flag exactly one option as correct.

### UC-AD-04: Manage users
- **Actor(s):** Admin
- **Summary:** Admin views, updates, locks, or resets student user accounts.
- **Main Flow:**
  1. Admin opens User Management portal to view searchable student roster.
  2. Admin selects a student account to view details.
3. Admin updates student profile, toggles account lock status, or resets password to default.

### UC-AD-05: Grade book & result *(Reports)*
- **Actor(s):** Teacher, Admin
- **Summary:** Generates class performance analytics, grade distributions, and CSV data exports.
- **Main Flow:**
  1. User navigates to Gradebook and selects a Quiz or Class filter.
  2. System aggregates submitted attempt scores, average points, pass rates, and completion percentages.
  3. User clicks "Export CSV" to download class gradebook file.
  

# 6. Data Model (Relational Database Schema)

Tài liệu này ánh xạ từ Sơ đồ lớp (Class Diagram) của hệ thống thi trắc nghiệm thành các bảng cơ sở dữ liệu quan hệ, xác định rõ ràng Khóa chính (PK), Khóa ngoại (FK), kiểu dữ liệu và các ràng buộc toàn vẹn.

### 1. Bảng `Users`
Lưu trữ thông tin tài khoản người dùng và vai trò phân quyền trong hệ thống.

| Column Name | Data Type | Constraints | Description |
| :--- | :--- | :--- | :--- |
| **userId** | INT | PRIMARY KEY, AUTO_INCREMENT | Mã định danh người dùng |
| username | VARCHAR(50) | NOT NULL, UNIQUE | Tên đăng nhập |
| password | VARCHAR(255) | NOT NULL | Mật khẩu (đã được mã hóa băm) |
| fullName | VARCHAR(100) | NOT NULL | Họ và tên đầy đủ |
| email | VARCHAR(100) | NOT NULL, UNIQUE | Địa chỉ email |
| role | VARCHAR(20) | NOT NULL | Vai trò (Ví dụ: Student, Teacher, Admin) |

---

### 2. Bảng `Quizzes`
Lưu trữ thông tin cấu hình đề thi.

| Column Name | Data Type | Constraints | Description |
| :--- | :--- | :--- | :--- |
| **quizId** | INT | PRIMARY KEY, AUTO_INCREMENT | Mã định danh đề thi |
| title | VARCHAR(150) | NOT NULL | Tiêu đề đề thi |
| description | TEXT | NULL | Mô tả chi tiết đề thi |
| durationMinutes | INT | NOT NULL | Thời gian làm bài tính bằng phút |
| passingScore | FLOAT | NOT NULL | Điểm đạt yêu cầu tối thiểu |
| isPublished | BOOLEAN | NOT NULL, DEFAULT FALSE | Trạng thái xuất bản (Đã công khai / Bản nháp) |

---

### 3. Bảng `Questions`
Lưu trữ danh sách câu hỏi thuộc về các đề thi.

| Column Name | Data Type | Constraints | Description |
| :--- | :--- | :--- | :--- |
| **questionId** | INT | PRIMARY KEY, AUTO_INCREMENT | Mã định danh câu hỏi |
| **quizId** | INT | FOREIGN KEY (Quizzes.quizId) | Khóa ngoại liên kết tới đề thi |
| content | TEXT | NOT NULL | Nội dung câu hỏi |
| questionType | VARCHAR(50) | NOT NULL | Loại câu hỏi |
| points | FLOAT | NOT NULL | Số điểm của câu hỏi |

---

### 4. Bảng `Options`
Lưu trữ các lựa chọn (đáp án) cho từng câu hỏi.

| Column Name | Data Type | Constraints | Description |
| :--- | :--- | :--- | :--- |
| **optionId** | INT | PRIMARY KEY, AUTO_INCREMENT | Mã định danh phương án lựa chọn |
| **questionId** | INT | FOREIGN KEY (Questions.questionId) | Khóa ngoại liên kết tới câu hỏi |
| content | TEXT | NOT NULL | Nội dung đáp án (A, B, C, D...) |
| isCorrect | BOOLEAN | NOT NULL, DEFAULT FALSE | Xác định đáp án đúng (True/False) |

---

### 5. Bảng `Attempts`
Lưu trữ thông tin lịch sử các lần thí sinh tham gia làm bài.

| Column Name | Data Type | Constraints | Description |
| :--- | :--- | :--- | :--- |
| **attemptId** | INT | PRIMARY KEY, AUTO_INCREMENT | Mã định danh lượt thi |
| **userId** | INT | FOREIGN KEY (Users.userId) | Khóa ngoại liên kết đến thí sinh làm bài |
| **quizId** | INT | FOREIGN KEY (Quizzes.quizId) | Khóa ngoại liên kết đến đề thi được làm |
| startTime | DATETIME | NOT NULL | Thời điểm bắt đầu làm bài |
| endTime | DATETIME | NULL | Thời điểm nộp bài / kết thúc |
| totalScore | FLOAT | NULL | Tổng điểm đạt được của lượt thi |

---

### 6. Bảng `AttemptDetails`
Lưu trữ chi tiết các đáp án mà thí sinh đã chọn cho từng câu hỏi trong mỗi lượt thi.

| Column Name | Data Type | Constraints | Description |
| :--- | :--- | :--- | :--- |
| **attemptDetailId** | INT | PRIMARY KEY, AUTO_INCREMENT | Mã định danh chi tiết câu trả lời |
| **attemptId** | INT | FOREIGN KEY (Attempts.attemptId) | Khóa ngoại liên kết đến lượt thi |
| **questionId** | INT | FOREIGN KEY (Questions.questionId) | Khóa ngoại liên kết đến câu hỏi |
| **selectedOptionId** | INT | FOREIGN KEY (Options.optionId) | Khóa ngoại liên kết đến đáp án thí sinh chọn |
| isCorrect | BOOLEAN | NOT NULL | Đánh giá đúng/sai cho câu trả lời của thí sinh |

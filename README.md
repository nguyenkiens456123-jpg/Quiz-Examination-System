# Quiz Examination System - Group 10

## Software Architecture
- **Pattern:** Model-View-Controller (MVC) + Object-Oriented Programming (OOP)
- **Language & GUI:** Python 3.11, PyQt6, SQLite3, BCrypt
- **Testing & DevOps:** pytest, Excel Test Cases, GitHub Actions CI, Docker

## Default Accounts (Password: `123456`)
- **Student:** `student01@uth.edu.vn`
- **Teacher:** `teacher@uth.edu.vn`
- **Admin:** `admin@uth.edu.vn`

## How to Run Locally
1. `pip install -r requirements.txt`
2. `python -m pytest -v`
3. `python -m src.main`

## How to Run via Docker
1. `docker build -t quiz-system-group10 .`
2. `docker run --rm quiz-system-group10`
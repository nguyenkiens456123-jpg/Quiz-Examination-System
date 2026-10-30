# 2. NON-FUNCTIONAL REQUIREMENTS

- **NFR-01 (Usability):** The system must feature a responsive web interface accessible via both desktop computers and mobile devices.
- **NFR-02 (Performance):** The system must process quiz answer submissions within 2 seconds and support up to 500 concurrent users taking exams simultaneously.
- **NFR-03 (Security):** All user passwords must be hashed before saving to the database. The system must sanitize user input to prevent SQL Injection and XSS attacks.
- **NFR-04 (Reliability):** The system database must maintain data integrity during unexpected session terminations, auto-saving active student selections every 10 seconds.

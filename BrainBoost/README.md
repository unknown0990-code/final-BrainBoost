# BrainBoost Test

**Tagline:** Challenge Your Mind • Improve Your Knowledge • Track Your Progress

BrainBoost Test is a web-based MCQ testing and knowledge assessment system developed as a college minor project. It provides a simple, interactive, and responsive platform for users to evaluate their knowledge across various subjects.

## Features
- **User Authentication:** Secure registration and login with password hashing.
- **Student Dashboard:** View overall statistics like total tests taken, best score, and average score.
- **MCQ Test System:** Subject-wise tests (Mathematics, Science, Computer, Environment, General Knowledge) with progress tracking.
- **Result Calculation:** Automatic scoring and percentage calculation upon test submission.
- **Result History:** Track previous test records and performance.
- **Admin Panel:** Complete dashboard for admins to add, edit, delete, and view the question bank, as well as view registered users.

## Technologies Used
- **Python:** Core programming language.
- **Streamlit:** Frontend web framework for building the interactive UI.
- **SQLite:** Lightweight local database for storing users, questions, and results.
- **CSS:** Custom styling for branding and interface enhancements.

## Folder Structure
```text
BrainBoost_IQ_TEST/
│
├── app.py              # Main application and routing
├── database.py         # SQLite database management and queries
├── auth.py             # User and Admin authentication system
├── test.py             # MCQ test rendering and logic
├── result.py           # User result statistics and history
├── admin.py            # Admin panel (manage questions and users)
├── style.css           # Custom UI styling
├── requirements.txt    # Python dependencies
├── README.md           # Project documentation
│
└── db_files/           # Auto-generated directory for SQLite
    └── iq_test.db      # Local database
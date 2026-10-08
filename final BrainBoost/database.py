import sqlite3
import os
import datetime

DB_DIR = "db_files"
DB_FILE = os.path.join(DB_DIR, "iq_test.db")

def get_connection():
    if not os.path.exists(DB_DIR):
        os.makedirs(DB_DIR)
    return sqlite3.connect(DB_FILE, check_same_thread=False)

def create_tables():
    conn = get_connection()
    cursor = conn.cursor()
    
    # USERS Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS USERS (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            username TEXT UNIQUE NOT NULL,
            phone TEXT NOT NULL,
            password TEXT NOT NULL
        )
    ''')
    
    # QUESTIONS Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS QUESTIONS (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            category TEXT NOT NULL,
            question TEXT NOT NULL,
            option1 TEXT NOT NULL,
            option2 TEXT NOT NULL,
            option3 TEXT NOT NULL,
            option4 TEXT NOT NULL,
            answer TEXT NOT NULL
        )
    ''')
    
    # RESULTS Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS RESULTS (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            category TEXT NOT NULL,
            score INTEGER NOT NULL,
            total INTEGER NOT NULL,
            percentage REAL NOT NULL,
            date TEXT NOT NULL
        )
    ''')
    
    conn.commit()
    
    # Initialize sample questions if empty
    cursor.execute("SELECT COUNT(*) FROM QUESTIONS")
    if cursor.fetchone()[0] == 0:
        insert_sample_questions(cursor)
        conn.commit()
        
    conn.close()

def insert_sample_questions(cursor):
    samples = [
        # Mathematics
        ("Mathematics", "What is the value of Pi to two decimal places?", "3.12", "3.14", "3.16", "3.18", "3.14"),
        ("Mathematics", "What is 15% of 200?", "20", "25", "30", "35", "30"),
        ("Mathematics", "What is the square root of 144?", "10", "11", "12", "14", "12"),
        ("Mathematics", "Solve: 5 + 2 * 3", "21", "11", "15", "10", "11"),
        ("Mathematics", "How many degrees are in a full circle?", "90", "180", "270", "360", "360"),
        
        # Science
        ("Science", "What is the chemical symbol for Gold?", "Au", "Ag", "Gd", "Go", "Au"),
        ("Science", "Which planet is known as the Red Planet?", "Venus", "Mars", "Jupiter", "Saturn", "Mars"),
        ("Science", "What gas do plants absorb from the atmosphere?", "Oxygen", "Nitrogen", "Carbon Dioxide", "Hydrogen", "Carbon Dioxide"),
        ("Science", "What is the powerhouse of the cell?", "Nucleus", "Ribosome", "Mitochondria", "Endoplasmic Reticulum", "Mitochondria"),
        ("Science", "What is the freezing point of water in Celsius?", "0", "32", "100", "-1", "0"),
        
        # Computer
        ("Computer", "Which language is commonly used for AI?", "Java", "Python", "HTML", "CSS", "Python"),
        ("Computer", "What does CPU stand for?", "Central Process Unit", "Computer Personal Unit", "Central Processing Unit", "Central Processor Unit", "Central Processing Unit"),
        ("Computer", "Which of these is not an operating system?", "Windows", "Linux", "Oracle", "macOS", "Oracle"),
        ("Computer", "What does HTTP stand for?", "HyperText Transfer Protocol", "HyperText Test Protocol", "Hyper Transfer Text Protocol", "HyperText Transfer Process", "HyperText Transfer Protocol"),
        ("Computer", "Which is a volatile memory?", "ROM", "Hard Disk", "Flash Drive", "RAM", "RAM"),
        
        # Environment
        ("Environment", "Which layer of the atmosphere protects us from UV rays?", "Troposphere", "Stratosphere", "Mesosphere", "Ozone Layer", "Ozone Layer"),
        ("Environment", "What is the main cause of global warming?", "Volcanoes", "Deforestation", "Greenhouse Gases", "Ocean Currents", "Greenhouse Gases"),
        ("Environment", "Which is a renewable energy source?", "Coal", "Natural Gas", "Solar Energy", "Petroleum", "Solar Energy"),
        ("Environment", "What does the 3R principle stand for?", "Reduce, Reuse, Recycle", "Read, Remember, Recite", "Renew, Remake, Restrict", "Random, Rare, Real", "Reduce, Reuse, Recycle"),
        ("Environment", "World Environment Day is celebrated on?", "June 5", "April 22", "March 21", "July 1", "June 5"),
        
        # General Knowledge
        ("General Knowledge", "Which is the largest continent?", "Africa", "Asia", "Europe", "North America", "Asia"),
        ("General Knowledge", "Who painted the Mona Lisa?", "Vincent van Gogh", "Pablo Picasso", "Leonardo da Vinci", "Claude Monet", "Leonardo da Vinci"),
        ("General Knowledge", "What is the capital of Japan?", "Seoul", "Beijing", "Tokyo", "Bangkok", "Tokyo"),
        ("General Knowledge", "Which ocean is the largest?", "Atlantic", "Indian", "Arctic", "Pacific", "Pacific"),
        ("General Knowledge", "Who is the author of Harry Potter?", "J.R.R. Tolkien", "J.K. Rowling", "George R.R. Martin", "Stephen King", "J.K. Rowling")
    ]
    
    cursor.executemany('''
        INSERT INTO QUESTIONS (category, question, option1, option2, option3, option4, answer)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', samples)

# --- USER FUNCTIONS ---

def register_user(name, username, phone, hashed_password):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO USERS (name, username, phone, password) VALUES (?, ?, ?, ?)",
                       (name, username, phone, hashed_password))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()

def get_user(username):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, username, phone, password FROM USERS WHERE username = ?", (username,))
    user = cursor.fetchone()
    conn.close()
    return user

def get_all_users():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, username, phone FROM USERS")
    users = cursor.fetchall()
    conn.close()
    return users


def update_user_profile(old_username, new_name, new_username, new_phone, new_password=None):
    """Update profile details and keep existing result history linked to the new username."""
    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("SELECT id FROM USERS WHERE username = ?", (old_username,))
        user = cursor.fetchone()

        if not user:
            return False, "User account not found."

        # Prevent another account from taking the requested username.
        cursor.execute(
            "SELECT id FROM USERS WHERE username = ? AND id != ?",
            (new_username, user[0])
        )
        if cursor.fetchone():
            return False, "Username already exists. Please choose another username."

        if new_password:
            cursor.execute(
                "UPDATE USERS SET name = ?, username = ?, phone = ?, password = ? WHERE id = ?",
                (new_name, new_username, new_phone, new_password, user[0])
            )
        else:
            cursor.execute(
                "UPDATE USERS SET name = ?, username = ?, phone = ? WHERE id = ?",
                (new_name, new_username, new_phone, user[0])
            )

        # RESULTS currently uses username rather than user id, so keep old
        # test history attached to the account after a username change.
        if old_username != new_username:
            cursor.execute(
                "UPDATE RESULTS SET username = ? WHERE username = ?",
                (new_username, old_username)
            )

        conn.commit()
        return True, "Profile updated successfully."

    except sqlite3.IntegrityError:
        conn.rollback()
        return False, "Username already exists. Please choose another username."
    except Exception as e:
        conn.rollback()
        return False, f"Could not update profile: {e}"
    finally:
        conn.close()

# --- QUESTION FUNCTIONS ---

def get_questions_by_category(category):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM QUESTIONS WHERE category = ?", (category,))
    questions = cursor.fetchall()
    conn.close()
    return questions

def get_all_questions():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM QUESTIONS")
    questions = cursor.fetchall()
    conn.close()
    return questions

def get_question_by_id(q_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM QUESTIONS WHERE id = ?", (q_id,))
    q = cursor.fetchone()
    conn.close()
    return q

def add_question(category, question, o1, o2, o3, o4, answer):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO QUESTIONS (category, question, option1, option2, option3, option4, answer)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (category, question, o1, o2, o3, o4, answer))
    conn.commit()
    conn.close()

def update_question(q_id, category, question, o1, o2, o3, o4, answer):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        UPDATE QUESTIONS 
        SET category=?, question=?, option1=?, option2=?, option3=?, option4=?, answer=?
        WHERE id=?
    ''', (category, question, o1, o2, o3, o4, answer, q_id))
    conn.commit()
    conn.close()

def delete_question(q_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM QUESTIONS WHERE id = ?", (q_id,))
    conn.commit()
    conn.close()

# --- RESULT FUNCTIONS ---

def save_result(username, category, score, total, percentage):
    date_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO RESULTS (username, category, score, total, percentage, date)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (username, category, score, total, percentage, date_str))
    conn.commit()
    conn.close()

def get_user_results(username):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT category, score, total, percentage, date FROM RESULTS WHERE username = ? ORDER BY id DESC", (username,))
    results = cursor.fetchall()
    conn.close()
    return results

def get_all_results():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM RESULTS ORDER BY id DESC")
    results = cursor.fetchall()
    conn.close()
    return results
import sqlite3
import os
from datetime import datetime


class Database:
    def __init__(self):
        # Android环境下使用应用数据目录
        if hasattr(os, 'environ') and 'ANDROID_APP_PATH' in os.environ:
            base_dir = os.environ['ANDROID_APP_PATH']
        else:
            # 开发环境
            base_dir = os.path.dirname(__file__)

        db_path = os.path.join(base_dir, 'quiz_system.db')
        self.conn = sqlite3.connect(db_path)
        # 确保使用UTF-8编码处理文本
        self.conn.text_factory = str
        self.cursor = self.conn.cursor()
        self.create_tables()

    def create_tables(self):
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS quiz_records (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                bank_name TEXT,
                total_questions INTEGER,
                correct_count INTEGER,
                accuracy REAL,
                start_time TEXT,
                end_time TEXT,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        ''')

        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS wrong_questions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                bank_name TEXT,
                question_index INTEGER,
                question_text TEXT,
                wrong_count INTEGER DEFAULT 1,
                last_wrong_time TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        ''')

        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS favorite_questions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                bank_name TEXT,
                question_index INTEGER,
                question_text TEXT,
                added_time TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id),
                UNIQUE(user_id, bank_name, question_index)
            )
        ''')

        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS mastered_questions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                bank_name TEXT,
                question_index INTEGER,
                mastered_time TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id),
                UNIQUE(user_id, bank_name, question_index)
            )
        ''')

        self.conn.commit()

    def add_user(self, username):
        try:
            self.cursor.execute('INSERT INTO users (username) VALUES (?)', (username,))
            self.conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False

    def get_user(self, username):
        self.cursor.execute('SELECT * FROM users WHERE username = ?', (username,))
        return self.cursor.fetchone()

    def get_all_users(self):
        self.cursor.execute('SELECT * FROM users ORDER BY created_at DESC')
        return self.cursor.fetchall()

    def delete_user(self, user_id):
        self.cursor.execute('DELETE FROM users WHERE id = ?', (user_id,))
        self.cursor.execute('DELETE FROM quiz_records WHERE user_id = ?', (user_id,))
        self.cursor.execute('DELETE FROM wrong_questions WHERE user_id = ?', (user_id,))
        self.cursor.execute('DELETE FROM favorite_questions WHERE user_id = ?', (user_id,))
        self.cursor.execute('DELETE FROM mastered_questions WHERE user_id = ?', (user_id,))
        self.conn.commit()

    def save_quiz_record(self, user_id, bank_name, total_questions, correct_count, accuracy, start_time, end_time):
        self.cursor.execute('''
            INSERT INTO quiz_records (user_id, bank_name, total_questions, correct_count, accuracy, start_time, end_time)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (user_id, bank_name, total_questions, correct_count, accuracy, start_time, end_time))
        self.conn.commit()

    def get_quiz_records(self, user_id, limit=50):
        self.cursor.execute('''
            SELECT * FROM quiz_records 
            WHERE user_id = ? 
            ORDER BY start_time DESC 
            LIMIT ?
        ''', (user_id, limit))
        return self.cursor.fetchall()

    def get_user_stats(self, user_id):
        self.cursor.execute('''
            SELECT 
                COUNT(*) as total_tests,
                SUM(total_questions) as total_questions,
                SUM(correct_count) as total_correct,
                AVG(accuracy) as avg_accuracy
            FROM quiz_records 
            WHERE user_id = ?
        ''', (user_id,))
        return self.cursor.fetchone()

    def add_wrong_question(self, user_id, bank_name, question_index, question_text):
        existing = self.cursor.execute('''
            SELECT id, wrong_count FROM wrong_questions 
            WHERE user_id = ? AND bank_name = ? AND question_index = ?
        ''', (user_id, bank_name, question_index)).fetchone()

        if existing:
            new_count = existing[1] + 1
            self.cursor.execute('''
                UPDATE wrong_questions 
                SET wrong_count = ?, last_wrong_time = CURRENT_TIMESTAMP 
                WHERE id = ?
            ''', (new_count, existing[0]))
        else:
            self.cursor.execute('''
                INSERT INTO wrong_questions (user_id, bank_name, question_index, question_text)
                VALUES (?, ?, ?, ?)
            ''', (user_id, bank_name, question_index, question_text))

        self.conn.commit()

    def get_wrong_questions(self, user_id, bank_name=None):
        if bank_name:
            self.cursor.execute('''
                SELECT * FROM wrong_questions 
                WHERE user_id = ? AND bank_name = ?
                ORDER BY last_wrong_time DESC
            ''', (user_id, bank_name))
        else:
            self.cursor.execute('''
                SELECT * FROM wrong_questions 
                WHERE user_id = ?
                ORDER BY last_wrong_time DESC
            ''', (user_id,))
        return self.cursor.fetchall()

    def remove_wrong_question(self, user_id, bank_name, question_index):
        self.cursor.execute('''
            DELETE FROM wrong_questions 
            WHERE user_id = ? AND bank_name = ? AND question_index = ?
        ''', (user_id, bank_name, question_index))
        self.conn.commit()

    def add_favorite(self, user_id, bank_name, question_index, question_text):
        try:
            self.cursor.execute('''
                INSERT INTO favorite_questions (user_id, bank_name, question_index, question_text)
                VALUES (?, ?, ?, ?)
            ''', (user_id, bank_name, question_index, question_text))
            self.conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False

    def remove_favorite(self, user_id, bank_name, question_index):
        self.cursor.execute('''
            DELETE FROM favorite_questions 
            WHERE user_id = ? AND bank_name = ? AND question_index = ?
        ''', (user_id, bank_name, question_index))
        self.conn.commit()

    def get_favorites(self, user_id, bank_name=None):
        if bank_name:
            self.cursor.execute('''
                SELECT * FROM favorite_questions 
                WHERE user_id = ? AND bank_name = ?
                ORDER BY added_time DESC
            ''', (user_id, bank_name))
        else:
            self.cursor.execute('''
                SELECT * FROM favorite_questions 
                WHERE user_id = ?
                ORDER BY added_time DESC
            ''', (user_id,))
        return self.cursor.fetchall()

    def is_favorite(self, user_id, bank_name, question_index):
        result = self.cursor.execute('''
            SELECT id FROM favorite_questions 
            WHERE user_id = ? AND bank_name = ? AND question_index = ?
        ''', (user_id, bank_name, question_index)).fetchone()
        return result is not None

    def mark_mastered(self, user_id, bank_name, question_index):
        try:
            self.cursor.execute('''
                INSERT INTO mastered_questions (user_id, bank_name, question_index)
                VALUES (?, ?, ?)
            ''', (user_id, bank_name, question_index))
            self.conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False

    def unmark_mastered(self, user_id, bank_name, question_index):
        self.cursor.execute('''
            DELETE FROM mastered_questions 
            WHERE user_id = ? AND bank_name = ? AND question_index = ?
        ''', (user_id, bank_name, question_index))
        self.conn.commit()

    def is_mastered(self, user_id, bank_name, question_index):
        result = self.cursor.execute('''
            SELECT id FROM mastered_questions 
            WHERE user_id = ? AND bank_name = ? AND question_index = ?
        ''', (user_id, bank_name, question_index)).fetchone()
        return result is not None

    def get_learning_curve_data(self, user_id, bank_name=None):
        if bank_name:
            self.cursor.execute('''
                SELECT start_time, accuracy 
                FROM quiz_records 
                WHERE user_id = ? AND bank_name = ?
                ORDER BY start_time ASC
                LIMIT 50
            ''', (user_id, bank_name))
        else:
            self.cursor.execute('''
                SELECT start_time, accuracy 
                FROM quiz_records 
                WHERE user_id = ?
                ORDER BY start_time ASC
                LIMIT 50
            ''', (user_id,))
        return self.cursor.fetchall()

    def close(self):
        self.conn.close()

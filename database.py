import sqlite3
import datetime
from typing import Optional, Dict, Any


def init_db():
    with sqlite3.connect('database.db') as conn:
        conn.execute('''
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                username TEXT,
                fullname TEXT,
                gender TEXT,
                passport TEXT,
                passport_date TEXT,
                email TEXT,
                phone TEXT,
                city TEXT,
                visa_category TEXT,
                visa_subcategory TEXT,
                is_monitoring BOOLEAN DEFAULT FALSE,
                last_active TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                registration_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # Таблица метрик
        conn.execute('''
            CREATE TABLE IF NOT EXISTS metrics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                slots_checked INTEGER DEFAULT 0,
                active_users INTEGER DEFAULT 0,
                successful_bookings INTEGER DEFAULT 0,
                errors INTEGER DEFAULT 0,
                last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')


        conn.execute('''
            CREATE TABLE IF NOT EXISTS monitoring_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                check_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                slots_available BOOLEAN,
                FOREIGN KEY(user_id) REFERENCES users(user_id)
        ''')


        conn.execute('''
            INSERT OR IGNORE INTO metrics (slots_checked, active_users) 
            VALUES (0, 0)
        ''')
        conn.commit()


def save_user(user_id: int, username: str, **kwargs):

    with sqlite3.connect('database.db') as conn:
        columns = ', '.join(kwargs.keys())
        placeholders = ', '.join(['?'] * len(kwargs))
        values = list(kwargs.values())

        # Вставка или обновление данных пользователя
        conn.execute(
            f'''
            INSERT INTO users (user_id, username, {columns}) 
            VALUES (?, ?, {placeholders})
            ON CONFLICT(user_id) DO UPDATE SET
                {', '.join([f"{k} = ?" for k in kwargs.keys()])},
                last_active = CURRENT_TIMESTAMP
            ''',
            [user_id, username] + values + values
        )
        conn.commit()


def get_user(user_id: int) -> Optional[Dict[str, Any]]:
    """Получение данных пользователя"""
    with sqlite3.connect('database.db') as conn:
        cursor = conn.execute('''
            SELECT * FROM users WHERE user_id = ?
        ''', (user_id,))
        row = cursor.fetchone()
        if row:
            columns = [column[0] for column in cursor.description]
            return dict(zip(columns, row))
        return None


def update_metrics(slots_checked: int = 0, active_users: int = 0,
                   successful: int = 0, errors: int = 0):
    """Обновление метрик"""
    with sqlite3.connect('database.db') as conn:
        conn.execute('''
            UPDATE metrics SET
                slots_checked = slots_checked + ?,
                active_users = active_users + ?,
                successful_bookings = successful_bookings + ?,
                errors = errors + ?,
                last_updated = CURRENT_TIMESTAMP
        ''', (slots_checked, active_users, successful, errors))
        conn.commit()


def log_monitoring_result(user_id: int, slots_available: bool):
    """Логирование результата проверки слотов"""
    with sqlite3.connect('database.db') as conn:
        conn.execute('''
            INSERT INTO monitoring_history (user_id, slots_available)
            VALUES (?, ?)
        ''', (user_id, slots_available))
        conn.commit()


def get_active_monitoring_users():
    """Получение списка пользователей с активным мониторингом"""
    with sqlite3.connect('database.db') as conn:
        cursor = conn.execute('''
            SELECT user_id, city, visa_category, visa_subcategory 
            FROM users 
            WHERE is_monitoring = TRUE
        ''')
        return cursor.fetchall()


def set_monitoring_status(user_id: int, status: bool):
    """Установка статуса мониторинга для пользователя"""
    with sqlite3.connect('database.db') as conn:
        conn.execute('''
            UPDATE users 
            SET is_monitoring = ?
            WHERE user_id = ?
        ''', (status, user_id))
        conn.commit()


def get_metrics():
    """Получение текущих метрик"""
    with sqlite3.connect('database.db') as conn:
        cursor = conn.execute('SELECT * FROM metrics ORDER BY id DESC LIMIT 1')
        row = cursor.fetchone()
        if row:
            columns = [column[0] for column in cursor.description]
            return dict(zip(columns, row))
        return None
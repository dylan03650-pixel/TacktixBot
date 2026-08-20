import sqlite3
import secrets
from datetime import datetime, timedelta
from contextlib import contextmanager
import time

DB_PATH = "bot.db"

@contextmanager
def get_db():
    conn = None
    try:
        conn = sqlite3.connect(DB_PATH, timeout=30, check_same_thread=False)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA journal_mode=WAL;")
        yield conn
        conn.commit()
    except Exception as e:
        if conn:
            conn.rollback()
        raise e
    finally:
        if conn:
            conn.close()

def init_db():
    with get_db() as conn:
        conn.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            username TEXT,
            first_name TEXT,
            referral_code TEXT UNIQUE,
            referred_by INTEGER,
            subscription_expires TEXT,
            balance REAL DEFAULT 0,
            referral_count INTEGER DEFAULT 0,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
        """)

def get_or_create_user(user_id: int, username: str = None, first_name: str = None, referred_by: int = None):
    with get_db() as conn:
        row = conn.execute("SELECT * FROM users WHERE user_id = ?", (user_id,)).fetchone()
        if row:
            return dict(row)
        
        code = secrets.token_urlsafe(8)[:10]
        conn.execute(
            "INSERT INTO users (user_id, username, first_name, referral_code, referred_by) VALUES (?, ?, ?, ?, ?)",
            (user_id, username, first_name, code, referred_by)
        )
        if referred_by:
            conn.execute("UPDATE users SET referral_count = referral_count + 1 WHERE user_id = ?", (referred_by,))
        
        row = conn.execute("SELECT * FROM users WHERE user_id = ?", (user_id,)).fetchone()
        return dict(row)

def is_subscribed(user_id: int) -> bool:
    with get_db() as conn:
        row = conn.execute("SELECT subscription_expires FROM users WHERE user_id = ?", (user_id,)).fetchone()
        if not row or not row["subscription_expires"]:
            return False
        try:
            return datetime.fromisoformat(row["subscription_expires"]) > datetime.utcnow()
        except:
            return False

def activate_subscription(user_id: int, months: int = 1):
    expires = datetime.utcnow() + timedelta(days=30 * months)
    with get_db() as conn:
        conn.execute(
            "UPDATE users SET subscription_expires = ? WHERE user_id = ?",
            (expires.isoformat(), user_id)
        )

def get_user(user_id: int):
    with get_db() as conn:
        row = conn.execute("SELECT * FROM users WHERE user_id = ?", (user_id,)).fetchone()
        return dict(row) if row else None

def get_user_by_referral_code(code: str):
    with get_db() as conn:
        row = conn.execute("SELECT * FROM users WHERE referral_code = ?", (code,)).fetchone()
        return dict(row) if row else None

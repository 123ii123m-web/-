import json
import sqlite3
import os
import logging
from typing import Any
from config import Config

logger = logging.getLogger(__name__)

class Storage:
    """ذخیره‌سازی لوکال — SQLite + JSON fallback"""

    def __init__(self):
        self.db_path = Config.STORAGE_PATH or "bot_data.db"
        self._init_db()

    def _init_db(self):
        """ساخت جدول‌ها اگه وجود نداشته باشن"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    user_id INTEGER PRIMARY KEY,
                    username TEXT,
                    first_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    data TEXT DEFAULT '{}'
                )
            """)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS stats (
                    key TEXT PRIMARY KEY,
                    value TEXT
                )
            """)
            conn.commit()
        logger.info(f"✅ Storage initialized: {self.db_path}")

    def get_user(self, user_id: int) -> dict | None:
        """گرفتن اطلاعات یوزر"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            row = conn.execute(
                "SELECT * FROM users WHERE user_id = ?", (user_id,)
            ).fetchone()
            if row:
                data = dict(row)
                data["data"] = json.loads(data.get("data", "{}"))
                return data
        return None

    def upsert_user(self, user_id: int, username: str = "", data: dict = None):
        """اضافه یا آپدیت یوزر"""
        existing = self.get_user(user_id)
        current_data = json.loads(existing["data"]) if existing else {}
        if data:
            current_data.update(data)

        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT INTO users (user_id, username, last_seen, data)
                VALUES (?, ?, CURRENT_TIMESTAMP, ?)
                ON CONFLICT(user_id) DO UPDATE SET
                    username = COALESCE(NULLIF(?, ''), username),
                    last_seen = CURRENT_TIMESTAMP,
                    data = ?
            """, (user_id, username, json.dumps(current_data),
                  username, json.dumps(current_data)))
            conn.commit()

    def get_stat(self, key: str) -> str | None:
        with sqlite3.connect(self.db_path) as conn:
            row = conn.execute(
                "SELECT value FROM stats WHERE key = ?", (key,)
            ).fetchone()
            return row[0] if row else None

    def set_stat(self, key: str, value: Any):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT INTO stats (key, value) VALUES (?, ?)
                ON CONFLICT(key) DO UPDATE SET value = ?
            """, (key, str(value), str(value)))
            conn.commit()

    def get_all_users(self) -> list[int]:
        """لیست همه user_id ها"""
        with sqlite3.connect(self.db_path) as conn:
            rows = conn.execute("SELECT user_id FROM users").fetchall()
            return [r[0] for r in rows]

    def count_users(self) -> int:
        with sqlite3.connect(self.db_path) as conn:
            return conn.execute("SELECT COUNT(*) FROM users").fetchone()[0]

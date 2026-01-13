import os
import sqlite3
from contextlib import contextmanager
from typing import Iterable, Tuple


DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "results.db")


def init_db() -> None:
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS results (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                message TEXT NOT NULL,
                method TEXT NOT NULL,
                result TEXT NOT NULL
            )
            """
        )


def insert_result(message: str, method: str, result: str) -> None:
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute(
            "INSERT INTO results (message, method, result) VALUES (?, ?, ?)",
            (message, method, result),
        )


def fetch_recent(limit: int = 50) -> Iterable[Tuple[int, str, str, str, str]]:
    with sqlite3.connect(DB_PATH) as conn:
        conn.row_factory = sqlite3.Row
        cur = conn.execute(
            "SELECT id, created_at, message, method, result FROM results ORDER BY id DESC LIMIT ?",
            (limit,),
        )
        for row in cur.fetchall():
            yield (
                row["id"],
                row["created_at"],
                row["message"],
                row["method"],
                row["result"],
            )



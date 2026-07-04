import sqlite3
import os
from config import DB_PATH


def get_connection() -> sqlite3.Connection:
    """Return a connection to the SQLite banking database."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def run_query(sql: str, params: tuple = ()) -> list[dict]:
    """Execute a read query and return results as a list of dicts."""
    conn = get_connection()
    try:
        cursor = conn.execute(sql, params)
        columns = [desc[0] for desc in cursor.description]
        rows = [dict(zip(columns, row)) for row in cursor.fetchall()]
        return rows
    finally:
        conn.close()


def run_write(sql: str, params: tuple = ()) -> int:
    """Execute a write query and return rows affected."""
    conn = get_connection()
    try:
        cursor = conn.execute(sql, params)
        conn.commit()
        return cursor.rowcount
    finally:
        conn.close()

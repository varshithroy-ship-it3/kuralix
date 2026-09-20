"""
Kuralix Offline Storage — SQLite
"""

import sqlite3
import json
import os
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "kuralix.db")


def init_db():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS submissions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            created_at TEXT NOT NULL,
            language TEXT,
            raw_text TEXT,
            form_data TEXT,
            overall_confidence REAL,
            synced INTEGER DEFAULT 0
        )
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS corrections (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            submission_id INTEGER,
            field_id TEXT,
            original_value TEXT,
            corrected_value TEXT,
            created_at TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()


def save_submission(language: str, raw_text: str, mapped: dict) -> int:
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO submissions (created_at, language, raw_text, form_data, overall_confidence)
        VALUES (?, ?, ?, ?, ?)
    """, (
        datetime.utcnow().isoformat(),
        language,
        raw_text,
        json.dumps(mapped["form"]),
        mapped["overall_confidence"],
    ))
    sid = cur.lastrowid
    conn.commit()
    conn.close()
    return sid


def save_correction(submission_id: int, field_id: str, original: str, corrected: str):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO corrections (submission_id, field_id, original_value, corrected_value, created_at)
        VALUES (?, ?, ?, ?, ?)
    """, (submission_id, field_id, original, corrected, datetime.utcnow().isoformat()))
    conn.commit()
    conn.close()


def get_pending_sync() -> list:
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT id, form_data FROM submissions WHERE synced = 0")
    rows = cur.fetchall()
    conn.close()
    return [{"id": r[0], "form_data": json.loads(r[1])} for r in rows]


def mark_synced(submission_id: int):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("UPDATE submissions SET synced = 1 WHERE id = ?", (submission_id,))
    conn.commit()
    conn.close()


def get_correction_stats() -> dict:
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT field_id, COUNT(*) FROM corrections GROUP BY field_id")
    rows = cur.fetchall()
    conn.close()
    return {r[0]: r[1] for r in rows}
import os
import sqlite3
from contextlib import contextmanager
from typing import Generator

from server.app.core.config import DB_PATH

_SCHEMA = """
CREATE TABLE IF NOT EXISTS workstations (
    id          INTEGER PRIMARY KEY,
    name        TEXT NOT NULL UNIQUE,
    ip_address  TEXT,
    is_online   INTEGER NOT NULL DEFAULT 0,
    last_seen   TEXT
);

CREATE TABLE IF NOT EXISTS sessions (
    id                INTEGER PRIMARY KEY AUTOINCREMENT,
    workstation_id    INTEGER NOT NULL REFERENCES workstations(id),
    student_name      TEXT NOT NULL,
    nim               TEXT NOT NULL,
    program_studi     TEXT NOT NULL DEFAULT '',
    keterangan        TEXT NOT NULL DEFAULT '',
    pin               TEXT NOT NULL UNIQUE,
    duration_minutes  INTEGER NOT NULL,
    started_at        TEXT,
    expires_at        TEXT,
    extended_minutes  INTEGER NOT NULL DEFAULT 0,
    status            TEXT NOT NULL DEFAULT 'PENDING',
    warning_sent      INTEGER NOT NULL DEFAULT 0,
    created_at        TEXT NOT NULL,
    ended_at          TEXT
);

CREATE TABLE IF NOT EXISTS session_extensions (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id      INTEGER NOT NULL REFERENCES sessions(id),
    added_minutes   INTEGER NOT NULL,
    extended_at     TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS audit_log (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    event_type      TEXT NOT NULL,
    session_id      INTEGER REFERENCES sessions(id),
    workstation_id  INTEGER REFERENCES workstations(id),
    detail          TEXT,
    created_at      TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_sessions_pin        ON sessions(pin);
CREATE INDEX IF NOT EXISTS idx_sessions_status     ON sessions(status);
CREATE INDEX IF NOT EXISTS idx_sessions_workstation ON sessions(workstation_id, status);

INSERT OR IGNORE INTO workstations (id, name) VALUES (1, 'PC-1');
INSERT OR IGNORE INTO workstations (id, name) VALUES (2, 'PC-2');
"""


def init_db() -> None:
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    with sqlite3.connect(DB_PATH) as conn:
        conn.executescript(_SCHEMA)
        for sql in [
            "ALTER TABLE sessions ADD COLUMN program_studi TEXT NOT NULL DEFAULT ''",
            "ALTER TABLE sessions ADD COLUMN keterangan TEXT NOT NULL DEFAULT ''",
        ]:
            try:
                conn.execute(sql)
            except Exception:
                pass
        conn.commit()


@contextmanager
def get_db() -> Generator[sqlite3.Connection, None, None]:
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()

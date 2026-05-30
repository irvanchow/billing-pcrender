import json
import sqlite3
from datetime import datetime, timezone
from typing import Optional

from shared.constants import SessionStatus


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _log(conn: sqlite3.Connection, event_type: str, session_id: Optional[int] = None,
         workstation_id: Optional[int] = None, detail: Optional[dict] = None) -> None:
    conn.execute(
        "INSERT INTO audit_log (event_type, session_id, workstation_id, detail, created_at) "
        "VALUES (?, ?, ?, ?, ?)",
        (event_type, session_id, workstation_id, json.dumps(detail) if detail else None, _now_iso()),
    )


def create_session(conn: sqlite3.Connection, workstation_id: int, student_name: str,
                   nim: str, duration_minutes: int, pin: str) -> int:
    cursor = conn.execute(
        "INSERT INTO sessions (workstation_id, student_name, nim, pin, duration_minutes, "
        "status, created_at) VALUES (?, ?, ?, ?, ?, ?, ?)",
        (workstation_id, student_name, nim, pin, duration_minutes,
         SessionStatus.PENDING.value, _now_iso()),
    )
    session_id = cursor.lastrowid
    _log(conn, "SESSION_CREATED", session_id=session_id, workstation_id=workstation_id,
         detail={"student_name": student_name, "nim": nim, "duration_minutes": duration_minutes})
    return session_id


def activate_session(conn: sqlite3.Connection, pin: str, workstation_id: int) -> Optional[dict]:
    row = conn.execute(
        "SELECT * FROM sessions WHERE pin = ? AND workstation_id = ? AND status = ?",
        (pin, workstation_id, SessionStatus.PENDING.value),
    ).fetchone()
    if row is None:
        return None

    now = datetime.now(timezone.utc)
    started_at = now.isoformat()
    total_minutes = row["duration_minutes"] + row["extended_minutes"]
    expires_at = datetime.fromtimestamp(
        now.timestamp() + total_minutes * 60, tz=timezone.utc
    ).isoformat()

    conn.execute(
        "UPDATE sessions SET status = ?, started_at = ?, expires_at = ? WHERE id = ?",
        (SessionStatus.ACTIVE.value, started_at, expires_at, row["id"]),
    )
    _log(conn, "PIN_USED", session_id=row["id"], workstation_id=workstation_id)

    return {
        "session_id": row["id"],
        "student_name": row["student_name"],
        "nim": row["nim"],
        "expires_at": expires_at,
        "remaining_seconds": total_minutes * 60,
    }


def extend_session(conn: sqlite3.Connection, session_id: int, added_minutes: int) -> Optional[dict]:
    row = conn.execute("SELECT * FROM sessions WHERE id = ?", (session_id,)).fetchone()
    if row is None:
        return None
    if row["status"] not in (SessionStatus.PENDING.value, SessionStatus.ACTIVE.value):
        return None

    conn.execute(
        "UPDATE sessions SET extended_minutes = extended_minutes + ? WHERE id = ?",
        (added_minutes, session_id),
    )

    new_expires_at = None
    remaining_seconds = None

    if row["status"] == SessionStatus.ACTIVE.value and row["expires_at"]:
        old_expires = datetime.fromisoformat(row["expires_at"])
        new_expires = datetime.fromtimestamp(
            old_expires.timestamp() + added_minutes * 60, tz=timezone.utc
        )
        new_expires_at = new_expires.isoformat()
        conn.execute(
            "UPDATE sessions SET expires_at = ? WHERE id = ?",
            (new_expires_at, session_id),
        )
        remaining_seconds = max(0, int(new_expires.timestamp() - datetime.now(timezone.utc).timestamp()))

    conn.execute(
        "INSERT INTO session_extensions (session_id, added_minutes, extended_at) VALUES (?, ?, ?)",
        (session_id, added_minutes, _now_iso()),
    )
    _log(conn, "SESSION_EXTENDED", session_id=session_id, detail={"added_minutes": added_minutes})

    return {"new_expires_at": new_expires_at, "remaining_seconds": remaining_seconds}


def terminate_session(conn: sqlite3.Connection, session_id: int) -> bool:
    row = conn.execute("SELECT status FROM sessions WHERE id = ?", (session_id,)).fetchone()
    if row is None:
        return False
    if row["status"] in (SessionStatus.EXPIRED.value, SessionStatus.TERMINATED.value,
                         SessionStatus.COMPLETED.value):
        return False

    conn.execute(
        "UPDATE sessions SET status = ?, ended_at = ? WHERE id = ?",
        (SessionStatus.TERMINATED.value, _now_iso(), session_id),
    )
    _log(conn, "SESSION_TERMINATED", session_id=session_id)
    return True


def expire_session(conn: sqlite3.Connection, session_id: int) -> bool:
    conn.execute(
        "UPDATE sessions SET status = ?, ended_at = ? WHERE id = ? AND status = ?",
        (SessionStatus.EXPIRED.value, _now_iso(), session_id, SessionStatus.ACTIVE.value),
    )
    _log(conn, "SESSION_EXPIRED", session_id=session_id)
    return True


def get_workstation_session(conn: sqlite3.Connection, workstation_id: int) -> Optional[dict]:
    row = conn.execute(
        "SELECT * FROM sessions WHERE workstation_id = ? AND status IN (?, ?) "
        "ORDER BY created_at DESC LIMIT 1",
        (workstation_id, SessionStatus.PENDING.value, SessionStatus.ACTIVE.value),
    ).fetchone()
    return dict(row) if row else None


def compute_remaining(expires_at: Optional[str]) -> int:
    if not expires_at:
        return 0
    expiry = datetime.fromisoformat(expires_at)
    remaining = expiry.timestamp() - datetime.now(timezone.utc).timestamp()
    return max(0, int(remaining))

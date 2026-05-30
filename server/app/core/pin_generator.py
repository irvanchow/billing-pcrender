import secrets
import sqlite3

from shared.constants import PIN_LENGTH, SessionStatus


def generate_unique_pin(conn: sqlite3.Connection) -> str:
    active_statuses = (SessionStatus.PENDING.value, SessionStatus.ACTIVE.value)
    placeholders = ",".join("?" * len(active_statuses))
    while True:
        pin = f"{secrets.randbelow(10 ** PIN_LENGTH):0{PIN_LENGTH}d}"
        row = conn.execute(
            f"SELECT id FROM sessions WHERE pin = ? AND status IN ({placeholders})",
            (pin, *active_statuses),
        ).fetchone()
        if row is None:
            return pin

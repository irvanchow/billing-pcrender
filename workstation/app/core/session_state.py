from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Optional


class State(Enum):
    LOCKED = "LOCKED"
    ACTIVE = "ACTIVE"


@dataclass
class SessionState:
    state: State = State.LOCKED
    session_id: Optional[int] = None
    student_name: Optional[str] = None
    expires_at: Optional[str] = None
    warning_shown: bool = False

    def activate(self, session_id: int, student_name: str, expires_at: str) -> None:
        self.state = State.ACTIVE
        self.session_id = session_id
        self.student_name = student_name
        self.expires_at = expires_at
        self.warning_shown = False

    def lock(self) -> None:
        self.state = State.LOCKED
        self.session_id = None
        self.student_name = None
        self.expires_at = None
        self.warning_shown = False

    def remaining_seconds(self) -> int:
        if not self.expires_at:
            return 0
        expiry = datetime.fromisoformat(self.expires_at)
        return max(0, int(expiry.timestamp() - datetime.now(timezone.utc).timestamp()))

    def sync_expiry(self, new_expires_at: str) -> None:
        self.expires_at = new_expires_at

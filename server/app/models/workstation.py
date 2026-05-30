from typing import Optional
from pydantic import BaseModel


class HeartbeatRequest(BaseModel):
    ip_address: Optional[str] = None


class UnlockRequest(BaseModel):
    pin: str


class UnlockResponse(BaseModel):
    session_id: int
    student_name: str
    nim: str
    expires_at: str
    remaining_seconds: int


class WorkstationSessionResponse(BaseModel):
    status: str  # IDLE, ACTIVE, LOCK
    session_id: Optional[int] = None
    student_name: Optional[str] = None
    expires_at: Optional[str] = None
    remaining_seconds: Optional[int] = None
    warning_threshold_seconds: int = 300


class WorkstationInfo(BaseModel):
    id: int
    name: str
    ip_address: Optional[str]
    is_online: bool
    last_seen: Optional[str]
    current_session: Optional[dict] = None


class SessionExpiredRequest(BaseModel):
    session_id: int

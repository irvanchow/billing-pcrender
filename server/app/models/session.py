from typing import Optional
from pydantic import BaseModel, Field


class SessionCreate(BaseModel):
    workstation_id: int = Field(..., ge=1, le=2)
    student_name: str = Field(..., min_length=1, max_length=100)
    nim: str = Field(..., min_length=1, max_length=20)
    duration_minutes: int = Field(..., ge=5, le=480)


class SessionExtend(BaseModel):
    additional_minutes: int = Field(..., ge=5, le=480)


class SessionResponse(BaseModel):
    session_id: int
    workstation_id: int
    student_name: str
    nim: str
    pin: str
    status: str
    duration_minutes: int
    extended_minutes: int
    started_at: Optional[str]
    expires_at: Optional[str]
    remaining_seconds: Optional[int]
    created_at: str
    ended_at: Optional[str]


class SessionCreatedResponse(BaseModel):
    session_id: int
    pin: str
    workstation_id: int
    student_name: str
    duration_minutes: int


class ExtendResponse(BaseModel):
    new_expires_at: Optional[str]
    remaining_seconds: Optional[int]

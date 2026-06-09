from typing import Optional
from pydantic import BaseModel, Field


class SessionCreate(BaseModel):
    workstation_id: int = Field(..., ge=1, le=4)
    student_name: str = Field(..., min_length=1, max_length=100)
    nim: str = Field(..., min_length=1, max_length=20)
    program_studi: str = Field(..., min_length=1, max_length=50)
    keterangan: str = Field("", max_length=500)
    duration_minutes: int = Field(..., ge=5, le=480)


class SessionExtend(BaseModel):
    additional_minutes: int = Field(..., ge=5, le=480)


class SessionResponse(BaseModel):
    session_id: int
    workstation_id: int
    student_name: str
    nim: str
    program_studi: str
    keterangan: str
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
    program_studi: str
    duration_minutes: int


class ExtendResponse(BaseModel):
    new_expires_at: Optional[str]
    remaining_seconds: Optional[int]

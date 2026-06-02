import sqlite3
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status

from server.app.api.deps import db_dep, verify_api_key
from server.app.core.pin_generator import generate_unique_pin
from server.app.core.session_manager import (
    compute_remaining,
    create_session,
    extend_session,
    terminate_session,
)
from server.app.models.session import (
    ExtendResponse,
    SessionCreate,
    SessionCreatedResponse,
    SessionExtend,
    SessionResponse,
)
from shared.constants import SessionStatus

router = APIRouter(prefix="/sessions", dependencies=[Depends(verify_api_key)])


def _row_to_response(row) -> SessionResponse:
    d = dict(row)
    remaining = compute_remaining(d.get("expires_at")) if d.get("status") == SessionStatus.ACTIVE else None
    return SessionResponse(
        session_id=d["id"],
        workstation_id=d["workstation_id"],
        student_name=d["student_name"],
        nim=d["nim"],
        program_studi=d.get("program_studi", ""),
        keterangan=d.get("keterangan", ""),
        pin=d["pin"],
        status=d["status"],
        duration_minutes=d["duration_minutes"],
        extended_minutes=d["extended_minutes"],
        started_at=d.get("started_at"),
        expires_at=d.get("expires_at"),
        remaining_seconds=remaining,
        created_at=d["created_at"],
        ended_at=d.get("ended_at"),
    )


@router.post("", response_model=SessionCreatedResponse, status_code=status.HTTP_201_CREATED)
def create(body: SessionCreate, conn: sqlite3.Connection = Depends(db_dep)):
    ws = conn.execute("SELECT id FROM workstations WHERE id = ?", (body.workstation_id,)).fetchone()
    if ws is None:
        raise HTTPException(status_code=404, detail="Workstation not found")

    occupied = conn.execute(
        "SELECT id FROM sessions WHERE workstation_id = ? AND status IN (?, ?)",
        (body.workstation_id, SessionStatus.PENDING.value, SessionStatus.ACTIVE.value),
    ).fetchone()
    if occupied:
        raise HTTPException(status_code=409, detail="Workstation already has an active/pending session")

    pin = generate_unique_pin(conn)
    session_id = create_session(conn, body.workstation_id, body.student_name, body.nim,
                                body.program_studi, body.keterangan, body.duration_minutes, pin)
    return SessionCreatedResponse(
        session_id=session_id,
        pin=pin,
        workstation_id=body.workstation_id,
        student_name=body.student_name,
        program_studi=body.program_studi,
        duration_minutes=body.duration_minutes,
    )


@router.get("", response_model=List[SessionResponse])
def list_sessions(
    status_filter: Optional[List[str]] = Query(None, alias="status"),
    conn: sqlite3.Connection = Depends(db_dep),
):
    if status_filter:
        placeholders = ",".join("?" * len(status_filter))
        rows = conn.execute(
            f"SELECT * FROM sessions WHERE status IN ({placeholders}) ORDER BY created_at DESC",
            status_filter,
        ).fetchall()
    else:
        rows = conn.execute(
            "SELECT * FROM sessions WHERE status IN (?, ?) ORDER BY created_at DESC",
            (SessionStatus.PENDING.value, SessionStatus.ACTIVE.value),
        ).fetchall()
    return [_row_to_response(r) for r in rows]


@router.get("/history", response_model=List[SessionResponse])
def history(
    date: Optional[str] = Query(None),
    workstation_id: Optional[int] = Query(None),
    page: int = Query(1, ge=1),
    limit: int = Query(50, ge=1, le=200),
    conn: sqlite3.Connection = Depends(db_dep),
):
    clauses = []
    params: list = []
    if date:
        clauses.append("DATE(created_at) = ?")
        params.append(date)
    if workstation_id:
        clauses.append("workstation_id = ?")
        params.append(workstation_id)

    where = ("WHERE " + " AND ".join(clauses)) if clauses else ""
    offset = (page - 1) * limit
    params.extend([limit, offset])
    rows = conn.execute(
        f"SELECT * FROM sessions {where} ORDER BY created_at DESC LIMIT ? OFFSET ?",
        params,
    ).fetchall()
    return [_row_to_response(r) for r in rows]


@router.get("/{session_id}", response_model=SessionResponse)
def get_session(session_id: int, conn: sqlite3.Connection = Depends(db_dep)):
    row = conn.execute("SELECT * FROM sessions WHERE id = ?", (session_id,)).fetchone()
    if row is None:
        raise HTTPException(status_code=404, detail="Session not found")
    return _row_to_response(row)


@router.patch("/{session_id}/extend", response_model=ExtendResponse)
def extend(session_id: int, body: SessionExtend, conn: sqlite3.Connection = Depends(db_dep)):
    result = extend_session(conn, session_id, body.additional_minutes)
    if result is None:
        raise HTTPException(status_code=404, detail="Session not found or not extendable")
    return ExtendResponse(**result)


@router.delete("/{session_id}", status_code=status.HTTP_200_OK)
def terminate(session_id: int, conn: sqlite3.Connection = Depends(db_dep)):
    ok = terminate_session(conn, session_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Session not found or already ended")
    return {"status": SessionStatus.TERMINATED.value}

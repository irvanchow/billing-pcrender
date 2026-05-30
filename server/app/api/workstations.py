import sqlite3
from datetime import datetime, timezone
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status

from server.app.api.deps import db_dep, verify_api_key
from server.app.core.session_manager import (
    activate_session,
    compute_remaining,
    expire_session,
    get_workstation_session,
)
from server.app.models.workstation import (
    HeartbeatRequest,
    SessionExpiredRequest,
    UnlockRequest,
    UnlockResponse,
    WorkstationInfo,
    WorkstationSessionResponse,
)
from shared.constants import SessionStatus, WARNING_THRESHOLD_SECONDS

router = APIRouter(prefix="/workstations", dependencies=[Depends(verify_api_key)])


@router.get("", response_model=List[WorkstationInfo])
def list_workstations(conn: sqlite3.Connection = Depends(db_dep)):
    rows = conn.execute("SELECT * FROM workstations ORDER BY id").fetchall()
    result = []
    for row in rows:
        d = dict(row)
        session = get_workstation_session(conn, d["id"])
        if session and session["status"] == SessionStatus.ACTIVE.value:
            session["remaining_seconds"] = compute_remaining(session.get("expires_at"))
        result.append(WorkstationInfo(
            id=d["id"],
            name=d["name"],
            ip_address=d.get("ip_address"),
            is_online=bool(d["is_online"]),
            last_seen=d.get("last_seen"),
            current_session=session,
        ))
    return result


@router.post("/{pc_id}/heartbeat")
def heartbeat(pc_id: int, body: HeartbeatRequest, conn: sqlite3.Connection = Depends(db_dep)):
    ws = conn.execute("SELECT id FROM workstations WHERE id = ?", (pc_id,)).fetchone()
    if ws is None:
        raise HTTPException(status_code=404, detail="Workstation not found")
    conn.execute(
        "UPDATE workstations SET is_online = 1, last_seen = ?, ip_address = COALESCE(?, ip_address) WHERE id = ?",
        (datetime.now(timezone.utc).isoformat(), body.ip_address, pc_id),
    )
    return {"status": "ok"}


@router.post("/{pc_id}/unlock", response_model=UnlockResponse)
def unlock(pc_id: int, body: UnlockRequest, conn: sqlite3.Connection = Depends(db_dep)):
    result = activate_session(conn, body.pin, pc_id)
    if result is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired PIN")
    return UnlockResponse(**result)


@router.get("/{pc_id}/session", response_model=WorkstationSessionResponse)
def get_session(pc_id: int, conn: sqlite3.Connection = Depends(db_dep)):
    ws = conn.execute("SELECT id FROM workstations WHERE id = ?", (pc_id,)).fetchone()
    if ws is None:
        raise HTTPException(status_code=404, detail="Workstation not found")

    session = get_workstation_session(conn, pc_id)

    if session is None:
        return WorkstationSessionResponse(status="IDLE")

    if session["status"] == SessionStatus.PENDING.value:
        return WorkstationSessionResponse(status="IDLE")

    if session["status"] == SessionStatus.ACTIVE.value:
        remaining = compute_remaining(session.get("expires_at"))
        if remaining <= 0:
            expire_session(conn, session["id"])
            return WorkstationSessionResponse(status="IDLE")

        if remaining <= WARNING_THRESHOLD_SECONDS and not session["warning_sent"]:
            conn.execute("UPDATE sessions SET warning_sent = 1 WHERE id = ?", (session["id"],))

        return WorkstationSessionResponse(
            status="ACTIVE",
            session_id=session["id"],
            student_name=session["student_name"],
            expires_at=session["expires_at"],
            remaining_seconds=remaining,
            warning_threshold_seconds=WARNING_THRESHOLD_SECONDS,
        )

    return WorkstationSessionResponse(status="LOCK")


@router.post("/{pc_id}/session/expired")
def report_expired(pc_id: int, body: SessionExpiredRequest, conn: sqlite3.Connection = Depends(db_dep)):
    expire_session(conn, body.session_id)
    return {"status": "ok"}

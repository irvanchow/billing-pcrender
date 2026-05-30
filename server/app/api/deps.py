import sqlite3
from typing import Generator

from fastapi import Depends, HTTPException, Security, status
from fastapi.security import APIKeyHeader

from server.app.core.config import API_KEY
from server.app.core.database import get_db

_api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)


def verify_api_key(key: str = Security(_api_key_header)) -> None:
    if key != API_KEY:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid API key")


def db_dep() -> Generator[sqlite3.Connection, None, None]:
    with get_db() as conn:
        yield conn

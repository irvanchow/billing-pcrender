import socket
import threading
import time
from typing import Callable, Optional

import requests

from shared.constants import API_PREFIX
from workstation.app.core.config import API_KEY, PC_ID, POLL_INTERVAL, SERVER_URL

_HEADERS = {"X-API-Key": API_KEY}
_TIMEOUT = 5


def _base() -> str:
    return f"{SERVER_URL}{API_PREFIX}/workstations/{PC_ID}"


def _my_ip() -> str:
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return ""


def send_heartbeat() -> None:
    try:
        requests.post(
            f"{_base()}/heartbeat",
            json={"ip_address": _my_ip()},
            headers=_HEADERS,
            timeout=_TIMEOUT,
        )
    except Exception:
        pass


def poll_session() -> Optional[dict]:
    try:
        r = requests.get(f"{_base()}/session", headers=_HEADERS, timeout=_TIMEOUT)
        if r.status_code == 200:
            return r.json()
    except Exception:
        pass
    return None


def unlock_with_pin(pin: str) -> Optional[dict]:
    try:
        r = requests.post(
            f"{_base()}/unlock",
            json={"pin": pin},
            headers=_HEADERS,
            timeout=_TIMEOUT,
        )
        if r.status_code == 200:
            return r.json()
        # Surface the server's error detail so the caller can show a meaningful message
        try:
            detail = r.json().get("detail", "")
        except Exception:
            detail = ""
        raise RuntimeError(detail or f"HTTP {r.status_code}")
    except requests.exceptions.ConnectionError:
        raise RuntimeError(f"Tidak dapat terhubung ke server ({SERVER_URL})")
    except requests.exceptions.Timeout:
        raise RuntimeError("Koneksi ke server timeout")


def report_expired(session_id: int) -> None:
    try:
        requests.post(
            f"{_base()}/session/expired",
            json={"session_id": session_id},
            headers=_HEADERS,
            timeout=_TIMEOUT,
        )
    except Exception:
        pass


class PollingThread(threading.Thread):
    def __init__(self, on_status: Callable[[dict], None]):
        super().__init__(daemon=True)
        self._on_status = on_status
        self._running = True
        self._heartbeat_counter = 0

    def run(self) -> None:
        send_heartbeat()
        while self._running:
            self._heartbeat_counter += 1
            if self._heartbeat_counter >= (10 // POLL_INTERVAL):
                send_heartbeat()
                self._heartbeat_counter = 0

            status = poll_session()
            if status is not None:
                self._on_status(status)
            time.sleep(POLL_INTERVAL)

    def stop(self) -> None:
        self._running = False

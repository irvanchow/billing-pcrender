import configparser
import os
import sys


def _get_config_path() -> str:
    if getattr(sys, "frozen", False):
        return os.path.join(os.path.dirname(sys.executable), "config.ini")
    return os.path.join(os.path.dirname(__file__), "..", "..", "config.ini")


def _load() -> dict:
    cfg = configparser.ConfigParser()
    path = _get_config_path()
    if os.path.exists(path):
        cfg.read(path)

    section = cfg["workstation"] if "workstation" in cfg else {}
    return {
        "server_url": section.get("SERVER_URL", "http://127.0.0.1:8765"),
        "api_key": section.get("API_KEY", "idb-bali-default-key"),
        "pc_id": int(section.get("PC_ID", "1")),
        "poll_interval": int(section.get("POLL_INTERVAL", "5")),
    }


_config = _load()

SERVER_URL: str = _config["server_url"].rstrip("/")
API_KEY: str = _config["api_key"]
PC_ID: int = _config["pc_id"]
POLL_INTERVAL: int = _config["poll_interval"]

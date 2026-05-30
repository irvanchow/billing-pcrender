import configparser
import os
import sys


def _get_data_dir() -> str:
    if getattr(sys, "frozen", False):
        return os.path.join(os.path.dirname(sys.executable), "data")
    return os.path.join(os.path.dirname(__file__), "..", "..", "..", "data")


def _get_config_path() -> str:
    if getattr(sys, "frozen", False):
        return os.path.join(os.path.dirname(sys.executable), "config.ini")
    return os.path.join(os.path.dirname(__file__), "..", "..", "..", "config.ini")


def _load() -> dict:
    cfg = configparser.ConfigParser()
    path = _get_config_path()
    if os.path.exists(path):
        cfg.read(path)

    section = cfg["server"] if "server" in cfg else {}
    return {
        "host": section.get("HOST", "0.0.0.0"),
        "port": int(section.get("PORT", "8765")),
        "api_key": section.get("API_KEY", "idb-bali-default-key"),
        "db_path": os.path.join(
            _get_data_dir(),
            section.get("DB_NAME", "rental.db"),
        ),
    }


_config = _load()

HOST: str = _config["host"]
PORT: int = _config["port"]
API_KEY: str = _config["api_key"]
DB_PATH: str = _config["db_path"]


def write_default_config() -> None:
    path = _get_config_path()
    if os.path.exists(path):
        return
    cfg = configparser.ConfigParser()
    cfg["server"] = {
        "HOST": "0.0.0.0",
        "PORT": "8765",
        "API_KEY": "CHANGE_THIS_SECRET_KEY",
        "DB_NAME": "rental.db",
    }
    with open(path, "w") as f:
        cfg.write(f)

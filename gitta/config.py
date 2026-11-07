"""Persistent settings, stored as JSON in %APPDATA%\\Gitta\\config.json."""

import json
import os

_DEFAULT = {
    "client_id": "",
    "token": "",
    "login": "",
    "user_id": 0,
    "name": "",
    "default_parent": "",
    "projects": {},  # "owner/repo" -> local folder
}


def _path():
    base = os.environ.get("APPDATA") or os.path.expanduser("~")
    return os.path.join(base, "Gitta", "config.json")


def load():
    cfg = json.loads(json.dumps(_DEFAULT))
    try:
        with open(_path(), encoding="utf-8") as fh:
            cfg.update(json.load(fh))
    except (OSError, ValueError):
        pass
    return cfg


def save(cfg):
    path = _path()
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(cfg, fh, indent=2, ensure_ascii=False)

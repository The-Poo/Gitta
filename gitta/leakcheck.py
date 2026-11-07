"""Warn before secrets are published.

Looks at file names (``.env``, ``*.pem`` ...) and at file contents (API keys,
tokens, private keys, ``password = "..."``). It never returns the secret
itself, only the file, line number and kind, so nothing sensitive ends up in a
dialog or log. It is a safety net, not a guarantee.
"""

import fnmatch
import os
import re

MAX_BYTES = 1_000_000
MAX_FILES = 5000
SKIP_DIRS = {".git", "node_modules", "__pycache__", ".venv", "venv", "dist", "build"}

NAME_PATTERNS = (".env", ".env.*", "*.pem", "*.key", "*.pfx", "*.p12", "*.kdbx",
                 "id_rsa*", "id_ed25519*", "*.token", "*secret*", "*password*",
                 "*credential*")

CONTENT_PATTERNS = (
    ("privat nyckel", re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY")),
    ("GitHub-token", re.compile(r"\bgh[pousr]_[A-Za-z0-9]{36,}\b")),
    ("GitHub-token", re.compile(r"\bgithub_pat_[A-Za-z0-9_]{50,}\b")),
    ("AWS-nyckel", re.compile(r"\bAKIA[0-9A-Z]{16}\b")),
    ("API-nyckel (sk-...)", re.compile(r"\bsk-[A-Za-z0-9_-]{20,}\b")),
    ("Google API-nyckel", re.compile(r"\bAIza[0-9A-Za-z_-]{35}\b")),
    ("Slack-token", re.compile(r"\bxox[baprs]-[A-Za-z0-9-]{10,}\b")),
    ("lösenord eller nyckel i text",
     re.compile(r"(?i)\b(password|passwd|pwd|secret|api[_-]?key|token)\b"
                r"\s*[:=]\s*[\"'][^\"'\s]{8,}[\"']")),
)


def _name_hit(name):
    base = os.path.basename(name).lower()
    return any(fnmatch.fnmatch(base, pat) for pat in NAME_PATTERNS)


def _scan_text(path):
    try:
        if os.path.getsize(path) > MAX_BYTES:
            return []
        with open(path, "rb") as fh:
            data = fh.read()
    except OSError:
        return []
    if b"\0" in data[:4096]:
        return []  # binary file
    hits = []
    for lineno, line in enumerate(data.decode("utf-8", errors="replace").splitlines(), 1):
        if len(line) > 2000:
            continue
        for kind, pattern in CONTENT_PATTERNS:
            if pattern.search(line):
                hits.append(f"rad {lineno}: {kind}")
                break
    return hits[:3]


def check_files(root, names):
    """Findings (strings) for the given relative file names under root."""
    findings = []
    for name in names:
        full = os.path.join(root, name)
        if _name_hit(name):
            findings.append(f"{name}: filnamnet ser ut som en hemlighet")
        if os.path.isfile(full):
            findings.extend(f"{name}, {hit}" for hit in _scan_text(full))
    return findings


def check_folder(root):
    """Findings for every file in a folder (used before first upload)."""
    names, count = [], 0
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
        for fn in filenames:
            names.append(os.path.relpath(os.path.join(dirpath, fn), root))
            count += 1
            if count >= MAX_FILES:
                return check_files(root, names)
    return check_files(root, names)

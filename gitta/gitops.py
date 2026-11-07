"""Thin wrapper around the git command line.

The GitHub token is passed per command through ``http.extraheader`` so it is
never written to ``.git/config`` or into a remote URL.
"""

import base64
import os
import re
import shutil
import subprocess

CREATE_NO_WINDOW = 0x08000000 if os.name == "nt" else 0
MIN_VERSION = (2, 25)

_CANDIDATES = [
    r"C:\Program Files\Git\cmd\git.exe",
    r"C:\Program Files (x86)\Git\cmd\git.exe",
    os.path.expandvars(r"%LOCALAPPDATA%\Programs\Git\cmd\git.exe"),
]

_git = "git"


class GitError(Exception):
    pass


def find_git():
    """Locate git.exe (PATH first, then the usual install folders)."""
    global _git
    found = shutil.which("git")
    if not found:
        found = next((c for c in _CANDIDATES if os.path.isfile(c)), None)
    if found:
        _git = found
    return found


def version():
    """Return (major, minor) of the installed git, or None."""
    try:
        out = run(["--version"])
    except (GitError, OSError):
        return None
    m = re.search(r"(\d+)\.(\d+)", out)
    return (int(m.group(1)), int(m.group(2))) if m else None


def _friendly(stderr):
    low = stderr.lower()
    hint = ""
    if "authentication failed" in low or "could not read username" in low \
            or "invalid username or password" in low or "403" in low:
        hint = ("GitHub avvisade inloggningen. Koppla kontot igen (Arkiv > "
                "Logga ut) och kontrollera att du har skrivrättigheter.")
    elif "non-fast-forward" in low or "fetch first" in low or "[rejected]" in low:
        hint = ("GitHub har nyare ändringar än din dator. Gör en pull först, "
                "sedan commit and push igen.")
    elif "not possible to fast-forward" in low or "diverging" in low:
        hint = ("Dina och GitHubs ändringar har gått isär, och Gitta slår inte "
                "ihop dem automatiskt. Be om hjälp innan du fortsätter.")
    elif "would be overwritten" in low:
        hint = ("Du har osparade ändringar som krockar med nyheterna. Gör "
                "commit and push först, sedan pull.")
    elif "could not resolve host" in low or "unable to access" in low:
        hint = "Kunde inte nå GitHub. Kontrollera internetanslutningen."
    return f"{hint}\n\nDetaljer från git:\n{stderr.strip()}" if hint else stderr.strip()


def run(args, cwd=None, token=None, stdin=None):
    cmd = [_git, "-c", "core.quotepath=false"]
    if token:
        cred = base64.b64encode(f"x-access-token:{token}".encode()).decode()
        cmd += ["-c", "credential.helper=",
                "-c", f"http.extraheader=Authorization: Basic {cred}"]
    cmd += args
    env = dict(os.environ, GIT_TERMINAL_PROMPT="0", LC_ALL="C")
    proc = subprocess.run(
        cmd, cwd=cwd, env=env, input=stdin, capture_output=True,
        text=True, encoding="utf-8", errors="replace",
        creationflags=CREATE_NO_WINDOW)
    if proc.returncode != 0:
        raise GitError(_friendly(proc.stderr or proc.stdout))
    return proc.stdout


def is_repo(path):
    return os.path.isdir(os.path.join(path, ".git"))


def clone(url, dest, token):
    run(["clone", url, dest], token=token)


def init(path, branch="main"):
    run(["init"], cwd=path)
    # Works on every git version (unlike ``init -b``).
    run(["symbolic-ref", "HEAD", f"refs/heads/{branch}"], cwd=path)


def add_remote(path, url):
    run(["remote", "add", "origin", url], cwd=path)


def remote_url(path):
    try:
        return run(["remote", "get-url", "origin"], cwd=path).strip()
    except GitError:
        return ""


def ensure_exclude(path, pattern):
    """Keep a file out of git without touching .gitignore."""
    rel = run(["rev-parse", "--git-path", "info/exclude"], cwd=path).strip()
    full = os.path.join(path, rel)
    os.makedirs(os.path.dirname(full), exist_ok=True)
    try:
        with open(full, encoding="utf-8") as fh:
            if pattern in fh.read().splitlines():
                return
    except OSError:
        pass
    with open(full, "a", encoding="utf-8") as fh:
        fh.write(f"\n{pattern}\n")


def status(path):
    """List of (code, filename) for changed files."""
    out = run(["status", "--porcelain", "-uall"], cwd=path)
    return [(line[:2], line[3:]) for line in out.splitlines() if line.strip()]


def files_to_commit(path):
    """Tracked plus untracked files, minus anything .gitignore excludes."""
    out = run(["ls-files", "--cached", "--others", "--exclude-standard"], cwd=path)
    return [line for line in out.splitlines() if line.strip()]


def branch(path):
    try:
        return run(["symbolic-ref", "--short", "-q", "HEAD"], cwd=path).strip()
    except GitError:
        return "(detached)"


def fetch(path, token):
    run(["fetch", "--quiet"], cwd=path, token=token)


def ahead_behind(path):
    """(ahead, behind) versus GitHub, or None if not tracked yet."""
    try:
        out = run(["rev-list", "--left-right", "--count", "@{u}...HEAD"], cwd=path)
    except GitError:
        return None
    behind, ahead = out.split()
    return int(ahead), int(behind)


def has_identity(path=None):
    try:
        return bool(run(["config", "--get", "user.name"], cwd=path).strip()
                    and run(["config", "--get", "user.email"], cwd=path).strip())
    except GitError:
        return False


def commit_all(path, message, identity=None):
    run(["add", "-A"], cwd=path)
    args = []
    if identity and not has_identity(path):
        args += ["-c", f"user.name={identity[0]}", "-c", f"user.email={identity[1]}"]
    run(args + ["commit", "-F", "-"], cwd=path, stdin=message)


def push(path, token):
    run(["push", "-u", "origin", "HEAD"], cwd=path, token=token)


def pull(path, token):
    return run(["pull", "--ff-only"], cwd=path, token=token)

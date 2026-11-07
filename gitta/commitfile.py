"""The commit-message marker file, ``.Gitta-commit``, in a project's root.

It is either a single file (its whole content is the message) or a folder
(all files, sorted by name, concatenated). It is removed after a successful
commit.
"""

import os
import shutil

FILENAME = ".Gitta-commit"


def _target(project):
    return os.path.join(project, FILENAME)


def is_dir(project):
    return os.path.isdir(_target(project))


def read(project):
    """Return the message text, or '' if there is no commit file."""
    target = _target(project)
    if os.path.isdir(target):
        parts = []
        for name in sorted(os.listdir(target)):
            full = os.path.join(target, name)
            if os.path.isfile(full):
                with open(full, encoding="utf-8", errors="replace") as fh:
                    parts.append(fh.read().strip())
        return "\n\n".join(p for p in parts if p)
    try:
        with open(target, encoding="utf-8", errors="replace") as fh:
            return fh.read()
    except OSError:
        return ""


def write(project, text):
    """Write the commit file (no-op for the folder form)."""
    if is_dir(project):
        return
    with open(_target(project), "w", encoding="utf-8", newline="\n") as fh:
        fh.write(text.strip() + "\n")


def remove(project):
    target = _target(project)
    if os.path.isdir(target):
        shutil.rmtree(target, ignore_errors=True)
    elif os.path.exists(target):
        os.remove(target)

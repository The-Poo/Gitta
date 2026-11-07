"""A small Markdown viewer for Tk Text widgets (enough for READMEs).

Handles headings, bullet/numbered lists, quotes, code blocks, horizontal
rules, **bold**, `code` and links. HTML tags are stripped and images are shown
as a placeholder. This is deliberately simple, not a full Markdown renderer.
"""

import html
import re

from . import theme

_INLINE = re.compile(
    r"(\*\*[^*]+\*\*|`[^`]+`|!\[[^\]]*\]\([^)]*\)|\[[^\]]+\]\([^)]*\))")
_TAG = re.compile(r"<[^>]+>")
_COMMENT = re.compile(r"<!--.*?-->")


def setup_tags(widget):
    base = "Segoe UI"
    widget.tag_configure("h1", font=(base, 18, "bold"), foreground=theme.PINK,
                         spacing1=10, spacing3=4)
    widget.tag_configure("h2", font=(base, 14, "bold"), foreground=theme.CYAN,
                         spacing1=8, spacing3=3)
    widget.tag_configure("h3", font=(base, 12, "bold"), foreground=theme.LIME,
                         spacing1=6, spacing3=2)
    widget.tag_configure("bold", font=(base, 10, "bold"))
    widget.tag_configure("code", font=("Consolas", 10), background=theme.PANEL,
                         foreground=theme.WARN)
    widget.tag_configure("link", foreground=theme.CYAN, underline=True)
    widget.tag_configure("muted", foreground=theme.MUTED)
    widget.tag_configure("quote", foreground=theme.MUTED, lmargin1=16, lmargin2=16,
                         font=(base, 10, "italic"))
    widget.tag_configure("bullet", lmargin1=10, lmargin2=26)
    widget.tag_configure("rule", foreground=theme.VIOLET)
    widget.tag_configure("mark", foreground=theme.MUTED)  # Markdown characters


def show_message(widget, text):
    widget.config(state="normal")
    widget.delete("1.0", "end")
    widget.insert("end", text, "muted")
    widget.config(state="disabled")


def _inline(widget, text, base_tag=None):
    tags = (base_tag,) if base_tag else ()
    for part in _INLINE.split(text):
        if not part:
            continue
        if part.startswith("**"):
            widget.insert("end", part[2:-2], tags + ("bold",))
        elif part.startswith("`"):
            widget.insert("end", part[1:-1], tags + ("code",))
        elif part.startswith("!["):
            alt = part[2:part.index("]")]
            widget.insert("end", f"[bild: {alt}]" if alt else "[bild]", tags + ("muted",))
        elif part.startswith("["):
            label, url = part[1:].split("](", 1)
            widget.insert("end", label, tags + ("link",))
            widget.insert("end", f" ({url[:-1]})", tags + ("muted",))
        else:
            widget.insert("end", part, tags)


def render(widget, markdown, first_line_title=False):
    """Render Markdown. With first_line_title the first line is shown as a
    heading even without '#' (git commit style: subject line, blank, body)."""
    widget.config(state="normal")
    widget.delete("1.0", "end")
    in_code = False
    title_pending = first_line_title
    text = _COMMENT.sub("", markdown.replace("\r\n", "\n"))
    for raw in text.split("\n"):
        line = raw.rstrip()
        if line.strip().startswith(("```", "~~~")):
            in_code = not in_code
            continue
        if in_code:
            widget.insert("end", line + "\n", "code")
            continue
        line = html.unescape(_TAG.sub("", line))
        if not line.strip():
            widget.insert("end", "\n")
            continue
        m = re.match(r"^\s{0,3}(#{1,6})\s+(.*?)\s*#*\s*$", line)
        if title_pending:
            title_pending = False
            if not m:
                _inline(widget, line.strip(), "h2")
                widget.insert("end", "\n")
                continue
        if m:
            _inline(widget, m.group(2), f"h{min(len(m.group(1)), 3)}")
            widget.insert("end", "\n")
            continue
        if re.match(r"^\s*([-*_])(\s*\1){2,}\s*$", line):
            widget.insert("end", "─" * 48 + "\n", "rule")
            continue
        if re.match(r"^\s*\|?[\s:|-]+\|[\s:|-]*$", line) and "-" in line:
            continue  # table separator row
        m = re.match(r"^(\s*)([-*+]|\d+[.)])\s+(.*)", line)
        if m:
            indent = "  " * (len(m.group(1)) // 2)
            marker = "•" if m.group(2) in "-*+" else m.group(2)
            widget.insert("end", f"{indent}{marker} ", "bullet")
            _inline(widget, m.group(3), "bullet")
            widget.insert("end", "\n")
            continue
        if line.lstrip().startswith(">"):
            _inline(widget, line.lstrip()[1:].strip(), "quote")
            widget.insert("end", "\n")
            continue
        _inline(widget, line)
        widget.insert("end", "\n")
    widget.config(state="disabled")
    widget.yview_moveto(0)


_H_LINE = re.compile(r"^(\s{0,3})(#{1,6})(\s+)")
_LIST_LINE = re.compile(r"^(\s*)([-*+]|\d+[.)])(\s+)")


def highlight(widget):
    """Style an editable Text in place: the text stays as typed, but headings,
    bold, lists and code are shown formatted (Markdown characters dimmed)."""
    for tag in ("h1", "h2", "h3", "bold", "code", "quote", "bullet", "mark", "link"):
        widget.tag_remove(tag, "1.0", "end")
    in_code = False
    lines = widget.get("1.0", "end-1c").split("\n")
    for n, line in enumerate(lines, 1):
        def at(col):
            return f"{n}.{col}"
        if line.strip().startswith(("```", "~~~")):
            in_code = not in_code
            widget.tag_add("code", at(0), at(len(line)))
            continue
        if in_code:
            widget.tag_add("code", at(0), at(len(line)))
            continue
        m = _H_LINE.match(line)
        if m:
            widget.tag_add(f"h{min(len(m.group(2)), 3)}", at(0), at(len(line)))
            widget.tag_add("mark", at(m.end(1)), at(m.end(3)))
        elif n == 1 and line.strip():
            widget.tag_add("h2", at(0), at(len(line)))
        else:
            m = _LIST_LINE.match(line)
            if m:
                widget.tag_add("bullet", at(0), at(len(line)))
                widget.tag_add("mark", at(m.end(1)), at(m.end(2)))
            elif line.lstrip().startswith(">"):
                widget.tag_add("quote", at(0), at(len(line)))
        for im in _INLINE.finditer(line):
            part = im.group(0)
            s, e = im.start(), im.end()
            if part.startswith("**"):
                widget.tag_add("bold", at(s), at(e))
                widget.tag_add("mark", at(s), at(s + 2))
                widget.tag_add("mark", at(e - 2), at(e))
            elif part.startswith("`"):
                widget.tag_add("code", at(s), at(e))
            elif part.startswith("[") and "](" in part:
                widget.tag_add("link", at(s), at(e))

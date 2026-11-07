"""Themed, friendlier replacements for tkinter.messagebox.

Same call style as messagebox (showinfo/showwarning/showerror/askyesno), but
with a coloured frame, a round badge and a short cheerful line.
"""

import random
import tkinter as tk
from tkinter import ttk, scrolledtext

from . import theme

# kind -> (badge glyph, accent colour, sign-off lines)
_KINDS = {
    "info": ("★", theme.LIME, ["Snyggt jobbat!", "Där satt den!", "Boom!", "Smidigt, va?"]),
    "warning": ("!", theme.WARN, ["Tänk efter en gång till.", "Bättre säker än sorry.",
                                  "Ta det lugnt, du hinner."]),
    "error": ("✖", theme.PINK, ["Hoppsan! Ingen panik, det går att fixa.",
                                "Klistra in texten för Claude så felsöker vi.",
                                "Det där var inte meningen."]),
    "question": ("?", theme.CYAN, ["Du bestämmer!", "Din tur att välja.", "Hmm, vad blir det?"]),
}


def _show(kind, title, message, buttons, default_index, cancel_value, parent):
    parent = parent or tk._default_root
    glyph, accent, lines = _KINDS[kind]
    win = tk.Toplevel(parent)
    win.title(title)
    win.configure(bg=accent)
    win.resizable(False, False)
    if parent is not None and parent.winfo_viewable():
        win.transient(parent)  # a transient of a hidden window would stay hidden

    inner = tk.Frame(win, bg=theme.BG, padx=22, pady=18)
    inner.pack(padx=3, pady=3, fill="both", expand=True)
    top = tk.Frame(inner, bg=theme.BG)
    top.pack(fill="x")

    badge = tk.Canvas(top, width=64, height=64, bg=theme.BG, highlightthickness=0)
    badge.pack(side="left", anchor="n", padx=(0, 16))
    badge.create_oval(4, 4, 60, 60, fill=accent, outline="")
    badge.create_text(32, 32, text=glyph, font=("Segoe UI", 26, "bold"), fill=theme.INK)

    col = tk.Frame(top, bg=theme.BG)
    col.pack(side="left", fill="both", expand=True)
    head_font = ("Segoe UI", 15, "bold")
    if kind == "info":
        theme.rainbow(col, title, head_font).pack(anchor="w")
    else:
        tk.Label(col, text=title, font=head_font, fg=accent, bg=theme.BG).pack(anchor="w")

    if len(message) > 700 or message.count("\n") > 14:
        box = scrolledtext.ScrolledText(col, width=62, height=12, wrap="word",
                                        font=theme.FONT, padx=6, pady=6)
        box.insert("1.0", message)
        box.config(state="disabled")
        box.pack(anchor="w", pady=(8, 0))
    else:
        tk.Label(col, text=message, font=theme.FONT, fg=theme.FG, bg=theme.BG,
                 wraplength=470, justify="left").pack(anchor="w", pady=(8, 0))
    tk.Label(col, text=random.choice(lines), font=("Segoe UI", 9, "italic"),
             fg=theme.MUTED, bg=theme.BG).pack(anchor="w", pady=(10, 0))

    result = {"value": cancel_value}

    def choose(value):
        result["value"] = value
        win.destroy()

    row = tk.Frame(inner, bg=theme.BG)
    row.pack(anchor="e", pady=(16, 0))
    widgets = []
    for label, value in buttons:
        btn = ttk.Button(row, text=label, command=lambda v=value: choose(v))
        btn.pack(side="left", padx=(8, 0))
        widgets.append(btn)
    widgets[default_index].focus_set()

    def on_return(_event):
        focused = win.focus_get()
        if isinstance(focused, ttk.Button):
            focused.invoke()
    win.bind("<Return>", on_return)
    win.bind("<Escape>", lambda _e: choose(cancel_value))
    win.protocol("WM_DELETE_WINDOW", lambda: choose(cancel_value))

    win.update_idletasks()
    if parent is not None and parent.winfo_viewable():
        x = parent.winfo_rootx() + (parent.winfo_width() - win.winfo_width()) // 2
        y = parent.winfo_rooty() + (parent.winfo_height() - win.winfo_height()) // 3
        win.geometry(f"+{max(x, 0)}+{max(y, 0)}")
    win.wait_visibility()
    win.grab_set()
    win.bell() if kind == "error" else None
    (parent or win).wait_window(win)
    return result["value"]


def showinfo(title, message, parent=None):
    _show("info", title, message, [("Kul, tack!", None)], 0, None, parent)


def showwarning(title, message, parent=None):
    _show("warning", title, message, [("Uppfattat", None)], 0, None, parent)


def showerror(title, message, parent=None):
    _show("error", title, message, [("Aj aj aj", None)], 0, None, parent)


def askyesno(title, message, icon=None, default=None, parent=None):
    kind = "warning" if icon == "warning" else "question"
    return bool(_show(kind, title, message, [("Ja", True), ("Nej", False)],
                      1 if default == "no" else 0, False, parent))

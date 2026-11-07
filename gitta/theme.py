"""Dark, slightly wild colour theme for Tkinter/ttk."""

import tkinter as tk
from tkinter import ttk

BG = "#1a1033"       # deep purple
PANEL = "#261848"
FIELD = "#120a26"
FG = "#f3eaff"
MUTED = "#a99bd0"
PINK = "#ff3cac"
CYAN = "#00e5ff"
LIME = "#b6ff3c"
WARN = "#ffb02e"
VIOLET = "#7b2ff7"
INK = "#1a0b2e"      # dark text on bright buttons
RAINBOW = [PINK, WARN, LIME, CYAN, "#c77dff"]

FONT = ("Segoe UI", 10)


def apply(root):
    root.configure(bg=BG)
    for pattern, value in {
        "*Text.background": FIELD,
        "*Text.foreground": FG,
        "*Text.insertBackground": CYAN,
        "*Text.selectBackground": VIOLET,
        "*Text.selectForeground": "#ffffff",
        "*Text.relief": "flat",
        "*Text.highlightThickness": 1,
        "*Text.highlightBackground": VIOLET,
        "*Text.highlightColor": PINK,
        "*Menu.background": PANEL,
        "*Menu.foreground": FG,
        "*Menu.activeBackground": PINK,
        "*Menu.activeForeground": INK,
        "*Menu.relief": "flat",
    }.items():
        root.option_add(pattern, value)

    s = ttk.Style(root)
    s.theme_use("clam")
    s.configure(".", background=BG, foreground=FG, fieldbackground=FIELD,
                bordercolor=VIOLET, lightcolor=BG, darkcolor=BG,
                troughcolor=FIELD, focuscolor=PINK, font=FONT)
    s.configure("TButton", background=PINK, foreground=INK, padding=(10, 5),
                borderwidth=0, font=("Segoe UI", 10, "bold"))
    s.map("TButton",
          background=[("disabled", "#4a3a70"), ("pressed", LIME), ("active", CYAN)],
          foreground=[("disabled", MUTED)])
    s.configure("TCheckbutton", background=BG, foreground=FG, indicatorcolor=FIELD)
    s.map("TCheckbutton", background=[("active", BG)],
          indicatorcolor=[("selected", PINK), ("active", VIOLET)])
    s.configure("TEntry", fieldbackground=FIELD, foreground=FG, insertcolor=CYAN,
                bordercolor=VIOLET)
    s.configure("Treeview", background=PANEL, fieldbackground=PANEL, foreground=FG,
                rowheight=28, borderwidth=0)
    s.map("Treeview", background=[("selected", VIOLET)],
          foreground=[("selected", "#ffffff")])
    s.configure("Treeview.Heading", background=VIOLET, foreground=FG,
                relief="flat", font=("Segoe UI", 10, "bold"))
    s.map("Treeview.Heading", background=[("active", PINK)],
          foreground=[("active", INK)])
    s.configure("TLabelframe", background=BG, bordercolor=PINK)
    s.configure("TLabelframe.Label", background=BG, foreground=CYAN,
                font=("Segoe UI", 10, "bold"))
    s.configure("TNotebook", background=BG, borderwidth=0, tabmargins=(0, 4, 0, 0))
    s.configure("TNotebook.Tab", background=PANEL, foreground=MUTED,
                padding=(14, 6), font=("Segoe UI", 10, "bold"))
    s.map("TNotebook.Tab", background=[("selected", VIOLET), ("active", PINK)],
          foreground=[("selected", "#ffffff"), ("active", INK)])
    s.configure("TPanedwindow", background=BG)
    s.configure("Sash", sashthickness=6, background=VIOLET)
    s.configure("Vertical.TScrollbar", background=VIOLET, troughcolor=FIELD,
                arrowcolor=FG, bordercolor=FIELD)


def rainbow(parent, text, font):
    """A title where every letter has its own colour."""
    frame = tk.Frame(parent, bg=BG)
    for i, ch in enumerate(text):
        tk.Label(frame, text=ch, font=font, fg=RAINBOW[i % len(RAINBOW)],
                 bg=BG, bd=0, padx=0, pady=0).pack(side="left")
    return frame

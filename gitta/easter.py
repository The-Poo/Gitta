"""Easter egg: set the program on fire (Hjälp > LegoOfDoom).

A borderless, see-through window is laid over the main window and flame
particles are drawn on it for a few seconds. Click or press Esc to stop early.
"""

import random
import tkinter as tk

KEY = "#010203"          # colour made see-through by Windows
FRAME_MS = 33
SPAWN_FRAMES = 150       # how long new flames are born
FLAME_COLOURS = ["#fff7a0", "#ffd93a", "#ff9a1f", "#f2540f", "#c91a0c", "#5a1208", "#2b0d0a"]


def ignite(window):
    """Burn ``window`` (a Tk root). Does nothing if overlays are unsupported."""
    try:
        Fire(window)
    except tk.TclError:
        pass


class Fire:
    def __init__(self, window):
        window.update_idletasks()
        self.w = max(window.winfo_width(), 200)
        self.h = max(window.winfo_height(), 200)
        self.top = tk.Toplevel(window)
        self.top.overrideredirect(True)
        self.top.attributes("-topmost", True)
        self.top.attributes("-transparentcolor", KEY)
        self.top.configure(bg=KEY)
        self.top.geometry(f"{self.w}x{self.h}+{window.winfo_rootx()}+{window.winfo_rooty()}")
        self.canvas = tk.Canvas(self.top, width=self.w, height=self.h, bg=KEY,
                                highlightthickness=0, cursor="hand2")
        self.canvas.pack()
        self.canvas.bind("<Button-1>", lambda _e: self.stop())
        self.top.bind("<Escape>", lambda _e: self.stop())
        self.top.focus_force()
        self.parts = []          # [x, y, vx, vy, radius, age, life]
        self.frame = 0
        self.alive = True
        self._tick()

    def stop(self):
        self.alive = False
        if self.top.winfo_exists():
            self.top.destroy()

    def _spawn(self, power):
        for _ in range(int(40 * power)):
            x = random.uniform(0, self.w)
            # taller flames in the middle of the window
            reach = 0.45 + 0.55 * (1 - abs(x - self.w / 2) / (self.w / 2))
            life = random.randint(25, int(30 + 70 * reach))
            self.parts.append([x, self.h - random.uniform(0, 8), random.uniform(-1.5, 1.5),
                               -random.uniform(4, 9), random.uniform(10, 26), 0, life])
        # flames licking up the sides as well
        for _ in range(int(8 * power)):
            side = random.choice((0, self.w))
            self.parts.append([side, random.uniform(self.h * 0.3, self.h), random.uniform(-1, 1),
                               -random.uniform(2, 5), random.uniform(8, 18), 0, random.randint(15, 40)])

    def _tick(self):
        if not self.alive or not self.top.winfo_exists():
            return
        self.frame += 1
        if self.frame < SPAWN_FRAMES:
            self._spawn(min(1.0, self.frame / 40))
        c = self.canvas
        c.delete("all")
        survivors = []
        for p in self.parts:
            p[0] += p[2] + random.uniform(-1.2, 1.2)
            p[1] += p[3]
            p[5] += 1
            if p[5] >= p[6]:
                continue
            t = p[5] / p[6]
            r = p[4] * (1 - t * 0.7)
            colour = FLAME_COLOURS[min(int(t * len(FLAME_COLOURS)), len(FLAME_COLOURS) - 1)]
            c.create_oval(p[0] - r, p[1] - r, p[0] + r, p[1] + r, fill=colour, outline="")
            survivors.append(p)
        self.parts = survivors
        if 25 < self.frame < SPAWN_FRAMES:
            c.create_text(self.w // 2, self.h // 2, text="LEGO OF DOOM",
                          font=("Impact", 54), fill=random.choice(FLAME_COLOURS[:4]))
        if self.frame >= SPAWN_FRAMES and not self.parts:
            self.stop()
            return
        self.top.after(FRAME_MS, self._tick)

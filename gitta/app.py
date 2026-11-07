"""Gitta GUI (Tkinter)."""

import os
import queue
import re
import subprocess
import sys
import threading
import tkinter as tk
import webbrowser
from tkinter import filedialog, scrolledtext, ttk

from . import __version__, commitfile, config, defaults, github, gitops, leakcheck, mdview, popups, texts, theme

FONT = ("Segoe UI", 10)
FONT_BIG = ("Segoe UI", 16, "bold")
FONT_HUGE = ("Segoe UI", 28, "bold")
FONT_CODE = ("Consolas", 22, "bold")
FONT_SMALL = ("Segoe UI", 9)
GREY = theme.MUTED
ORANGE = theme.WARN

STATUS_WORDS = {"??": "ny", "M": "ändrad", "A": "tillagd", "D": "borttagen",
                "R": "omdöpt", "U": "konflikt"}
REPO_NAME_RE = re.compile(r"^[A-Za-z0-9._-]+$")


def _word(code):
    code = code.strip()
    return STATUS_WORDS.get(code, STATUS_WORDS.get(code[:1], "ändrad"))


class GittaApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title(f"Gitta!!! {__version__}")
        self.geometry("1100x740")
        self.minsize(900, 600)
        self.option_add("*Font", FONT)
        theme.apply(self)

        self.cfg = config.load()
        self.repos = []
        self._readmes = {}           # full_name -> README text ('' if none)
        self.current = None         # repo dict of the selected project
        self.local_path = None
        self._loaded_text = ""
        self._cancel_login = threading.Event()
        self._q = queue.Queue()
        self.after(100, self._pump)
        self.protocol("WM_DELETE_WINDOW", self._on_close)

        self._build_menu()
        self._check_git()
        if self.cfg.get("token"):
            self._show_main()
        else:
            self._show_login()

    # ------------------------------------------------------------------ infra

    def bg(self, fn, done=None, fail=None):
        """Run fn in a thread; deliver the result to done() on the UI thread."""
        def work():
            try:
                res = fn()
            except Exception as exc:  # noqa: BLE001 - shown to the user
                self._q.put((fail or self._show_error, (exc,)))
            else:
                if done:
                    self._q.put((done, (res,)))
        threading.Thread(target=work, daemon=True).start()

    def _pump(self):
        try:
            while True:
                fn, args = self._q.get_nowait()
                fn(*args)
        except queue.Empty:
            pass
        self.after(100, self._pump)

    def _show_error(self, exc):
        self._set_busy(False)
        popups.showerror("Något gick fel", str(exc))

    def _set_busy(self, busy, text=""):
        if hasattr(self, "busy_label"):
            self.busy_label.config(text=text if busy else "")
        self.config(cursor="watch" if busy else "")

    def _clear(self):
        for child in self.winfo_children():
            if not isinstance(child, tk.Menu):
                child.destroy()

    def _on_close(self):
        self._cancel_login.set()
        try:
            self._save_draft()
        except Exception:  # noqa: BLE001
            pass
        self.destroy()

    def _build_menu(self):
        menubar = tk.Menu(self)
        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="Logga ut", command=self._logout)
        file_menu.add_command(label="Avsluta", command=self._on_close)
        menubar.add_cascade(label="Arkiv", menu=file_menu)
        help_menu = tk.Menu(menubar, tearoff=0)
        help_menu.add_command(label="Kom igång", command=lambda: self._help("Kom igång", texts.HELP_START))
        help_menu.add_command(label="Commit-filen", command=lambda: self._help("Commit-filen", texts.HELP_COMMIT))
        help_menu.add_command(label="Ordlista", command=lambda: self._help("Ordlista", texts.HELP_GLOSSARY))
        help_menu.add_command(label="Skapa OAuth App", command=lambda: self._help("Skapa OAuth App", texts.OAUTH_GUIDE))
        menubar.add_cascade(label="Hjälp", menu=help_menu)
        self.config(menu=menubar)

    def _help(self, title, body):
        win = tk.Toplevel(self)
        win.title(title)
        win.geometry("640x480")
        box = scrolledtext.ScrolledText(win, wrap="word", font=FONT, padx=12, pady=12)
        box.insert("1.0", body)
        box.config(state="disabled")
        box.pack(fill="both", expand=True)

    # -------------------------------------------------------------- git check

    def _check_git(self):
        if not gitops.find_git():
            if popups.askyesno(
                    "Git saknas",
                    "Gitta behöver programmet Git, men det hittades inte på "
                    "datorn.\n\nVill du installera det nu? (Det görs med "
                    "Windows egen pakethanterare winget.)"):
                self._install_git()
            return
        ver = gitops.version()
        if ver is None or ver < gitops.MIN_VERSION:
            popups.showwarning(
                "Git är för gammalt",
                "Den installerade versionen av Git verkar vara äldre än "
                f"{gitops.MIN_VERSION[0]}.{gitops.MIN_VERSION[1]} eller kunde "
                "inte läsas av. Uppdatera Git från git-scm.com om något inte "
                "fungerar.")

    def _install_git(self):
        try:
            subprocess.Popen(
                ["winget", "install", "--id", "Git.Git", "-e", "--source", "winget"],
                creationflags=getattr(subprocess, "CREATE_NEW_CONSOLE", 0))
            popups.showinfo(
                "Installerar Git",
                "Ett svart fönster öppnas där Git installeras. När det är "
                "klart: stäng Gitta och starta den igen.")
        except OSError:
            webbrowser.open("https://git-scm.com/download/win")
            popups.showinfo(
                "Installera Git manuellt",
                "winget finns inte på den här datorn. Hemsidan för Git har "
                "öppnats. Ladda ner och installera, och starta sedan om Gitta.")

    def _need_git(self):
        if gitops.find_git():
            return True
        popups.showerror("Git saknas", "Installera Git och starta om Gitta.")
        return False

    # ------------------------------------------------------------------ login

    def _logout(self):
        if not popups.askyesno("Logga ut", "Koppla bort ditt GitHub-konto från Gitta?"):
            return
        self._save_draft()
        self.cfg.update(token="", login="", user_id=0, name="")
        config.save(self.cfg)
        self._show_login()

    def _show_login(self):
        self._clear()
        self._cancel_login = threading.Event()
        f = ttk.Frame(self, padding=30)
        f.pack(fill="both", expand=True)
        theme.rainbow(f, "Gitta!!!", FONT_HUGE).pack(anchor="w")
        ttk.Label(f, text="Välkommen!", font=FONT_BIG, foreground=theme.CYAN).pack(anchor="w")
        ttk.Label(f, text=texts.LOGIN_INTRO, wraplength=760, justify="left").pack(anchor="w", pady=12)

        self.client_id = self.cfg.get("client_id") or defaults.CLIENT_ID
        if not self.client_id:
            ttk.Label(f, text="Client ID saknas. Följ instruktionen och klistra in det här:",
                      foreground=ORANGE).pack(anchor="w")
            guide = tk.Text(f, height=14, wrap="word", font=FONT_SMALL)
            guide.insert("1.0", texts.OAUTH_GUIDE)
            guide.config(state="disabled")
            guide.pack(fill="x", pady=6)
            row = ttk.Frame(f)
            row.pack(anchor="w")
            self.cid_var = tk.StringVar()
            ttk.Entry(row, textvariable=self.cid_var, width=40).pack(side="left")
            ttk.Button(row, text="Spara Client ID", command=self._save_client_id).pack(side="left", padx=8)
            return

        self.login_btn = ttk.Button(f, text="Koppla GitHub-konto", command=self._start_login)
        self.login_btn.pack(anchor="w", pady=8)
        self.login_box = ttk.Frame(f)
        self.login_box.pack(anchor="w", fill="x", pady=10)

    def _save_client_id(self):
        cid = self.cid_var.get().strip()
        if not cid:
            return
        self.cfg["client_id"] = cid
        config.save(self.cfg)
        self._show_login()

    def _start_login(self):
        if not self._need_git():
            return
        self.login_btn.config(state="disabled")
        self.bg(lambda: github.device_start(self.client_id), self._login_code,
                self._login_failed)

    def _login_failed(self, exc):
        self.login_btn.config(state="normal")
        self._show_error(exc)

    def _login_code(self, info):
        for w in self.login_box.winfo_children():
            w.destroy()
        ttk.Label(self.login_box, text="1. Din kod (kopierad till urklipp):").pack(anchor="w")
        ttk.Label(self.login_box, text=info["user_code"], font=FONT_CODE,
                  foreground=theme.LIME).pack(anchor="w", pady=4)
        ttk.Label(self.login_box,
                  text=f"2. Skriv in koden på {info['verification_uri']} (öppnas automatiskt) "
                       "och godkänn.\n3. Vänta här - Gitta går vidare av sig själv.",
                  justify="left").pack(anchor="w")
        ttk.Button(self.login_box, text="Öppna GitHub igen",
                   command=lambda: webbrowser.open(info["verification_uri"])).pack(anchor="w", pady=8)
        self.clipboard_clear()
        self.clipboard_append(info["user_code"])
        webbrowser.open(info["verification_uri"])
        self.bg(lambda: github.device_poll(self.client_id, info, self._cancel_login),
                self._login_token, self._login_failed)

    def _login_token(self, token):
        def fetch_user():
            return token, github.get_user(token)
        self.bg(fetch_user, self._login_done, self._login_failed)

    def _login_done(self, result):
        token, user = result
        self.cfg.update(token=token, login=user["login"], user_id=user["id"],
                        name=user.get("name") or user["login"])
        config.save(self.cfg)
        self._show_main()

    # ------------------------------------------------------------------- main

    def _show_main(self):
        self._clear()
        self.current = None
        self.local_path = None

        top = ttk.Frame(self, padding=(10, 8))
        top.pack(fill="x")
        theme.rainbow(top, "Gitta!!!", ("Segoe UI", 18, "bold")).pack(side="left")
        ttk.Label(top, text=f"   inloggad som {self.cfg['login']}", foreground=GREY).pack(side="left")
        self.busy_label = ttk.Label(top, text="", foreground=ORANGE)
        self.busy_label.pack(side="right")

        panes = ttk.PanedWindow(self, orient="horizontal")
        panes.pack(fill="both", expand=True)

        left = ttk.Frame(panes, padding=8)
        panes.add(left, weight=1)
        bar = ttk.Frame(left)
        bar.pack(fill="x", pady=(0, 6))
        ttk.Button(bar, text="Nytt projekt", command=self._new_project).grid(row=0, column=0, sticky="we")
        ttk.Button(bar, text="Uppdatera listan", command=self._reload_repos).grid(
            row=0, column=1, sticky="we", padx=(6, 0))
        ttk.Button(bar, text="Lägg till befintlig mapp", command=self._add_existing).grid(
            row=1, column=0, columnspan=2, sticky="we", pady=(6, 0))
        ttk.Button(bar, text="clone - hämta flera projekt", command=self._clone_many).grid(
            row=2, column=0, columnspan=2, sticky="we", pady=(6, 0))
        bar.columnconfigure((0, 1), weight=1)
        self.tree = ttk.Treeview(left, columns=("vis", "status"), selectmode="browse")
        self.tree.heading("#0", text="Projekt")
        self.tree.heading("vis", text="Synlighet")
        self.tree.heading("status", text="Status")
        self.tree.column("#0", width=200)
        self.tree.column("vis", width=70, anchor="center")
        self.tree.column("status", width=130)
        self.tree.tag_configure("dirty", foreground=theme.WARN)
        self.tree.tag_configure("clean", foreground=theme.LIME)
        self.tree.tag_configure("remote", foreground=theme.MUTED)
        self.tree.pack(fill="both", expand=True)
        self.tree.bind("<<TreeviewSelect>>", self._on_select)

        right = ttk.Frame(panes, padding=14)
        panes.add(right, weight=3)
        self._build_detail(right)
        self._reload_repos()

    def _reload_repos(self, select=None):
        self._readmes.clear()  # README may have changed after pull/push
        self._set_busy(True, "Hämtar projekt från GitHub...")
        token = self.cfg["token"]
        projects = dict(self.cfg["projects"])

        def work():
            repos = github.list_repos(token)
            changes = {}
            if gitops.find_git():
                for r in repos:
                    p = projects.get(r["full_name"])
                    if p and os.path.isdir(p) and gitops.is_repo(p):
                        try:
                            changes[r["full_name"]] = len(gitops.status(p))
                        except gitops.GitError:
                            pass
            return repos, changes
        self.bg(work, lambda res: self._fill_tree(res, select))

    def _fill_tree(self, result, select):
        self._set_busy(False)
        self.repos, changes = result
        self.tree.delete(*self.tree.get_children())
        for r in self.repos:
            full = r["full_name"]
            p = self.cfg["projects"].get(full)
            if not p or not os.path.isdir(p):
                status, tag = "Ej på datorn", "remote"
            elif changes.get(full):
                status, tag = f"● {changes[full]} ändringar", "dirty"
            else:
                status, tag = "Allt sparat", "clean"
            self.tree.insert("", "end", iid=full, text=r["name"], tags=(tag,),
                             values=("Private" if r["private"] else "Public", status))
        if select and self.tree.exists(select):
            self.tree.selection_set(select)
        elif self.current and self.tree.exists(self.current["full_name"]):
            self.tree.selection_set(self.current["full_name"])

    def _on_select(self, _event=None):
        sel = self.tree.selection()
        if not sel:
            return
        self._save_draft()
        self.current = next((r for r in self.repos if r["full_name"] == sel[0]), None)
        self._load_detail()

    # ----------------------------------------------------------------- detail

    def _build_detail(self, parent):
        self.d_empty = ttk.Label(parent, text="Välj ett projekt i listan till vänster,\n"
                                              "eller skapa ett nytt.", foreground=GREY)
        self.d_empty.pack(pady=40)

        self.d_main = ttk.Frame(parent)
        self.d_title = ttk.Label(self.d_main, font=FONT_BIG)
        self.d_title.pack(anchor="w")
        self.d_desc = ttk.Label(self.d_main, foreground=GREY, wraplength=620, justify="left")
        self.d_desc.pack(anchor="w", pady=(0, 4))
        links = ttk.Frame(self.d_main)
        links.pack(anchor="w", pady=4)
        ttk.Button(links, text="Öppna på GitHub",
                   command=lambda: webbrowser.open(self.current["html_url"])).pack(side="left")
        self.open_folder_btn = ttk.Button(links, text="Visa mappen", command=self._open_folder)
        self.open_folder_btn.pack(side="left", padx=6)

        self.d_tabs = ttk.Notebook(self.d_main)
        self.d_tabs.pack(fill="both", expand=True, pady=(6, 0))
        self.d_tab_main = ttk.Frame(self.d_tabs, padding=8)
        self.d_tab_pull = ttk.Frame(self.d_tabs, padding=8)
        self.d_tab_readme = ttk.Frame(self.d_tabs, padding=8)
        self.d_tabs.add(self.d_tab_main, text="Commit and push")
        self.d_tabs.add(self.d_tab_pull, text="Pull")
        self.d_tabs.add(self.d_tab_readme, text="README")
        self.d_readme = scrolledtext.ScrolledText(
            self.d_tab_readme, wrap="word", font=FONT, state="disabled", padx=12, pady=8)
        self.d_readme.pack(fill="both", expand=True)
        mdview.setup_tags(self.d_readme)

        # Not on this computer
        self.d_remote = ttk.LabelFrame(self.d_tab_main, text="Projektet finns inte på den här datorn", padding=10)
        self._action(self.d_remote, "clone", self._clone, texts.CLONE_EXPLAIN)
        self._action(self.d_remote, "Länka befintlig mapp", self._link_folder, texts.LINK_EXPLAIN)

        # On this computer
        self.d_local = ttk.Frame(self.d_tab_main)
        self.d_path = ttk.Label(self.d_local, foreground=GREY)
        self.d_path.pack(anchor="w")
        self.d_state = ttk.Label(self.d_local, justify="left", wraplength=620)
        self.d_state.pack(anchor="w", pady=6)
        self.d_files = tk.Text(self.d_local, height=4, font=("Consolas", 9),
                               state="disabled")
        self.d_files.pack(fill="x")

        ttk.Label(self.d_local, text="Beskrivning av ändringarna (commit-filen .Gitta-commit):",
                  font=("Segoe UI", 10, "bold")).pack(anchor="w", pady=(10, 2))
        self.d_hint = ttk.Label(self.d_local, foreground=ORANGE, wraplength=620, justify="left")
        self.d_hint.pack(anchor="w")
        self.d_commit = scrolledtext.ScrolledText(self.d_local, height=7, wrap="word", font=FONT)
        self.d_commit.pack(fill="both", expand=True, pady=4)
        self.d_commit.bind("<KeyRelease>", lambda _e: self._update_preview())
        ttk.Label(self.d_local, text=texts.PREVIEW_HINT, foreground=GREY,
                  font=FONT_SMALL).pack(anchor="w")
        self.d_preview = scrolledtext.ScrolledText(
            self.d_local, height=8, wrap="word", font=FONT, state="disabled", padx=10, pady=6)
        self.d_preview.pack(fill="both", expand=True, pady=4)
        mdview.setup_tags(self.d_preview)
        self._action(self.d_local, "commit and push  -  Spara ändringar",
                     self._commit_push, texts.COMMIT_EXPLAIN)

        # Pull tab (used less often, so it has its own tab)
        self.d_sync = ttk.Label(self.d_tab_pull, justify="left", wraplength=620)
        self.d_sync.pack(anchor="w", pady=6)
        self._action(self.d_tab_pull, "pull", self._pull, texts.PULL_EXPLAIN)
        ttk.Label(self.d_tab_pull, text=texts.PULL_LONG, wraplength=620, foreground=GREY,
                  justify="left").pack(anchor="w", pady=14)

    def _action(self, parent, label, command, explain):
        row = ttk.Frame(parent)
        row.pack(fill="x", pady=5)
        btn = ttk.Button(row, text=label, command=command, width=34)
        btn.pack(side="left")
        ttk.Label(row, text=explain, foreground=GREY, font=FONT_SMALL,
                  wraplength=330, justify="left").pack(side="left", padx=10)
        return btn

    def _load_detail(self):
        repo = self.current
        self.d_empty.pack_forget()
        self.d_main.pack(fill="both", expand=True)
        self.d_title.config(text=repo["full_name"])
        self.d_desc.config(text=repo.get("description") or "(ingen beskrivning)")
        self._show_readme(repo["full_name"])
        path = self.cfg["projects"].get(repo["full_name"])
        if path and os.path.isdir(path) and gitops.is_repo(path):
            self.local_path = path
            self.d_remote.pack_forget()
            self.d_local.pack(fill="both", expand=True)
            self.open_folder_btn.config(state="normal")
            self.d_path.config(text=f"Mapp: {path}")
            self.d_state.config(text="Läser status...")
            self._loaded_text = commitfile.read(path)
            self.d_commit.config(state="normal")
            self.d_commit.delete("1.0", "end")
            self.d_commit.insert("1.0", self._loaded_text)
            if commitfile.is_dir(path):
                self.d_commit.config(state="disabled")
            self.d_tabs.tab(self.d_tab_pull, state="normal")
            self.d_sync.config(text="Läser status...")
            self._update_preview()
            self._refresh_state()
        else:
            self.local_path = None
            self.d_local.pack_forget()
            self.d_remote.pack(fill="x", pady=10)
            self.open_folder_btn.config(state="disabled")
            self.d_tabs.tab(self.d_tab_pull, state="hidden")  # nothing to pull yet
            if self.d_tabs.select() == str(self.d_tab_pull):
                self.d_tabs.select(self.d_tab_main)

    def _update_preview(self):
        text = self.d_commit.get("1.0", "end").strip()
        if text:
            mdview.render(self.d_preview, text, first_line_title=True)
        else:
            mdview.show_message(self.d_preview, "Här visas beskrivningen med formatering "
                                                "så fort du skrivit något.")

    def fetch_readme(self, full, callback):
        """callback(text, error): text '' means the project has no README."""
        if full in self._readmes:
            callback(self._readmes[full], None)
            return

        def done(text):
            self._readmes[full] = text or ""
            callback(self._readmes[full], None)
        self.bg(lambda: github.get_readme(self.cfg["token"], full), done,
                lambda exc: callback(None, str(exc)))

    def render_readme(self, widget, text, error):
        if error:
            mdview.show_message(widget, f"Kunde inte hämta README: {error}")
        elif not text.strip():
            mdview.show_message(
                widget, "Det här projektet har ingen README ännu.\n\n"
                        "Tips: se docs/03-readme-guide.md för hur man skriver en.")
        else:
            mdview.render(widget, text)

    def _show_readme(self, full):
        mdview.show_message(self.d_readme, "Hämtar README...")

        def show(text, error):
            if self.current and self.current["full_name"] == full:
                self.render_readme(self.d_readme, text, error)
        self.fetch_readme(full, show)

    def _refresh_state(self):
        path, token = self.local_path, self.cfg["token"]
        if not path:
            return

        def work():
            offline = False
            try:
                gitops.fetch(path, token)
            except gitops.GitError:
                offline = True
            return {
                "path": path, "offline": offline,
                "files": gitops.status(path),
                "branch": gitops.branch(path),
                "ab": gitops.ahead_behind(path),
            }
        self.bg(work, self._fill_state)

    def _fill_state(self, info):
        if info["path"] != self.local_path:
            return  # user switched project meanwhile
        files = info["files"]
        lines = [f"Gren (branch): {info['branch']}"]
        lines.append(f"{len(files)} ändrade filer sedan senaste commit." if files
                     else "Inga osparade ändringar.")
        sync = []
        if info["offline"]:
            lines.append("Kunde inte kontakta GitHub just nu.")
            sync.append("Kunde inte kontakta GitHub just nu.")
        elif info["ab"] is None:
            lines.append("Projektet är inte kopplat till GitHub än - gör commit and push.")
            sync.append("Projektet är inte kopplat till GitHub än.")
        else:
            ahead, behind = info["ab"]
            if ahead:
                lines.append(f"{ahead} commits ligger bara på din dator - gör en push.")
            if behind:
                sync.append(f"{behind} nyheter finns på GitHub - gör en pull.")
            else:
                sync.append("Inga nyheter att hämta från GitHub.")
            if not behind and not ahead:
                lines.append("Datorn och GitHub är i synk.")
        self.d_state.config(text="\n".join(lines))
        self.d_sync.config(text="\n".join(sync))
        self.d_files.config(state="normal")
        self.d_files.delete("1.0", "end")
        for code, name in files:
            self.d_files.insert("end", f"{_word(code):<10}{name}\n")
        self.d_files.config(state="disabled")
        has_text = bool(self.d_commit.get("1.0", "end").strip())
        self.d_hint.config(
            text="Du har osparade ändringar. Skriv en kort beskrivning nedan och "
                 "tryck commit and push." if files and not has_text else "")

    def _open_folder(self):
        if self.local_path:
            os.startfile(self.local_path)  # noqa: S606 - Windows only

    # ----------------------------------------------------------- draft saving

    def _save_draft(self):
        path = self.local_path
        if not path or not os.path.isdir(path) or commitfile.is_dir(path):
            return
        text = self.d_commit.get("1.0", "end").strip()
        if text == self._loaded_text.strip():
            return
        if text:
            commitfile.write(path, text)
        else:
            commitfile.remove(path)
        self._loaded_text = text

    # ---------------------------------------------------------------- actions

    def _identity(self):
        login = self.cfg["login"]
        return (self.cfg.get("name") or login,
                f"{self.cfg['user_id']}+{login}@users.noreply.github.com")

    def _remember(self, full_name, path):
        self.cfg["projects"][full_name] = path
        config.save(self.cfg)

    def _clone(self):
        if not self._need_git():
            return
        parent = filedialog.askdirectory(
            title="Välj mappen som projektet ska ligga i",
            initialdir=self.cfg.get("default_parent") or os.path.expanduser("~"))
        if not parent:
            return
        repo = self.current
        dest = os.path.join(parent, repo["name"])
        if os.path.exists(dest):
            popups.showerror("Mappen finns redan", f"{dest} finns redan. Välj en annan plats.")
            return
        self.cfg["default_parent"] = parent
        self._set_busy(True, "Kör clone...")

        def work():
            gitops.clone(repo["clone_url"], dest, self.cfg["token"])
            gitops.ensure_exclude(dest, commitfile.FILENAME)
            return dest
        self.bg(work, lambda d: self._after_link(repo["full_name"], d))

    def _after_link(self, full_name, path):
        self._remember(full_name, path)
        self._set_busy(False)
        self._reload_repos(select=full_name)
        self._load_detail()

    def _link_folder(self):
        if not self._need_git():
            return
        folder = filedialog.askdirectory(title="Välj projektmappen")
        if not folder:
            return
        repo = self.current
        if not gitops.is_repo(folder):
            popups.showerror("Inte ett projekt", "Mappen är inte ett git-projekt (saknar .git).")
            return
        if repo["full_name"].lower() not in gitops.remote_url(folder).lower():
            popups.showerror("Fel projekt",
                                 f"Mappen hör inte till {repo['full_name']} på GitHub.")
            return
        gitops.ensure_exclude(folder, commitfile.FILENAME)
        self._after_link(repo["full_name"], folder)

    def _pull(self):
        path, token = self.local_path, self.cfg["token"]
        self._set_busy(True, "Kör pull...")

        def work():
            return gitops.pull(path, token)
        def done(out):
            self._set_busy(False)
            popups.showinfo("pull klar", out.strip() or "Klart.")
            self._refresh_state()
            self._reload_repos()
        self.bg(work, done)

    def _commit_push(self):
        path, token = self.local_path, self.cfg["token"]
        message = self.d_commit.get("1.0", "end").strip()
        if not message:
            popups.showwarning("Beskrivning saknas",
                                   "Skriv en kort beskrivning av ändringarna först.")
            return
        if commitfile.is_dir(path):
            message = commitfile.read(path)
        findings = leakcheck.check_files(path, [n for _c, n in gitops.status(path)])
        if findings and not self._confirm_secrets(findings, public=not self.current["private"]):
            return
        identity = self._identity()
        self._set_busy(True, "Sparar och skickar till GitHub...")

        def work():
            if not gitops.status(path):
                gitops.push(path, token)  # maybe only a push is missing
                return "push"
            gitops.commit_all(path, message, identity)
            gitops.push(path, token)
            return "commit"
        def done(kind):
            self._set_busy(False)
            commitfile.remove(path)
            self.d_commit.config(state="normal")
            self.d_commit.delete("1.0", "end")
            self._update_preview()
            self._loaded_text = ""
            popups.showinfo(
                "Sparat",
                "Dina ändringar är nu sparade (commit) och skickade till GitHub (push)."
                if kind == "commit" else "Befintliga commits skickades till GitHub (push).")
            self._refresh_state()
            self._reload_repos()
        self.bg(work, done)

    # ------------------------------------------------------------ new project

    def _new_project(self):
        if not self._need_git():
            return
        NewProjectDialog(self)

    def _add_existing(self):
        if not self._need_git():
            return
        NewProjectDialog(self, existing=True)

    def _clone_many(self):
        if not self._need_git():
            return
        if not self.repos:
            popups.showinfo("Inga projekt", "Projektlistan är tom eller inte laddad än.")
            return
        CloneManyDialog(self)

    def is_local(self, repo):
        path = self.cfg["projects"].get(repo["full_name"])
        return bool(path) and os.path.isdir(path)

    def create_project(self, name, desc, parent, new_folder, private, on_done):
        folder = os.path.join(parent, name) if new_folder else parent
        existing_repo = gitops.is_repo(folder)
        if existing_repo and gitops.remote_url(folder):
            popups.showerror(
                "Redan kopplat till GitHub",
                f"{folder} är redan ett git-projekt med en GitHub-adress "
                f"({gitops.remote_url(folder)}).\n\nFinns projektet i listan väljer du det "
                "och trycker 'Länka befintlig mapp'.")
            return

        def scan():
            if not os.path.isdir(folder):
                return []
            if existing_repo:  # respects .gitignore
                return leakcheck.check_files(folder, gitops.files_to_commit(folder))
            return leakcheck.check_folder(folder)

        def after_scan(findings):
            self._set_busy(False)
            if findings and not self._confirm_secrets(findings, public=not private):
                return
            self._create_now(name, desc, parent, new_folder, private, on_done,
                            folder, existing_repo)
        self._set_busy(True, "Kontrollerar att inga hemligheter följer med...")
        self.bg(scan, after_scan)

    def _confirm_secrets(self, findings, public):
        shown = "\n  ".join(findings[:12])
        more = f"\n  ...och {len(findings) - 12} till" if len(findings) > 12 else ""
        warn = ("OBS: projektet är PUBLIC. Vem som helst på internet kan läsa det.\n\n"
                if public else "")
        return popups.askyesno(
            "Möjliga hemligheter hittades",
            f"{warn}Gitta hittade saker som kan vara lösenord, nycklar eller andra "
            f"hemligheter:\n\n  {shown}{more}\n\n"
            "Det som skickas till GitHub går inte att ta tillbaka på riktigt. "
            "Ta bort det ur filerna, eller lägg filen i .gitignore, och försök igen.\n\n"
            "Vill du ändå fortsätta?\n(Svara Nej om du är osäker. "
            "Se docs/07-uppdatera-programmet.md.)",
            icon="warning", default="no")

    def _create_now(self, name, desc, parent, new_folder, private, on_done,
                    folder, existing_repo):
        token = self.cfg["token"]
        identity = self._identity()
        self._set_busy(True, "Skapar projektet...")

        def work():
            repo = github.create_repo(token, name, desc, private)
            os.makedirs(folder, exist_ok=True)
            if not existing_repo:
                gitops.init(folder)
            readme = os.path.join(folder, "README.md")
            if not os.path.exists(readme):
                with open(readme, "w", encoding="utf-8", newline="\n") as fh:
                    fh.write(f"# {name}\n\n{desc}\n" if desc else f"# {name}\n")
            gitops.ensure_exclude(folder, commitfile.FILENAME)
            gitops.add_remote(folder, repo["clone_url"])
            if gitops.status(folder):
                gitops.commit_all(folder, "Initial commit" if not existing_repo
                                  else "Add project to GitHub", identity)
            gitops.push(folder, token)
            return repo["full_name"], folder

        def done(res):
            full, path = res
            self._remember(full, path)
            self.cfg["default_parent"] = parent if new_folder else os.path.dirname(parent)
            config.save(self.cfg)
            self._set_busy(False)
            on_done()
            self._reload_repos(select=full)
            popups.showinfo("Projektet skapades",
                                f"{full} finns nu på GitHub och i mappen\n{path}")
        self.bg(work, done)


class NewProjectDialog(tk.Toplevel):
    """Create a GitHub project from a new folder, or from an existing one."""

    def __init__(self, app, existing=False):
        super().__init__(app)
        self.app = app
        self.existing = existing
        self.title("Lägg till befintlig mapp" if existing else "Nytt projekt")
        self.configure(bg=theme.BG)
        self.transient(app)
        self.grab_set()
        f = ttk.Frame(self, padding=16)
        f.pack(fill="both", expand=True)

        start = app.cfg.get("default_parent") or os.path.join(os.path.expanduser("~"), "Documents")
        self.name = tk.StringVar()
        self.desc = tk.StringVar()
        self.parent = tk.StringVar(value="" if existing else start)
        self.new_folder = tk.BooleanVar(value=True)
        self.public = tk.BooleanVar(value=False)
        self._name_touched = False

        row = 0
        if existing:
            ttk.Label(f, text="Välj mappen som redan finns på datorn:").grid(row=row, column=0, sticky="w")
            row += 1
            ttk.Entry(f, textvariable=self.parent, width=44).grid(row=row, column=0, sticky="we")
            ttk.Button(f, text="Bläddra...", command=self._browse).grid(row=row, column=1, padx=6)
            row += 1

        ttk.Label(f, text="Projektnamn på GitHub (bokstäver, siffror, - _ .):").grid(
            row=row, column=0, sticky="w", pady=(10 if existing else 0, 0))
        row += 1
        name_entry = ttk.Entry(f, textvariable=self.name, width=44)
        name_entry.grid(row=row, column=0, columnspan=2, sticky="we")
        name_entry.bind("<Key>", lambda _e: setattr(self, "_name_touched", True))
        row += 1
        ttk.Label(f, text="Kort beskrivning (valfritt):").grid(row=row, column=0, sticky="w", pady=(10, 0))
        row += 1
        ttk.Entry(f, textvariable=self.desc, width=44).grid(row=row, column=0, columnspan=2, sticky="we")
        row += 1

        if not existing:
            ttk.Label(f, text="Vilken mapp ska projektet bo i?").grid(row=row, column=0, sticky="w", pady=(10, 0))
            row += 1
            ttk.Entry(f, textvariable=self.parent, width=44).grid(row=row, column=0, sticky="we")
            ttk.Button(f, text="Bläddra...", command=self._browse).grid(row=row, column=1, padx=6)
            row += 1
            ttk.Checkbutton(f, text="Skapa en ny mapp med projektets namn i den mappen",
                            variable=self.new_folder, command=self._preview).grid(
                row=row, column=0, columnspan=2, sticky="w", pady=4)
            row += 1
        self.preview = ttk.Label(f, foreground=GREY, font=FONT_SMALL)
        self.preview.grid(row=row, column=0, columnspan=2, sticky="w")
        row += 1

        ttk.Checkbutton(f, text="Gör projektet public (synligt för alla)",
                        variable=self.public).grid(row=row, column=0, columnspan=2, sticky="w", pady=(12, 0))
        row += 1
        ttk.Label(f, text=texts.PRIVATE_EXPLAIN, wraplength=480, foreground=GREY,
                  font=FONT_SMALL, justify="left").grid(row=row, column=0, columnspan=2, sticky="w")
        row += 1
        ttk.Label(f, text=texts.EXISTING_FILES_WARNING, wraplength=480, foreground=ORANGE,
                  font=FONT_SMALL, justify="left").grid(row=row, column=0, columnspan=2, sticky="w", pady=(8, 0))
        row += 1

        btns = ttk.Frame(f)
        btns.grid(row=row, column=0, columnspan=2, sticky="e", pady=(14, 0))
        ttk.Button(btns, text="Avbryt", command=self.destroy).pack(side="right", padx=6)
        ttk.Button(btns, text="Skapa projekt", command=self._create).pack(side="right")

        for var in (self.name, self.parent):
            var.trace_add("write", lambda *_: self._preview())
        self._preview()

    def _browse(self):
        d = filedialog.askdirectory(parent=self, title="Välj mapp",
                                    initialdir=self.parent.get() or None)
        if not d:
            return
        self.parent.set(os.path.normpath(d))
        if self.existing and not self._name_touched:
            guess = re.sub(r"[^A-Za-z0-9._-]+", "-", os.path.basename(os.path.normpath(d))).strip("-")
            self.name.set(guess)

    def _target(self):
        base = self.parent.get().strip()
        if self.existing:
            return base or "(välj en mapp)"
        return os.path.join(base, self.name.get().strip()) if self.new_folder.get() else base

    def _preview(self):
        self.preview.config(text=f"Projektet hamnar i: {self._target()}")

    def _create(self):
        name = self.name.get().strip()
        parent = self.parent.get().strip()
        if not REPO_NAME_RE.match(name):
            popups.showwarning("Ogiltigt namn", "Använd bara bokstäver, siffror, - _ och . (inga mellanslag).",
                                   parent=self)
            return
        if not os.path.isdir(parent):
            popups.showwarning("Mappen finns inte", "Välj en mapp som finns.", parent=self)
            return
        self.app.create_project(name, self.desc.get().strip(), os.path.normpath(parent),
                                False if self.existing else self.new_folder.get(),
                                not self.public.get(), self.destroy)


class ReadmeWindow(tk.Toplevel):
    """Read a project's README from GitHub without cloning it."""

    def __init__(self, app, full_name):
        super().__init__(app)
        self.title(f"README - {full_name}")
        self.configure(bg=theme.BG)
        self.geometry("740x620")
        box = scrolledtext.ScrolledText(self, wrap="word", font=FONT, state="disabled",
                                        padx=14, pady=10)
        box.pack(fill="both", expand=True)
        mdview.setup_tags(box)
        mdview.show_message(box, "Hämtar README...")

        def show(text, error):
            if self.winfo_exists():
                app.render_readme(box, text, error)
        app.fetch_readme(full_name, show)


class CloneManyDialog(tk.Toplevel):
    """Pick a root folder and several GitHub projects, then clone them all."""

    def __init__(self, app):
        super().__init__(app)
        self.app = app
        self.title("clone - hämta flera projekt")
        self.configure(bg=theme.BG)
        self.geometry("640x580")
        self.transient(app)
        self.grab_set()
        f = ttk.Frame(self, padding=16)
        f.pack(fill="both", expand=True)

        ttk.Label(f, text=texts.CLONE_MANY_EXPLAIN, wraplength=590, foreground=GREY,
                  justify="left").pack(anchor="w")

        ttk.Label(f, text="1. Välj rotmappen som projekten ska hamna i:").pack(anchor="w", pady=(12, 2))
        row = ttk.Frame(f)
        row.pack(fill="x")
        self.root_var = tk.StringVar(value=app.cfg.get("default_parent") or
                                     os.path.join(os.path.expanduser("~"), "Documents"))
        ttk.Entry(row, textvariable=self.root_var).pack(side="left", fill="x", expand=True)
        ttk.Button(row, text="Bläddra...", command=self._browse).pack(side="left", padx=6)
        ttk.Label(f, text="Varje projekt får en egen undermapp med projektets namn.",
                  foreground=GREY, font=FONT_SMALL).pack(anchor="w")

        self.candidates = [r for r in app.repos if not app.is_local(r)]
        local_count = len(app.repos) - len(self.candidates)
        ttk.Label(f, text="2. Välj vilka projekt som ska hämtas (Ctrl/Shift för flera):").pack(
            anchor="w", pady=(12, 2))
        tools = ttk.Frame(f)
        tools.pack(fill="x", pady=(0, 4))
        ttk.Button(tools, text="Markera alla", command=self._select_all).pack(side="left")
        ttk.Button(tools, text="Avmarkera alla", command=self._select_none).pack(side="left", padx=6)
        ttk.Button(tools, text="Läs README", command=self._read_readme).pack(side="left")
        self.count = ttk.Label(tools, text="", foreground=theme.CYAN)
        self.count.pack(side="right")

        box = ttk.Frame(f)
        box.pack(fill="both", expand=True)
        self.tree = ttk.Treeview(box, columns=("vis",), selectmode="extended")
        self.tree.heading("#0", text="Projekt")
        self.tree.heading("vis", text="Synlighet")
        self.tree.column("#0", width=380)
        self.tree.column("vis", width=90, anchor="center")
        scroll = ttk.Scrollbar(box, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scroll.set)
        self.tree.pack(side="left", fill="both", expand=True)
        scroll.pack(side="right", fill="y")
        for r in self.candidates:
            self.tree.insert("", "end", iid=r["full_name"], text=r["full_name"],
                             values=("Private" if r["private"] else "Public",))
        self.tree.bind("<<TreeviewSelect>>", lambda _e: self._update_count())

        note = (f"{local_count} projekt finns redan på datorn och visas inte."
                if local_count else "")
        if not self.candidates:
            note = "Alla dina projekt finns redan på den här datorn."
        self.progress = ttk.Label(f, text=note, foreground=GREY, font=FONT_SMALL)
        self.progress.pack(anchor="w", pady=(6, 0))

        btns = ttk.Frame(f)
        btns.pack(fill="x", pady=(10, 0))
        self.cancel_btn = ttk.Button(btns, text="Avbryt", command=self.destroy)
        self.cancel_btn.pack(side="right", padx=6)
        self.go_btn = ttk.Button(btns, text="clone valda", command=self._start)
        self.go_btn.pack(side="right")
        self._update_count()

    def _browse(self):
        d = filedialog.askdirectory(parent=self, title="Välj rotmapp",
                                    initialdir=self.root_var.get() or None)
        if d:
            self.root_var.set(os.path.normpath(d))

    def _read_readme(self):
        full = self.tree.focus() or (self.tree.selection() or [None])[0]
        if full:
            ReadmeWindow(self.app, full)
        else:
            popups.showinfo("Välj ett projekt", "Klicka på ett projekt i listan först.", parent=self)

    def _select_all(self):
        self.tree.selection_set(self.tree.get_children())

    def _select_none(self):
        self.tree.selection_remove(self.tree.selection())

    def _update_count(self):
        n = len(self.tree.selection())
        self.count.config(text=f"{n} av {len(self.candidates)} valda")
        self.go_btn.config(state="normal" if n else "disabled")

    def _start(self):
        root = os.path.normpath(self.root_var.get().strip())
        picked = [r for r in self.candidates if r["full_name"] in self.tree.selection()]
        if not picked or not self.root_var.get().strip():
            return
        if not os.path.isdir(root):
            if not popups.askyesno("Mappen finns inte", f"Skapa mappen\n{root}\n?", parent=self):
                return
            try:
                os.makedirs(root)
            except OSError as exc:
                popups.showerror("Kunde inte skapa mappen", str(exc), parent=self)
                return
        if not popups.askyesno(
                "Hämta projekt",
                f"Hämta {len(picked)} projekt till\n{root}\n\nDet kan ta en stund.", parent=self):
            return
        self.go_btn.config(state="disabled")
        self.cancel_btn.config(state="disabled")
        token, app = self.app.cfg["token"], self.app

        def work():
            res = {"cloned": [], "linked": [], "skipped": [], "failed": [], "paths": {}}
            for i, r in enumerate(picked, 1):
                app._q.put((self._progress, (i, len(picked), r["name"])))
                dest = os.path.join(root, r["name"])
                try:
                    if os.path.exists(dest):
                        if gitops.is_repo(dest) and r["full_name"].lower() in gitops.remote_url(dest).lower():
                            res["linked"].append(r["full_name"])
                        else:
                            res["skipped"].append((r["full_name"], "mappen finns redan och är inte detta projekt"))
                            continue
                    else:
                        gitops.clone(r["clone_url"], dest, token)
                        res["cloned"].append(r["full_name"])
                    gitops.ensure_exclude(dest, commitfile.FILENAME)
                    res["paths"][r["full_name"]] = dest
                except gitops.GitError as exc:
                    res["failed"].append((r["full_name"], str(exc).strip().splitlines()[-1]))
            return res
        app.bg(work, lambda res: self._finish(root, res), self._fail)

    def _progress(self, i, n, name):
        self.progress.config(text=f"Hämtar {i} av {n}: {name} ...", foreground=theme.CYAN)

    def _fail(self, exc):
        self.go_btn.config(state="normal")
        self.cancel_btn.config(state="normal")
        self.app._show_error(exc)

    def _finish(self, root, res):
        app = self.app
        app.cfg["projects"].update(res["paths"])
        app.cfg["default_parent"] = root
        config.save(app.cfg)
        lines = []
        if res["cloned"]:
            lines.append(f"Hämtade {len(res['cloned'])} projekt.")
        if res["linked"]:
            lines.append(f"Kopplade {len(res['linked'])} mappar som redan fanns i {root}.")
        for name, why in res["skipped"]:
            lines.append(f"Hoppade över {name}: {why}")
        for name, why in res["failed"]:
            lines.append(f"Misslyckades med {name}: {why}")
        self.destroy()
        app._reload_repos()
        (popups.showwarning if res["failed"] or res["skipped"] else popups.showinfo)(
            "clone klar", "\n".join(lines) or "Inget att göra.")


def main():
    GittaApp().mainloop()


if __name__ == "__main__":
    sys.exit(main())

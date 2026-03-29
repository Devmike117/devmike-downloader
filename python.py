#Devmike117
"""
Descarga videos de sitios como:
° YouTube
° Facebook (videos públicos)
° X (twitter)
° TikTok
° Instagram — reels, posts, stories
° Twitch - VODs, clips
° SoundCloud — audio
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import threading
import subprocess
import sys
import os
import re
import platform
from datetime import datetime

if platform.system() == "Windows":
    import winreg


# ─── Paleta de colores ────────────────────────────────────────────────────────
BG        = "#0d0d0f"
BG2       = "#141418"
BG3       = "#1c1c22"
SURFACE   = "#22222b"
BORDER    = "#2e2e3a"
ACCENT    = "#c084fc"        
ACCENT2   = "#818cf8"        
GREEN     = "#34d399"
RED       = "#f87171"
YELLOW    = "#fbbf24"
FG        = "#f1f0ff"
FG2       = "#a19fc8"
FG3       = "#6b6994"


def check_ytdlp():
    try:
        subprocess.run(["yt-dlp", "--version"],
                       capture_output=True, check=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False

FFMPEG_INSTALL_DIR = r"C:\ffmpeg\bin" if platform.system() == "Windows" else "/usr/local/bin"


def _ensure_ffmpeg_in_path():
    exe = os.path.join(FFMPEG_INSTALL_DIR, "ffmpeg.exe"
                       if platform.system() == "Windows" else "ffmpeg")
    if os.path.isfile(exe):
        if FFMPEG_INSTALL_DIR not in os.environ.get("PATH", ""):
            os.environ["PATH"] = FFMPEG_INSTALL_DIR + os.pathsep + os.environ.get("PATH", "")

def check_ffmpeg():
    _ensure_ffmpeg_in_path()
    try:
        subprocess.run(["ffmpeg", "-version"],
                       capture_output=True, check=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False

def install_ytdlp():
    subprocess.run([sys.executable, "-m", "pip", "install", "-U", "yt-dlp"],
                   check=True)


class FancyEntry(tk.Frame):
    def __init__(self, parent, placeholder="", **kwargs):
        super().__init__(parent, bg=BG, bd=0, highlightthickness=0)
        self.placeholder = placeholder
        self._active = False

        self.canvas = tk.Canvas(self, height=46, bg=BG, bd=0,
                                highlightthickness=0)
        self.canvas.pack(fill="x")

        self.entry = tk.Entry(self.canvas, font=("Consolas", 11),
                              bg=SURFACE, fg=FG2, insertbackground=ACCENT,
                              relief="flat", bd=0)
        self.entry.place(x=14, y=12, relwidth=1, width=-28, height=22)
        self.entry.bind("<FocusIn>",  self._on_focus_in)
        self.entry.bind("<FocusOut>", self._on_focus_out)
        self.entry.bind("<Configure>", lambda e: self._draw())
        self.bind("<Configure>", lambda e: self._draw())
        self.after(50, self._draw)
        self._set_placeholder()

    def _draw(self):
        w = self.canvas.winfo_width()
        if w < 2:
            return
        h = 46
        r = 8
        c = self.canvas
        c.delete("all")
        c.create_rectangle(0, 0, w, h, fill=SURFACE, outline="")
        color = ACCENT if self._active else BORDER
        c.create_arc(0, 0, r*2, r*2, start=90, extent=90,
                     outline=color, style="arc", width=1)
        c.create_arc(w-r*2, 0, w, r*2, start=0, extent=90,
                     outline=color, style="arc", width=1)
        c.create_arc(0, h-r*2, r*2, h, start=180, extent=90,
                     outline=color, style="arc", width=1)
        c.create_arc(w-r*2, h-r*2, w, h, start=270, extent=90,
                     outline=color, style="arc", width=1)
        c.create_line(r, 0, w-r, 0, fill=color)
        c.create_line(r, h-1, w-r, h-1, fill=color)
        c.create_line(0, r, 0, h-r, fill=color)
        c.create_line(w-1, r, w-1, h-r, fill=color)

    def _set_placeholder(self):
        self.entry.insert(0, self.placeholder)
        self.entry.config(fg=FG3)

    def _on_focus_in(self, e):
        self._active = True
        self._draw()
        if self.entry.get() == self.placeholder:
            self.entry.delete(0, "end")
            self.entry.config(fg=FG)

    def _on_focus_out(self, e):
        self._active = False
        self._draw()
        if not self.entry.get():
            self._set_placeholder()

    def get(self):
        val = self.entry.get()
        return "" if val == self.placeholder else val

    def set(self, val):
        self.entry.delete(0, "end")
        if val:
            self.entry.config(fg=FG)
            self.entry.insert(0, val)
        else:
            self._set_placeholder()


# ── CAMBIO 1: GlowProgressBar ahora tiene color dinámico ─────────────────────
class GlowProgressBar(tk.Canvas):
    def __init__(self, parent, **kwargs):
        super().__init__(parent, height=8, bg=BG, bd=0,
                         highlightthickness=0, **kwargs)
        self._pct   = 0
        self._color = ACCENT   # color activo de la barra
        self.bind("<Configure>", lambda e: self._draw())

    def set(self, pct):
        self._pct = max(0, min(100, pct))
        self._draw()

    def set_color(self, color):
        """Cambia el color de la barra y redibuja."""
        self._color = color
        self._draw()

    def reset(self):
        """Vuelve a 0 % y al color morado por defecto."""
        self._pct   = 0
        self._color = ACCENT
        self._draw()

    def _draw(self):
        w = self.winfo_width()
        if w < 2:
            return
        h = self.winfo_height()
        self.delete("all")
        # Fondo
        self.create_rectangle(0, 0, w, h, fill=SURFACE, outline="")
        # Relleno
        fill_w = int(w * self._pct / 100)
        if fill_w > 0:
            self.create_rectangle(0, 0, fill_w, h, fill=self._color, outline="")
            # Brillo superior — cambia de tono según el color activo
            if self._color == GREEN:
                highlight = "#6ee7b7"
            elif self._color == RED:
                highlight = "#fca5a5"
            else:
                highlight = "#e9d5ff"   # morado claro (ACCENT)
            self.create_rectangle(0, 0, fill_w, 2, fill=highlight, outline="")


class YTDLPApp(tk.Tk):
    def __init__(self):
        super().__init__()
        import os
        icon_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "favicon.ico")
        self.iconbitmap(icon_path)
        self.wm_iconbitmap(icon_path)
        self.title("Devmike117  ·  Descargador")
        self.geometry("820x680")
        self.minsize(700, 560)
        self.configure(bg=BG)
        self.resizable(True, True)
 
        self._dl_thread   = None
        self._proc        = None
        self._ffmpeg_ok   = check_ffmpeg()
        self._ytdlp_ok    = check_ytdlp()
        self._output_dir  = tk.StringVar(value=os.path.expanduser("~/Downloads"))
        self._format_var  = tk.StringVar(value="video_best")
        self._audio_fmt   = tk.StringVar(value="mp3")
        self._video_fmt   = tk.StringVar(value="mp4")
        self._speed_var   = tk.StringVar(value="")
        self._sub_var     = tk.BooleanVar(value=False)
        self._thumb_var   = tk.BooleanVar(value=False)
        self._playlist_var= tk.BooleanVar(value=False)
        self._status_msg  = tk.StringVar(value="Listo")
        self._progress    = 0
 
        self._build_ui()
        self._check_dep()
 
    def _check_dep(self):
        if not self._ytdlp_ok:
            self._dl_btn.configure(state="disabled")
            self._log("⚠ yt-dlp no encontrado. Instálalo con el botón de arriba.", "warn")
 
    def _install_ytdlp_auto(self):
        self._ytdlp_install_btn.configure(state="disabled", text="Instalando…")
        self._log("⬇ Instalando yt-dlp via pip…", "acc")
 
        def _run():
            try:
                proc = subprocess.Popen(
                    [sys.executable, "-m", "pip", "install", "-U", "yt-dlp"],
                    stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
                for line in proc.stdout:
                    line = line.strip()
                    if line:
                        self.after(0, lambda l=line: self._log(l, "dim"))
                proc.wait()
                if proc.returncode == 0 and check_ytdlp():
                    self._ytdlp_ok = True
                    self.after(0, self._on_ytdlp_installed)
                else:
                    self.after(0, lambda: self._log("✗ Error al instalar yt-dlp.", "err"))
                    self.after(0, lambda: self._ytdlp_install_btn.configure(
                        state="normal", text="⬇ Instalar yt-dlp"))
            except Exception as e:
                self.after(0, lambda: self._log(f"✗ {e}", "err"))
                self.after(0, lambda: self._ytdlp_install_btn.configure(
                    state="normal", text="⬇ Instalar yt-dlp"))
 
        threading.Thread(target=_run, daemon=True).start()
 
    def _on_ytdlp_installed(self):
        self._log("✓ yt-dlp instalado correctamente.", "ok")
        self._ytdlp_dot.configure(text="●", fg=GREEN)
        self._ytdlp_install_btn.destroy()
        self._dl_btn.configure(state="normal")
 
    def _build_ui(self):
        header = tk.Frame(self, bg=BG, pady=0)
        header.pack(fill="x", padx=28, pady=(22, 0))
 
        title_row = tk.Frame(header, bg=BG)
        title_row.pack(fill="x")
 
        tk.Label(title_row, text="Devmike",
                 font=("Georgia", 20, "bold"), bg=BG, fg=FG).pack(side="left")
        tk.Label(title_row, text=" downloader",
                 font=("Georgia", 20), bg=BG, fg=ACCENT).pack(side="left")
        tk.Label(title_row, text="  powered by yt-dlp",
                 font=("Consolas", 9), bg=BG, fg=FG3).pack(side="left", pady=(6, 0))
 
        sites_row = tk.Frame(header, bg=BG)
        sites_row.pack(fill="x", pady=(8, 0))
 
        tk.Label(sites_row, text="Descarga desde:",
                 font=("Consolas", 8), bg=BG, fg=FG3).pack(side="left", padx=(0, 8))
 
        platforms = [
            ("YouTube",    "#FF0000"),
            ("TikTok",     "#00f2ea"),
            ("Instagram",  "#C13584"),
            ("Twitter/X",  "#e1e1e1"),
            ("Facebook",   "#1877F2"),
            ("Twitch",     "#9146FF"),
            ("Vimeo",      "#1ab7ea"),
            ("SoundCloud", "#FF5500"),
            ("+ más",   FG3),
        ]
 
        for name, color in platforms:
            badge = tk.Frame(sites_row, bg=BG3,
                             highlightthickness=1, highlightbackground=BORDER)
            badge.pack(side="left", padx=(0, 4))
            tk.Label(badge, text=name, font=("Consolas", 8),
                     bg=BG3, fg=color, padx=6, pady=3).pack()
 
        sep = tk.Frame(self, bg=BORDER, height=1)
        sep.pack(fill="x", padx=28, pady=(12, 0))
 
        dep_bar = tk.Frame(self, bg=BG2)
        dep_bar.pack(fill="x", padx=28, pady=(6, 0))
        self._dep_bar = dep_bar

        tk.Label(dep_bar, text="yt-dlp", font=("Consolas", 8, "bold"),
                 bg=BG2, fg=FG3).pack(side="left", padx=(0, 4))
        ytdlp_color = GREEN if self._ytdlp_ok else RED
        self._ytdlp_dot = tk.Label(dep_bar,
                                    text="●" if self._ytdlp_ok else "● no encontrado",
                                    font=("Consolas", 8), bg=BG2, fg=ytdlp_color)
        self._ytdlp_dot.pack(side="left", padx=(0, 6))

        if not self._ytdlp_ok:
            self._ytdlp_install_btn = tk.Button(
                dep_bar, text="⬇ Instalar yt-dlp",
                font=("Consolas", 8, "bold"), bg=ACCENT, fg="#0d0d0f",
                activebackground=ACCENT2, activeforeground="#0d0d0f",
                relief="flat", padx=10, pady=2, cursor="hand2",
                command=self._install_ytdlp_auto)
            self._ytdlp_install_btn.pack(side="left", padx=(0, 14))
        else:
            tk.Frame(dep_bar, bg=BG2, width=14).pack(side="left") 

        tk.Label(dep_bar, text="ffmpeg", font=("Consolas", 8, "bold"),
                 bg=BG2, fg=FG3).pack(side="left", padx=(0, 4))
        ffmpeg_color = GREEN if self._ffmpeg_ok else RED
        self._ffmpeg_dot = tk.Label(dep_bar,
                                     text="●" if self._ffmpeg_ok else "● no encontrado",
                                     font=("Consolas", 8), bg=BG2, fg=ffmpeg_color)
        self._ffmpeg_dot.pack(side="left", padx=(0, 8))

        self._ffmpeg_status = None

        if not self._ffmpeg_ok:
            self._ffmpeg_warn_lbl = tk.Label(
                dep_bar,
                text="— sin ffmpeg: calidad reducida",
                font=("Consolas", 8), bg=BG2, fg=YELLOW)
            self._ffmpeg_warn_lbl.pack(side="left")

            self._ffmpeg_install_btn = tk.Button(
                dep_bar, text="⬇ Instalar ffmpeg",
                font=("Consolas", 8, "bold"), bg=ACCENT, fg="#0d0d0f",
                activebackground=ACCENT2, activeforeground="#0d0d0f",
                relief="flat", padx=10, pady=2, cursor="hand2",
                command=self._install_ffmpeg)
            self._ffmpeg_install_btn.pack(side="left", padx=(10, 0))

        body = tk.Frame(self, bg=BG)
        body.pack(fill="both", expand=True, padx=28, pady=16)
        body.columnconfigure(0, weight=1)

        self._url_row(body)
        self._dir_row(body)
        self._format_row(body)
        self._options_row(body)
        self._action_row(body)
        self._progress_row(body)
        self._log_row(body)

    def _section(self, parent, label, row):
        tk.Label(parent, text=label, font=("Consolas", 9, "bold"),
                 bg=BG, fg=FG3).grid(row=row, column=0, sticky="w",
                                      pady=(14, 2))

    def _url_row(self, p):
        self._section(p, "URL  ·  pega el enlace aquí", 0)
        self._url_entry = FancyEntry(p, placeholder="https://youtube.com/watch?v=…")
        self._url_entry.grid(row=1, column=0, sticky="ew", pady=(0, 0))

    def _dir_row(self, p):
        self._section(p, "CARPETA DE DESTINO", 2)
        row = tk.Frame(p, bg=BG)
        row.grid(row=3, column=0, sticky="ew")
        row.columnconfigure(0, weight=1)

        dir_entry = tk.Entry(row, textvariable=self._output_dir,
                             font=("Consolas", 10), bg=SURFACE, fg=FG,
                             insertbackground=ACCENT, relief="flat",
                             highlightthickness=1,
                             highlightcolor=ACCENT,
                             highlightbackground=BORDER)
        dir_entry.grid(row=0, column=0, sticky="ew", ipady=8, padx=(0, 8))

        tk.Button(row, text="Explorar", font=("Consolas", 9),
                  bg=SURFACE, fg=ACCENT, activebackground=BG3,
                  activeforeground=ACCENT, relief="flat", padx=12,
                  cursor="hand2",
                  command=self._browse_dir).grid(row=0, column=1)

    def _format_row(self, p):
        self._section(p, "FORMATO DE DESCARGA", 4)
        frow = tk.Frame(p, bg=BG)
        frow.grid(row=5, column=0, sticky="ew")

        opts = [
            ("🎬  Video (mejor calidad MP4)",  "video_best"),
            ("🎬  Video MP4",              "video_mp4"),
            ("🎵  Solo audio",             "audio"),
            ("📋  Personalizado",          "custom"),
        ]
        for i, (label, val) in enumerate(opts):
            rb = tk.Radiobutton(frow, text=label, variable=self._format_var,
                                value=val, font=("Consolas", 10),
                                bg=BG, fg=FG2, selectcolor=BG,
                                activebackground=BG, activeforeground=ACCENT,
                                indicatoron=True, cursor="hand2",
                                command=self._on_format_change)
            rb.grid(row=0, column=i, padx=(0, 18), sticky="w")

        self._fmt_sub_frame = tk.Frame(p, bg=BG)
        self._fmt_sub_frame.grid(row=6, column=0, sticky="ew", pady=(6, 0))
        self._on_format_change()

    def _on_format_change(self):
        for w in self._fmt_sub_frame.winfo_children():
            w.destroy()
        fmt = self._format_var.get()
        if fmt == "audio":
            tk.Label(self._fmt_sub_frame, text="Formato:",
                     font=("Consolas", 9), bg=BG, fg=FG3).pack(side="left")
            for f in ("mp3", "m4a", "flac", "wav", "opus"):
                tk.Radiobutton(self._fmt_sub_frame, text=f,
                               variable=self._audio_fmt, value=f,
                               font=("Consolas", 9), bg=BG, fg=FG2,
                               selectcolor=BG, activebackground=BG,
                               activeforeground=ACCENT,
                               cursor="hand2").pack(side="left", padx=6)
        elif fmt == "video_mp4":
            tk.Label(self._fmt_sub_frame, text="Resolución:",
                     font=("Consolas", 9), bg=BG, fg=FG3).pack(side="left")
            self._res_var = tk.StringVar(value="best")
            for r in ("best", "1080", "720", "480", "360"):
                tk.Radiobutton(self._fmt_sub_frame, text=r,
                               variable=self._res_var, value=r,
                               font=("Consolas", 9), bg=BG, fg=FG2,
                               selectcolor=BG, activebackground=BG,
                               activeforeground=ACCENT,
                               cursor="hand2").pack(side="left", padx=6)
        elif fmt == "custom":
            tk.Label(self._fmt_sub_frame, text="-f ",
                     font=("Consolas", 10, "bold"), bg=BG, fg=ACCENT
                     ).pack(side="left")
            self._custom_fmt = tk.Entry(self._fmt_sub_frame,
                                        font=("Consolas", 10),
                                        bg=SURFACE, fg=FG,
                                        insertbackground=ACCENT,
                                        relief="flat", width=28,
                                        highlightthickness=1,
                                        highlightbackground=BORDER,
                                        highlightcolor=ACCENT)
            self._custom_fmt.insert(0, "bestvideo+bestaudio/best")
            self._custom_fmt.pack(side="left", ipady=5, padx=(0, 8))

    def _options_row(self, p):
        self._section(p, "OPCIONES", 7)
        orow = tk.Frame(p, bg=BG)
        orow.grid(row=8, column=0, sticky="ew")

        checks = [
            ("Subtítulos automáticos", self._sub_var),
            ("Miniatura embebida",     self._thumb_var),
            ("Descargar lista completa", self._playlist_var),
        ]
        for i, (label, var) in enumerate(checks):
            tk.Checkbutton(orow, text=label, variable=var,
                           font=("Consolas", 9), bg=BG, fg=FG2,
                           selectcolor=BG, activebackground=BG,
                           activeforeground=ACCENT,
                           cursor="hand2").grid(row=0, column=i,
                                               padx=(0, 18), sticky="w")

        tk.Label(orow, text="Límite velocidad:", font=("Consolas", 9),
                 bg=BG, fg=FG3).grid(row=0, column=3, padx=(14, 4))
        sp = tk.Entry(orow, textvariable=self._speed_var,
                      font=("Consolas", 9), bg=SURFACE, fg=FG,
                      insertbackground=ACCENT, relief="flat", width=7,
                      highlightthickness=1, highlightbackground=BORDER,
                      highlightcolor=ACCENT)
        sp.grid(row=0, column=4, ipady=4)
        tk.Label(orow, text="(ej: 500K)", font=("Consolas", 8),
                 bg=BG, fg=FG3).grid(row=0, column=5, padx=(4, 0))

    def _action_row(self, p):
        arow = tk.Frame(p, bg=BG)
        arow.grid(row=9, column=0, sticky="ew", pady=(18, 4))

        self._dl_btn = tk.Button(
            arow, text="▼  DESCARGAR", font=("Consolas", 11, "bold"),
            bg=ACCENT, fg="#0d0d0f", activebackground=ACCENT2,
            activeforeground="#0d0d0f", relief="flat",
            padx=24, pady=10, cursor="hand2",
            command=self._start_download)
        self._dl_btn.pack(side="left")

        self._stop_btn = tk.Button(
            arow, text="■  DETENER", font=("Consolas", 11),
            bg=SURFACE, fg=RED, activebackground=BG3,
            activeforeground=RED, relief="flat",
            padx=18, pady=10, cursor="hand2",
            state="disabled",
            command=self._stop_download)
        self._stop_btn.pack(side="left", padx=(10, 0))

        self._update_btn = tk.Button(
            arow, text="↑ Comprobar actualización",
            font=("Consolas", 9), bg=SURFACE, fg=YELLOW,
            activebackground=BG3, activeforeground=YELLOW,
            relief="flat", padx=12, pady=10, cursor="hand2",
            command=self._check_ytdlp_update)
        self._update_btn.pack(side="right", padx=(0, 8))

        tk.Button(arow, text="Limpiar log",
                  font=("Consolas", 9), bg=BG, fg=FG3,
                  activebackground=BG, activeforeground=FG2,
                  relief="flat", padx=12, pady=10, cursor="hand2",
                  command=self._clear_log).pack(side="right")

    def _progress_row(self, p):
        prow = tk.Frame(p, bg=BG)
        prow.grid(row=10, column=0, sticky="ew", pady=(2, 8))
        prow.columnconfigure(0, weight=1)

        self._pbar = GlowProgressBar(prow)
        self._pbar.grid(row=0, column=0, sticky="ew", pady=(0, 4))

        status_row = tk.Frame(prow, bg=BG)
        status_row.grid(row=1, column=0, sticky="ew")
        status_row.columnconfigure(0, weight=1)

        self._status_lbl = tk.Label(status_row, textvariable=self._status_msg,
                                    font=("Consolas", 9), bg=BG, fg=FG2,
                                    anchor="w")
        self._status_lbl.grid(row=0, column=0, sticky="w")
        self._pct_lbl = tk.Label(status_row, text="",
                                  font=("Consolas", 9, "bold"),
                                  bg=BG, fg=ACCENT)
        self._pct_lbl.grid(row=0, column=1, sticky="e")

    def _log_row(self, p):
        lf = tk.Frame(p, bg=SURFACE, highlightthickness=1,
                      highlightbackground=BORDER)
        lf.grid(row=11, column=0, sticky="nsew", pady=(0, 4))
        p.rowconfigure(11, weight=1)

        header = tk.Frame(lf, bg=BG3)
        header.pack(fill="x")
        tk.Label(header, text="● SALIDA", font=("Consolas", 8, "bold"),
                 bg=BG3, fg=FG3, padx=10, pady=5).pack(side="left")

        self._log_text = tk.Text(lf, font=("Consolas", 9),
                                  bg=SURFACE, fg=FG2, relief="flat",
                                  wrap="word", state="disabled",
                                  padx=10, pady=6, insertbackground=ACCENT)
        scroll = ttk.Scrollbar(lf, command=self._log_text.yview)
        self._log_text.configure(yscrollcommand=scroll.set)
        scroll.pack(side="right", fill="y")
        self._log_text.pack(fill="both", expand=True)

        self._log_text.tag_config("ok",    foreground=GREEN)
        self._log_text.tag_config("err",   foreground=RED)
        self._log_text.tag_config("warn",  foreground=YELLOW)
        self._log_text.tag_config("acc",   foreground=ACCENT)
        self._log_text.tag_config("dim",   foreground=FG3)

    def _get_installed_version(self):
        try:
            r = subprocess.run(["yt-dlp", "--version"],
                               capture_output=True, text=True)
            return r.stdout.strip()
        except Exception:
            return None

    def _get_latest_version(self):
        import urllib.request, json
        url = "https://pypi.org/pypi/yt-dlp/json"
        with urllib.request.urlopen(url, timeout=8) as r:
            data = json.loads(r.read())
        return data["info"]["version"]

    def _normalize_version(self, v):
        try:
            return tuple(int(x) for x in v.strip().split("."))
        except Exception:
            return (0,)

    def _check_ytdlp_update(self):
        self._update_btn.configure(state="disabled", text="Comprobando…",
                                   fg=FG3)
        self._log("Comprobando versión de yt-dlp…", "dim")

        def _run():
            try:
                installed = self._get_installed_version()
                latest    = self._get_latest_version()

                if installed is None:
                    self.after(0, lambda: (
                        self._log("✗ No se pudo detectar la versión instalada.", "err"),
                        self._update_btn.configure(
                            state="normal",
                            text="↑ Comprobar actualización",
                            fg=YELLOW, bg=SURFACE)
                    ))
                    return

                self.after(0, lambda: self._log(
                    f"  Instalada: {installed}   Última: {latest}", "dim"))

                if self._normalize_version(installed) >= self._normalize_version(latest):
                    self.after(0, lambda: (
                        self._log(f"✓ yt-dlp {installed} — ya tienes la última versión.", "ok"),
                        self._update_btn.configure(
                            state="normal",
                            text=f"✓ v{installed} — al día",
                            fg=GREEN, bg=SURFACE,
                            activeforeground=GREEN,
                            command=self._check_ytdlp_update)
                    ))
                else:
                    self.after(0, lambda: (
                        self._log(
                            f"⬆ Nueva versión disponible: {latest}  (tienes {installed})",
                            "warn"),
                        self._update_btn.configure(
                            state="normal",
                            text=f"⬆ Actualizar  {installed} → {latest}",
                            fg="#0d0d0f", bg=YELLOW,
                            activebackground="#d97706",
                            activeforeground="#0d0d0f",
                            command=lambda: self._do_update_ytdlp(latest))
                    ))

            except Exception as e:
                self.after(0, lambda: (
                    self._log(f"✗ Error al comprobar versión: {e}", "err"),
                    self._update_btn.configure(
                        state="normal",
                        text="↑ Comprobar actualización",
                        fg=YELLOW, bg=SURFACE,
                        command=self._check_ytdlp_update)
                ))

        threading.Thread(target=_run, daemon=True).start()

    def _do_update_ytdlp(self, latest):
        self._update_btn.configure(state="disabled",
                                   text="Actualizando…", fg=FG3, bg=SURFACE)
        self._log(f"⬆ Actualizando yt-dlp a {latest}…", "acc")

        def _run():
            try:
                proc = subprocess.run(
                    [sys.executable, "-m", "pip", "install", "-U", "yt-dlp"],
                    capture_output=True, text=True)
                if proc.returncode == 0:
                    self.after(0, lambda: (
                        self._log(f"✓ yt-dlp actualizado a {latest}.", "ok"),
                        self._update_btn.configure(
                            state="normal",
                            text=f"✓ v{latest} — al día",
                            fg=GREEN, bg=SURFACE,
                            activeforeground=GREEN,
                            command=self._check_ytdlp_update)
                    ))
                else:
                    self.after(0, lambda: (
                        self._log(f"✗ Error al actualizar:\n{proc.stderr}", "err"),
                        self._update_btn.configure(
                            state="normal",
                            text="↑ Comprobar actualización",
                            fg=YELLOW, bg=SURFACE,
                            command=self._check_ytdlp_update)
                    ))
            except Exception as e:
                self.after(0, lambda: (
                    self._log(f"✗ {e}", "err"),
                    self._update_btn.configure(
                        state="normal",
                        text="↑ Comprobar actualización",
                        fg=YELLOW, bg=SURFACE,
                        command=self._check_ytdlp_update)
                ))

        threading.Thread(target=_run, daemon=True).start()

    def _install_ffmpeg(self):
        import urllib.request, zipfile

        FFMPEG_URL = (
            "https://github.com/BtbN/ffmpeg-builds/releases/download/latest/"
            "ffmpeg-master-latest-win64-gpl.zip"
        )
        INSTALL_DIR = r"C:\ffmpeg"
        BIN_DIR     = os.path.join(INSTALL_DIR, "bin")
        ZIP_TMP     = os.path.join(os.environ.get("TEMP", "C:\\Temp"), "ffmpeg_dl.zip")

        self._ffmpeg_install_btn.configure(state="disabled", text="Instalando…")

        def _run():
            try:
                self.after(0, lambda: self._log("⬇ Descargando ffmpeg (~90 MB)…", "acc"))

                def _progress(block, block_size, total):
                    if total > 0:
                        pct = min(100, block * block_size * 100 // total)
                        self.after(0, lambda p=pct: (
                            self._pbar.set(p),
                            self._pct_lbl.configure(text=f"{p}%"),
                            self._status_msg.set(f"Descargando ffmpeg… {p}%")
                        ))

                urllib.request.urlretrieve(FFMPEG_URL, ZIP_TMP, _progress)
                self.after(0, lambda: self._log("✓ Descarga completada. Extrayendo…", "ok"))

                with zipfile.ZipFile(ZIP_TMP, "r") as zf:
                    members = zf.namelist()
                    bin_members = [m for m in members
                                   if re.search(r"/bin/(ffmpeg|ffprobe|ffplay)\.exe$", m)]
                    os.makedirs(BIN_DIR, exist_ok=True)
                    for member in bin_members:
                        fname = os.path.basename(member)
                        dest  = os.path.join(BIN_DIR, fname)
                        with zf.open(member) as src, open(dest, "wb") as dst:
                            dst.write(src.read())

                os.remove(ZIP_TMP)
                self.after(0, lambda: self._log(f"✓ ffmpeg extraído en {BIN_DIR}", "ok"))

                added = False
                try:
                    key = winreg.OpenKey(
                        winreg.HKEY_LOCAL_MACHINE,
                        r"SYSTEM\CurrentControlSet\Control\Session Manager\Environment",
                        0, winreg.KEY_READ | winreg.KEY_WRITE)
                    path_val, _ = winreg.QueryValueEx(key, "Path")
                    if BIN_DIR.lower() not in path_val.lower():
                        winreg.SetValueEx(key, "Path", 0, winreg.REG_EXPAND_SZ,
                                          path_val + ";" + BIN_DIR)
                    winreg.CloseKey(key)
                    added = True
                    self.after(0, lambda: self._log("✓ PATH del sistema actualizado.", "ok"))
                except PermissionError:
                    try:
                        key = winreg.OpenKey(
                            winreg.HKEY_CURRENT_USER,
                            r"Environment",
                            0, winreg.KEY_READ | winreg.KEY_WRITE)
                        try:
                            path_val, _ = winreg.QueryValueEx(key, "Path")
                        except FileNotFoundError:
                            path_val = ""
                        if BIN_DIR.lower() not in path_val.lower():
                            winreg.SetValueEx(key, "Path", 0, winreg.REG_EXPAND_SZ,
                                              (path_val + ";" if path_val else "") + BIN_DIR)
                        winreg.CloseKey(key)
                        added = True
                        self.after(0, lambda: self._log(
                            "✓ PATH del usuario actualizado (sin privilegios de admin).", "ok"))
                    except Exception as e2:
                        self.after(0, lambda: self._log(
                            f"⚠ No se pudo escribir el PATH: {e2}\n"
                            f"  Agrega manualmente '{BIN_DIR}' a tu PATH.", "warn"))

                os.environ["PATH"] = os.environ.get("PATH", "") + ";" + BIN_DIR

                if check_ffmpeg():
                    self._ffmpeg_ok = True
                    self.after(0, self._on_ffmpeg_installed)
                else:
                    self.after(0, lambda: self._log(
                        "⚠ ffmpeg instalado pero no responde aún. "
                        "Reinicia la aplicación.", "warn"))
                    self.after(0, lambda: self._ffmpeg_install_btn.configure(
                        state="normal", text="⬇ Instalar ffmpeg automáticamente"))

            except Exception as e:
                self.after(0, lambda: self._log(f"✗ Error instalando ffmpeg: {e}", "err"))
                self.after(0, lambda: self._ffmpeg_install_btn.configure(
                    state="normal", text="⬇ Instalar ffmpeg automáticamente"))
            finally:
                self.after(0, lambda: (self._pbar.set(0),
                                       self._pct_lbl.configure(text=""),
                                       self._status_msg.set("Listo")))

        threading.Thread(target=_run, daemon=True).start()

    def _on_ffmpeg_installed(self):
        self._log("✓ ¡ffmpeg instalado y listo! Ahora puedes descargar en máxima calidad.", "ok")
        self._ffmpeg_dot.configure(text="●", fg=GREEN)
        try:
            self._ffmpeg_warn_lbl.destroy()
            self._ffmpeg_install_btn.destroy()
        except Exception:
            pass

    def _browse_dir(self):
        d = filedialog.askdirectory(initialdir=self._output_dir.get())
        if d:
            self._output_dir.set(d)

    def _log(self, msg, tag=None):
        self._log_text.configure(state="normal")
        ts = datetime.now().strftime("%H:%M:%S")
        line = f"[{ts}] {msg}\n"
        if tag:
            self._log_text.insert("end", line, tag)
        else:
            self._log_text.insert("end", line)
        self._log_text.see("end")
        self._log_text.configure(state="disabled")

    def _clear_log(self):
        self._log_text.configure(state="normal")
        self._log_text.delete("1.0", "end")
        self._log_text.configure(state="disabled")

    def _set_downloading(self, active: bool):
        state_dl   = "disabled" if active else "normal"
        state_stop = "normal"   if active else "disabled"
        self._dl_btn.configure(state=state_dl)
        self._stop_btn.configure(state=state_stop)

    def _build_cmd(self, url):
        fmt = self._format_var.get()
        cmd = ["yt-dlp", "--newline", "--progress", "--no-update"]

        if not self._playlist_var.get():
            cmd += ["--no-playlist"]

        out = os.path.join(self._output_dir.get(), "%(title)s.%(ext)s")
        cmd += ["-o", out]

        if fmt == "video_best":
            if self._ffmpeg_ok:
                cmd += ["-f", "bestvideo[ext=mp4]+bestaudio[ext=m4a]/bestvideo+bestaudio/best",
                        "--merge-output-format", "mp4"]
            else:
                cmd += ["-f", "best",
                        "--format-sort", "vcodec:h264,res,fps,acodec:aac"]

        elif fmt == "video_mp4":
            res = getattr(self, "_res_var", None)
            h   = res.get() if (res and res.get() != "best") else None
            if self._ffmpeg_ok:
                if h:
                    cmd += ["-f",
                            f"bestvideo[height<={h}][ext=mp4]+bestaudio[ext=m4a]"
                            f"/bestvideo[height<={h}]+bestaudio"
                            f"/best[height<={h}]",
                            "--merge-output-format", "mp4"]
                else:
                    cmd += ["-f",
                            "bestvideo[ext=mp4]+bestaudio[ext=m4a]"
                            "/bestvideo+bestaudio/best",
                            "--merge-output-format", "mp4"]
            else:
                if h:
                    cmd += ["-f",
                            f"best[height<={h}][ext=mp4]"
                            f"/best[height<={h}]"
                            f"/best[ext=mp4]/best",
                            "--format-sort", "res,fps"]
                else:
                    cmd += ["-f", "best[ext=mp4]/best",
                            "--format-sort", "res,fps"]

        elif fmt == "audio":
            afmt = self._audio_fmt.get()
            if self._ffmpeg_ok:
                cmd += ["-x", "--audio-format", afmt, "--audio-quality", "0"]
            else:
                cmd += ["-f", "bestaudio[ext=m4a]/bestaudio",
                        "--audio-quality", "0"]
                if afmt not in ("m4a", "webm"):
                    self.after(0, lambda: self._log(
                        f"⚠ Sin ffmpeg no se puede convertir a {afmt}. "
                        "Se descargará en m4a nativo.", "warn"))

        elif fmt == "custom":
            cf = getattr(self, "_custom_fmt", None)
            if cf:
                cmd += ["-f", cf.get()]

        if self._sub_var.get():
            cmd += ["--write-auto-sub", "--sub-langs", "es,en",
                    "--convert-subs", "srt"]

        if self._thumb_var.get():
            cmd += ["--embed-thumbnail"]

        sp = self._speed_var.get().strip()
        if sp:
            cmd += ["--limit-rate", sp]

        cmd.append(url)
        return cmd

    def _start_download(self):
        url = self._url_entry.get().strip()
        if not url:
            messagebox.showwarning("URL vacía", "Pega un enlace primero.")
            return

        out_dir = self._output_dir.get()
        if not os.path.isdir(out_dir):
            messagebox.showerror("Directorio inválido",
                                 f"La carpeta no existe:\n{out_dir}")
            return

        if not self._ffmpeg_ok and self._format_var.get() in ("video_best", "video_mp4"):
            if not messagebox.askyesno(
                    "ffmpeg no encontrado",
                    "Sin ffmpeg la descarga usará el mejor formato ya fusionado disponible "
                    "(generalmente 720p). La calidad será menor que con ffmpeg.\n\n"
                    "¿Continuar de todas formas?"):
                return

        self._set_downloading(True)
        # ── CAMBIO 2: reset al iniciar -> morado + 0% ─────────────────────────
        self._pbar.reset()
        self._pct_lbl.configure(text="")
        self._status_msg.set("Iniciando descarga…")
        self._log(f"URL: {url}", "acc")
        self._log(f"Destino: {out_dir}", "dim")

        cmd = self._build_cmd(url)
        self._log("Comando: " + " ".join(cmd), "dim")

        self._dl_thread = threading.Thread(
            target=self._run_download, args=(cmd,), daemon=True)
        self._dl_thread.start()

    def _run_download(self, cmd):
        try:
            creationflags = 0
            startupinfo = None
            if platform.system() == "Windows":
                creationflags = subprocess.CREATE_NO_WINDOW

            self._proc = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
                creationflags=creationflags,
                startupinfo=startupinfo
            )

            for line in self._proc.stdout:
                line = line.rstrip()
                if not line:
                    continue
                self._parse_line(line)

            self._proc.wait()
            rc = self._proc.returncode
            if rc == 0:
                self.after(0, self._on_done_ok)
            else:
                self.after(0, lambda: self._on_done_err(rc))
        except Exception as e:
            self.after(0, lambda: self._log(f"✗ Excepción: {e}", "err"))
            self.after(0, lambda: self._set_downloading(False))
        finally:
            self._proc = None

    def _parse_line(self, line):
        m = re.search(r"\[download\]\s+([\d.]+)%", line)
        if m:
            pct = float(m.group(1))
            self.after(0, lambda p=pct: self._update_progress(p, line))
            return

        if "[download] Destination:" in line or \
           "[Merger] Merging formats" in line or \
           "[ffmpeg]" in line:
            self.after(0, lambda: self._log(line, "dim"))
            return

        if "ERROR:" in line:
            self.after(0, lambda: self._log(line, "err"))
            return

        if "WARNING:" in line:
            self.after(0, lambda: self._log(line, "warn"))
            return

        self.after(0, lambda: self._log(line))

    def _update_progress(self, pct, line):
        self._pbar.set(pct)
        self._pct_lbl.configure(text=f"{pct:.1f}%")
        speed = re.search(r"at\s+([\d.]+\s*\w+/s)", line)
        eta   = re.search(r"ETA\s+(\S+)", line)
        parts = []
        if speed: parts.append(f"⇣ {speed.group(1)}")
        if eta:   parts.append(f"ETA {eta.group(1)}")
        self._status_msg.set("  ".join(parts) if parts else "Descargando…")

    # ── CAMBIO 3: al terminar bien -> barra VERDE ──────────────────────────────
    def _on_done_ok(self):
        self._pbar.set(100)
        self._pbar.set_color(GREEN)
        self._pct_lbl.configure(text="100%")
        self._status_msg.set("✓ Descarga completada")
        self._log("✓ ¡Descarga completada!", "ok")
        self._set_downloading(False)

    # ── CAMBIO 4: al terminar con error-> barra ROJA ──────────────────────────
    def _on_done_err(self, rc):
        self._pbar.set_color(RED)
        self._status_msg.set(f"✗ Error (código {rc})")
        self._log(f"✗ Proceso terminó con código {rc}", "err")
        self._set_downloading(False)

    def _stop_download(self):
        if self._proc:
            self._proc.terminate()
            self._log("■ Descarga cancelada por el usuario.", "warn")
            self._status_msg.set("Cancelado")
        self._set_downloading(False)


def apply_style():
    style = ttk.Style()
    style.theme_use("default")
    style.configure("Vertical.TScrollbar",
                    background=SURFACE, troughcolor=BG3,
                    bordercolor=BG, arrowcolor=FG3,
                    relief="flat")


if __name__ == "__main__":
    app = YTDLPApp()
    apply_style()
    app.mainloop()
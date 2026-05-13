import customtkinter as ctk
from tkinter import filedialog
from data.display_manager import DisplayManager
from data.manager import DataManager
import subprocess
import threading
import os


class SettingsView(ctk.CTkFrame):
    """Settings page: project path, languages, display options, actions."""

    def __init__(self, master, display_manager: DisplayManager,
                 data_manager: DataManager, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        self.dm = display_manager
        self.data_manager = data_manager

        # Header
        ctk.CTkLabel(
            self, text="Settings",
            font=ctk.CTkFont(family="League Spartan", size=28, weight="bold")
        ).pack(pady=(24, 4), padx=28, anchor="w")

        # Scrollable content
        self.scroll = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.scroll.pack(fill="both", expand=True, padx=24, pady=(8, 8))

        self._build_project_section()
        self._build_languages_section()
        self._build_display_section()
        self._build_actions_section()

        # Bottom bar
        bottom = ctk.CTkFrame(self, fg_color="transparent")
        bottom.pack(fill="x", padx=28, pady=(4, 20))

        self.status_label = ctk.CTkLabel(
            bottom, text="", font=ctk.CTkFont(family="Open Sans", size=12),
            text_color="gray")
        self.status_label.pack(side="left")

        ctk.CTkButton(
            bottom, text="Save Settings", height=36, width=160,
            font=ctk.CTkFont(family="League Spartan", size=15, weight="bold"),
            command=self._save
        ).pack(side="right")

    # ── Helpers ──────────────────────────────────────────────────────

    def _section(self, title: str) -> ctk.CTkFrame:
        card = ctk.CTkFrame(self.scroll, corner_radius=10)
        card.pack(fill="x", pady=6, padx=4)

        ctk.CTkLabel(
            card, text=title,
            font=ctk.CTkFont(family="League Spartan", size=16, weight="bold")
        ).pack(anchor="w", padx=16, pady=(12, 6))

        inner = ctk.CTkFrame(card, fg_color="transparent")
        inner.pack(fill="x", padx=16, pady=(0, 14))
        return inner

    # ── Signage Project ──────────────────────────────────────────────

    def _build_project_section(self):
        inner = self._section("Signage Project")

        row = ctk.CTkFrame(inner, fg_color="transparent")
        row.pack(fill="x")

        ctk.CTkLabel(row, text="Path:", width=50, anchor="w",
                     font=ctk.CTkFont(family="Open Sans", size=13)).pack(side="left")

        self.path_entry = ctk.CTkEntry(
            row, font=ctk.CTkFont(family="Open Sans", size=12),
            height=30, state="disabled")
        self.path_entry.pack(side="left", fill="x", expand=True, padx=(0, 8))

        path_str = str(self.dm.signage_root)
        self.path_entry.configure(state="normal")
        self.path_entry.insert(0, path_str)
        self.path_entry.configure(state="disabled")

        ctk.CTkButton(
            row, text="Browse...", width=90, height=30,
            font=ctk.CTkFont(family="League Spartan", size=12, weight="bold"),
            command=self._pick_project_dir
        ).pack(side="right")

        # Status
        self.project_status = ctk.CTkLabel(
            inner, text="", font=ctk.CTkFont(family="Open Sans", size=11))
        self.project_status.pack(anchor="w", pady=(4, 0))
        self._validate_project_path()

    def _pick_project_dir(self):
        path = filedialog.askdirectory(
            parent=self.winfo_toplevel(),
            title="Select Signage Project Directory")
        if path:
            self.path_entry.configure(state="normal")
            self.path_entry.delete(0, "end")
            self.path_entry.insert(0, path)
            self.path_entry.configure(state="disabled")
            self._validate_project_path()

    def _validate_project_path(self):
        path = self.path_entry.get() if self.path_entry.cget("state") == "normal" else self.path_entry._entry.get() if hasattr(self.path_entry, '_entry') else ""
        # Fallback: read from the display widget
        self.path_entry.configure(state="normal")
        path = self.path_entry.get()
        self.path_entry.configure(state="disabled")

        if os.path.isdir(path) and os.path.isdir(os.path.join(path, "frontend")):
            self.project_status.configure(text="Connected", text_color="#4CAF50")
        else:
            self.project_status.configure(text="Project not found at this path", text_color="#e53935")

    # ── Languages ────────────────────────────────────────────────────

    def _build_languages_section(self):
        inner = self._section("Languages")

        self.lang_vars = {}
        languages = self.data_manager.get_languages()

        for code, label in languages:
            var = ctk.BooleanVar(value=True)
            cb = ctk.CTkCheckBox(
                inner, text=f"{label} ({code})", variable=var,
                font=ctk.CTkFont(family="Open Sans", size=13))
            cb.pack(anchor="w", pady=2)
            if code == "en":
                cb.configure(state="disabled")
            self.lang_vars[code] = var

    # ── Display Settings ─────────────────────────────────────────────

    def _build_display_section(self):
        inner = self._section("Display")

        # Timeout
        row = ctk.CTkFrame(inner, fg_color="transparent")
        row.pack(fill="x", pady=3)

        ctk.CTkLabel(row, text="Timeout (seconds)", width=180, anchor="w",
                     font=ctk.CTkFont(family="Open Sans", size=13)).pack(side="left")

        self.timeout_entry = ctk.CTkEntry(
            row, width=80, height=30,
            font=ctk.CTkFont(family="Open Sans", size=12))
        self.timeout_entry.pack(side="left")
        self.timeout_entry.insert(0, str(self.dm.get("settings.timeout_seconds", 15)))

        # Toggles
        self.autoplay_var = ctk.BooleanVar(value=self.dm.get("settings.video_autoplay", True))
        self.muted_var = ctk.BooleanVar(value=self.dm.get("settings.video_muted", True))
        self.controls_var = ctk.BooleanVar(value=self.dm.get("settings.video_controls", True))

        for label, var in [("Video Autoplay", self.autoplay_var),
                           ("Video Muted", self.muted_var),
                           ("Show Video Controls", self.controls_var)]:
            ctk.CTkSwitch(
                inner, text=label, variable=var,
                font=ctk.CTkFont(family="Open Sans", size=13)
            ).pack(anchor="w", pady=3)

    # ── Actions ──────────────────────────────────────────────────────

    def _build_actions_section(self):
        inner = self._section("Actions")

        self.rebuild_status = ctk.CTkLabel(
            inner, text="",
            font=ctk.CTkFont(family="Open Sans", size=11), text_color="gray")

        btn_row = ctk.CTkFrame(inner, fg_color="transparent")
        btn_row.pack(fill="x")

        self.rebuild_btn = ctk.CTkButton(
            btn_row, text="Rebuild Frontend", width=160, height=34,
            font=ctk.CTkFont(family="League Spartan", size=13, weight="bold"),
            command=self._rebuild_frontend)
        self.rebuild_btn.pack(side="left", padx=(0, 10))

        self.rebuild_status.pack(anchor="w", pady=(6, 0))

    def _rebuild_frontend(self):
        frontend_dir = self.dm.signage_root / "frontend"
        if not frontend_dir.exists():
            self.rebuild_status.configure(text="Frontend directory not found", text_color="#e53935")
            return

        self.rebuild_btn.configure(state="disabled", text="Building...")
        self.rebuild_status.configure(text="Running npm build...", text_color="gray")

        def run():
            try:
                result = subprocess.run(
                    ["npm", "run", "build"],
                    cwd=str(frontend_dir),
                    capture_output=True, text=True, timeout=120)
                if result.returncode == 0:
                    msg, color = "Build completed successfully.", "#4CAF50"
                else:
                    msg, color = f"Build failed: {result.stderr[:200]}", "#e53935"
            except FileNotFoundError:
                msg, color = "npm not found. Install Node.js first.", "#e53935"
            except subprocess.TimeoutExpired:
                msg, color = "Build timed out after 120 seconds.", "#e53935"
            except Exception as e:
                msg, color = f"Error: {e}", "#e53935"

            self.after(0, lambda: self._rebuild_done(msg, color))

        threading.Thread(target=run, daemon=True).start()

    def _rebuild_done(self, msg: str, color: str):
        self.rebuild_btn.configure(state="normal", text="Rebuild Frontend")
        self.rebuild_status.configure(text=msg, text_color=color)

    # ── Save ─────────────────────────────────────────────────────────

    def _save(self):
        # Timeout
        try:
            timeout = int(self.timeout_entry.get())
            self.dm.set("settings.timeout_seconds", timeout)
        except ValueError:
            pass

        # Toggles
        self.dm.set("settings.video_autoplay", self.autoplay_var.get())
        self.dm.set("settings.video_muted", self.muted_var.get())
        self.dm.set("settings.video_controls", self.controls_var.get())

        self.dm.save()

        self.status_label.configure(text="Settings saved.", text_color="#4CAF50")
        self.after(4000, lambda: self.status_label.configure(text=""))

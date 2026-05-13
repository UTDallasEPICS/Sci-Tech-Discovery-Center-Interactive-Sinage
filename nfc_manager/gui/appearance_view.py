import customtkinter as ctk
from tkinter import colorchooser, filedialog
from PIL import Image
from data.display_manager import DisplayManager, GOOGLE_FONTS
import os


class AppearanceView(ctk.CTkFrame):
    """Visual configuration page: background, colors, fonts, text."""

    def __init__(self, master, display_manager: DisplayManager, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        self.dm = display_manager
        self.color_swatches = {}
        self.color_hex_labels = {}

        # Header
        ctk.CTkLabel(
            self, text="Appearance",
            font=ctk.CTkFont(family="League Spartan", size=28, weight="bold")
        ).pack(pady=(24, 4), padx=28, anchor="w")

        # Scrollable content
        self.scroll = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.scroll.pack(fill="both", expand=True, padx=24, pady=(8, 8))

        self._build_background_section()
        self._build_colors_section()
        self._build_fonts_section()
        self._build_text_section()

        # Bottom bar
        bottom = ctk.CTkFrame(self, fg_color="transparent")
        bottom.pack(fill="x", padx=28, pady=(4, 20))

        self.status_label = ctk.CTkLabel(
            bottom, text="", font=ctk.CTkFont(family="Open Sans", size=12),
            text_color="gray")
        self.status_label.pack(side="left")

        ctk.CTkButton(
            bottom, text="Apply Changes", height=36, width=160,
            font=ctk.CTkFont(family="League Spartan", size=15, weight="bold"),
            command=self._apply
        ).pack(side="right")

    # ── Sections ─────────────────────────────────────────────────────

    def _section(self, title: str) -> ctk.CTkFrame:
        """Create a grouped section card."""
        card = ctk.CTkFrame(self.scroll, corner_radius=10)
        card.pack(fill="x", pady=6, padx=4)

        ctk.CTkLabel(
            card, text=title,
            font=ctk.CTkFont(family="League Spartan", size=16, weight="bold")
        ).pack(anchor="w", padx=16, pady=(12, 6))

        inner = ctk.CTkFrame(card, fg_color="transparent")
        inner.pack(fill="x", padx=16, pady=(0, 14))
        return inner

    # ── Background Image ─────────────────────────────────────────────

    def _build_background_section(self):
        inner = self._section("Background Image")

        preview_row = ctk.CTkFrame(inner, fg_color="transparent")
        preview_row.pack(fill="x")

        # Thumbnail preview
        self.bg_preview_label = ctk.CTkLabel(preview_row, text="No image selected",
                                             width=200, height=120,
                                             corner_radius=8,
                                             fg_color=("gray80", "gray25"))
        self.bg_preview_label.pack(side="left", padx=(0, 12))

        info_col = ctk.CTkFrame(preview_row, fg_color="transparent")
        info_col.pack(side="left", fill="both", expand=True)

        self.bg_path_label = ctk.CTkLabel(
            info_col, text="No file selected",
            font=ctk.CTkFont(family="Open Sans", size=11), text_color="gray",
            wraplength=300, anchor="w", justify="left")
        self.bg_path_label.pack(anchor="w", pady=(10, 6))

        ctk.CTkButton(
            info_col, text="Change Background...", width=180, height=32,
            font=ctk.CTkFont(family="League Spartan", size=13, weight="bold"),
            command=self._pick_background
        ).pack(anchor="w")

        self._refresh_bg_preview()

    def _refresh_bg_preview(self):
        path = self.dm.get("appearance.background_image", "")

        # Try the signage project's current background if no override set
        if not path or not os.path.exists(path):
            fallback = self.dm.signage_root / "frontend" / "src" / "assets" / "background.png"
            if fallback.exists():
                path = str(fallback)

        if path and os.path.exists(path):
            try:
                img = Image.open(path)
                img.thumbnail((200, 120))
                ctk_img = ctk.CTkImage(light_image=img, dark_image=img,
                                       size=(200, 120))
                self.bg_preview_label.configure(image=ctk_img, text="")
                self.bg_preview_label._ctk_image = ctk_img  # prevent GC
                self.bg_path_label.configure(text=os.path.basename(path))
            except Exception:
                self.bg_preview_label.configure(image=None, text="Preview error")
        else:
            self.bg_preview_label.configure(image=None, text="No image selected")
            self.bg_path_label.configure(text="No file selected")

    def _pick_background(self):
        path = filedialog.askopenfilename(
            parent=self.winfo_toplevel(),
            title="Select Background Image",
            filetypes=[("Images", "*.png *.jpg *.jpeg *.webp")])
        if path:
            self.dm.set("appearance.background_image", path)
            self._refresh_bg_preview()

    # ── Colors ───────────────────────────────────────────────────────

    def _build_colors_section(self):
        inner = self._section("Colors")

        color_rows = [
            ("appearance.colors.primary", "Primary"),
            ("appearance.colors.accent", "Accent"),
            ("appearance.colors.text", "Text"),
        ]
        for key, label in color_rows:
            self._color_row(inner, key, label)

        # Separator
        ctk.CTkLabel(inner, text="Language Button Colors",
                     font=ctk.CTkFont(family="League Spartan", size=13, weight="bold")
                     ).pack(anchor="w", pady=(10, 4))

        button_colors = [
            ("appearance.colors.button_english", "English"),
            ("appearance.colors.button_spanish", "Spanish"),
            ("appearance.colors.button_telugu", "Telugu"),
        ]
        for key, label in button_colors:
            self._color_row(inner, key, label)

    def _color_row(self, parent, config_key: str, label: str):
        row = ctk.CTkFrame(parent, fg_color="transparent")
        row.pack(fill="x", pady=3)

        ctk.CTkLabel(
            row, text=label, width=120, anchor="w",
            font=ctk.CTkFont(family="Open Sans", size=13)
        ).pack(side="left")

        current = self.dm.get(config_key, "#ffffff")

        swatch = ctk.CTkFrame(row, width=32, height=32, corner_radius=6,
                               fg_color=current, border_width=2,
                               border_color=("gray60", "gray40"))
        swatch.pack(side="left", padx=(0, 8))
        swatch.pack_propagate(False)
        self.color_swatches[config_key] = swatch

        hex_label = ctk.CTkLabel(
            row, text=current, width=80,
            font=ctk.CTkFont(family="Open Sans", size=12, weight="bold"))
        hex_label.pack(side="left", padx=(0, 8))
        self.color_hex_labels[config_key] = hex_label

        ctk.CTkButton(
            row, text="Pick", width=60, height=28,
            font=ctk.CTkFont(family="League Spartan", size=12, weight="bold"),
            command=lambda k=config_key: self._pick_color(k)
        ).pack(side="left")

    def _pick_color(self, config_key: str):
        current = self.dm.get(config_key, "#ffffff")
        result = colorchooser.askcolor(initialcolor=current, parent=self.winfo_toplevel())
        if result and result[1]:
            hex_val = result[1]
            self.dm.set(config_key, hex_val)
            self.color_swatches[config_key].configure(fg_color=hex_val)
            self.color_hex_labels[config_key].configure(text=hex_val)

    # ── Fonts ────────────────────────────────────────────────────────

    def _build_fonts_section(self):
        inner = self._section("Fonts")

        for key, label in [("appearance.fonts.title", "Title Font"),
                           ("appearance.fonts.body", "Body Font")]:
            row = ctk.CTkFrame(inner, fg_color="transparent")
            row.pack(fill="x", pady=4)

            ctk.CTkLabel(
                row, text=label, width=120, anchor="w",
                font=ctk.CTkFont(family="Open Sans", size=13)
            ).pack(side="left")

            current = self.dm.get(key, "Fredoka")
            combo = ctk.CTkComboBox(
                row, values=GOOGLE_FONTS, width=240, height=32,
                font=ctk.CTkFont(family="Open Sans", size=12))
            combo.set(current)
            combo.pack(side="left", padx=(0, 8))

            # Bind selection change
            combo.configure(command=lambda val, k=key: self.dm.set(k, val))
            # Also store ref for manual get
            setattr(self, f"_font_combo_{key.split('.')[-1]}", combo)

    # ── Text Content ─────────────────────────────────────────────────

    def _build_text_section(self):
        inner = self._section("Display Text")

        text_fields = [
            ("appearance.scan_page.title", "Scan Page Title"),
            ("appearance.scan_page.subtitle", "Scan Page Subtitle"),
            ("appearance.language_select_page.title", "Language Page Title"),
            ("appearance.language_select_page.subtitle", "Language Page Subtitle"),
            ("appearance.language_select_page.footer", "Language Page Footer"),
        ]

        for key, label in text_fields:
            row = ctk.CTkFrame(inner, fg_color="transparent")
            row.pack(fill="x", pady=3)

            ctk.CTkLabel(
                row, text=label, width=180, anchor="w",
                font=ctk.CTkFont(family="Open Sans", size=13)
            ).pack(side="left")

            current = self.dm.get(key, "")
            entry = ctk.CTkEntry(
                row, font=ctk.CTkFont(family="Open Sans", size=12),
                height=30)
            entry.pack(side="left", fill="x", expand=True)
            if current:
                entry.insert(0, current)

            # Save on focus-out
            entry.bind("<FocusOut>", lambda e, k=key, w=entry: self.dm.set(k, w.get()))
            # Also store for apply
            setattr(self, f"_text_{key.replace('.', '_')}", entry)

    # ── Apply ────────────────────────────────────────────────────────

    def _apply(self):
        # Flush all text entries to config
        for attr_name in dir(self):
            if attr_name.startswith("_text_appearance_"):
                entry = getattr(self, attr_name)
                key = attr_name[len("_text_"):].replace("_", ".", 4)
                # reconstruct dotted key: appearance.scan_page.title etc.
                self._flush_text_entry(attr_name, entry)

        # Flush font combos
        for suffix in ("title", "body"):
            combo = getattr(self, f"_font_combo_{suffix}", None)
            if combo:
                self.dm.set(f"appearance.fonts.{suffix}", combo.get())

        result = self.dm.apply_to_signage()
        self.status_label.configure(text=result)
        self.after(5000, lambda: self.status_label.configure(text=""))

    def _flush_text_entry(self, attr_name: str, entry):
        """Convert attr name back to dotted config key and save."""
        # attr: _text_appearance_scan_page_title -> appearance.scan_page.title
        raw = attr_name[len("_text_"):]
        # Known structure: appearance.<section>.<field>
        parts = raw.split("_")
        # Reconstruct: appearance.scan_page.title or appearance.language_select_page.title
        # Find the dotted key by matching against known keys
        for key_template in [
            "appearance.scan_page.title",
            "appearance.scan_page.subtitle",
            "appearance.language_select_page.title",
            "appearance.language_select_page.subtitle",
            "appearance.language_select_page.footer",
        ]:
            normalized = key_template.replace(".", "_")
            if raw == normalized:
                self.dm.set(key_template, entry.get())
                return

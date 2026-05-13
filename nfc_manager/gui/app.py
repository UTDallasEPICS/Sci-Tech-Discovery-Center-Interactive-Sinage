import customtkinter as ctk
from PIL import Image
from typing import Dict
from data.manager import DataManager
from data.display_manager import DisplayManager
from nfc_reader.base import BaseNFCReader
from nfc_reader.mock_reader import MockNFCReader
from .views import ExhibitsView
from .appearance_view import AppearanceView
from .settings_view import SettingsView
from .modals import TagModal
import os


class App(ctk.CTk):
    SIDEBAR_COLOR = "#73008f"
    SIDEBAR_WIDTH = 240
    NAV_ACTIVE = "#9b30b5"
    NAV_HOVER = "#8a209f"

    def __init__(self, data_manager: DataManager, nfc_reader: BaseNFCReader,
                 display_manager: DisplayManager):
        super().__init__()

        self.data_manager = data_manager
        self.nfc_reader = nfc_reader
        self.display_manager = display_manager

        self.title("Exhibit Manager")
        self.geometry("1050x700")
        self.minsize(900, 600)
        ctk.set_appearance_mode("System")

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        self._build_sidebar()
        self._build_pages()

        self.nfc_reader.set_callback(self.on_tag_scanned)
        self.show_page("exhibits")

    # ── Sidebar ──────────────────────────────────────────────────────

    def _build_sidebar(self):
        self.sidebar = ctk.CTkFrame(self, width=self.SIDEBAR_WIDTH, corner_radius=0,
                                    fg_color=self.SIDEBAR_COLOR)
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        self.sidebar.grid_propagate(False)
        self.sidebar.grid_columnconfigure(0, weight=1)
        # rows: 0=logo, 1=status, 2=nav_exhibits, 3=nav_appearance, 4=nav_settings, 5=spacer, 6=mock
        self.sidebar.grid_rowconfigure(5, weight=1)

        # Logo
        logo_path = os.path.join(os.path.dirname(__file__), "logo_small.png")
        if os.path.exists(logo_path):
            logo_img = ctk.CTkImage(light_image=Image.open(logo_path),
                                    dark_image=Image.open(logo_path),
                                    size=(110, 110))
            logo_label = ctk.CTkLabel(self.sidebar, text="", image=logo_img)
            logo_label.grid(row=0, column=0, padx=20, pady=(24, 4))
        else:
            logo_label = ctk.CTkLabel(
                self.sidebar, text="Exhibit Manager",
                font=ctk.CTkFont(family="League Spartan", size=22, weight="bold"),
                text_color="#ffffff")
            logo_label.grid(row=0, column=0, padx=20, pady=(24, 4))

        self.status_label = ctk.CTkLabel(
            self.sidebar, text="Reader: Connected",
            font=ctk.CTkFont(family="Open Sans", size=12),
            text_color="#fffd24")
        self.status_label.grid(row=1, column=0, padx=20, pady=(0, 20))

        # Navigation buttons
        self.nav_buttons = {}
        nav_items = [
            ("exhibits", "Tags", 2),
            ("appearance", "Appearance", 3),
            ("settings", "Settings", 4),
        ]
        for name, label, row in nav_items:
            btn = ctk.CTkButton(
                self.sidebar, text=f"  {label}", anchor="w", height=40,
                corner_radius=8,
                fg_color="transparent", hover_color=self.NAV_HOVER,
                text_color="#ffffff",
                font=ctk.CTkFont(family="League Spartan", size=15, weight="bold"),
                command=lambda n=name: self.show_page(n))
            btn.grid(row=row, column=0, padx=14, pady=2, sticky="ew")
            self.nav_buttons[name] = btn

        # Mock controls
        if isinstance(self.nfc_reader, MockNFCReader):
            mock_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
            mock_frame.grid(row=6, column=0, padx=16, pady=(10, 18), sticky="sew")

            ctk.CTkLabel(mock_frame, text="Dev: Simulate Scan",
                         text_color="#ffffff",
                         font=ctk.CTkFont(family="League Spartan", size=13)).pack(pady=(0, 4))

            self.mock_uid_entry = ctk.CTkEntry(
                mock_frame, placeholder_text="Enter UID...",
                font=ctk.CTkFont(family="Open Sans", size=12),
                fg_color="#ffffff", text_color="#000000", height=30)
            self.mock_uid_entry.pack(fill="x", padx=4, pady=2)
            self.mock_uid_entry.insert(0, "1212866967841409")

            ctk.CTkButton(
                mock_frame, text="Simulate", height=30,
                font=ctk.CTkFont(family="League Spartan", size=13, weight="bold"),
                command=self._simulate_scan).pack(fill="x", padx=4, pady=(4, 0))

    # ── Pages ────────────────────────────────────────────────────────

    def _build_pages(self):
        self.pages = {}

        self.pages["exhibits"] = ExhibitsView(
            self, data_manager=self.data_manager,
            on_edit_callback=self.open_tag_modal)

        self.pages["appearance"] = AppearanceView(
            self, display_manager=self.display_manager)

        self.pages["settings"] = SettingsView(
            self, display_manager=self.display_manager,
            data_manager=self.data_manager)

        for page in self.pages.values():
            page.grid(row=0, column=1, sticky="nsew")
            page.grid_remove()

    def show_page(self, name: str):
        for key, page in self.pages.items():
            page.grid_remove()
        self.pages[name].grid()

        for key, btn in self.nav_buttons.items():
            if key == name:
                btn.configure(fg_color=self.NAV_ACTIVE)
            else:
                btn.configure(fg_color="transparent")

    # ── NFC / Tag Handling ───────────────────────────────────────────

    def _simulate_scan(self):
        uid = self.mock_uid_entry.get().strip()
        if uid:
            self.nfc_reader.simulate_scan(uid)

    def open_tag_modal(self, tag_data: dict = None, uid: str = None):
        if tag_data:
            target_uid = tag_data.get("uid")
            existing_data = tag_data
        else:
            target_uid = uid
            existing_data = self.data_manager.get_tag(uid)

        languages = self.data_manager.get_languages()

        def _open():
            modal = TagModal(
                self, uid=target_uid, existing_data=existing_data,
                on_save=self.save_tag_handler, languages=languages)
            modal.focus()

        self.after(0, _open)

    def on_tag_scanned(self, uid: str):
        self.after(0, lambda: self.open_tag_modal(uid=uid))

    def save_tag_handler(self, uid: str, name: str, video_paths: Dict[str, str]):
        existing = self.data_manager.get_tag(uid)
        try:
            if existing:
                self.data_manager.update_tag(uid, name, video_paths)
            else:
                self.data_manager.add_tag(uid, name, video_paths)
        except Exception as e:
            print(f"Error saving data: {e}")

        self.pages["exhibits"].refresh_list()

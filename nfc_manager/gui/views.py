import customtkinter as ctk
from typing import Callable


class ExhibitsView(ctk.CTkFrame):
    """View to list and manage all existing exhibit tags."""

    def __init__(self, master, data_manager, on_edit_callback: Callable[[dict], None], **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        self.data_manager = data_manager
        self.on_edit_callback = on_edit_callback

        # Header row
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.pack(fill="x", padx=28, pady=(24, 4))

        ctk.CTkLabel(
            header_frame, text="Manage Tags",
            font=ctk.CTkFont(family="League Spartan", size=28, weight="bold")
        ).pack(side="left")

        # Scrollable list
        self.scroll_frame = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.scroll_frame.pack(fill="both", expand=True, padx=24, pady=(8, 20))

        self.refresh_list()

    def refresh_list(self):
        for widget in self.scroll_frame.winfo_children():
            widget.destroy()

        tags = self.data_manager.get_all_tags()

        if not tags:
            ctk.CTkLabel(
                self.scroll_frame,
                text="No tags configured.\nScan a tag to add one.",
                font=ctk.CTkFont(family="Open Sans", size=14),
                text_color="gray"
            ).pack(pady=60)
            return

        for tag in tags:
            self._create_tag_row(tag)

    def _create_tag_row(self, tag: dict):
        row = ctk.CTkFrame(self.scroll_frame, corner_radius=10)
        row.pack(fill="x", pady=4, padx=4)

        # Accent bar on the left
        accent = ctk.CTkFrame(row, width=5, corner_radius=3, fg_color="#73008f")
        accent.pack(side="left", fill="y", padx=(6, 0), pady=8)

        # Info
        info = ctk.CTkFrame(row, fg_color="transparent")
        info.pack(side="left", padx=12, pady=10, fill="x", expand=True)

        ctk.CTkLabel(
            info, text=tag.get("name", "Unknown"),
            font=ctk.CTkFont(family="League Spartan", size=17, weight="bold")
        ).pack(anchor="w")

        ctk.CTkLabel(
            info, text=f"UID: {tag.get('uid')}",
            font=ctk.CTkFont(family="Open Sans", size=11), text_color="gray"
        ).pack(anchor="w")

        path_dict = tag.get("path", {})
        lang_labels = dict(self.data_manager.get_languages())
        langs = ", ".join(lang_labels.get(k, k) for k in sorted(path_dict.keys())) if path_dict else "none"
        ctk.CTkLabel(
            info, text=f"Videos: {langs}",
            font=ctk.CTkFont(family="Open Sans", size=11), text_color="gray"
        ).pack(anchor="w")

        # Action buttons
        btn_frame = ctk.CTkFrame(row, fg_color="transparent")
        btn_frame.pack(side="right", padx=12, pady=10)

        ctk.CTkButton(
            btn_frame, text="Edit", width=64, height=30,
            font=ctk.CTkFont(family="League Spartan", size=13, weight="bold"),
            command=lambda t=tag: self.on_edit_callback(t)
        ).pack(pady=2)

        ctk.CTkButton(
            btn_frame, text="Delete", width=64, height=30,
            font=ctk.CTkFont(family="League Spartan", size=13, weight="bold"),
            fg_color="#e53935", hover_color="#b71c1c",
            command=lambda u=tag["uid"]: self._confirm_delete(u)
        ).pack(pady=2)

    def _confirm_delete(self, uid: str):
        dialog = ctk.CTkToplevel(self)
        dialog.title("Confirm Delete")
        dialog.geometry("340x150")
        dialog.transient(self.winfo_toplevel())
        dialog.grab_set()
        dialog.resizable(False, False)

        ctk.CTkLabel(
            dialog, text="Delete this tag?",
            font=ctk.CTkFont(family="League Spartan", size=18, weight="bold")
        ).pack(pady=(20, 6))
        ctk.CTkLabel(
            dialog, text="This will also remove its video files.",
            font=ctk.CTkFont(family="Open Sans", size=12), text_color="gray"
        ).pack()

        btn_row = ctk.CTkFrame(dialog, fg_color="transparent")
        btn_row.pack(pady=16)

        ctk.CTkButton(
            btn_row, text="Cancel", width=100, height=32,
            fg_color="gray50", hover_color="gray40",
            font=ctk.CTkFont(family="League Spartan", size=13, weight="bold"),
            command=dialog.destroy
        ).pack(side="left", padx=8)

        def do_delete():
            self.data_manager.delete_tag(uid)
            dialog.destroy()
            self.refresh_list()

        ctk.CTkButton(
            btn_row, text="Delete", width=100, height=32,
            fg_color="#e53935", hover_color="#b71c1c",
            font=ctk.CTkFont(family="League Spartan", size=13, weight="bold"),
            command=do_delete
        ).pack(side="left", padx=8)

import json
import shutil
from pathlib import Path
from typing import Any, Optional


DEFAULT_DISPLAY_CONFIG = {
    "appearance": {
        "background_image": "",
        "colors": {
            "primary": "#f5224c",
            "accent": "#fd5600",
            "text": "#ffffff",
            "button_english": "#f5224c",
            "button_spanish": "#fd5600",
            "button_telugu": "#7d42fd",
        },
        "fonts": {
            "title": "Fredoka",
            "body": "Noto Sans Telugu",
        },
        "scan_page": {
            "title": "Scan Here",
            "subtitle": "",
        },
        "language_select_page": {
            "title": "Welcome",
            "subtitle": "to the Human Machine",
            "footer": "Choose your language to explore the amazing human body",
        },
    },
    "settings": {
        "timeout_seconds": 15,
        "video_autoplay": True,
        "video_muted": True,
        "video_controls": True,
    },
}

GOOGLE_FONTS = [
    "Fredoka", "Bubblegum Sans", "Comic Neue", "Nunito", "Poppins",
    "Quicksand", "Baloo 2", "Patrick Hand", "Chewy", "Luckiest Guy",
    "Bangers", "Righteous", "Lilita One", "Concert One", "Pacifico",
    "Noto Sans Telugu", "Open Sans", "Roboto", "Montserrat", "Lato",
    "Inter", "Raleway", "Playfair Display", "Merriweather", "Source Sans 3",
]


def _deep_merge(base: dict, override: dict) -> dict:
    """Merge override into base, filling missing keys from base."""
    result = base.copy()
    for key, val in override.items():
        if key in result and isinstance(result[key], dict) and isinstance(val, dict):
            result[key] = _deep_merge(result[key], val)
        else:
            result[key] = val
    return result


class DisplayManager:
    """Manages display/appearance configuration for the signage system."""

    def __init__(self, config_path: str, signage_root: Path):
        self.config_path = Path(config_path)
        self.signage_root = signage_root
        self.config = self._load()

    def _load(self) -> dict:
        if self.config_path.exists():
            try:
                with open(self.config_path, "r") as f:
                    data = json.load(f)
                return _deep_merge(DEFAULT_DISPLAY_CONFIG, data)
            except (json.JSONDecodeError, IOError):
                pass
        return json.loads(json.dumps(DEFAULT_DISPLAY_CONFIG))

    def save(self):
        """Persist config to disk."""
        self.config_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.config_path, "w") as f:
            json.dump(self.config, f, indent=4)

    def get(self, dotted_key: str, default: Any = None) -> Any:
        """Get a value by dotted path, e.g. 'appearance.colors.primary'."""
        parts = dotted_key.split(".")
        node = self.config
        for p in parts:
            if isinstance(node, dict) and p in node:
                node = node[p]
            else:
                return default
        return node

    def set(self, dotted_key: str, value: Any):
        """Set a value by dotted path."""
        parts = dotted_key.split(".")
        node = self.config
        for p in parts[:-1]:
            if p not in node or not isinstance(node[p], dict):
                node[p] = {}
            node = node[p]
        node[parts[-1]] = value

    def apply_to_signage(self) -> str:
        """Push all configuration to the signage project. Returns status message."""
        self.save()
        errors = []

        try:
            self._copy_background_image()
        except Exception as e:
            errors.append(f"Background: {e}")

        try:
            self._write_tailwind_config()
        except Exception as e:
            errors.append(f"Tailwind: {e}")

        try:
            self._write_index_css()
        except Exception as e:
            errors.append(f"CSS: {e}")

        try:
            self._write_display_config_json()
        except Exception as e:
            errors.append(f"Display config: {e}")

        if errors:
            return "Applied with warnings:\n" + "\n".join(errors)
        return "All changes applied successfully."

    def _copy_background_image(self):
        src = self.get("appearance.background_image", "")
        if not src:
            return
        src_path = Path(src)
        if not src_path.exists():
            return
        dest = self.signage_root / "frontend" / "src" / "assets" / "background.png"
        dest.parent.mkdir(parents=True, exist_ok=True)
        # Convert to PNG if needed via Pillow
        if src_path.suffix.lower() in (".jpg", ".jpeg", ".webp"):
            from PIL import Image
            img = Image.open(src_path)
            img.save(dest, "PNG")
        else:
            shutil.copy2(src_path, dest)

    def _write_tailwind_config(self):
        colors = self.get("appearance.colors", {})
        fonts = self.get("appearance.fonts", {})

        title_font = fonts.get("title", "Fredoka")
        body_font = fonts.get("body", "Noto Sans Telugu")

        content = f'''/** @type {{import('tailwindcss').Config}} */
/* Auto-generated by Exhibit Manager — manual edits will be overwritten */

export default {{
  content: [
    "./index.html",
    "./src/**/*.{{js,ts,jsx,tsx}}",
  ],
  theme: {{
    extend: {{
      gridTemplateRows: {{
        '12': 'repeat(12, minmax(0, 1fr))',
      }},
      fontFamily: {{
        title: ["{title_font}", "sans-serif"],
        subtitle: ["{body_font}", "sans-serif"],
      }},
      colors: {{
        "pink": "{colors.get("primary", "#f5224c")}",
        "orange": "{colors.get("accent", "#fd5600")}",
        "purple": "{colors.get("button_telugu", "#7d42fd")}",
        "pink-500": "{colors.get("button_english", "#ec4899")}",
        "purple-500": "#a855f7",
        "rose-500": "{colors.get("button_english", "#f43f5e")}",
        "indigo-500": "#6366f1",
      }},
    }},
  }},
  plugins: [],
}}
'''
        dest = self.signage_root / "frontend" / "tailwind.config.js"
        if dest.parent.exists():
            with open(dest, "w") as f:
                f.write(content)

    def _write_index_css(self):
        fonts = self.get("appearance.fonts", {})
        title_font = fonts.get("title", "Fredoka")
        body_font = fonts.get("body", "Noto Sans Telugu")

        # Build Google Fonts import URLs
        font_imports = set()
        for font in [title_font, body_font]:
            url_name = font.replace(" ", "+")
            font_imports.add(f"@import url('https://fonts.googleapis.com/css2?family={url_name}:wght@400;500;700&display=swap');")

        imports_str = "\n".join(sorted(font_imports))

        content = f"""{imports_str}

@tailwind base;
@tailwind components;
@tailwind utilities;

@layer utilities {{
  .bg-lang-bg {{
    background-image: url('./assets/background.png');
  }}
}}
"""
        dest = self.signage_root / "frontend" / "src" / "index.css"
        if dest.parent.exists():
            with open(dest, "w") as f:
                f.write(content)

    def _write_display_config_json(self):
        """Write a runtime-consumable config to the signage project root."""
        dest = self.signage_root / "display_config.json"
        with open(dest, "w") as f:
            json.dump(self.config, f, indent=4)

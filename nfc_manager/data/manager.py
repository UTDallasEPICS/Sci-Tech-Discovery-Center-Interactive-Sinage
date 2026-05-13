import json
import re
import shutil
from pathlib import Path, PurePosixPath
from typing import Dict, List, Optional


class DataManager:
    """Manages NFC tag data in the signage project's live testdata.json file."""

    def __init__(self, config_path: str = "config.json"):
        manager_dir = Path(__file__).resolve().parents[1]
        config_file = Path(config_path).expanduser()
        if not config_file.is_absolute():
            config_file = config_file.resolve() if config_file.exists() else manager_dir / config_file

        self.base_dir = config_file.parent

        # Load config
        config = self._load_config(config_file)
        signage_rel = config.get("signage_project_path", "..")
        self.languages = config.get("languages", ["en", "es", "te"])
        self.language_labels = config.get("language_labels", {"en": "English", "es": "Spanish", "te": "Telugu"})

        # Resolve signage project paths
        self.signage_root = self._resolve_signage_root(signage_rel)
        self.artifacts_dir = self.signage_root / "artifacts"
        self.data_file = self.signage_root / "interactive-signage-backend" / "polls" / "testdata.json"

        if not self.data_file.exists():
            raise FileNotFoundError(
                f"NFC tag database not found: {self.data_file}. "
                "Expected interactive-signage-backend/polls/testdata.json in the signage project."
            )

    def _load_config(self, config_path: Path) -> dict:
        """Load config.json."""
        if config_path.exists():
            with open(config_path, "r", encoding="utf-8") as f:
                return json.load(f)
        return {}

    def _resolve_signage_root(self, configured_path: str) -> Path:
        """Resolve and validate the actual signage project root."""
        configured = Path(configured_path).expanduser()
        root = configured if configured.is_absolute() else self.base_dir / configured
        root = root.resolve()

        required_dirs = ["frontend", "interactive-signage-backend", "artifacts"]
        missing = [name for name in required_dirs if not (root / name).is_dir()]
        if missing:
            raise FileNotFoundError(
                f"Invalid signage_project_path '{configured_path}' resolved to '{root}'. "
                f"Missing required project directories: {', '.join(missing)}."
            )

        return root

    def _load_exhibits(self) -> List[dict]:
        """Load tag records from the signage project's live testdata.json."""
        if not self.data_file.exists():
            return []
        try:
            with open(self.data_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            return []

    def _save_exhibits(self, data: List[dict]):
        """Save tag records to the signage project's live testdata.json."""
        with open(self.data_file, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)

    def _slugify(self, value: str) -> str:
        slug = re.sub(r"[^a-z0-9]+", "_", value.strip().lower()).strip("_")
        return slug or "untitled"

    def _artifact_folder_from_paths(self, path_dict: Dict[str, str], fallback_name: str) -> str:
        """Preserve the current artifacts/<folder>/... folder when editing."""
        for rel_path in path_dict.values():
            clean_path = str(rel_path).lstrip("/")
            parts = PurePosixPath(clean_path).parts
            if len(parts) >= 3 and parts[0] == "artifacts" and parts[1]:
                return parts[1]
        return self._slugify(fallback_name)

    def _copy_video(self, artifact_folder: str, lang: str, source_path: str) -> str:
        """Copy a video file into the signage artifacts directory.
        Returns the relative path used in testdata.json (e.g. 'artifacts/heart/en.mp4').
        """
        source = Path(source_path)
        if not source.exists():
            raise FileNotFoundError(f"Video file not found: {source_path}")

        dest_dir = self.artifacts_dir / artifact_folder
        dest_dir.mkdir(parents=True, exist_ok=True)

        dest_file = dest_dir / f"{lang}.mp4"
        if source.resolve() != dest_file.resolve():
            shutil.copy2(source, dest_file)

        return f"artifacts/{artifact_folder}/{lang}.mp4"

    def _delete_artifact_dir(self, artifact_folder: str):
        """Remove an artifact's video directory."""
        artifact_dir = self.artifacts_dir / artifact_folder
        if artifact_dir.exists():
            shutil.rmtree(artifact_dir)

    def validate_video_paths(self) -> List[str]:
        """Return missing root-artifacts video paths referenced by the tag database."""
        missing = []
        for item in self._load_exhibits():
            for rel_path in item.get("path", {}).values():
                clean_path = str(rel_path).lstrip("/")
                parts = PurePosixPath(clean_path).parts
                if len(parts) < 3 or parts[0] != "artifacts":
                    missing.append(str(rel_path))
                    continue
                video_path = self.signage_root / clean_path
                if not video_path.is_file():
                    missing.append(str(rel_path))
        return missing

    def get_languages(self):
        """Return list of (code, label) tuples for configured languages."""
        return [(code, self.language_labels.get(code, code)) for code in self.languages]

    def get_all_tags(self) -> List[dict]:
        """Return all exhibits as a list of dicts with uid included."""
        exhibits = self._load_exhibits()
        result = []
        for item in exhibits:
            tag = {
                "uid": item["id"],
                "name": item["name"],
                "path": item.get("path", {}),
            }
            result.append(tag)
        return result

    def get_tag(self, uid: str) -> Optional[dict]:
        """Get a single exhibit by UID."""
        exhibits = self._load_exhibits()
        for item in exhibits:
            if item.get("id") == uid:
                return {
                    "uid": item["id"],
                    "name": item["name"],
                    "path": item.get("path", {}),
                }
        return None

    def add_tag(self, uid: str, name: str, video_paths: Dict[str, str]) -> dict:
        """Add a new exhibit.

        Args:
            uid: NFC tag decimal ID string
            name: Exhibit/artifact name (used to derive folder name, e.g. 'heart')
            video_paths: Dict mapping language codes to source file paths,
                         e.g. {'en': '/path/to/en.mp4', 'es': '/path/to/es.mp4'}
        """
        exhibits = self._load_exhibits()

        # Check for duplicate UID
        for item in exhibits:
            if item.get("id") == uid:
                raise ValueError(f"Tag {uid} already exists.")

        # Copy videos and build path dict
        artifact_folder = self._slugify(name)
        path_dict = {}
        for lang, source in video_paths.items():
            if source:
                path_dict[lang] = self._copy_video(artifact_folder, lang, source)

        exhibit = {
            "id": uid,
            "name": name,
            "path": path_dict,
        }
        exhibits.append(exhibit)
        self._save_exhibits(exhibits)

        return {"uid": uid, "name": name, "path": path_dict}

    def update_tag(self, uid: str, name: str, video_paths: Optional[Dict[str, str]] = None) -> dict:
        """Update an existing exhibit.

        Args:
            uid: NFC tag decimal ID string
            name: New exhibit name
            video_paths: Optional dict of language to source file path.
                         Only languages with non-None values are updated.
        """
        exhibits = self._load_exhibits()

        target = None
        for item in exhibits:
            if item.get("id") == uid:
                target = item
                break

        if target is None:
            raise KeyError(f"Tag {uid} not found.")

        path_dict = target.get("path", {})
        artifact_folder = self._artifact_folder_from_paths(path_dict, name)

        # Copy any new video files
        if video_paths:
            for lang, source in video_paths.items():
                if source and not str(source).startswith("artifacts/"):
                    # It's a new file to copy (not an existing relative path)
                    path_dict[lang] = self._copy_video(artifact_folder, lang, source)

        target["name"] = name
        target["path"] = path_dict
        self._save_exhibits(exhibits)

        return {"uid": uid, "name": name, "path": path_dict}

    def delete_tag(self, uid: str):
        """Delete an exhibit and its video files."""
        exhibits = self._load_exhibits()
        new_exhibits = []
        deleted_folder = None

        for item in exhibits:
            if item.get("id") == uid:
                deleted_folder = self._artifact_folder_from_paths(
                    item.get("path", {}),
                    item.get("name", ""),
                )
            else:
                new_exhibits.append(item)

        if deleted_folder:
            self._delete_artifact_dir(deleted_folder)

        self._save_exhibits(new_exhibits)

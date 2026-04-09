"""JSON 파일 기반 로컬 저장소."""

import json
import os
from pathlib import Path


class JsonStore:
    """~/AppData/RainDrop/ 또는 ~/Library/Application Support/RainDrop/에 JSON 저장."""

    def __init__(self):
        if os.name == "nt":  # Windows
            base = Path(os.environ.get("APPDATA", Path.home()))
        else:  # macOS/Linux
            base = Path.home() / "Library" / "Application Support"
        self.directory = base / "RainDrop"
        self.directory.mkdir(parents=True, exist_ok=True)

    def load(self, filename: str, default=None):
        path = self.directory / filename
        if not path.exists():
            return default
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return default

    def save(self, filename: str, data):
        path = self.directory / filename
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2, default=str)

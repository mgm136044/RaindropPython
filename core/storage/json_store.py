"""JSON 파일 기반 로컬 저장소."""

import json
import os
import platform
from pathlib import Path


class JsonStore:
    """플랫폼별 앱 데이터 디렉토리에 JSON 저장."""

    def __init__(self):
        if os.name == "nt":  # Windows
            base = Path(os.environ.get("APPDATA", str(Path.home())))
        elif platform.system() == "Darwin":  # macOS
            base = Path.home() / "Library" / "Application Support"
        else:  # Linux
            base = Path(os.environ.get("XDG_DATA_HOME", str(Path.home() / ".local" / "share")))
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

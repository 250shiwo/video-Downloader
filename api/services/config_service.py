from __future__ import annotations

import json
from pathlib import Path

from api.config import DOWNLOADS_DIR, SETTINGS_FILE
from api.models import AppSettings


class ConfigService:
    def __init__(self, settings_file: Path = SETTINGS_FILE) -> None:
        self.settings_file = settings_file

    def get_settings(self) -> AppSettings:
        if not self.settings_file.exists():
            settings = AppSettings(download_dir=str(DOWNLOADS_DIR))
            self.save_settings(settings)
            return settings

        raw = json.loads(self.settings_file.read_text(encoding="utf-8"))
        settings = AppSettings.model_validate(raw)
        download_dir = Path(settings.download_dir).expanduser()
        download_dir.mkdir(parents=True, exist_ok=True)
        return settings

    def save_settings(self, settings: AppSettings) -> AppSettings:
        download_dir = Path(settings.download_dir).expanduser()
        download_dir.mkdir(parents=True, exist_ok=True)

        self.settings_file.parent.mkdir(parents=True, exist_ok=True)
        self.settings_file.write_text(
            settings.model_dump_json(indent=2),
            encoding="utf-8",
        )
        return settings

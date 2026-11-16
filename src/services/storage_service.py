"""Per-project filesystem storage."""

from __future__ import annotations

import json
import uuid
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path

from config.settings import Settings
from src.models.schemas import ProjectRecord
from src.utils.file_utils import atomic_write_text, safe_filename


@dataclass(frozen=True)
class ProjectPaths:
    project_id: str
    root: Path
    script: Path
    assets: Path
    videos: Path
    images: Path
    audio: Path
    subtitles: Path
    output: Path
    logs: Path


class ProjectStorage:
    def __init__(self, settings: Settings | None = None) -> None:
        self.settings = settings or Settings.from_env()
        self.settings.ensure_directories()

    def create(self, topic: str) -> ProjectPaths:
        stamp = datetime.now(UTC).strftime("%Y%m%d_%H%M%S")
        project_id = f"project_{stamp}_{uuid.uuid4().hex[:6]}"
        root = self.settings.storage_dir / "projects" / project_id
        paths = ProjectPaths(project_id, root, root / "script", root / "assets", root / "assets" / "videos", root / "assets" / "images", root / "audio", root / "subtitles", root / "output", root / "logs")
        for path in (paths.script, paths.videos, paths.images, paths.audio, paths.subtitles, paths.output, paths.logs):
            path.mkdir(parents=True, exist_ok=True)
        self.write_json(paths.root / "project.json", {"project_id": project_id, "topic": topic, "created_at": datetime.now(UTC).isoformat(), "status": "created"})
        return paths

    @staticmethod
    def write_json(path: Path, payload: dict) -> Path:
        atomic_write_text(path, json.dumps(payload, indent=2, ensure_ascii=False))
        return path

    @staticmethod
    def write_text(path: Path, text: str) -> Path:
        atomic_write_text(path, text)
        return path


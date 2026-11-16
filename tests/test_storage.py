from pathlib import Path

from config.settings import Settings
from src.services.history_service import HistoryService
from src.services.storage_service import ProjectStorage


def test_project_storage_creates_expected_tree(tmp_path: Path) -> None:
    settings = Settings(storage_dir=tmp_path / "storage", database_path=tmp_path / "storage" / "history.db")
    project = ProjectStorage(settings).create("A topic")
    assert project.output.is_dir()
    assert (project.root / "project.json").exists()


def test_history_round_trip(tmp_path: Path) -> None:
    history = HistoryService(tmp_path / "history.db")
    history.upsert("project_1", "Topic", "complete", "output.mp4", "thumbnail.png")
    records = history.list_projects()
    assert records[0].project_id == "project_1"
    assert records[0].status == "complete"


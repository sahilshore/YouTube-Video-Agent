from pathlib import Path

import pytest

from src.models.schemas import Scene, VideoScript
from src.utils.file_utils import ensure_within, safe_filename
from src.utils.validators import approximate_duration, parse_model_json


def test_script_normalizes_scene_numbers_and_duration() -> None:
    script = VideoScript.model_validate({
        "video_title": "AI",
        "hook": "Imagine this.",
        "scenes": [
            {"scene_number": 9, "scene_title": "One", "narration": "A", "visual_description": "A", "visual_search_query": "ai", "estimated_duration": 4},
            {"scene_number": 9, "scene_title": "Two", "narration": "B", "visual_description": "B", "visual_search_query": "future", "estimated_duration": 6},
        ],
    })
    assert [scene.scene_number for scene in script.scenes] == [1, 2]
    assert script.estimated_duration == 10


def test_parse_model_json_accepts_fenced_json() -> None:
    scene = parse_model_json('```json\n{"scene_number": 1, "scene_title": "x", "narration": "y", "visual_description": "z", "visual_search_query": "x", "estimated_duration": 2}\n```', Scene)
    assert scene.scene_number == 1


def test_scene_duration_defaults_when_provider_omits_it() -> None:
    scene = Scene(scene_number=1, scene_title="x", narration="y", visual_description="z", visual_search_query="x")
    assert scene.estimated_duration == 1.0


def test_safe_filename_and_root_check(tmp_path: Path) -> None:
    assert safe_filename("hello world!.mp4") == "hello_world_.mp4"
    assert ensure_within(tmp_path / "child", tmp_path) == (tmp_path / "child").resolve()
    with pytest.raises(ValueError):
        ensure_within(tmp_path.parent / "outside", tmp_path)


def test_approximate_duration_is_positive() -> None:
    assert approximate_duration("one two three") > 0


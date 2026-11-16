from pathlib import Path

from src.services.video.scene_composer import compose_filter, subtitles_filter
from src.services.video.thumbnail_generator import generate_thumbnail
from src.services.video.video_renderer import VideoRenderer


def test_compose_filter_contains_crop_and_concat() -> None:
    graph = compose_filter([Path("one.mp4"), Path("two.mp4")], 1080, 1920, [3, 4])
    assert "crop=1080:1920" in graph
    assert "concat=n=2" in graph


def test_renderer_builds_safe_argument_list(tmp_path: Path) -> None:
    command = VideoRenderer().build_command([Path("one.mp4")], tmp_path / "out.mp4", 1920, 1080, [5])
    assert command[0] == "ffmpeg"
    assert "-filter_complex" in command
    assert "out.mp4" in str(command[-1])


def test_thumbnail_is_1280x720(tmp_path: Path) -> None:
    output = generate_thumbnail("A useful video title", tmp_path / "thumbnail.png")
    from PIL import Image

    assert Image.open(output).size == (1280, 720)


from pathlib import Path

from src.services.audio.subtitle_service import sentence_cues, write_ass, write_srt


def test_sentence_cues_cover_requested_duration() -> None:
    cues = sentence_cues("First sentence. Second sentence!", 10)
    assert len(cues) == 2
    assert cues[0].start == 0
    assert cues[-1].end == 10


def test_subtitle_files_are_written(tmp_path: Path) -> None:
    cues = sentence_cues("Hello world.", 2)
    srt = write_srt(cues, tmp_path / "subtitles.srt")
    ass = write_ass(cues, tmp_path / "subtitles.ass")
    assert "00:00:00,000 --> 00:00:02,000" in srt.read_text(encoding="utf-8")
    assert "Dialogue:" in ass.read_text(encoding="utf-8")


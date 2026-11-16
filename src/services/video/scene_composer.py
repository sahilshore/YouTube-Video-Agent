"""Build safe FFmpeg filter graphs for scene clips."""

from __future__ import annotations

from pathlib import Path


def compose_filter(clips: list[Path], width: int, height: int, durations: list[float], fps: int = 30) -> str:
    parts: list[str] = []
    labels: list[str] = []
    for index, (duration, _) in enumerate(zip(durations, clips)):
        label = f"v{index}"
        parts.append(f"[{index}:v]scale={width}:{height}:force_original_aspect_ratio=increase,crop={width}:{height},setsar=1,fps={fps},trim=duration={max(0.1, duration)},setpts=PTS-STARTPTS[{label}]")
        labels.append(f"[{label}]")
    parts.append("".join(labels) + f"concat=n={len(labels)}:v=1:a=0,format=yuv420p[vout]")
    return ";".join(parts)


def subtitles_filter(path: Path) -> str:
    escaped = path.resolve().as_posix().replace(":", r"\:").replace("'", r"\'")
    return f"subtitles=filename='{escaped}'"


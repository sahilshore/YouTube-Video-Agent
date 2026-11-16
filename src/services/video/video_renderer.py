"""CPU-friendly FFmpeg renderer and FFprobe validation."""

from __future__ import annotations

import json
import subprocess
from pathlib import Path

from config.settings import Settings
from src.core.constants import FPS
from src.core.exceptions import RenderError
from src.services.video.scene_composer import compose_filter, subtitles_filter


class VideoRenderer:
    def __init__(self, settings: Settings | None = None) -> None:
        self.settings = settings or Settings.from_env()

    def build_command(self, clips: list[Path], output: Path, width: int, height: int, durations: list[float], audio: Path | None = None, subtitles: Path | None = None, title: str | None = None) -> list[str]:
        if not clips:
            raise RenderError("At least one video clip is required")
        if len(clips) != len(durations):
            raise RenderError("Each clip must have a matching duration")
        video_filter = compose_filter(clips, width, height, durations, FPS)
        if subtitles:
            video_filter += f";[vout]{subtitles_filter(subtitles)}[vsub]"
            video_map = "[vsub]"
        else:
            video_map = "[vout]"
        command = [self.settings.ffmpeg_path, "-y"]
        for clip in clips:
            command.extend(["-i", str(clip)])
        if audio:
            command.extend(["-i", str(audio)])
        command.extend(["-filter_complex", video_filter, "-map", video_map])
        if audio:
            command.extend(["-map", f"{len(clips)}:a:0", "-shortest"])
        command.extend(["-r", str(FPS), "-c:v", "libx264", "-preset", "veryfast", "-crf", "22", "-pix_fmt", "yuv420p", "-c:a", "aac", "-movflags", "+faststart", str(output)])
        return command

    def render(self, clips: list[Path], output: Path, width: int, height: int, durations: list[float], audio: Path | None = None, subtitles: Path | None = None, title: str | None = None) -> Path:
        output.parent.mkdir(parents=True, exist_ok=True)
        command = self.build_command(clips, output, width, height, durations, audio, subtitles, title)
        result = subprocess.run(command, capture_output=True, text=True, check=False)
        if result.returncode != 0:
            raise RenderError(f"FFmpeg rendering failed: {result.stderr[-2000:]}")
        self.validate(output, width, height)
        return output

    def probe(self, path: Path) -> dict:
        result = subprocess.run([self.settings.ffprobe_path, "-v", "error", "-show_streams", "-show_format", "-of", "json", str(path)], capture_output=True, text=True, check=False)
        if result.returncode != 0:
            raise RenderError(f"FFprobe failed: {result.stderr[-1000:]}")
        return json.loads(result.stdout)

    def validate(self, path: Path, width: int, height: int) -> dict:
        if not path.exists() or path.stat().st_size == 0:
            raise RenderError("Rendered video is missing or empty")
        metadata = self.probe(path)
        video = next((stream for stream in metadata.get("streams", []) if stream.get("codec_type") == "video"), None)
        if not video:
            raise RenderError("Rendered file has no video stream")
        if int(video.get("width", 0)) != width or int(video.get("height", 0)) != height:
            raise RenderError(f"Rendered resolution is {video.get('width')}x{video.get('height')}, expected {width}x{height}")
        return metadata


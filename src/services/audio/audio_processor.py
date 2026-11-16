"""FFmpeg-backed audio trim, loop, fade, and mix helpers."""

from __future__ import annotations

import subprocess
from pathlib import Path

from config.settings import Settings
from src.core.exceptions import RenderError


class AudioProcessor:
    def __init__(self, settings: Settings | None = None) -> None:
        self.settings = settings or Settings.from_env()

    def mix(self, narration: Path, music: Path | None, output: Path, duration: float, music_volume: float = 0.12) -> Path:
        output.parent.mkdir(parents=True, exist_ok=True)
        if music is None:
            command = [self.settings.ffmpeg_path, "-y", "-i", str(narration), "-t", str(duration), "-c:a", "aac", str(output)]
        else:
            command = [self.settings.ffmpeg_path, "-y", "-i", str(narration), "-stream_loop", "-1", "-i", str(music), "-filter_complex", f"[1:a]volume={music_volume},afade=t=in:st=0:d=1,afade=t=out:st={max(0, duration - 2)}:d=2[m];[0:a][m]amix=inputs=2:duration=first:dropout_transition=2[a]", "-map", "[a]", "-t", str(duration), "-c:a", "aac", str(output)]
        result = subprocess.run(command, capture_output=True, text=True, check=False)
        if result.returncode != 0:
            raise RenderError(f"Audio processing failed: {result.stderr[-1000:]}")
        return output


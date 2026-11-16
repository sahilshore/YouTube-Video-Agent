"""Edge TTS narration generation."""

from __future__ import annotations

import asyncio
from pathlib import Path

from src.core.exceptions import ProviderError
from src.utils.validators import approximate_duration


class TTSService:
    def __init__(self, voice: str = "en-US-AriaNeural", rate: str = "+0%", pitch: str = "+0Hz") -> None:
        self.voice = voice
        self.rate = rate
        self.pitch = pitch

    async def _save_async(self, text: str, output: Path) -> None:
        import edge_tts

        communicate = edge_tts.Communicate(text, self.voice, rate=self.rate, pitch=self.pitch)
        await communicate.save(str(output))

    def generate(self, text: str, output: Path) -> Path:
        if not text.strip():
            raise ProviderError("Cannot generate narration from empty text")
        output.parent.mkdir(parents=True, exist_ok=True)
        try:
            asyncio.run(self._save_async(text, output))
        except Exception as exc:
            raise ProviderError(f"Edge TTS failed: {exc}") from exc
        if not output.exists() or output.stat().st_size == 0:
            raise ProviderError("Edge TTS produced an empty narration file")
        return output

    @staticmethod
    async def _voices_async() -> list[dict]:
        import edge_tts

        return await edge_tts.list_voices()

    def list_voices(self) -> list[dict]:
        try:
            return asyncio.run(self._voices_async())
        except Exception as exc:
            raise ProviderError(f"Unable to list Edge TTS voices: {exc}") from exc

    def estimated_duration(self, text: str) -> float:
        return approximate_duration(text)


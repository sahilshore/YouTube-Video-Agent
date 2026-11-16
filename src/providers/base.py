"""Provider contract and common retry/error handling."""

from __future__ import annotations

from abc import ABC, abstractmethod

from src.core.exceptions import ConfigurationError, ProviderError
from src.models.schemas import ScriptRequest, VideoScript, YouTubeMetadata


class LLMProvider(ABC):
    name: str
    model: str

    @abstractmethod
    def generate_text(self, prompt: str, *, temperature: float = 0.7) -> str:
        raise NotImplementedError

    @abstractmethod
    def test_connection(self) -> tuple[bool, str]:
        raise NotImplementedError

    def generate_script(self, request: ScriptRequest) -> VideoScript:
        from src.services.script_service import build_script_prompt, parse_script_response

        raw = self.generate_text(build_script_prompt(request), temperature=0.75)
        return parse_script_response(raw)

    def generate_video_title(self, topic: str) -> str:
        response = self.generate_text(f"Create one compelling YouTube title for: {topic}. Return only the title.", temperature=0.8)
        return response.strip().strip('"')

    def generate_scene_plan(self, request: ScriptRequest) -> VideoScript:
        return self.generate_script(request)

    def generate_metadata(self, script: VideoScript) -> YouTubeMetadata:
        from src.services.metadata_service import build_metadata_prompt, parse_metadata_response

        return parse_metadata_response(self.generate_text(build_metadata_prompt(script), temperature=0.6))

    @staticmethod
    def require_key(key: str, provider: str) -> None:
        if not key:
            raise ConfigurationError(f"{provider} API key is not configured. Add it in .env or Settings.")


def provider_error(provider: str, exc: Exception) -> ProviderError:
    message = str(exc).lower()
    if "401" in message or "403" in message or "authentication" in message or "api key" in message:
        return ProviderError(f"{provider} authentication failed. Check the configured API key.")
    if "429" in message or "rate limit" in message:
        return ProviderError(f"{provider} rate limit reached. Try again later or use the configured fallback.")
    return ProviderError(f"{provider} request failed: {exc}")


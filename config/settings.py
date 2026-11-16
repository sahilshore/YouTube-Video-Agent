"""Environment-backed application settings with safe defaults."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv


def _bool(name: str, default: bool) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


@dataclass(frozen=True)
class Settings:
    app_name: str = "YOUTUBE VIDEO AGENT"
    free_only_mode: bool = True
    default_llm_provider: str = "ollama"
    default_llm_model: str = "llama3.2"
    gemini_api_key: str = ""
    gemini_model: str = "gemini-2.0-flash"
    groq_api_key: str = ""
    groq_base_url: str = "https://api.groq.com/openai/v1"
    groq_model: str = "llama-3.3-70b-versatile"
    openrouter_api_key: str = ""
    openrouter_base_url: str = "https://openrouter.ai/api/v1"
    openrouter_model: str = "openrouter/free"
    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "llama3.2"
    pixabay_api_key: str = ""
    pexels_api_key: str = ""
    tts_voice: str = "en-US-AriaNeural"
    ffmpeg_path: str = "ffmpeg"
    ffprobe_path: str = "ffprobe"
    storage_dir: Path = Path("storage")
    database_path: Path = Path("storage/youtube_agent.db")

    @classmethod
    def from_env(cls, env_file: str | Path | None = ".env") -> "Settings":
        if env_file:
            load_dotenv(env_file, override=False)
        storage = Path(os.getenv("STORAGE_DIR", "storage"))
        database = Path(os.getenv("DATABASE_PATH", str(storage / "youtube_agent.db")))
        return cls(
            app_name=os.getenv("APP_NAME", cls.app_name),
            free_only_mode=_bool("FREE_ONLY_MODE", cls.free_only_mode),
            default_llm_provider=os.getenv("DEFAULT_LLM_PROVIDER", cls.default_llm_provider),
            default_llm_model=os.getenv("DEFAULT_LLM_MODEL", cls.default_llm_model),
            gemini_api_key=os.getenv("GEMINI_API_KEY", ""),
            gemini_model=os.getenv("GEMINI_MODEL", cls.gemini_model),
            groq_api_key=os.getenv("GROQ_API_KEY", ""),
            groq_base_url=os.getenv("GROQ_BASE_URL", cls.groq_base_url),
            groq_model=os.getenv("GROQ_MODEL", cls.groq_model),
            openrouter_api_key=os.getenv("OPENROUTER_API_KEY", ""),
            openrouter_base_url=os.getenv("OPENROUTER_BASE_URL", cls.openrouter_base_url),
            openrouter_model=os.getenv("OPENROUTER_MODEL", cls.openrouter_model),
            ollama_base_url=os.getenv("OLLAMA_BASE_URL", cls.ollama_base_url),
            ollama_model=os.getenv("OLLAMA_MODEL", os.getenv("DEFAULT_LLM_MODEL", cls.ollama_model)),
            pixabay_api_key=os.getenv("PIXABAY_API_KEY", ""),
            pexels_api_key=os.getenv("PEXELS_API_KEY", ""),
            tts_voice=os.getenv("TTS_VOICE", cls.tts_voice),
            ffmpeg_path=os.getenv("FFMPEG_PATH", cls.ffmpeg_path),
            ffprobe_path=os.getenv("FFPROBE_PATH", cls.ffprobe_path),
            storage_dir=storage,
            database_path=database,
        )

    def ensure_directories(self) -> None:
        (self.storage_dir / "projects").mkdir(parents=True, exist_ok=True)

    def masked(self, value: str) -> str:
        return "********" if value else ""


settings = Settings.from_env()


# YOUTUBE VIDEO AGENT

YOUTUBE VIDEO AGENT is a modular Windows-friendly Streamlit application that turns a topic into a structured YouTube script, scene plan, narration, subtitles, media-backed composition, thumbnail, and upload-ready metadata. It supports Shorts (1080x1920) and long videos (1920x1080).

The design is free-first: Gemini, Groq, OpenRouter, and local Ollama models share one interface; Pixabay is the primary stock-media provider with optional Pexels fallback; Edge TTS supplies narration; Pillow creates thumbnails; and FFmpeg performs final rendering. No provider is silently upgraded to paid usage, and API secrets are never stored in SQLite.

## Features

- Structured Pydantic script and scene plans with one correction retry for malformed provider JSON.
- Gemini, Groq, OpenRouter, and Ollama providers with selection, connection status, retry, and fallback routing.
- Scene-specific Pixabay/Pexels searches, bounded downloads, duplicate-safe filenames, caching, and credits.
- Edge TTS narration, sentence-level SRT/ASS subtitles, optional background music mixing, fades, and volume control.
- CPU-friendly FFmpeg scene composition with crop-to-fill, 30 FPS H.264/AAC output, FFprobe validation, and 1280x720 thumbnails.
- Per-project storage and SQLite generation history.
- Streamlit Dashboard, Create Video, Video Library, Settings, and System Diagnostics pages.

## Architecture

`app.py` delegates to `src/ui/app.py`. The UI calls `VideoPipeline`, which coordinates `script_service`, `media`, `audio`, `video`, `metadata_service`, and `storage_service`. Provider adapters implement `LLMProvider` and are selected by `LLMRouter`. Each project is isolated below `storage/projects/<project_id>/`.

## Installation on Windows

1. Install Python 3.11 or newer.
2. Install FFmpeg and FFprobe, then verify in PowerShell:

```powershell
ffmpeg -version
ffprobe -version
```

3. From this repository directory:

```powershell
Set-ExecutionPolicy -Scope Process Bypass
.\setup.ps1
```

The setup script creates `.venv`, installs `requirements.txt`, creates resource/storage directories, and copies `.env.example` to `.env` only when `.env` does not already exist. It never overwrites an existing `.env`.

## Provider configuration

Edit `.env` and configure one or more providers:

- `GEMINI_API_KEY`: create a key in Google AI Studio; set `GEMINI_MODEL` to a model available to that account.
- `GROQ_API_KEY`: create a developer key in the Groq console; configure `GROQ_MODEL` as needed.
- `OPENROUTER_API_KEY`: create an OpenRouter key; `OPENROUTER_MODEL=openrouter/free` is the safe default. With `FREE_ONLY_MODE=true`, paid model IDs are rejected.
- Ollama: install Ollama, run `ollama pull llama3.2`, and set `OLLAMA_BASE_URL`/`OLLAMA_MODEL`. Ollama requires no cloud key.
- `PIXABAY_API_KEY`: optional stock video search key. `PEXELS_API_KEY` is an optional fallback.

Set `DEFAULT_LLM_PROVIDER` and the matching model variables. The UI also allows provider selection per generation. External API limits and free-tier availability are controlled by each provider and can change; the application does not enable billing.

## Run

```powershell
.\run.ps1
```

Alternatively use `run.bat`. Streamlit opens at `http://localhost:8501`. Add an LLM key or run Ollama before generating a script. Add Pixabay/Pexels keys for stock footage; if no footage is available, the pipeline uses a generated fallback scene card rather than crashing. Leave music disabled when no local track is configured.

## Development and tests

```powershell
.\.venv\Scripts\python.exe -m pytest -q
```

The tests mock external providers and cover schema validation, provider fallback, media parsing/routing/download validation, subtitle generation, thumbnail generation, FFmpeg command construction, and SQLite storage. A live provider is not claimed to work unless the user supplies credentials and tests it from Diagnostics.

## Project layout

```text
app.py
config/settings.py
src/core/                 exceptions, logging, constants
src/models/               Pydantic domain schemas
src/providers/            Gemini, Groq, OpenRouter, Ollama, router
src/services/             pipeline, scripts, metadata, storage, history
src/services/media/       Pixabay, Pexels, router, downloader
src/services/audio/       Edge TTS, audio mixing, SRT/ASS
src/services/video/       FFmpeg renderer, composition, thumbnails
src/ui/                   Streamlit pages
tests/                    provider-free unit tests
storage/projects/         generated projects, ignored by Git
```

## Generated project files

Each project contains `script/script.json`, `script/script.md`, downloaded assets, `audio/narration.mp3`, `subtitles/subtitles.srt`, `subtitles/subtitles.ass`, `output/final_video.mp4`, `output/thumbnail.png`, `output/youtube_metadata.json`, `credits.txt`, logs, and `project.json`. Generated media, databases, `.env`, and temporary files are excluded by `.gitignore`.

## Licensing and attribution

Use only footage and music that you are licensed to use. Pixabay/Pexels response metadata and source links are recorded in `credits.txt`; review the provider license and attribution rules before publishing. This project does not scrape YouTube or download copyrighted videos from other platforms. Automatic YouTube publishing is intentionally not included; metadata is prepared for manual upload.

## Git workflow

The canonical remote is `https://github.com/sahilshore/YouTube-Video-Agent.git`. Development is kept in incremental conventional commits. To work from a clone:

```powershell
git clone https://github.com/sahilshore/YouTube-Video-Agent.git
cd YouTube-Video-Agent
git pull origin main
```

Never commit `.env`, credentials, generated media, local databases, or `.venv`. Use a feature branch for contributions and run the test suite before opening a pull request.

## Troubleshooting

- `Python 3.11+ is required`: install a supported Python and rerun setup.
- `FFmpeg was not found`: install FFmpeg or set absolute `FFMPEG_PATH` and `FFPROBE_PATH` values in `.env`.
- Provider authentication or model errors: check the matching key/model variables and the provider's current free-tier model list.
- Ollama connection errors: start Ollama and verify `ollama list` contains the configured model.
- No media results: add a Pixabay/Pexels key; the pipeline keeps going with fallback scene cards.
- Edge TTS errors: check network access and retry; narration failures are surfaced and never replaced with an empty audio file.


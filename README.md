# YOUTUBE VIDEO AGENT

YOUTUBE VIDEO AGENT is a Windows-friendly Streamlit application that turns a topic into a structured YouTube script, scene plan, narration, subtitles, media-backed composition, thumbnail, and upload-ready metadata.

The application is designed around free-first providers. Gemini, Groq, OpenRouter, and local Ollama models share one interface; Pixabay is the primary stock-media provider; Edge TTS supplies narration; and FFmpeg performs final rendering. External APIs remain optional until the corresponding feature is used.

## Current milestone

This repository is being developed in small, reviewable Git milestones. The architecture keeps provider integrations, media retrieval, audio, rendering, storage, and Streamlit UI separate so each layer can be tested without live credentials.

## Windows quick start

```powershell
Set-ExecutionPolicy -Scope Process Bypass
.\setup.ps1
.\run.ps1
```

Copy `.env.example` to `.env` and add only the provider keys you intend to use. `.env` is ignored by Git. Install FFmpeg and ensure both `ffmpeg` and `ffprobe` are available on PATH, or set their full paths in `.env`.

## Development

```powershell
py -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m pytest
```

Git milestones are pushed to `https://github.com/sahilshore/YouTube-Video-Agent` when authentication and network access are available. Do not commit API keys, generated media, local databases, or virtual environments.


"""Streamlit UI for YOUTUBE VIDEO AGENT."""

from __future__ import annotations

import shutil
from pathlib import Path

import streamlit as st

from config.settings import Settings
from src.core.constants import LLM_PROVIDERS
from src.models.schemas import ScriptRequest, VideoType
from src.providers.llm_router import LLMRouter
from src.services.history_service import HistoryService
from src.services.video_pipeline import VideoPipeline


def _settings() -> Settings:
    return Settings.from_env()


def _css() -> None:
    st.markdown("""<style>
    .block-container { max-width: 1200px; padding-top: 2rem; }
    .hero { padding: 1.5rem; border-radius: 18px; background: linear-gradient(135deg,#111827,#312e81); color: white; margin-bottom: 1.5rem; }
    div[data-testid="stMetric"] { background: #111827; padding: 1rem; border-radius: 14px; }
    </style>""", unsafe_allow_html=True)


def dashboard(settings: Settings) -> None:
    st.markdown('<div class="hero"><h1>YOUTUBE VIDEO AGENT</h1><p>Turn an idea into a production-ready YouTube project.</p></div>', unsafe_allow_html=True)
    records = HistoryService(settings.database_path).list_projects()
    cols = st.columns(3)
    cols[0].metric("Projects", len(records))
    cols[1].metric("Completed", sum(record.status == "complete" for record in records))
    usage = shutil.disk_usage(settings.storage_dir.resolve() if settings.storage_dir.exists() else Path.cwd())
    cols[2].metric("Free storage", f"{usage.free / 1024**3:.1f} GB")
    st.subheader("Recent projects")
    if records:
        st.dataframe([record.model_dump() for record in records[:10]], use_container_width=True, hide_index=True)
    else:
        st.info("No projects yet. Open Create Video to start.")


def create_video(settings: Settings) -> None:
    st.title("Create Video")
    with st.form("create_video"):
        topic = st.text_area("Video topic", placeholder="How artificial intelligence is changing the world")
        left, right = st.columns(2)
        video_type = left.selectbox("Video type", [item.value for item in VideoType])
        duration = right.slider("Target duration (seconds)", 15, 600, 60)
        language = left.selectbox("Language", ["English", "Hindi", "Hinglish"])
        category = right.selectbox("Category", ["Educational", "Documentary", "Technology", "Storytelling", "Motivational", "Informational", "Science", "History"])
        style = left.selectbox("Writing style", ["Educational", "Documentary", "Storytelling", "Informational", "Entertainment"])
        audience = right.text_input("Target audience", "General audience")
        provider = st.selectbox("LLM provider", list(LLM_PROVIDERS), index=3)
        submitted = st.form_submit_button("Generate Video", type="primary")
    if submitted:
        if len(topic.strip()) < 3:
            st.error("Enter a topic with at least 3 characters.")
            return
        request = ScriptRequest(topic=topic, video_type=VideoType(video_type), target_duration=duration, language=language, category=category, style=style, audience=audience)
        progress = st.progress(0)
        status = st.empty()

        def update(stage: str, message: str, value: float) -> None:
            progress.progress(value, text=f"{stage}: {message}")
            status.info(message)

        try:
            paths = VideoPipeline(settings).run(request, provider_name=provider, callback=update)
            status.success(f"Complete: {paths.project_id}")
            st.video(str(paths.output / "final_video.mp4"))
            with (paths.output / "final_video.mp4").open("rb") as handle:
                st.download_button("Download MP4", handle, file_name="final_video.mp4", mime="video/mp4")
        except Exception as exc:
            st.error(str(exc))


def library(settings: Settings) -> None:
    st.title("Video Library")
    for record in HistoryService(settings.database_path).list_projects():
        with st.container(border=True):
            st.write(f"**{record.topic}** — `{record.status}` — {record.created_at}")
            if record.output_path and Path(record.output_path).exists():
                st.video(record.output_path)
                with Path(record.output_path).open("rb") as handle:
                    st.download_button("Download", handle, file_name=f"{record.project_id}.mp4", key=record.project_id)


def settings_page(settings: Settings) -> None:
    st.title("Settings")
    st.caption("Secrets are read from .env and are never saved to SQLite or displayed in logs.")
    for label, configured in (("Gemini API key", settings.gemini_api_key), ("Groq API key", settings.groq_api_key), ("OpenRouter API key", settings.openrouter_api_key), ("Pixabay API key", settings.pixabay_api_key), ("Pexels API key", settings.pexels_api_key)):
        st.write(f"{label}: {'configured' if configured else 'not configured'}")
    st.code("Copy .env.example to .env, add keys, then restart Streamlit.")


def diagnostics(settings: Settings) -> None:
    st.title("System Diagnostics")
    st.write(f"Python: {__import__('sys').version.split()[0]}")
    st.write(f"FFmpeg: {'available' if shutil.which(settings.ffmpeg_path) else 'not found'}")
    st.write(f"FFprobe: {'available' if shutil.which(settings.ffprobe_path) else 'not found'}")
    st.write(f"Storage directory: {'ready' if settings.storage_dir.exists() else 'will be created'}")
    if st.button("Test configured providers"):
        for name, (ok, message) in LLMRouter(settings).connection_status().items():
            (st.success if ok else st.warning)(f"{name}: {message}")


def main() -> None:
    st.set_page_config(page_title="YOUTUBE VIDEO AGENT", page_icon="🎬", layout="wide")
    _css()
    settings = _settings()
    page = st.sidebar.radio("Navigate", ["Dashboard", "Create Video", "Video Library", "Settings", "System Diagnostics"])
    if page == "Dashboard":
        dashboard(settings)
    elif page == "Create Video":
        create_video(settings)
    elif page == "Video Library":
        library(settings)
    elif page == "Settings":
        settings_page(settings)
    else:
        diagnostics(settings)


"""End-to-end orchestration for one generated video project."""

from __future__ import annotations

import subprocess
from collections.abc import Callable
from pathlib import Path

from config.settings import Settings
from src.core.constants import LONG_VIDEO_SIZE, SHORTS_SIZE
from src.core.exceptions import RenderError
from src.models.schemas import ScriptRequest, VideoScript, VideoType
from src.providers.llm_router import LLMRouter
from src.services.audio.audio_processor import AudioProcessor
from src.services.audio.subtitle_service import sentence_cues, write_ass, write_srt
from src.services.audio.tts_service import TTSService
from src.services.history_service import HistoryService
from src.services.media.media_downloader import MediaDownloader
from src.services.media.media_router import MediaRouter
from src.services.metadata_service import generate_metadata, metadata_to_json
from src.services.script_service import generate_script, script_to_json, script_to_markdown
from src.services.storage_service import ProjectPaths, ProjectStorage
from src.services.video.thumbnail_generator import generate_thumbnail
from src.services.video.video_renderer import VideoRenderer


ProgressCallback = Callable[[str, str, float], None]


class VideoPipeline:
    def __init__(self, settings: Settings | None = None, router: LLMRouter | None = None) -> None:
        self.settings = settings or Settings.from_env()
        self.router = router or LLMRouter(self.settings)
        self.storage = ProjectStorage(self.settings)
        self.history = HistoryService(self.settings.database_path)

    @staticmethod
    def _notify(callback: ProgressCallback | None, stage: str, message: str, progress: float) -> None:
        if callback:
            callback(stage, message, progress)

    def _placeholder(self, output: Path, width: int, height: int, duration: float) -> Path:
        command = [self.settings.ffmpeg_path, "-y", "-f", "lavfi", "-i", f"color=c=0x111827:s={width}x{height}:d={max(1, duration)}", "-r", "30", "-pix_fmt", "yuv420p", "-c:v", "libx264", str(output)]
        result = subprocess.run(command, capture_output=True, text=True, check=False)
        if result.returncode != 0:
            raise RenderError(f"Could not create fallback scene: {result.stderr[-1000:]}")
        return output

    def run(self, request: ScriptRequest, provider_name: str | None = None, voice: str | None = None, music: Path | None = None, callback: ProgressCallback | None = None) -> ProjectPaths:
        paths = self.storage.create(request.topic)
        self.history.upsert(paths.project_id, request.topic, "running")
        try:
            self._notify(callback, "script", "Generating structured script", 0.08)
            script = generate_script(self.router.get(provider_name), request)
            self.storage.write_text(paths.script / "script.json", script_to_json(script))
            self.storage.write_text(paths.script / "script.md", script_to_markdown(script))

            width, height = SHORTS_SIZE if request.video_type == VideoType.SHORTS else LONG_VIDEO_SIZE
            self._notify(callback, "media", "Finding scene footage", 0.22)
            media_router = MediaRouter()
            try:
                from src.services.media.pexels_service import PexelsService
                from src.services.media.pixabay_service import PixabayService

                media_router = MediaRouter(PixabayService(self.settings.pixabay_api_key) if self.settings.pixabay_api_key else None, PexelsService(self.settings.pexels_api_key) if self.settings.pexels_api_key else None)
            except Exception:
                pass
            downloader = MediaDownloader()
            clips: list[Path] = []
            selected_assets = []
            durations = [scene.estimated_duration for scene in script.scenes]
            for index, scene in enumerate(script.scenes, 1):
                asset = media_router.search_scene(scene.visual_search_query, orientation="portrait" if request.video_type == VideoType.SHORTS else "landscape")
                if asset:
                    selected_assets.append(asset)
                    clips.append(downloader.download(asset, paths.videos))
                else:
                    clips.append(self._placeholder(paths.videos / f"fallback_scene_{index}.mp4", width, height, scene.estimated_duration))
            self.storage.write_text(paths.root / "credits.txt", MediaRouter.credits(selected_assets))

            self._notify(callback, "narration", "Generating narration", 0.42)
            narration = TTSService(voice or self.settings.tts_voice).generate(script.narration_text, paths.audio / "narration.mp3")
            total_duration = sum(durations)
            self._notify(callback, "subtitles", "Creating subtitles", 0.52)
            cues = sentence_cues(script.narration_text, total_duration)
            subtitle_srt = write_srt(cues, paths.subtitles / "subtitles.srt")
            write_ass(cues, paths.subtitles / "subtitles.ass")
            self._notify(callback, "audio", "Processing audio mix", 0.62)
            mixed_audio = AudioProcessor(self.settings).mix(narration, music, paths.audio / "mixed_audio.m4a", total_duration)
            self._notify(callback, "render", "Rendering final video", 0.76)
            final_video = VideoRenderer(self.settings).render(clips, paths.output / "final_video.mp4", width, height, durations, mixed_audio, subtitle_srt)
            self._notify(callback, "thumbnail", "Generating thumbnail and metadata", 0.9)
            thumbnail = generate_thumbnail(script.video_title, paths.output / "thumbnail.png")
            metadata = generate_metadata(self.router.get(provider_name), script)
            self.storage.write_text(paths.output / "youtube_metadata.json", metadata_to_json(metadata))
            self.history.upsert(paths.project_id, request.topic, "complete", str(final_video), str(thumbnail))
            self._notify(callback, "complete", "Video project is ready", 1.0)
            return paths
        except Exception:
            self.history.upsert(paths.project_id, request.topic, "failed")
            raise


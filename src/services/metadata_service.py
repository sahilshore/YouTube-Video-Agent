"""YouTube metadata generation and safe fallback formatting."""

from __future__ import annotations

import json

from src.models.schemas import VideoScript, YouTubeMetadata
from src.providers.base import LLMProvider
from src.utils.validators import parse_model_json


def build_metadata_prompt(script: VideoScript) -> str:
    return f"""Create YouTube upload metadata for this video script. Return only valid JSON with title, description, tags (array), hashtags (array), chapters (array of objects with time and title), and pinned_comment. Keep title under 100 characters.\n{script.video_title}\n{script.narration_text[:12000]}"""


def parse_metadata_response(raw: str) -> YouTubeMetadata:
    return parse_model_json(raw, YouTubeMetadata)


def generate_metadata(provider: LLMProvider, script: VideoScript) -> YouTubeMetadata:
    try:
        return parse_metadata_response(provider.generate_text(build_metadata_prompt(script), temperature=0.5))
    except Exception:
        return YouTubeMetadata(
            title=script.video_title[:100],
            description=f"{script.introduction}\n\n{script.conclusion}\n\nSubscribe for more.",
            tags=list(dict.fromkeys([*scene.keywords for scene in script.scenes]))[:30],
            hashtags=["#YouTube", "#Education"],
            pinned_comment="What did you think? Share your perspective below!",
        )


def metadata_to_json(metadata: YouTubeMetadata) -> str:
    return json.dumps(metadata.model_dump(mode="json"), indent=2, ensure_ascii=False)


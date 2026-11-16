"""Pydantic schemas for scripts, scenes, metadata, and generation requests."""

from __future__ import annotations

from enum import Enum
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, field_validator


class VideoType(str, Enum):
    SHORTS = "Shorts"
    LONG = "Long Video"


class Scene(BaseModel):
    scene_number: int = Field(ge=1)
    scene_title: str = Field(min_length=1, max_length=120)
    narration: str = Field(min_length=1)
    visual_description: str = Field(min_length=1)
    visual_search_query: str = Field(min_length=1, max_length=200)
    on_screen_text: str = Field(default="", max_length=200)
    keywords: list[str] = Field(default_factory=list, max_length=20)
    estimated_duration: float = Field(gt=0, le=300)


class VideoScript(BaseModel):
    model_config = ConfigDict(extra="ignore")

    video_title: str = Field(min_length=1, max_length=120)
    hook: str = Field(min_length=1)
    introduction: str = Field(default="")
    scenes: list[Scene] = Field(min_length=1, max_length=100)
    conclusion: str = Field(default="")
    call_to_action: str = Field(default="Subscribe for more")

    @field_validator("scenes")
    @classmethod
    def sequential_scenes(cls, scenes: list[Scene]) -> list[Scene]:
        for index, scene in enumerate(scenes, start=1):
            scene.scene_number = index
        return scenes

    @property
    def estimated_duration(self) -> float:
        return sum(scene.estimated_duration for scene in self.scenes)

    @property
    def narration_text(self) -> str:
        parts = [self.hook, self.introduction]
        parts.extend(scene.narration for scene in self.scenes)
        parts.extend([self.conclusion, self.call_to_action])
        return "\n\n".join(part for part in parts if part)


class ScriptRequest(BaseModel):
    topic: str = Field(min_length=3, max_length=500)
    video_type: VideoType = VideoType.LONG
    target_duration: int = Field(default=60, ge=15, le=3600)
    language: str = "English"
    category: str = "Informational"
    style: str = "Educational"
    audience: str = "General audience"
    tone: str = "Clear and engaging"


class YouTubeMetadata(BaseModel):
    title: str = Field(min_length=1, max_length=100)
    description: str = ""
    tags: list[str] = Field(default_factory=list, max_length=30)
    hashtags: list[str] = Field(default_factory=list, max_length=15)
    chapters: list[dict[str, Any]] = Field(default_factory=list)
    pinned_comment: str = ""


class ProjectRecord(BaseModel):
    project_id: str
    topic: str
    status: str
    created_at: str
    output_path: str | None = None
    thumbnail_path: str | None = None


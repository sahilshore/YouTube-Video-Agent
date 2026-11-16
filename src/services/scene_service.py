"""Scene planning helpers kept independent from provider code."""

from __future__ import annotations

from src.models.schemas import Scene, VideoScript


def plan_scenes(script: VideoScript) -> list[Scene]:
    return sorted(script.scenes, key=lambda scene: scene.scene_number)


def scene_search_queries(script: VideoScript) -> list[str]:
    return [scene.visual_search_query for scene in plan_scenes(script)]


"""Prompting and validation for structured AI scripts."""

from __future__ import annotations

import json

from src.core.exceptions import ValidationError
from src.models.schemas import ScriptRequest, VideoScript
from src.providers.base import LLMProvider
from src.utils.validators import approximate_duration, parse_model_json


def build_script_prompt(request: ScriptRequest) -> str:
    return f"""You are a professional YouTube script writer. Create a {request.target_duration}-second {request.video_type.value} about {request.topic!r}.
Language: {request.language}. Category: {request.category}. Style: {request.style}. Audience: {request.audience}. Tone: {request.tone}.
Return ONLY valid JSON matching this exact shape, with no Markdown fences:
{{"video_title":"...","hook":"...","introduction":"...","scenes":[{{"scene_number":1,"scene_title":"...","narration":"...","visual_description":"...","visual_search_query":"...","on_screen_text":"...","keywords":["..."],"estimated_duration":10}}],"conclusion":"...","call_to_action":"..."}}
Use 3-12 meaningful scenes. Keep scene narration natural for text-to-speech, make visual queries specific to each scene, and make total scene durations close to the requested duration."""


def _align_durations(script: VideoScript, target_seconds: int) -> VideoScript:
    narration_durations = [approximate_duration(scene.narration) for scene in script.scenes]
    total = sum(narration_durations) or target_seconds
    for scene, duration in zip(script.scenes, narration_durations):
        scene.estimated_duration = max(1.0, round(duration / total * target_seconds, 1))
    return script


def parse_script_response(raw: str) -> VideoScript:
    return parse_model_json(raw, VideoScript)


def generate_script(provider: LLMProvider, request: ScriptRequest) -> VideoScript:
    prompt = build_script_prompt(request)
    raw = provider.generate_text(prompt, temperature=0.75)
    try:
        return _align_durations(parse_script_response(raw), request.target_duration)
    except ValidationError as first_error:
        correction = f"Fix this response into valid JSON for the requested script schema. Return JSON only.\nOriginal response:\n{raw[:12000]}"
        try:
            return _align_durations(parse_script_response(provider.generate_text(correction, temperature=0.1)), request.target_duration)
        except ValidationError as second_error:
            raise ValidationError(f"Script generation failed validation after one correction attempt: {second_error}") from first_error


def script_to_markdown(script: VideoScript) -> str:
    lines = [f"# {script.video_title}", "", f"## Hook\n{script.hook}", f"## Introduction\n{script.introduction}"]
    for scene in script.scenes:
        lines.extend([f"## Scene {scene.scene_number}: {scene.scene_title}", scene.narration, f"*Visual:* {scene.visual_description}", f"*Search:* {scene.visual_search_query}"])
    lines.extend([f"## Conclusion\n{script.conclusion}", f"## Call to action\n{script.call_to_action}"])
    return "\n\n".join(lines)


def script_to_json(script: VideoScript) -> str:
    return json.dumps(script.model_dump(mode="json"), indent=2, ensure_ascii=False)


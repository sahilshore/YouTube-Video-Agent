import json

import pytest

from src.core.exceptions import ValidationError
from src.models.schemas import ScriptRequest
from src.providers.base import LLMProvider
from src.services.script_service import generate_script, script_to_markdown


class ScriptProvider(LLMProvider):
    name = "fake"
    model = "fake"

    def __init__(self, responses: list[str]) -> None:
        self.responses = responses

    def generate_text(self, prompt: str, *, temperature: float = 0.7) -> str:
        return self.responses.pop(0)

    def test_connection(self) -> tuple[bool, str]:
        return True, "ok"


def valid_script() -> str:
    return json.dumps({"video_title": "AI Today", "hook": "Look closer.", "introduction": "Intro", "scenes": [{"scene_number": 1, "scene_title": "Start", "narration": "AI is changing work.", "visual_description": "A modern office", "visual_search_query": "modern office technology", "keywords": ["AI"], "estimated_duration": 10}], "conclusion": "The future is here.", "call_to_action": "Subscribe"})


def test_generate_script_aligns_duration_and_exports_markdown() -> None:
    script = generate_script(ScriptProvider([valid_script()]), ScriptRequest(topic="AI future", target_duration=30))
    assert script.scenes[0].estimated_duration == 30.0
    assert "# AI Today" in script_to_markdown(script)


def test_generate_script_retries_invalid_json() -> None:
    script = generate_script(ScriptProvider(["not json", valid_script()]), ScriptRequest(topic="AI future"))
    assert script.video_title == "AI Today"


def test_generate_script_raises_after_correction_failure() -> None:
    with pytest.raises(ValidationError):
        generate_script(ScriptProvider(["bad", "still bad"]), ScriptRequest(topic="AI future"))


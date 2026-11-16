"""Input and generated-response validation helpers."""

from __future__ import annotations

import json
from typing import TypeVar

from pydantic import BaseModel, ValidationError as PydanticValidationError

from src.core.exceptions import ValidationError

ModelT = TypeVar("ModelT", bound=BaseModel)


def parse_model_json(raw: str, model_type: type[ModelT]) -> ModelT:
    text = raw.strip()
    if text.startswith("```"):
        text = text.split("\n", 1)[1] if "\n" in text else text
        text = text.rsplit("```", 1)[0].strip()
    try:
        data = json.loads(text)
        return model_type.model_validate(data)
    except (json.JSONDecodeError, PydanticValidationError, TypeError) as exc:
        raise ValidationError(f"Provider returned invalid {model_type.__name__} JSON: {exc}") from exc


def approximate_duration(text: str, words_per_minute: int = 145) -> float:
    words = len(text.split())
    return max(0.1, words / max(1, words_per_minute) * 60)


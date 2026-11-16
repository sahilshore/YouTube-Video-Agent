"""SRT and ASS subtitle generation."""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class SubtitleCue:
    index: int
    start: float
    end: float
    text: str


def _timestamp(seconds: float, ass: bool = False) -> str:
    seconds = max(0.0, seconds)
    hours, remainder = divmod(seconds, 3600)
    minutes, remainder = divmod(remainder, 60)
    whole = int(remainder)
    millis = int(round((remainder - whole) * 1000))
    if ass:
        return f"{int(hours)}:{int(minutes):02d}:{whole:02d}.{millis // 10:02d}"
    return f"{int(hours):02d}:{int(minutes):02d}:{whole:02d},{millis:03d}"


def sentence_cues(text: str, total_duration: float) -> list[SubtitleCue]:
    sentences = [part.strip() for part in re.split(r"(?<=[.!?])\s+", text.strip()) if part.strip()]
    if not sentences:
        return []
    weights = [max(1, len(sentence.split())) for sentence in sentences]
    total_words = sum(weights)
    cues: list[SubtitleCue] = []
    cursor = 0.0
    for index, (sentence, weight) in enumerate(zip(sentences, weights), 1):
        end = total_duration if index == len(sentences) else cursor + total_duration * weight / total_words
        cues.append(SubtitleCue(index, cursor, end, sentence))
        cursor = end
    return cues


def write_srt(cues: list[SubtitleCue], output: Path) -> Path:
    output.parent.mkdir(parents=True, exist_ok=True)
    content = "\n\n".join(f"{cue.index}\n{_timestamp(cue.start)} --> {_timestamp(cue.end)}\n{cue.text}" for cue in cues) + ("\n" if cues else "")
    output.write_text(content, encoding="utf-8")
    return output


def write_ass(cues: list[SubtitleCue], output: Path, font_name: str = "Arial", font_size: int = 42) -> Path:
    output.parent.mkdir(parents=True, exist_ok=True)
    header = ("[Script Info]\nScriptType: v4.00+\nPlayResX: 1920\nPlayResY: 1080\n\n"
              "[V4+ Styles]\nFormat: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding\n"
              f"Style: Default,{font_name},{font_size},&H00FFFFFF,&H00FFFFFF,&H00000000,&H80000000,0,0,0,0,100,100,0,0,1,3,0,2,80,80,70,1\n\n"
              "[Events]\nFormat: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text\n")
    events = "\n".join(f"Dialogue: 0,{_timestamp(cue.start, True)},{_timestamp(cue.end, True)},Default,,0,0,0,,{cue.text}" for cue in cues)
    output.write_text(header + events + ("\n" if events else ""), encoding="utf-8")
    return output


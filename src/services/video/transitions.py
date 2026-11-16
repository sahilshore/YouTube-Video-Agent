"""Small FFmpeg transition filter helpers."""


def crossfade_filter(first: str, second: str, offset: float, duration: float = 0.35) -> str:
    return f"[{first}][{second}]xfade=transition=fade:duration={duration}:offset={offset}[v]"


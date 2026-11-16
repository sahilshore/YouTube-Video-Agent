"""Pillow thumbnail generation."""

from __future__ import annotations

import textwrap
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


def generate_thumbnail(title: str, output: Path, background: Path | None = None, size: tuple[int, int] = (1280, 720)) -> Path:
    if background and background.exists():
        image = Image.open(background).convert("RGB").resize(size)
    else:
        image = Image.new("RGB", size, (11, 18, 32))
        pixels = image.load()
        for y in range(size[1]):
            ratio = y / size[1]
            color = (int(12 + 20 * ratio), int(25 + 35 * ratio), int(54 + 70 * ratio))
            for x in range(size[0]):
                pixels[x, y] = color
    overlay = Image.new("RGBA", size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    draw.rectangle((0, 0, size[0], size[1]), fill=(0, 0, 0, 85))
    font = ImageFont.truetype("arial.ttf", 68) if Path("C:/Windows/Fonts/arial.ttf").exists() else ImageFont.load_default()
    lines = textwrap.wrap(title, width=25)[:4]
    y = size[1] // 2 - len(lines) * 40
    for line in lines:
        box = draw.textbbox((0, 0), line, font=font, stroke_width=3)
        x = (size[0] - (box[2] - box[0])) // 2
        draw.text((x, y), line, font=font, fill="white", stroke_width=3, stroke_fill="black")
        y += 82
    image = Image.alpha_composite(image.convert("RGBA"), overlay).convert("RGB")
    output.parent.mkdir(parents=True, exist_ok=True)
    image.save(output, format="PNG")
    return output


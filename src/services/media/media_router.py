"""Media provider fallback and in-process search cache."""

from __future__ import annotations

from src.core.exceptions import ConfigurationError, MediaError
from src.services.media.models import MediaAsset


class MediaRouter:
    def __init__(self, pixabay=None, pexels=None) -> None:
        self.providers = [provider for provider in (pixabay, pexels) if provider is not None]
        self.cache: dict[tuple[str, str], list[MediaAsset]] = {}

    def search(self, query: str, *, orientation: str = "all") -> list[MediaAsset]:
        key = (query.strip().lower(), orientation)
        if key in self.cache:
            return self.cache[key]
        errors: list[str] = []
        for provider in self.providers:
            try:
                results = provider.search(query, orientation=orientation)
                if results:
                    self.cache[key] = results
                    return results
            except Exception as exc:
                errors.append(str(exc))
        if errors:
            raise MediaError("No media provider returned results: " + " | ".join(errors))
        raise ConfigurationError("No media provider is configured")

    def search_scene(self, query: str, *, orientation: str = "all") -> MediaAsset | None:
        try:
            results = self.search(query, orientation=orientation)
            return results[0] if results else None
        except MediaError:
            return None

    @staticmethod
    def credits(assets: list[MediaAsset]) -> str:
        lines = ["Media credits", "", *[f"{asset.provider}: {asset.author or 'Unknown author'} — {asset.source_url}" for asset in assets if asset.source_url]]
        return "\n".join(lines) + "\n"


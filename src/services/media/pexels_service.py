"""Optional Pexels video API integration."""

from __future__ import annotations

import requests

from src.core.exceptions import ConfigurationError, ProviderError
from src.services.media.models import MediaAsset


class PexelsService:
    endpoint = "https://api.pexels.com/videos/search"

    def __init__(self, api_key: str, timeout: float = 20) -> None:
        if not api_key:
            raise ConfigurationError("Pexels API key is not configured")
        self.api_key = api_key
        self.timeout = timeout

    def search(self, query: str, *, orientation: str = "landscape", per_page: int = 10) -> list[MediaAsset]:
        try:
            response = requests.get(self.endpoint, headers={"Authorization": self.api_key}, params={"query": query, "orientation": orientation, "per_page": per_page}, timeout=self.timeout)
            response.raise_for_status()
            payload = response.json()
        except Exception as exc:
            raise ProviderError(f"Pexels search failed: {exc}") from exc
        assets: list[MediaAsset] = []
        for video in payload.get("videos", []):
            files = sorted(video.get("video_files", []), key=lambda item: item.get("width", 0) * item.get("height", 0), reverse=True)
            selected = next((item for item in files if item.get("file_type", "").lower() == "video/mp4" and item.get("link")), None)
            if not selected:
                continue
            assets.append(MediaAsset(str(video.get("id")), "pexels", query, selected["link"], video.get("url", ""), width=selected.get("width", 0), height=selected.get("height", 0), duration=video.get("duration", 0), author=video.get("user", {}).get("name", ""), metadata=video))
        return assets


"""Pixabay video API integration."""

from __future__ import annotations

import requests

from src.core.exceptions import ConfigurationError, ProviderError
from src.services.media.models import MediaAsset


class PixabayService:
    endpoint = "https://pixabay.com/api/videos/"

    def __init__(self, api_key: str, timeout: float = 20) -> None:
        if not api_key:
            raise ConfigurationError("Pixabay API key is not configured")
        self.api_key = api_key
        self.timeout = timeout

    def search(self, query: str, *, orientation: str = "all", per_page: int = 10) -> list[MediaAsset]:
        try:
            response = requests.get(self.endpoint, params={"key": self.api_key, "q": query, "orientation": orientation, "per_page": per_page}, timeout=self.timeout)
            response.raise_for_status()
            payload = response.json()
        except Exception as exc:
            raise ProviderError(f"Pixabay search failed: {exc}") from exc
        assets: list[MediaAsset] = []
        for hit in payload.get("hits", []):
            files = hit.get("videos", {})
            selected = next((files.get(name) for name in ("large", "medium", "small", "tiny") if files.get(name)), None)
            if not selected or not selected.get("url"):
                continue
            assets.append(MediaAsset(str(hit.get("id")), "pixabay", query, selected["url"], hit.get("pageURL", ""), width=selected.get("width", 0), height=selected.get("height", 0), duration=hit.get("duration", 0), author=hit.get("user", ""), metadata=hit))
        return assets


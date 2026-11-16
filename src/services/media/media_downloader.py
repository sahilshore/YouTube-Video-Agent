"""Bounded, validated media downloads."""

from __future__ import annotations

import hashlib
from pathlib import Path

import requests

from src.core.exceptions import MediaError
from src.services.media.models import MediaAsset
from src.utils.file_utils import safe_filename


class MediaDownloader:
    def __init__(self, timeout: float = 45, max_bytes: int = 250 * 1024 * 1024) -> None:
        self.timeout = timeout
        self.max_bytes = max_bytes

    def download(self, asset: MediaAsset, destination: Path) -> Path:
        destination.mkdir(parents=True, exist_ok=True)
        suffix = ".mp4" if asset.media_type == "video" else ".jpg"
        filename = safe_filename(f"{asset.provider}_{asset.asset_id}") + suffix
        output = destination / filename
        if output.exists() and output.stat().st_size > 0:
            return output
        temporary = output.with_suffix(output.suffix + ".part")
        try:
            with requests.get(asset.download_url, stream=True, timeout=self.timeout, headers={"User-Agent": "YouTubeVideoAgent/0.1"}) as response:
                response.raise_for_status()
                content_type = response.headers.get("content-type", "").lower()
                if content_type and not (content_type.startswith("video/") or content_type.startswith("image/") or "octet-stream" in content_type):
                    raise MediaError(f"Unexpected media content type: {content_type}")
                content_length = int(response.headers.get("content-length", 0) or 0)
                if content_length > self.max_bytes:
                    raise MediaError("Media file exceeds the configured download limit")
                total = 0
                with temporary.open("wb") as handle:
                    for chunk in response.iter_content(chunk_size=1024 * 256):
                        if not chunk:
                            continue
                        total += len(chunk)
                        if total > self.max_bytes:
                            raise MediaError("Media file exceeds the configured download limit")
                        handle.write(chunk)
            if total == 0:
                raise MediaError("Downloaded media is empty")
            temporary.replace(output)
            return output
        except MediaError:
            if temporary.exists():
                temporary.unlink()
            raise
        except Exception as exc:
            if temporary.exists():
                temporary.unlink()
            raise MediaError(f"Media download failed: {exc}") from exc

    @staticmethod
    def checksum(path: Path) -> str:
        digest = hashlib.sha256()
        with path.open("rb") as handle:
            for chunk in iter(lambda: handle.read(1024 * 1024), b""):
                digest.update(chunk)
        return digest.hexdigest()


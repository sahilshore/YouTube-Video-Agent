from pathlib import Path

import pytest

from src.services.media.media_downloader import MediaDownloader
from src.services.media.media_router import MediaRouter
from src.services.media.models import MediaAsset


class FakeProvider:
    def __init__(self, results=None, error=None):
        self.results = results or []
        self.error = error
        self.calls = 0

    def search(self, query, orientation="all"):
        self.calls += 1
        if self.error:
            raise self.error
        return self.results


def test_media_router_caches_and_falls_back() -> None:
    asset = MediaAsset("1", "fake", "space", "https://example.com/a.mp4", "https://example.com/source")
    first = FakeProvider(error=RuntimeError("down"))
    second = FakeProvider([asset])
    router = MediaRouter(first, second)
    assert router.search_scene("space").asset_id == "1"
    assert router.search_scene("space").asset_id == "1"
    assert second.calls == 1


def test_downloader_writes_stream_and_skips_existing(tmp_path: Path, monkeypatch) -> None:
    class Response:
        headers = {"content-type": "video/mp4", "content-length": "4"}

        def __enter__(self): return self
        def __exit__(self, *args): return None
        def raise_for_status(self): return None
        def iter_content(self, chunk_size): return [b"test"]

    monkeypatch.setattr("src.services.media.media_downloader.requests.get", lambda *args, **kwargs: Response())
    asset = MediaAsset("1", "fake", "space", "https://example.com/a.mp4", "https://example.com/source")
    downloader = MediaDownloader()
    output = downloader.download(asset, tmp_path)
    assert output.read_bytes() == b"test"
    assert downloader.download(asset, tmp_path) == output


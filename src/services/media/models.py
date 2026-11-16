"""Provider-neutral media records."""

from dataclasses import dataclass, field


@dataclass(frozen=True)
class MediaAsset:
    asset_id: str
    provider: str
    query: str
    download_url: str
    source_url: str
    media_type: str = "video"
    width: int = 0
    height: int = 0
    duration: float = 0
    author: str = ""
    metadata: dict = field(default_factory=dict)


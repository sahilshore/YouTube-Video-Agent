"""Redacting application logger."""

from __future__ import annotations

import logging
import re
from pathlib import Path


class SecretRedactor(logging.Filter):
    _pattern = re.compile(r"(?i)(api[_ -]?key|token|password)(\s*[=:]\s*)[^\s,;]+")

    def filter(self, record: logging.LogRecord) -> bool:
        record.msg = self._pattern.sub(r"\1\2[REDACTED]", str(record.msg))
        record.args = ()
        return True


def get_logger(name: str = "youtube_agent", log_file: str | Path | None = None) -> logging.Logger:
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    logger.propagate = False
    if not logger.handlers:
        handler = logging.StreamHandler()
        handler.addFilter(SecretRedactor())
        handler.setFormatter(logging.Formatter("%(asctime)s | %(levelname)s | %(message)s"))
        logger.addHandler(handler)
    if log_file and not any(getattr(h, "baseFilename", None) == str(Path(log_file).resolve()) for h in logger.handlers):
        path = Path(log_file)
        path.parent.mkdir(parents=True, exist_ok=True)
        handler = logging.FileHandler(path, encoding="utf-8")
        handler.addFilter(SecretRedactor())
        handler.setFormatter(logging.Formatter("%(asctime)s | %(levelname)s | %(message)s"))
        logger.addHandler(handler)
    return logger


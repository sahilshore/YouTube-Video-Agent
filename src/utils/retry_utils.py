"""Bounded exponential-backoff helpers."""

from __future__ import annotations

import time
from collections.abc import Callable
from typing import TypeVar

T = TypeVar("T")


def retry(operation: Callable[[], T], attempts: int = 3, base_delay: float = 0.5, retry_on: tuple[type[Exception], ...] = (Exception,)) -> T:
    last_error: Exception | None = None
    for attempt in range(attempts):
        try:
            return operation()
        except retry_on as exc:
            last_error = exc
            if attempt == attempts - 1:
                break
            time.sleep(base_delay * (2**attempt))
    assert last_error is not None
    raise last_error


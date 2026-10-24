from __future__ import annotations

import threading
from typing import Any


class FileLock:
    _lock = threading.RLock()

    def __enter__(self) -> "FileLock":
        type(self)._lock.acquire()
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        type(self)._lock.release()

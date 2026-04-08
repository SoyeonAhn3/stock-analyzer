"""메모리 캐시 모듈 — TTL 기반, 수동 무효화 지원."""

import time
from typing import Any, Optional


class Cache:
    """TTL 기반 인메모리 캐시.

    키: (함수명, 티커, 파라미터) 조합
    TTL: quick_look 5분, ai_result 1시간, sector 6시간
    """

    def __init__(self):
        self._store: dict[str, dict[str, Any]] = {}

    def _make_key(self, func_name: str, ticker: str, **kwargs) -> str:
        parts = [func_name, ticker] + [f"{k}={v}" for k, v in sorted(kwargs.items())]
        return "|".join(parts)

    def get(self, func_name: str, ticker: str, **kwargs) -> Optional[Any]:
        key = self._make_key(func_name, ticker, **kwargs)
        entry = self._store.get(key)
        if entry is None:
            return None
        if time.time() > entry["expires_at"]:
            del self._store[key]
            return None
        return entry["value"]

    def set(self, func_name: str, ticker: str, value: Any, ttl: int, **kwargs):
        key = self._make_key(func_name, ticker, **kwargs)
        self._store[key] = {
            "value": value,
            "expires_at": time.time() + ttl,
        }

    def invalidate(self, ticker: str):
        keys_to_delete = [k for k in self._store if f"|{ticker}|" in k or k.startswith(f"{ticker}|") or k.endswith(f"|{ticker}")]
        # More robust: check if ticker appears as second segment
        keys_to_delete = []
        for k in self._store:
            parts = k.split("|")
            if len(parts) >= 2 and parts[1] == ticker:
                keys_to_delete.append(k)
        for k in keys_to_delete:
            del self._store[k]

    def force_expire(self):
        now = time.time()
        for entry in self._store.values():
            entry["expires_at"] = now - 1

    def clear(self):
        self._store.clear()

    @property
    def size(self) -> int:
        return len(self._store)


# Global singleton
cache = Cache()

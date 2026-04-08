"""AI 일일 사용량 추적 모듈.

사이드바에 "오늘 AI 사용: 47/100회" 표시용.
80회 이상 시 경고, 100회 도달 시 AI 분석 비활성화.
"""

from datetime import date
from typing import Optional

from config.api_config import DAILY_LIMITS


class UsageTracker:
    """AI Agent 호출 횟수를 일 단위로 추적."""

    def __init__(self):
        self._date: Optional[date] = None
        self._count: int = 0
        self._limit: int = DAILY_LIMITS.get("ai_agent", 100)

    def _check_reset(self):
        today = date.today()
        if self._date != today:
            self._date = today
            self._count = 0

    def increment(self) -> int:
        self._check_reset()
        self._count += 1
        return self._count

    @property
    def count(self) -> int:
        self._check_reset()
        return self._count

    @property
    def limit(self) -> int:
        return self._limit

    @property
    def remaining(self) -> int:
        return max(0, self._limit - self.count)

    @property
    def is_warning(self) -> bool:
        return self.count >= self._limit * 0.8

    @property
    def is_exhausted(self) -> bool:
        return self.count >= self._limit

    def status_text(self) -> str:
        return f"오늘 AI 사용: {self.count}/{self._limit}회"

    def warning_text(self) -> Optional[str]:
        if self.is_exhausted:
            return "AI 분석 일일 한도에 도달했습니다. Quick Look(데이터 조회)은 계속 사용 가능합니다."
        if self.is_warning:
            return f"오늘 AI 분석 잔여 횟수가 적습니다 ({self.remaining}회 남음)"
        return None


# Global singleton
usage_tracker = UsageTracker()

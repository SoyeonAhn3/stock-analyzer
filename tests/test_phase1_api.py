"""Phase 1 테스트 — API 래퍼 + 통합 클라이언트 + 캐싱.

사내 네트워크에서 Yahoo Finance / Finnhub / TwelveData / FMP 차단됨.
→ Mock 기반 단위 테스트로 코드 로직 검증
→ FRED만 실제 API 테스트

실행: pytest tests/test_phase1_api.py -v
완료 기준: 전체 테스트 pass
"""

import sys
import os
import time
from unittest.mock import patch, MagicMock

import pytest

# 프로젝트 루트를 path에 추가
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from data.yfinance_client import YFinanceClient
from data.finnhub_client import FinnhubClient
from data.twelvedata_client import TwelveDataClient
from data.fmp_client import FMPClient
from data.fred_client import FREDClient
from data.api_client import APIClient
from data.cache import Cache
from utils.usage_tracker import UsageTracker


# ============================================================
# Mock 응답 데이터
# ============================================================

MOCK_YF_FAST_INFO = MagicMock(
    last_price=120.50,
    previous_close=118.30,
    open=119.00,
    day_high=121.00,
    day_low=117.50,
    last_volume=45000000,
    market_cap=2950000000000,
)

MOCK_FINNHUB_QUOTE = {
    "c": 120.50, "d": 2.20, "dp": 1.86,
    "h": 121.00, "l": 117.50, "o": 119.00, "pc": 118.30, "t": 1700000000,
}

MOCK_TWELVEDATA_RSI = {
    "values": [
        {"datetime": "2026-04-07", "rsi": "55.32"},
        {"datetime": "2026-04-04", "rsi": "52.10"},
    ]
}

MOCK_FMP_PROFILE = [{
    "symbol": "NVDA", "companyName": "NVIDIA Corp",
    "mktCap": 2950000000000, "pe": 65.2, "eps": 1.85,
    "sector": "Technology", "industry": "Semiconductors",
    "lastDiv": 0.04, "range": "40.00-140.00",
    "fullTimeEmployees": 29600, "country": "US",
}]

MOCK_FMP_SCREENER = [
    {"symbol": "NVDA", "companyName": "NVIDIA", "marketCap": 2950000000000,
     "sector": "Technology", "industry": "Semiconductors", "price": 120.5, "volume": 45000000},
    {"symbol": "AAPL", "companyName": "Apple", "marketCap": 3000000000000,
     "sector": "Technology", "industry": "Consumer Electronics", "price": 195.0, "volume": 55000000},
]


# ============================================================
# 1. 개별 API 래퍼 테스트 (Mock)
# ============================================================

class TestYFinanceClient:
    @patch("data.yfinance_client.yf")
    def test_get_quote(self, mock_yf):
        """TC-001: yfinance 시세 조회 — Mock."""
        mock_ticker = MagicMock()
        mock_ticker.fast_info = MOCK_YF_FAST_INFO
        mock_yf.Ticker.return_value = mock_ticker

        client = YFinanceClient()
        result = client.get_quote("NVDA")

        assert result is not None
        assert result["source"] == "yfinance"
        assert result["ticker"] == "NVDA"
        assert result["price"] == 120.50
        assert result["volume"] == 45000000
        assert client.call_count == 1

    @patch("data.yfinance_client.yf")
    def test_get_quote_failure_returns_none(self, mock_yf):
        """TC-008: yfinance 예외 시 None 반환."""
        mock_yf.Ticker.side_effect = Exception("Network error")

        client = YFinanceClient()
        result = client.get_quote("ZZZZZ999")

        assert result is None


class TestFinnhubClient:
    @patch("data.finnhub_client.requests.get")
    @patch("data.finnhub_client.FINNHUB_API_KEY", "test_key")
    def test_get_quote(self, mock_get):
        """TC-002: Finnhub 시세 조회 — Mock."""
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = MOCK_FINNHUB_QUOTE
        mock_resp.raise_for_status = MagicMock()
        mock_get.return_value = mock_resp

        client = FinnhubClient()
        result = client.get_quote("NVDA")

        assert result is not None
        assert result["source"] == "finnhub"
        assert result["price"] == 120.50
        assert result["change_pct"] == 1.86

    @patch("data.finnhub_client.FINNHUB_API_KEY", "")
    def test_no_api_key_returns_none(self):
        """TC-013: API 키 미설정 시 None 반환."""
        client = FinnhubClient()
        result = client.get_quote("NVDA")
        assert result is None


class TestTwelveDataClient:
    @patch("data.twelvedata_client.requests.get")
    @patch("data.twelvedata_client.TWELVEDATA_API_KEY", "test_key")
    def test_get_rsi(self, mock_get):
        """TC-003: Twelve Data RSI 조회 — Mock."""
        mock_resp = MagicMock()
        mock_resp.json.return_value = MOCK_TWELVEDATA_RSI
        mock_resp.raise_for_status = MagicMock()
        mock_get.return_value = mock_resp

        client = TwelveDataClient()
        result = client.get_rsi("NVDA")

        assert result is not None
        assert result["source"] == "twelvedata"
        assert result["indicator"] == "RSI"
        assert len(result["values"]) == 2
        assert 0 <= result["values"][0]["rsi"] <= 100


class TestFMPClient:
    @patch("data.fmp_client.requests.get")
    @patch("data.fmp_client.FMP_API_KEY", "test_key")
    def test_screen_stocks(self, mock_get):
        """TC-004: FMP 섹터 스크리닝 — Mock."""
        mock_resp = MagicMock()
        mock_resp.json.return_value = MOCK_FMP_SCREENER
        mock_resp.raise_for_status = MagicMock()
        mock_get.return_value = mock_resp

        client = FMPClient()
        result = client.screen_stocks(sector="Technology", limit=5)

        assert result is not None
        assert result["source"] == "fmp"
        assert len(result["stocks"]) == 2
        assert result["stocks"][0]["ticker"] == "NVDA"


# ============================================================
# 2. FRED — 실제 API 테스트 (사내 네트워크 허용)
# ============================================================

class TestFREDClient:
    def test_get_fed_rate(self):
        """TC-005: FRED 금리 데이터 — 실제 API."""
        client = FREDClient()
        result = client.get_fed_rate()
        if result is None:
            pytest.skip("FRED API key not set or API unavailable")
        assert result["source"] == "fred"
        assert result["indicator"] == "fed_rate"
        assert result["latest"]["value"] is not None

    def test_get_macro_summary(self):
        """TC-005b: FRED 매크로 요약 — 실제 API."""
        client = FREDClient()
        result = client.get_macro_summary()
        if result is None:
            pytest.skip("FRED API key not set or API unavailable")
        assert result["source"] == "fred"
        assert "fed_rate" in result


# ============================================================
# 3. 통합 클라이언트 테스트 (Mock)
# ============================================================

class TestAPIClientFallback:
    def test_fallback_to_second_source(self):
        """TC-012: 1순위 실패 → 2순위 폴백 성공."""
        client = APIClient()

        # Finnhub 강제 실패, yfinance Mock 성공
        client.finnhub.get_quote = lambda ticker: None
        client.yfinance.get_quote = lambda ticker: {
            "source": "yfinance", "ticker": ticker, "price": 120.50,
            "previous_close": 118.30, "open": 119.00,
            "day_high": 121.00, "day_low": 117.50,
            "volume": 45000000, "market_cap": 2950000000000,
        }
        # 캐시 클리어
        from data.cache import cache
        cache.clear()

        result = client.get_quote("AAPL")
        assert result is not None
        assert result["source"] == "yfinance"

    def test_all_sources_fail_returns_none(self):
        """TC-014: 모든 소스 실패 시 None 반환."""
        client = APIClient()
        client.finnhub.get_quote = lambda ticker: None
        client.yfinance.get_quote = lambda ticker: None
        from data.cache import cache
        cache.clear()

        result = client.get_quote("AAPL")
        assert result is None


# ============================================================
# 4. 캐시 테스트
# ============================================================

class TestCache:
    def test_cache_hit(self):
        """TC-007: 캐시 히트 — 동일 키 2회 조회 시 캐시 반환."""
        c = Cache()
        c.set("quote", "NVDA", {"price": 120.50}, ttl=300)

        result1 = c.get("quote", "NVDA")
        result2 = c.get("quote", "NVDA")

        assert result1 is not None
        assert result2 is not None
        assert result1["price"] == result2["price"] == 120.50

    def test_cache_expiry(self):
        """TC-010: 캐시 만료 후 None 반환."""
        c = Cache()
        c.set("test_func", "NVDA", {"price": 100}, ttl=1)

        assert c.get("test_func", "NVDA") is not None
        time.sleep(1.1)
        assert c.get("test_func", "NVDA") is None

    def test_cache_invalidate(self):
        """TC-011: 수동 무효화 후 None 반환."""
        c = Cache()
        c.set("quote", "NVDA", {"price": 100}, ttl=300)
        assert c.get("quote", "NVDA") is not None

        c.invalidate("NVDA")
        assert c.get("quote", "NVDA") is None

    def test_force_expire(self):
        """캐시 전체 강제 만료."""
        c = Cache()
        c.set("a", "NVDA", {"v": 1}, ttl=300)
        c.set("b", "AAPL", {"v": 2}, ttl=300)

        c.force_expire()
        assert c.get("a", "NVDA") is None
        assert c.get("b", "AAPL") is None

    def test_empty_ticker(self):
        """TC-009: 빈 문자열 티커도 크래시 없이 처리."""
        c = Cache()
        c.set("quote", "", {"price": 0}, ttl=300)
        assert c.get("quote", "") == {"price": 0}


# ============================================================
# 5. 사용량 추적 테스트
# ============================================================

class TestUsageTracker:
    def test_increment_and_count(self):
        """TC-015: 사용량 카운트 증가."""
        tracker = UsageTracker()
        tracker.increment()
        tracker.increment()
        tracker.increment()
        assert tracker.count == 3

    def test_daily_reset(self):
        """TC-015: 날짜 변경 시 카운트 리셋."""
        from datetime import date, timedelta
        tracker = UsageTracker()
        tracker.increment()
        tracker.increment()
        assert tracker.count == 2

        # 어제 날짜로 강제 변경
        tracker._date = date.today() - timedelta(days=1)
        assert tracker.count == 0  # _check_reset 트리거

    def test_warning_and_exhausted(self):
        """TC-016: 80회 경고, 100회 한도 도달."""
        tracker = UsageTracker()
        tracker._date = __import__("datetime").date.today()
        tracker._count = 79

        assert not tracker.is_warning
        tracker.increment()  # 80회
        assert tracker.is_warning
        assert not tracker.is_exhausted

        tracker._count = 99
        tracker.increment()  # 100회
        assert tracker.is_exhausted
        assert "일일 한도에 도달" in tracker.warning_text()

    def test_status_text(self):
        """사용량 상태 텍스트 포맷."""
        tracker = UsageTracker()
        tracker._date = __import__("datetime").date.today()
        tracker._count = 47
        assert tracker.status_text() == "오늘 AI 사용: 47/100회"

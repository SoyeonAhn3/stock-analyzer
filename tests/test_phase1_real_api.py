"""Phase 1 실제 API 테스트 — 실제 API 호출.

실행: pytest tests/test_phase1_real_api.py -v -s
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest

from data.yfinance_client import YFinanceClient
from data.finnhub_client import FinnhubClient
from data.twelvedata_client import TwelveDataClient
from data.fmp_client import FMPClient
from data.fred_client import FREDClient
from data.finviz_client import FinvizClient
from data.api_client import APIClient
from data.cache import cache

TICKER = "AAPL"


# ============================================================
# 1. yfinance — 실제 호출
# ============================================================

class TestYFinanceReal:
    def test_get_quote(self):
        """yfinance 시세 조회."""
        client = YFinanceClient()
        result = client.get_quote(TICKER)
        assert result is not None, "yfinance get_quote returned None"
        assert result["source"] == "yfinance"
        assert result["price"] > 0
        assert result["volume"] > 0
        print(f"  yfinance quote: ${result['price']}, vol={result['volume']}")

    def test_get_history(self):
        """yfinance 히스토리 조회."""
        client = YFinanceClient()
        result = client.get_history(TICKER, period="1mo")
        assert result is not None, "yfinance get_history returned None"
        assert len(result["data"]) > 10
        print(f"  yfinance history: {len(result['data'])} rows")

    def test_get_fundamentals(self):
        """yfinance 재무 지표 조회."""
        client = YFinanceClient()
        result = client.get_fundamentals(TICKER)
        assert result is not None, "yfinance get_fundamentals returned None"
        assert result["sector"] is not None
        assert result["pe_ratio"] is not None or result["market_cap"] is not None
        print(f"  yfinance fundamentals: sector={result['sector']}, PE={result['pe_ratio']}")

    def test_get_market_indices(self):
        """yfinance 시장 지수 조회."""
        client = YFinanceClient()
        result = client.get_market_indices()
        assert result is not None, "yfinance get_market_indices returned None"
        assert "SPY" in result["indices"]
        assert "VIX" in result["indices"]
        for name, data in result["indices"].items():
            print(f"  {name}: {data['price']:.2f} ({data['change_pct']:+.2f}%)")

    def test_invalid_ticker(self):
        """yfinance 잘못된 티커 — None 또는 price=0."""
        client = YFinanceClient()
        result = client.get_quote("ZZZZZZ999")
        # yfinance는 잘못된 티커에 대해 None 또는 price 0 반환 가능
        if result is not None:
            assert result["price"] == 0 or result["price"] is None
        print(f"  yfinance invalid ticker: {result}")


# ============================================================
# 2. Finnhub — 실제 호출
# ============================================================

class TestFinnhubReal:
    def test_get_quote(self):
        """Finnhub 시세 조회."""
        client = FinnhubClient()
        result = client.get_quote(TICKER)
        assert result is not None, "Finnhub get_quote returned None — API 키 확인 필요"
        assert result["source"] == "finnhub"
        assert result["price"] > 0
        print(f"  Finnhub quote: ${result['price']}, change={result['change_pct']:+.2f}%")

    def test_get_news(self):
        """Finnhub 뉴스 조회."""
        client = FinnhubClient()
        result = client.get_news(TICKER)
        assert result is not None, "Finnhub get_news returned None"
        assert len(result["articles"]) > 0
        print(f"  Finnhub news: {len(result['articles'])} articles")
        print(f"  Latest: {result['articles'][0]['headline'][:60]}...")

    def test_get_analyst(self):
        """Finnhub 애널리스트 추천."""
        client = FinnhubClient()
        result = client.get_analyst_recommendations(TICKER)
        assert result is not None, "Finnhub get_analyst returned None"
        total = result["strong_buy"] + result["buy"] + result["hold"] + result["sell"] + result["strong_sell"]
        assert total > 0
        print(f"  Finnhub analyst: buy={result['buy']}, hold={result['hold']}, sell={result['sell']}")


# ============================================================
# 3. Twelve Data — 실제 호출
# ============================================================

class TestTwelveDataReal:
    def test_get_rsi(self):
        """Twelve Data RSI 조회."""
        client = TwelveDataClient()
        result = client.get_rsi(TICKER)
        assert result is not None, "TwelveData get_rsi returned None — API 키 확인 필요"
        assert result["indicator"] == "RSI"
        assert len(result["values"]) > 0
        latest_rsi = result["values"][0]["rsi"]
        assert 0 <= latest_rsi <= 100
        print(f"  TwelveData RSI: {latest_rsi:.2f}")

    def test_get_macd(self):
        """Twelve Data MACD 조회."""
        client = TwelveDataClient()
        result = client.get_macd(TICKER)
        assert result is not None, "TwelveData get_macd returned None"
        assert result["indicator"] == "MACD"
        assert len(result["values"]) > 0
        latest = result["values"][0]
        print(f"  TwelveData MACD: {latest['macd']:.4f}, signal={latest['signal']:.4f}")

    def test_get_bbands(self):
        """Twelve Data 볼린저밴드 조회."""
        client = TwelveDataClient()
        result = client.get_bbands(TICKER)
        assert result is not None, "TwelveData get_bbands returned None"
        latest = result["values"][0]
        assert latest["upper"] > latest["lower"]
        print(f"  TwelveData BBands: upper={latest['upper']:.2f}, lower={latest['lower']:.2f}")


# ============================================================
# 4. FMP — 실제 호출
# ============================================================

class TestFMPReal:
    def test_get_fundamentals(self):
        """FMP 재무 지표 조회 — 무료 플랜 제한으로 실패 가능."""
        client = FMPClient()
        result = client.get_fundamentals(TICKER)
        if result is None:
            pytest.skip("FMP free tier blocked (403) — Finviz로 대체됨")
        assert result["source"] == "fmp"
        print(f"  FMP fundamentals: sector={result['sector']}, PE={result['pe_ratio']}")

    def test_screen_stocks(self):
        """FMP 섹터 스크리닝 — 무료 플랜 제한으로 실패 가능."""
        client = FMPClient()
        result = client.screen_stocks(sector="Technology", limit=5)
        if result is None:
            pytest.skip("FMP free tier blocked (403) — Finviz로 대체됨")
        assert len(result["stocks"]) > 0
        print(f"  FMP screener: {len(result['stocks'])} stocks")

    def test_get_sector_pe(self):
        """FMP 섹터 평균 PE — 무료 플랜 제한으로 실패 가능."""
        client = FMPClient()
        result = client.get_sector_pe("Technology")
        if result is None:
            pytest.skip("FMP free tier blocked (403) — Finviz로 대체됨")
        assert result["median_pe"] > 0
        print(f"  FMP sector PE: median={result['median_pe']}, samples={result['sample_size']}")


# ============================================================
# 4-2. Finviz — 실제 호출 (FMP 대체)
# ============================================================

class TestFinvizReal:
    def test_screen_stocks(self):
        """Finviz 섹터 스크리닝."""
        client = FinvizClient()
        result = client.screen_stocks(sector="Technology", limit=5)
        assert result is not None, "Finviz screen_stocks returned None"
        assert result["source"] == "finviz"
        assert len(result["stocks"]) > 0
        print(f"  Finviz screener: {result['total_count']} total, showing {len(result['stocks'])}")
        for s in result["stocks"][:3]:
            print(f"    {s['ticker']}: ${s['price']}, PE={s['pe_ratio']}")

    def test_get_sector_pe(self):
        """Finviz 섹터 평균 PE."""
        client = FinvizClient()
        result = client.get_sector_pe("Technology")
        assert result is not None, "Finviz get_sector_pe returned None"
        assert result["median_pe"] > 0
        assert result["sample_size"] > 10
        print(f"  Finviz sector PE: median={result['median_pe']}, samples={result['sample_size']}")

    def test_get_fundamentals(self):
        """Finviz 개별 종목 조회."""
        client = FinvizClient()
        result = client.get_fundamentals(TICKER)
        assert result is not None, "Finviz get_fundamentals returned None"
        assert result["sector"] is not None
        print(f"  Finviz fundamentals: sector={result['sector']}, PE={result['pe_ratio']}")


# ============================================================
# 5. FRED — 실제 호출
# ============================================================

class TestFREDReal:
    def test_get_fed_rate(self):
        """FRED 금리 데이터."""
        client = FREDClient()
        result = client.get_fed_rate()
        assert result is not None, "FRED get_fed_rate returned None — API 키 확인 필요"
        assert result["source"] == "fred"
        assert result["latest"]["value"] is not None
        print(f"  FRED fed rate: {result['latest']['value']}%")

    def test_get_macro_summary(self):
        """FRED 매크로 요약."""
        client = FREDClient()
        result = client.get_macro_summary()
        assert result is not None, "FRED get_macro_summary returned None"
        assert "fed_rate" in result
        print(f"  FRED macro summary keys: {list(result.keys())}")


# ============================================================
# 6. 통합 클라이언트 — 실제 폴백 테스트
# ============================================================

class TestAPIClientReal:
    def setup_method(self):
        cache.clear()

    def test_get_quote_with_fallback(self):
        """통합 시세 조회 — 실제 폴백 경로."""
        client = APIClient()
        result = client.get_quote(TICKER)
        assert result is not None, "APIClient get_quote returned None — 모든 소스 실패"
        print(f"  APIClient quote: ${result['price']} (source: {result['source']})")

    def test_get_history(self):
        """통합 히스토리 조회."""
        client = APIClient()
        result = client.get_history(TICKER, period="1mo")
        assert result is not None
        print(f"  APIClient history: {len(result['data'])} rows (source: {result['source']})")

    def test_get_fundamentals(self):
        """통합 재무 지표 — 실제 폴백 경로."""
        client = APIClient()
        result = client.get_fundamentals(TICKER)
        assert result is not None
        print(f"  APIClient fundamentals: PE={result.get('pe_ratio')} (source: {result['source']})")

    def test_get_technicals(self):
        """통합 기술지표 조회."""
        client = APIClient()
        result = client.get_technicals(TICKER)
        assert result is not None
        print(f"  APIClient technicals: RSI available={result['rsi'] is not None} (source: {result['source']})")

    def test_get_macro(self):
        """통합 매크로 조회."""
        client = APIClient()
        result = client.get_macro()
        assert result is not None
        print(f"  APIClient macro: source={result['source']}")

    def test_get_market_indices(self):
        """통합 시장 지수 조회."""
        client = APIClient()
        result = client.get_market_indices()
        assert result is not None
        print(f"  APIClient indices: {list(result['indices'].keys())}")

    def test_get_sector_stocks(self):
        """통합 섹터 스크리닝 — Finviz → FMP 폴백."""
        client = APIClient()
        result = client.get_sector_stocks("Technology", limit=5)
        assert result is not None, "섹터 스크리닝 전체 실패"
        print(f"  APIClient sector: {len(result['stocks'])} stocks (source: {result['source']})")

    def test_get_sector_pe(self):
        """통합 섹터 PE — Finviz → FMP 폴백."""
        client = APIClient()
        result = client.get_sector_pe("Technology")
        assert result is not None, "섹터 PE 전체 실패"
        print(f"  APIClient sector PE: {result['median_pe']} (source: {result['source']})")

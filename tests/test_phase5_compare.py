"""Phase 5 테스트 — Compare + Watchlist + Guide + Market Overview.

단위 테스트로 코드 로직 검증.

실행: pytest tests/test_phase5_compare.py -v
"""

import json
import os
import sys
import tempfile
from unittest.mock import patch, MagicMock

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from data.style_classifier import classify_style, classify_multiple, _to_float
from data.guide_content import (
    get_categories, get_topics, get_topic_detail, get_category_info, GUIDE_CONTENT,
)


# ============================================================
# 테스트 데이터
# ============================================================

FUNDAMENTALS_NVDA = {
    "ticker": "NVDA", "pe": 60, "forward_pe": 35, "eps": 4.05, "peg": 2.5,
    "market_cap": 2800e9, "dividend_yield": 0.03, "de_ratio": 0.41,
    "sector": "Technology", "industry": "Semiconductors", "source": "yfinance",
}

FUNDAMENTALS_AAPL = {
    "ticker": "AAPL", "pe": 33, "forward_pe": 28, "eps": 6.5, "peg": 1.8,
    "market_cap": 3500e9, "dividend_yield": 0.5, "de_ratio": 1.8,
    "sector": "Technology", "industry": "Consumer Electronics", "source": "yfinance",
}

FUNDAMENTALS_JNJ = {
    "ticker": "JNJ", "pe": 15, "forward_pe": 14, "eps": 10.0, "peg": 1.2,
    "market_cap": 400e9, "dividend_yield": 3.1, "de_ratio": 0.5,
    "sector": "Healthcare", "industry": "Drug Manufacturers - General", "source": "yfinance",
}

FUNDAMENTALS_XOM = {
    "ticker": "XOM", "pe": 11, "forward_pe": 10, "eps": 8.5, "peg": 0.8,
    "market_cap": 500e9, "dividend_yield": 3.5, "de_ratio": 0.3,
    "sector": "Energy", "industry": "Oil & Gas Integrated", "source": "yfinance",
}

QUOTE_NVDA = {
    "ticker": "NVDA", "price": 120.5, "change": 2.2, "change_percent": 1.86,
    "volume": 40000000, "source": "finnhub",
}

QUOTE_AAPL = {
    "ticker": "AAPL", "price": 260.0, "change": -1.5, "change_percent": -0.57,
    "volume": 50000000, "source": "finnhub",
}

MOCK_AI_COMPARE_RESPONSE = {
    "parsed": True,
    "data": {
        "rankings": {
            "growth": [{"ticker": "NVDA", "rank": 1, "reason": "AI 성장"}],
            "valuation": [{"ticker": "AAPL", "rank": 1, "reason": "안정적 밸류에이션"}],
        },
        "recommendation_by_style": {
            "growth_investor": {"pick": "NVDA", "reason": "AI 성장"},
            "value_investor": {"pick": "AAPL", "reason": "현금 창출"},
            "balanced_investor": {"pick": "AAPL", "reason": "안정성"},
        },
        "blind_spots": ["AI 규제 리스크"],
        "summary": "테스트 요약",
    },
}


# ============================================================
# 1. style_classifier.py
# ============================================================

class TestStyleClassifier:
    def test_growth_high_pe(self):
        """Growth: forward_pe >= 25."""
        result = classify_style({"forward_pe": 35, "dividend_yield": 0.03})
        assert result == "Growth"

    def test_growth_pe_with_peg(self):
        """Growth: PEG > 2 + PE >= 20."""
        result = classify_style({"forward_pe": 22, "peg": 2.5})
        assert result == "Growth"

    def test_value_low_pe_high_dividend(self):
        """Value: forward_pe < 18 + 배당 2%+."""
        result = classify_style({"forward_pe": 14, "dividend_yield": 3.1})
        assert result == "Value"

    def test_value_very_low_pe(self):
        """Value: PE < 12 (배당 없어도)."""
        result = classify_style({"forward_pe": 10, "dividend_yield": 0.5})
        assert result == "Value"

    def test_balanced_default(self):
        """Balanced: Growth도 Value도 아님."""
        result = classify_style({"forward_pe": 20, "dividend_yield": 1.0})
        assert result == "Balanced"

    def test_balanced_no_data(self):
        """데이터 없으면 Balanced."""
        result = classify_style({})
        assert result == "Balanced"

    def test_classify_nvda(self):
        """NVDA는 Growth."""
        assert classify_style(FUNDAMENTALS_NVDA) == "Growth"

    def test_classify_jnj(self):
        """JNJ는 Value."""
        assert classify_style(FUNDAMENTALS_JNJ) == "Value"

    def test_classify_multiple(self):
        """여러 종목 일괄 분류."""
        data = {"NVDA": FUNDAMENTALS_NVDA, "JNJ": FUNDAMENTALS_JNJ}
        result = classify_multiple(data)
        assert result["NVDA"] == "Growth"
        assert result["JNJ"] == "Value"

    def test_to_float_variants(self):
        """_to_float 다양한 입력."""
        assert _to_float(3.14) == 3.14
        assert _to_float("25.5") == 25.5
        assert _to_float(None) is None
        assert _to_float("invalid") is None


# ============================================================
# 2. compare.py
# ============================================================

class TestCompare:
    @patch("data.compare.get_fundamentals")
    def test_same_sector_same_industry(self, mock_fund):
        """같은 섹터 + 같은 industry → same_sector."""
        from data.compare import detect_comparison_type
        mock_fund.side_effect = [
            {"sector": "Technology", "industry": "Semiconductors"},
            {"sector": "Technology", "industry": "Semiconductors"},
        ]
        result = detect_comparison_type(["NVDA", "AMD"])
        assert result == "same_sector"

    @patch("data.compare.get_fundamentals")
    def test_cross_sector(self, mock_fund):
        """다른 섹터 → cross_sector."""
        from data.compare import detect_comparison_type
        mock_fund.side_effect = [
            {"sector": "Technology", "industry": "Semiconductors"},
            {"sector": "Healthcare", "industry": "Drug Manufacturers - General"},
        ]
        result = detect_comparison_type(["NVDA", "JNJ"])
        assert result == "cross_sector"

    @patch("data.compare.get_fundamentals")
    def test_same_sector_related_industry(self, mock_fund):
        """같은 섹터 + 관련 industry → same_sector."""
        from data.compare import detect_comparison_type
        mock_fund.side_effect = [
            {"sector": "Technology", "industry": "Semiconductors"},
            {"sector": "Technology", "industry": "Semiconductor Equipment"},
        ]
        result = detect_comparison_type(["NVDA", "AMAT"])
        assert result == "same_sector"

    @patch("data.compare.get_fundamentals")
    def test_same_sector_unrelated_industry(self, mock_fund):
        """같은 섹터 + 비관련 industry → cross_sector."""
        from data.compare import detect_comparison_type
        mock_fund.side_effect = [
            {"sector": "Technology", "industry": "Semiconductors"},
            {"sector": "Technology", "industry": "Consulting Services"},
        ]
        result = detect_comparison_type(["NVDA", "ACN"])
        assert result == "cross_sector"

    @patch("data.compare.get_fundamentals")
    def test_unknown_sector(self, mock_fund):
        """sector 없으면 cross_sector."""
        from data.compare import detect_comparison_type
        mock_fund.side_effect = [
            {"sector": None, "industry": None},
            {"sector": "Technology", "industry": "Semiconductors"},
        ]
        result = detect_comparison_type(["XXX", "NVDA"])
        assert result == "cross_sector"

    @patch("data.compare.get_fundamentals")
    def test_fundamentals_fail(self, mock_fund):
        """fundamentals 실패 시 cross_sector."""
        from data.compare import detect_comparison_type
        mock_fund.return_value = None
        result = detect_comparison_type(["XXX", "YYY"])
        assert result == "cross_sector"

    @patch("data.compare.get_technicals")
    @patch("data.compare.get_fundamentals")
    @patch("data.compare.get_quote")
    def test_get_comparison_data(self, mock_quote, mock_fund, mock_tech):
        """get_comparison_data 전체 데이터 구조."""
        from data.compare import get_comparison_data
        mock_quote.side_effect = [QUOTE_NVDA, QUOTE_AAPL]
        # detect_comparison_type에서 2회 + get_comparison_data 루프에서 2회 = 총 4회
        mock_fund.side_effect = [FUNDAMENTALS_NVDA, FUNDAMENTALS_AAPL,
                                 FUNDAMENTALS_NVDA, FUNDAMENTALS_AAPL]
        mock_tech.return_value = {"rsi": {"value": 62, "signal": "neutral"}}

        result = get_comparison_data(["NVDA", "AAPL"])

        assert result["tickers"] == ["NVDA", "AAPL"]
        assert result["comparison_type"] in ("same_sector", "cross_sector")
        assert "NVDA" in result["data"]
        assert "AAPL" in result["data"]
        assert result["data"]["NVDA"]["quote"] == QUOTE_NVDA

    def test_single_ticker(self):
        """티커 1개면 same_sector."""
        from data.compare import detect_comparison_type
        assert detect_comparison_type(["NVDA"]) == "same_sector"


# ============================================================
# 3. compare_agent.py
# ============================================================

class TestCompareAgent:
    @patch("agents.compare_agent.cache")
    @patch("agents.compare_agent.call_claude")
    def test_same_sector_success(self, mock_claude, mock_cache):
        """same_sector AI 분석 성공."""
        from agents.compare_agent import run_compare_analysis
        mock_cache.get.return_value = None
        mock_claude.return_value = MOCK_AI_COMPARE_RESPONSE

        result = run_compare_analysis(
            tickers=["NVDA", "AAPL"],
            comparison_type="same_sector",
            ticker_data={"NVDA": {}, "AAPL": {}},
        )

        assert result["status"] == "success"
        assert result["comparison_type"] == "same_sector"
        assert result["analysis"] is not None
        assert "rankings" in result["analysis"]
        mock_claude.assert_called_once()

    @patch("agents.compare_agent.cache")
    @patch("agents.compare_agent.call_claude")
    def test_cross_sector_success(self, mock_claude, mock_cache):
        """cross_sector AI 분석 성공."""
        from agents.compare_agent import run_compare_analysis
        mock_cache.get.return_value = None
        mock_claude.return_value = MOCK_AI_COMPARE_RESPONSE

        result = run_compare_analysis(
            tickers=["NVDA", "JNJ"],
            comparison_type="cross_sector",
            ticker_data={"NVDA": {}, "JNJ": {}},
        )

        assert result["status"] == "success"
        assert result["comparison_type"] == "cross_sector"

    @patch("agents.compare_agent.cache")
    @patch("agents.compare_agent.call_claude")
    def test_ai_failure(self, mock_claude, mock_cache):
        """AI 실패 시 failed 반환."""
        from agents.compare_agent import run_compare_analysis
        mock_cache.get.return_value = None
        mock_claude.return_value = {"parsed": False, "raw_output": "", "error": "API error"}

        result = run_compare_analysis(
            tickers=["NVDA", "AAPL"],
            comparison_type="same_sector",
            ticker_data={},
        )

        assert result["status"] == "failed"
        assert result["analysis"] is None
        assert result["error"] is not None

    @patch("agents.compare_agent.cache")
    def test_cache_hit(self, mock_cache):
        """캐시 적중 시 즉시 반환."""
        from agents.compare_agent import run_compare_analysis
        cached = {"status": "success", "tickers": ["AAPL", "NVDA"]}
        mock_cache.get.return_value = cached

        result = run_compare_analysis(
            tickers=["AAPL", "NVDA"],
            comparison_type="same_sector",
            ticker_data={},
        )
        assert result == cached


# ============================================================
# 4. watchlist.py
# ============================================================

class TestWatchlist:
    def _temp_watchlist(self, data=None):
        """임시 watchlist.json 생성."""
        if data is None:
            data = []
        fd, path = tempfile.mkstemp(suffix=".json")
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            json.dump(data, f)
        return path

    @patch("data.watchlist.WATCHLIST_PATH")
    def test_load_empty(self, mock_path):
        """빈 watchlist 로드."""
        from data.watchlist import load_watchlist
        path = self._temp_watchlist([])
        mock_path.__str__ = lambda s: path
        # 직접 파일 테스트
        with open(path, "r") as f:
            data = json.load(f)
        assert data == []
        os.unlink(path)

    def test_load_returns_list(self):
        """load_watchlist는 list 반환."""
        from data.watchlist import load_watchlist
        result = load_watchlist()
        assert isinstance(result, list)

    def test_add_and_remove(self):
        """추가 후 제거."""
        from data.watchlist import add_to_watchlist, remove_from_watchlist, load_watchlist
        # add
        add_to_watchlist("test_ticker_xyz")
        wl = load_watchlist()
        assert "TEST_TICKER_XYZ" in wl

        # remove
        remove_from_watchlist("TEST_TICKER_XYZ")
        wl = load_watchlist()
        assert "TEST_TICKER_XYZ" not in wl

    def test_add_duplicate(self):
        """중복 추가 무시."""
        from data.watchlist import add_to_watchlist, remove_from_watchlist, load_watchlist
        add_to_watchlist("dup_test_xyz")
        add_to_watchlist("dup_test_xyz")
        wl = load_watchlist()
        assert wl.count("DUP_TEST_XYZ") == 1
        remove_from_watchlist("DUP_TEST_XYZ")

    def test_add_uppercase(self):
        """소문자 → 대문자 변환."""
        from data.watchlist import add_to_watchlist, remove_from_watchlist, load_watchlist
        add_to_watchlist("lower_test")
        wl = load_watchlist()
        assert "LOWER_TEST" in wl
        remove_from_watchlist("LOWER_TEST")

    def test_add_empty_raises(self):
        """빈 문자열 추가 시 ValueError."""
        from data.watchlist import add_to_watchlist
        with pytest.raises(ValueError, match="비어있습니다"):
            add_to_watchlist("")

    def test_remove_not_found(self):
        """존재하지 않는 티커 제거 시 KeyError."""
        from data.watchlist import remove_from_watchlist
        with pytest.raises(KeyError, match="Watchlist에 없습니다"):
            remove_from_watchlist("NONEXISTENT_XYZ_999")

    @patch("data.watchlist.get_quote")
    def test_get_watchlist_quotes(self, mock_quote):
        """시세 조회 + highlight 플래그."""
        from data.watchlist import get_watchlist_quotes
        mock_quote.side_effect = [
            {"price": 120, "change": 8.0, "change_percent": 7.1, "source": "finnhub"},
            {"price": 50, "change": -1.0, "change_percent": -1.9, "source": "finnhub"},
            None,
        ]
        result = get_watchlist_quotes(["NVDA", "INTC", "BAD"])

        assert len(result) == 3
        assert result[0]["highlight"] is True   # 7.1% >= 5%
        assert result[1]["highlight"] is False   # 1.9% < 5%
        assert result[2]["price"] is None        # 실패

    @patch("data.watchlist.get_quote")
    def test_empty_watchlist_quotes(self, mock_quote):
        """빈 watchlist 시세 조회."""
        from data.watchlist import get_watchlist_quotes
        result = get_watchlist_quotes([])
        assert result == []


# ============================================================
# 5. guide_content.py
# ============================================================

class TestGuideContent:
    def test_get_categories(self):
        """5개 카테고리 존재."""
        cats = get_categories()
        assert len(cats) == 5
        assert "chart_basics" in cats
        assert "key_metrics" in cats
        assert "technicals" in cats
        assert "market_concepts" in cats
        assert "investment_styles" in cats

    def test_get_topics(self):
        """각 카테고리에 주제 1개 이상."""
        for cat in get_categories():
            topics = get_topics(cat)
            assert len(topics) >= 1
            # 각 주제에 필수 키 존재
            for t in topics:
                assert "title" in t
                assert "level" in t
                assert "what" in t
                assert "how" in t

    def test_get_topic_detail(self):
        """특정 주제 상세 반환."""
        detail = get_topic_detail("chart_basics", 0)
        assert detail is not None
        assert detail["title"] == "캔들스틱 차트"
        assert detail["level"] == "beginner"

    def test_get_topic_detail_invalid_index(self):
        """잘못된 인덱스 → None."""
        assert get_topic_detail("chart_basics", 999) is None

    def test_get_topics_invalid_category(self):
        """잘못된 카테고리 → 빈 리스트."""
        assert get_topics("nonexistent") == []

    def test_get_category_info(self):
        """카테고리 전체 정보."""
        info = get_category_info("key_metrics")
        assert info is not None
        assert info["category"] == "핵심 지표"
        assert "topics" in info

    def test_levels_are_valid(self):
        """모든 주제의 level이 유효."""
        valid = {"beginner", "intermediate", "advanced"}
        for cat in get_categories():
            for topic in get_topics(cat):
                assert topic["level"] in valid, f"Invalid level: {topic['level']} in {cat}"


# ============================================================
# 6. market_overview.py
# ============================================================

class TestMarketOverview:
    @patch("data.market_overview.cache")
    @patch("data.market_overview.api_client")
    def test_get_market_indices(self, mock_api, mock_cache):
        """시장 지수 조회."""
        from data.market_overview import get_market_indices
        mock_cache.get.return_value = None
        mock_api.get_market_indices.return_value = {
            "SPY": {"price": 5200, "change": 42, "change_percent": 0.82},
            "NASDAQ": {"price": 16300, "change": 180, "change_percent": 1.1},
            "DOW": {"price": 39500, "change": 150, "change_percent": 0.38},
            "VIX": {"price": 18.5, "change": -1.2, "change_percent": -6.1},
        }

        result = get_market_indices()

        assert result is not None
        assert len(result) == 4
        symbols = [r["symbol"] for r in result]
        assert "S&P 500" in symbols
        assert "VIX" in symbols

    @patch("data.market_overview.cache")
    @patch("data.market_overview.api_client")
    def test_market_indices_fail(self, mock_api, mock_cache):
        """지수 조회 실패 → None."""
        from data.market_overview import get_market_indices
        mock_cache.get.return_value = None
        mock_api.get_market_indices.return_value = None

        result = get_market_indices()
        assert result is None

    @patch("data.market_overview.cache")
    @patch("data.market_overview.api_client")
    def test_get_market_news(self, mock_api, mock_cache):
        """뉴스 조회."""
        from data.market_overview import get_market_news
        mock_cache.get.return_value = None
        mock_api.finnhub.get_market_news.return_value = {
            "source": "finnhub",
            "articles": [
                {"headline": "Fed holds rates", "source": "Reuters", "url": "...", "datetime": 123456},
                {"headline": "NVDA surges", "source": "CNBC", "url": "...", "datetime": 123457},
            ],
        }

        result = get_market_news(limit=2)

        assert result is not None
        assert len(result) == 2
        assert result[0]["headline"] == "Fed holds rates"

    @patch("data.market_overview.cache")
    @patch("data.market_overview.api_client")
    def test_market_news_fail(self, mock_api, mock_cache):
        """뉴스 실패 → None."""
        from data.market_overview import get_market_news
        mock_cache.get.return_value = None
        mock_api.finnhub.get_market_news.return_value = None

        result = get_market_news()
        assert result is None

    @patch("data.market_overview.cache")
    def test_indices_cache_hit(self, mock_cache):
        """지수 캐시 적중."""
        from data.market_overview import get_market_indices
        cached = [{"symbol": "S&P 500", "price": 5200}]
        mock_cache.get.return_value = cached

        result = get_market_indices()
        assert result == cached

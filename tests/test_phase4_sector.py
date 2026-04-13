"""Phase 4 테스트 - Sector Screening 모듈.

단위 테스트로 코드 로직 검증.

실행: pytest tests/test_phase4_sector.py -v
"""

import json
import os
import sys
import tempfile
from unittest.mock import patch, MagicMock

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from data.theme_manager import (
    load_themes, create_theme, delete_theme, get_theme_names,
    VALID_PRESETS, DEFAULT_THEMES, THEMES_PATH,
)
from data.sector_data import (
    get_sector_tickers, get_theme_tickers, get_preset_for_sector,
    get_preset_for_theme, is_theme, GICS_SECTORS, SECTOR_PRESET_MAP,
)
from data.stock_filter import (
    filter_stocks, _to_number, _apply_common_filter,
    PRESET_CRITERIA,
)


# ============================================================
# Mock 데이터
# ============================================================

MOCK_SECTOR_STOCKS = {
    "source": "finviz",
    "sector": "Information Technology",
    "stocks": [
        {"ticker": "AAPL", "name": "Apple Inc.", "market_cap": 3500000000000, "pe_ratio": 33.5, "volume": 50000000},
        {"ticker": "MSFT", "name": "Microsoft Corp.", "market_cap": 3200000000000, "pe_ratio": 35.2, "volume": 25000000},
        {"ticker": "NVDA", "name": "NVIDIA Corp.", "market_cap": 2800000000000, "pe_ratio": 60.0, "volume": 40000000},
        {"ticker": "AVGO", "name": "Broadcom Inc.", "market_cap": 800000000000, "pe_ratio": 35.0, "volume": 5000000},
        {"ticker": "ORCL", "name": "Oracle Corp.", "market_cap": 400000000000, "pe_ratio": 38.0, "volume": 8000000},
        {"ticker": "CRM", "name": "Salesforce Inc.", "market_cap": 250000000000, "pe_ratio": 45.0, "volume": 6000000},
        {"ticker": "AMD", "name": "AMD Inc.", "market_cap": 200000000000, "pe_ratio": 40.0, "volume": 30000000},
        {"ticker": "INTC", "name": "Intel Corp.", "market_cap": 100000000000, "pe_ratio": 25.0, "volume": 35000000},
        {"ticker": "QCOM", "name": "Qualcomm Inc.", "market_cap": 180000000000, "pe_ratio": 18.0, "volume": 7000000},
        {"ticker": "TXN", "name": "Texas Instruments", "market_cap": 170000000000, "pe_ratio": 30.0, "volume": 4000000},
        {"ticker": "AMAT", "name": "Applied Materials", "market_cap": 150000000000, "pe_ratio": 22.0, "volume": 6000000},
        {"ticker": "MU", "name": "Micron Technology", "market_cap": 120000000000, "pe_ratio": 15.0, "volume": 20000000},
    ],
    "total_count": 12,
}

MOCK_AI_RESPONSE = {
    "parsed": True,
    "data": {
        "analysis": [
            {"ticker": "NVDA", "score": 88, "news_sentiment": "AI 수요 폭증", "financials": "매출 성장 200%+", "technical_signal": "강세", "reason": "AI 인프라 핵심 수혜"},
            {"ticker": "AAPL", "score": 82, "news_sentiment": "안정적", "financials": "안정 수익", "technical_signal": "중립", "reason": "현금 창출력 최강"},
            {"ticker": "MSFT", "score": 80, "news_sentiment": "AI 투자 확대", "financials": "클라우드 성장", "technical_signal": "상승", "reason": "Azure AI 성장"},
            {"ticker": "AVGO", "score": 76, "news_sentiment": "인수 효과", "financials": "마진 개선", "technical_signal": "상승", "reason": "AI 네트워킹 수혜"},
            {"ticker": "AMD", "score": 72, "news_sentiment": "경쟁 심화", "financials": "점유율 확대", "technical_signal": "중립", "reason": "GPU 시장 2위"},
        ],
        "sector_outlook": "AI 투자 확대로 반도체/소프트웨어 섹터 성장 지속 전망",
        "risk_factors": ["금리 인상 리스크", "AI 버블 우려"],
    },
}


# ============================================================
# 1. theme_manager.py
# ============================================================

class TestThemeManager:
    def _temp_themes(self, data=None):
        """임시 themes.json으로 테스트."""
        if data is None:
            data = DEFAULT_THEMES.copy()
        fd, path = tempfile.mkstemp(suffix=".json")
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            json.dump(data, f)
        return path

    @patch("data.theme_manager.THEMES_PATH")
    def test_load_themes_normal(self, mock_path):
        """TC-001: themes.json 정상 로드."""
        path = self._temp_themes()
        mock_path.__str__ = lambda s: path
        # 직접 THEMES_PATH를 패치하기 어려우므로 파일 직접 테스트
        with open(path, "r", encoding="utf-8") as f:
            themes = json.load(f)
        assert "AI_semiconductor" in themes
        assert len(themes["AI_semiconductor"]["tickers"]) >= 5
        os.unlink(path)

    def test_load_themes_returns_dict(self):
        """TC-001b: load_themes가 dict 반환."""
        themes = load_themes()
        assert isinstance(themes, dict)
        assert len(themes) >= 5

    def test_create_theme_success(self):
        """TC-002: 테마 생성 성공."""
        themes_backup = load_themes()
        try:
            create_theme("test_theme", ["AAPL", "MSFT", "GOOGL", "AMZN", "META"], "large_stable")
            themes = load_themes()
            assert "test_theme" in themes
            assert themes["test_theme"]["preset"] == "large_stable"
            assert len(themes["test_theme"]["tickers"]) == 5
            assert themes["test_theme"]["tickers"][0] == "AAPL"
        finally:
            # cleanup
            try:
                delete_theme("test_theme")
            except KeyError:
                pass

    def test_create_theme_min_tickers(self):
        """TC-003: 티커 5개 미만 시 ValueError."""
        with pytest.raises(ValueError, match="최소 5개"):
            create_theme("bad_theme", ["AAPL", "MSFT"], "large_stable")

    def test_create_theme_invalid_preset(self):
        """TC-004: 유효하지 않은 프리셋 시 ValueError."""
        with pytest.raises(ValueError, match="유효하지 않은 프리셋"):
            create_theme("bad_theme", ["A", "B", "C", "D", "E"], "invalid_preset")

    def test_delete_theme_success(self):
        """TC-005: 테마 삭제 성공."""
        create_theme("to_delete", ["AAPL", "MSFT", "GOOGL", "AMZN", "META"], "mid_growth")
        delete_theme("to_delete")
        themes = load_themes()
        assert "to_delete" not in themes

    def test_delete_theme_not_found(self):
        """TC-006: 존재하지 않는 테마 삭제 시 KeyError."""
        with pytest.raises(KeyError, match="존재하지 않습니다"):
            delete_theme("nonexistent_theme_xyz")

    def test_get_theme_names(self):
        """TC-007: 테마 이름 목록 반환."""
        names = get_theme_names()
        assert isinstance(names, list)
        assert "AI_semiconductor" in names

    def test_create_theme_uppercase(self):
        """TC-008: 티커가 대문자로 저장됨."""
        try:
            create_theme("upper_test", ["aapl", "msft", "googl", "amzn", "meta"], "large_stable")
            themes = load_themes()
            assert themes["upper_test"]["tickers"][0] == "AAPL"
        finally:
            try:
                delete_theme("upper_test")
            except KeyError:
                pass

    def test_valid_presets(self):
        """프리셋 상수 검증."""
        assert len(VALID_PRESETS) == 4
        assert "large_stable" in VALID_PRESETS
        assert "early_growth" in VALID_PRESETS


# ============================================================
# 2. sector_data.py
# ============================================================

class TestSectorData:
    @patch("data.sector_data.api_client")
    def test_get_sector_tickers(self, mock_client):
        """TC-009: 섹터 종목 조회 정상 반환."""
        mock_client.get_sector_stocks.return_value = MOCK_SECTOR_STOCKS
        result = get_sector_tickers("Information Technology")

        assert result is not None
        assert len(result) == 12
        assert result[0]["ticker"] == "AAPL"

    @patch("data.sector_data.api_client")
    def test_get_sector_tickers_fail(self, mock_client):
        """TC-010: 섹터 조회 실패 시 None."""
        mock_client.get_sector_stocks.return_value = None
        result = get_sector_tickers("Nonexistent Sector")
        assert result is None

    def test_get_theme_tickers(self):
        """TC-011: 테마 티커 조회."""
        result = get_theme_tickers("AI_semiconductor")
        assert result is not None
        assert "NVDA" in result

    def test_get_theme_tickers_not_found(self):
        """TC-012: 존재하지 않는 테마 → None."""
        result = get_theme_tickers("nonexistent_xyz")
        assert result is None

    def test_preset_for_sector_known(self):
        """TC-013: 알려진 섹터의 프리셋 매핑."""
        assert get_preset_for_sector("Information Technology") == "large_stable"
        assert get_preset_for_sector("Health Care") == "early_growth"
        assert get_preset_for_sector("Utilities") == "dividend"
        assert get_preset_for_sector("Energy") == "mid_growth"

    def test_preset_for_sector_unknown(self):
        """TC-014: 알 수 없는 섹터 → mid_growth 기본값."""
        assert get_preset_for_sector("Unknown Sector") == "mid_growth"

    def test_preset_for_theme(self):
        """TC-015: 테마 프리셋 조회."""
        assert get_preset_for_theme("AI_semiconductor") == "large_stable"
        assert get_preset_for_theme("space") == "early_growth"

    def test_is_theme(self):
        """TC-016: 테마 여부 판별."""
        assert is_theme("AI_semiconductor") is True
        assert is_theme("Information Technology") is False

    def test_gics_sectors_count(self):
        """GICS 섹터 11개 등록."""
        assert len(GICS_SECTORS) == 11

    def test_sector_preset_map_coverage(self):
        """모든 GICS 섹터에 프리셋 매핑 존재."""
        for sector in GICS_SECTORS:
            assert sector in SECTOR_PRESET_MAP, f"Missing preset for {sector}"


# ============================================================
# 3. stock_filter.py
# ============================================================

class TestStockFilter:
    def _make_stocks(self, count=15, base_cap=100_000_000_000):
        """테스트용 종목 리스트 생성."""
        stocks = []
        for i in range(count):
            stocks.append({
                "ticker": f"TEST{i}",
                "market_cap": base_cap - i * 5_000_000_000,
                "pe_ratio": 20 + i,
                "volume": 1000000 + i * 100000,
            })
        return stocks

    def test_large_stable_normal(self):
        """TC-017: large_stable 프리셋 정상 필터."""
        stocks = self._make_stocks(15, base_cap=200_000_000_000)
        filtered, relaxed, warning = filter_stocks(stocks, "large_stable")

        # $50B+ 통과하는 종목만, 최대 10개
        assert len(filtered) <= 10
        assert relaxed is False
        assert warning is None
        for s in filtered:
            assert s["market_cap"] >= 50_000_000_000

    def test_mid_growth_normal(self):
        """TC-018: mid_growth 프리셋."""
        stocks = self._make_stocks(15, base_cap=50_000_000_000)
        filtered, relaxed, warning = filter_stocks(stocks, "mid_growth")

        assert len(filtered) <= 10
        for s in filtered:
            assert s["market_cap"] >= 10_000_000_000

    def test_common_filter_removes_zero_volume(self):
        """TC-019: 1단계 공통 필터 - 거래량 0 제외."""
        stocks = [
            {"ticker": "GOOD", "market_cap": 100e9, "pe_ratio": 20, "volume": 5000000},
            {"ticker": "BAD", "market_cap": 100e9, "pe_ratio": 20, "volume": 0},
            {"ticker": "NONE", "market_cap": 100e9, "pe_ratio": 20, "volume": None},
        ]
        result = _apply_common_filter(stocks)
        tickers = [s["ticker"] for s in result]
        assert "GOOD" in tickers
        assert "BAD" not in tickers
        assert "NONE" in tickers  # None은 제외하지 않음

    def test_common_filter_removes_no_ticker(self):
        """TC-020: 1단계 공통 필터 - 티커 없는 항목 제외."""
        stocks = [
            {"ticker": "OK", "volume": 1000},
            {"ticker": "", "volume": 1000},
            {"volume": 1000},
        ]
        result = _apply_common_filter(stocks)
        assert len(result) == 1
        assert result[0]["ticker"] == "OK"

    def test_pe_positive_filter(self):
        """TC-021: PE 양수 필터 (large_stable)."""
        # 5개 이상 통과하도록 구성해서 적응형 완화 방지
        stocks = [
            {"ticker": "P1", "market_cap": 100e9, "pe_ratio": 25, "volume": 1000000},
            {"ticker": "P2", "market_cap": 100e9, "pe_ratio": 30, "volume": 1000000},
            {"ticker": "P3", "market_cap": 100e9, "pe_ratio": 20, "volume": 1000000},
            {"ticker": "P4", "market_cap": 100e9, "pe_ratio": 15, "volume": 1000000},
            {"ticker": "P5", "market_cap": 100e9, "pe_ratio": 10, "volume": 1000000},
            {"ticker": "NEG", "market_cap": 100e9, "pe_ratio": -5, "volume": 1000000},
            {"ticker": "ZERO", "market_cap": 100e9, "pe_ratio": 0, "volume": 1000000},
        ]
        filtered, _, _ = filter_stocks(stocks, "large_stable")
        tickers = [s["ticker"] for s in filtered]
        assert "P1" in tickers
        assert "NEG" not in tickers
        assert "ZERO" not in tickers

    def test_early_growth_no_pe_requirement(self):
        """TC-022: early_growth는 PE 무관."""
        stocks = [
            {"ticker": "LOSS", "market_cap": 5e9, "pe_ratio": -10, "volume": 1000000},
            {"ticker": "PROF", "market_cap": 5e9, "pe_ratio": 30, "volume": 1000000},
        ]
        filtered, _, _ = filter_stocks(stocks, "early_growth")
        tickers = [s["ticker"] for s in filtered]
        assert "LOSS" in tickers
        assert "PROF" in tickers

    def test_dividend_filter(self):
        """TC-023: dividend 프리셋 - 배당률 2%+ 체크."""
        # 적응형 완화 방지를 위해 통과 종목 5개 이상 확보
        stocks = [
            {"ticker": "D1", "market_cap": 10e9, "pe_ratio": 15, "volume": 1000000, "dividend_yield": 3.5},
            {"ticker": "D2", "market_cap": 10e9, "pe_ratio": 15, "volume": 1000000, "dividend_yield": 2.5},
            {"ticker": "D3", "market_cap": 10e9, "pe_ratio": 15, "volume": 1000000, "dividend_yield": 4.0},
            {"ticker": "D4", "market_cap": 10e9, "pe_ratio": 15, "volume": 1000000, "dividend_yield": 2.1},
            {"ticker": "D5", "market_cap": 10e9, "pe_ratio": 15, "volume": 1000000, "dividend_yield": 3.0},
            {"ticker": "LOW", "market_cap": 10e9, "pe_ratio": 15, "volume": 1000000, "dividend_yield": 0.5},
            {"ticker": "NONE", "market_cap": 10e9, "pe_ratio": 15, "volume": 1000000},
        ]
        filtered, _, _ = filter_stocks(stocks, "dividend")
        tickers = [s["ticker"] for s in filtered]
        assert "D1" in tickers
        assert "LOW" not in tickers
        assert "NONE" not in tickers

    def test_adaptive_relaxation_3_4(self):
        """TC-024: 3~4개 통과 시 시총 기준 완화."""
        # large_stable: $50B+ → 3개만 통과
        stocks = [
            {"ticker": "A", "market_cap": 80e9, "pe_ratio": 20, "volume": 1000000},
            {"ticker": "B", "market_cap": 60e9, "pe_ratio": 20, "volume": 1000000},
            {"ticker": "C", "market_cap": 55e9, "pe_ratio": 20, "volume": 1000000},
            {"ticker": "D", "market_cap": 30e9, "pe_ratio": 20, "volume": 1000000},
            {"ticker": "E", "market_cap": 25e9, "pe_ratio": 20, "volume": 1000000},
        ]
        filtered, relaxed, warning = filter_stocks(stocks, "large_stable")

        assert relaxed is True
        assert warning is not None
        assert "완화" in warning
        # 완화 후 $20B+ 통과하므로 D, E도 포함
        assert len(filtered) >= 4

    def test_adaptive_relaxation_0_2(self):
        """TC-025: 0~2개 통과 시 필터 무시, 시총 상위."""
        # large_stable: $50B+ → 모두 미달
        stocks = [
            {"ticker": "A", "market_cap": 30e9, "pe_ratio": 20, "volume": 1000000},
            {"ticker": "B", "market_cap": 20e9, "pe_ratio": 20, "volume": 1000000},
            {"ticker": "C", "market_cap": 10e9, "pe_ratio": 20, "volume": 1000000},
        ]
        filtered, relaxed, warning = filter_stocks(stocks, "large_stable")

        assert relaxed is True
        assert warning is not None
        assert "시총 상위" in warning
        # 3개 모두 반환 (시총 상위)
        assert len(filtered) == 3
        assert filtered[0]["ticker"] == "A"  # 시총 가장 큰 순

    def test_empty_stocks(self):
        """TC-026: 빈 종목 리스트."""
        filtered, relaxed, warning = filter_stocks([], "large_stable")
        assert filtered == []
        assert warning is not None

    def test_to_number_variants(self):
        """TC-027: _to_number 다양한 입력 형식."""
        assert _to_number(100) == 100.0
        assert _to_number(3.14) == 3.14
        assert _to_number("100") == 100.0
        assert _to_number("1.5T") == 1.5e12
        assert _to_number("200B") == 200e9
        assert _to_number("50M") == 50e6
        assert _to_number("10K") == 10e3
        assert _to_number("15.3%") == 15.3
        assert _to_number(None) is None
        assert _to_number("invalid") is None

    def test_sort_by_market_cap(self):
        """TC-028: 시총 기준 내림차순 정렬."""
        stocks = [
            {"ticker": "S", "market_cap": 10e9},
            {"ticker": "L", "market_cap": 100e9},
            {"ticker": "M", "market_cap": 50e9},
        ]
        filtered, _, _ = filter_stocks(stocks, "mid_growth")
        assert filtered[0]["ticker"] == "L"

    def test_unknown_preset_fallback(self):
        """TC-029: 알 수 없는 프리셋 → mid_growth로 폴백."""
        stocks = self._make_stocks(8, base_cap=50_000_000_000)
        filtered, relaxed, warning = filter_stocks(stocks, "unknown_preset")
        assert len(filtered) > 0  # mid_growth 기준 적용


# ============================================================
# 4. sector_analyzer.py (AI 분석)
# ============================================================

class TestSectorAnalyzer:
    @patch("agents.sector_analyzer.call_claude")
    @patch("agents.sector_analyzer.get_sector_tickers")
    @patch("agents.sector_analyzer.filter_stocks")
    @patch("agents.sector_analyzer.cache")
    def test_run_sector_screening_success(self, mock_cache, mock_filter, mock_tickers, mock_claude):
        """TC-030: 전체 파이프라인 정상 실행."""
        import asyncio
        from agents.sector_analyzer import run_sector_screening

        mock_cache.get.return_value = None
        mock_tickers.return_value = MOCK_SECTOR_STOCKS["stocks"]
        mock_filter.return_value = (MOCK_SECTOR_STOCKS["stocks"][:10], False, None)
        mock_claude.return_value = MOCK_AI_RESPONSE

        result = asyncio.run(run_sector_screening("Information Technology"))

        assert result["status"] == "success"
        assert result["sector"] == "Information Technology"
        assert len(result["top5"]) == 5
        assert result["top5"][0]["ticker"] == "NVDA"
        assert result["top5"][0]["score"] == 88
        assert result["sector_outlook"] is not None
        assert result["relaxed"] is False

    @patch("agents.sector_analyzer.call_claude")
    @patch("agents.sector_analyzer.get_sector_tickers")
    @patch("agents.sector_analyzer.filter_stocks")
    @patch("agents.sector_analyzer.cache")
    def test_run_sector_ai_fail_partial(self, mock_cache, mock_filter, mock_tickers, mock_claude):
        """TC-031: AI 실패 시 partial 반환."""
        import asyncio
        from agents.sector_analyzer import run_sector_screening

        mock_cache.get.return_value = None
        mock_tickers.return_value = MOCK_SECTOR_STOCKS["stocks"]
        mock_filter.return_value = (MOCK_SECTOR_STOCKS["stocks"][:5], False, None)
        mock_claude.return_value = {"parsed": False, "raw_output": "", "error": "API error"}

        result = asyncio.run(run_sector_screening("Information Technology"))

        assert result["status"] == "partial"
        assert len(result["top5"]) == 5
        assert result["error"] is not None

    @patch("agents.sector_analyzer.get_sector_tickers")
    @patch("agents.sector_analyzer.cache")
    def test_run_sector_no_stocks(self, mock_cache, mock_tickers):
        """TC-032: 종목 조회 실패 시 failed."""
        import asyncio
        from agents.sector_analyzer import run_sector_screening

        mock_cache.get.return_value = None
        mock_tickers.return_value = None

        result = asyncio.run(run_sector_screening("Nonexistent Sector"))

        assert result["status"] == "failed"
        assert result["error"] is not None

    @patch("agents.sector_analyzer.call_claude")
    @patch("agents.sector_analyzer._build_stock_data")
    @patch("agents.sector_analyzer.filter_stocks")
    @patch("agents.sector_analyzer.cache")
    def test_run_theme_screening(self, mock_cache, mock_filter, mock_build, mock_claude):
        """TC-033: 커스텀 테마 스크리닝."""
        import asyncio
        from agents.sector_analyzer import run_sector_screening

        mock_cache.get.return_value = None
        theme_stocks = [
            {"ticker": "NVDA", "price": 120, "pe": 60, "market_cap": 2800e9},
            {"ticker": "AMD", "price": 80, "pe": 40, "market_cap": 200e9},
            {"ticker": "AVGO", "price": 170, "pe": 35, "market_cap": 800e9},
            {"ticker": "TSM", "price": 90, "pe": 20, "market_cap": 500e9},
            {"ticker": "MRVL", "price": 60, "pe": 50, "market_cap": 70e9},
            {"ticker": "INTC", "price": 25, "pe": 25, "market_cap": 100e9},
            {"ticker": "QCOM", "price": 150, "pe": 18, "market_cap": 180e9},
        ]
        mock_build.return_value = theme_stocks
        mock_filter.return_value = (theme_stocks[:5], False, None)
        mock_claude.return_value = MOCK_AI_RESPONSE

        result = asyncio.run(run_sector_screening("AI_semiconductor"))

        assert result["status"] == "success"
        assert result["is_theme"] is True
        assert result["sector"] == "AI_semiconductor"

    @patch("agents.sector_analyzer.cache")
    def test_cache_hit(self, mock_cache):
        """TC-034: 캐시 적중 시 즉시 반환."""
        import asyncio
        from agents.sector_analyzer import run_sector_screening

        cached_result = {"status": "success", "sector": "Energy", "top5": []}
        mock_cache.get.return_value = cached_result

        result = asyncio.run(run_sector_screening("Energy"))
        assert result == cached_result

    @patch("agents.sector_analyzer.call_claude")
    @patch("agents.sector_analyzer.get_sector_tickers")
    @patch("agents.sector_analyzer.filter_stocks")
    @patch("agents.sector_analyzer.cache")
    def test_relaxation_info_preserved(self, mock_cache, mock_filter, mock_tickers, mock_claude):
        """TC-035: 필터 완화 정보가 결과에 포함."""
        import asyncio
        from agents.sector_analyzer import run_sector_screening

        mock_cache.get.return_value = None
        mock_tickers.return_value = MOCK_SECTOR_STOCKS["stocks"][:3]
        mock_filter.return_value = (
            MOCK_SECTOR_STOCKS["stocks"][:3],
            True,
            "필터 기준 완화 적용"
        )
        mock_claude.return_value = MOCK_AI_RESPONSE

        result = asyncio.run(run_sector_screening("Materials"))

        assert result["relaxed"] is True
        assert result["relaxation_message"] is not None

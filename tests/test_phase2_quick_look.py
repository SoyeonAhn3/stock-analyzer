"""Phase 2 테스트 — Quick Look 데이터 수집 계층.

단위 테스트로 코드 로직 검증.

실행: pytest tests/test_phase2_quick_look.py -v
"""

import sys
import os
from unittest.mock import patch, MagicMock

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from data.quote import get_quote, get_premarket
from data.history import get_history, PERIOD_MAP
from data.fundamentals import get_fundamentals
from data.technicals import get_technicals, _rsi_signal, _macd_signal, _bbands_signal, _ma_signal
from utils.indicators import calc_rsi, calc_macd, calc_bbands, calc_ma
from utils.chart_builder import build_price_chart
from utils.tooltips import TOOLTIPS, get_tooltip


# ============================================================
# Mock 데이터
# ============================================================

MOCK_QUOTE_RAW = {
    "source": "finnhub", "ticker": "NVDA",
    "price": 120.5, "previous_close": 118.3,
    "change": 2.2, "change_pct": 1.86,
    "high": 121.0, "low": 117.5, "open": 119.0,
    "volume": 45000000, "market_cap": 2950000000000,
}

MOCK_FUNDAMENTALS_RAW = {
    "source": "yfinance", "ticker": "NVDA",
    "pe_ratio": 35.2, "forward_pe": 28.1, "eps": 4.05,
    "peg_ratio": 1.8, "market_cap": 2950000000000,
    "52w_high": 153.0, "52w_low": 76.0,
    "dividend_yield": 0.0003, "debt_to_equity": 0.41,
    "sector": "Technology", "industry": "Semiconductors",
    "employees": 29600, "country": "US",
}

MOCK_TECHNICALS_RAW = {
    "source": "twelvedata", "ticker": "NVDA",
    "rsi": {"values": [{"datetime": "2026-04-07", "rsi": 62.5}]},
    "macd": {"values": [{"datetime": "2026-04-07", "macd": 1.5, "signal": 1.2, "histogram": 0.3}]},
    "bbands": {"values": [{"datetime": "2026-04-07", "upper": 130.0, "middle": 120.0, "lower": 110.0}]},
    "ma50": {"values": [{"datetime": "2026-04-07", "ma": 115.0}]},
    "ma200": {"values": [{"datetime": "2026-04-07", "ma": 100.0}]},
}


def _make_ohlcv_df(rows=100):
    """테스트용 OHLCV DataFrame 생성."""
    np.random.seed(42)
    dates = pd.date_range("2025-04-01", periods=rows, freq="B")
    close = 100 + np.cumsum(np.random.randn(rows) * 2)
    return pd.DataFrame({
        "Date": dates,
        "Open": close - np.random.rand(rows),
        "High": close + np.random.rand(rows) * 2,
        "Low": close - np.random.rand(rows) * 2,
        "Close": close,
        "Volume": np.random.randint(10000000, 90000000, rows),
    })


def _make_history_raw(rows=100):
    """api_client.get_history Mock 반환용 dict."""
    df = _make_ohlcv_df(rows)
    return {
        "source": "yfinance", "ticker": "NVDA",
        "period": "1y", "interval": "1d",
        "data": df.to_dict(orient="records"),
        "columns": list(df.columns),
    }


# ============================================================
# 1. quote.py
# ============================================================

class TestQuote:
    @patch("data.quote.api_client")
    def test_get_quote_normal(self, mock_client):
        """TC-001: 시세 조회 정상 반환."""
        mock_client.get_quote.return_value = MOCK_QUOTE_RAW
        result = get_quote("NVDA")

        assert result is not None
        assert result["ticker"] == "NVDA"
        assert result["price"] == 120.5
        assert result["change"] == 2.2
        assert result["change_percent"] == 1.86
        assert result["source"] == "finnhub"

    @patch("data.quote.api_client")
    def test_get_quote_invalid_ticker(self, mock_client):
        """TC-012: 존재하지 않는 티커 → None."""
        mock_client.get_quote.return_value = None
        result = get_quote("ZZZZZ999")
        assert result is None

    @patch("data.quote.api_client")
    def test_get_quote_api_fail(self, mock_client):
        """TC-019: API 전체 실패 시 None."""
        mock_client.get_quote.return_value = None
        result = get_quote("NVDA")
        assert result is None

    @patch("data.quote.api_client")
    def test_get_quote_calc_change(self, mock_client):
        """change 필드 없을 때 price - previous_close로 자동 계산."""
        mock_client.get_quote.return_value = {
            "source": "yfinance", "ticker": "NVDA",
            "price": 120.5, "previous_close": 118.0,
            "volume": 45000000,
        }
        result = get_quote("NVDA")
        assert result is not None
        assert result["change"] == round(120.5 - 118.0, 4)
        assert result["change_percent"] == round(2.5 / 118.0 * 100, 2)


# ============================================================
# 2. history.py
# ============================================================

class TestHistory:
    @patch("data.history.api_client")
    def test_get_history_1y(self, mock_client):
        """TC-002: 1Y 히스토리 DataFrame 반환."""
        mock_client.get_history.return_value = _make_history_raw(100)
        result = get_history("NVDA", "1Y")

        assert isinstance(result, pd.DataFrame)
        assert len(result) == 100
        for col in ["Date", "Open", "High", "Low", "Close", "Volume"]:
            assert col in result.columns

    @patch("data.history.api_client")
    def test_get_history_has_ma(self, mock_client):
        """TC-003: MA50/MA200 컬럼 포함."""
        mock_client.get_history.return_value = _make_history_raw(100)
        result = get_history("NVDA", "1Y")

        assert "MA50" in result.columns
        assert "MA200" in result.columns
        assert result["MA50"].notna().sum() > 0

    @patch("data.history.api_client")
    def test_get_history_unknown_period(self, mock_client):
        """TC-013: 매핑에 없는 기간 → 기본값 1y로 폴백."""
        mock_client.get_history.return_value = _make_history_raw(100)
        result = get_history("NVDA", "10Y")

        assert isinstance(result, pd.DataFrame)
        # 기본값 ("1y", "1d")로 호출됐는지 확인
        call_args = mock_client.get_history.call_args
        assert call_args.kwargs["period"] == "1y"

    @patch("data.history.api_client")
    def test_get_history_api_fail(self, mock_client):
        """TC-020: API 전체 실패 시 None."""
        mock_client.get_history.return_value = None
        result = get_history("NVDA", "1Y")
        assert result is None


# ============================================================
# 3. fundamentals.py
# ============================================================

class TestFundamentals:
    @patch("data.fundamentals.api_client")
    def test_get_fundamentals_normal(self, mock_client):
        """TC-004: 재무 지표 정상 반환."""
        mock_client.get_fundamentals.return_value = MOCK_FUNDAMENTALS_RAW
        result = get_fundamentals("NVDA")

        assert result is not None
        assert result["pe"] == 35.2
        assert result["eps"] == 4.05
        assert result["sector"] == "Technology"
        assert result["industry"] == "Semiconductors"

    @patch("data.fundamentals.api_client")
    def test_get_fundamentals_force_fallback(self, mock_client):
        """TC-014: force_fallback=True → Finviz 직접 호출."""
        mock_client.finviz.get_fundamentals.return_value = MOCK_FUNDAMENTALS_RAW
        result = get_fundamentals("NVDA", force_fallback=True)

        assert result is not None
        mock_client.finviz.get_fundamentals.assert_called_once_with("NVDA")
        mock_client.get_fundamentals.assert_not_called()

    @patch("data.fundamentals.api_client")
    def test_get_fundamentals_fail(self, mock_client):
        """fundamentals API 실패 시 None."""
        mock_client.get_fundamentals.return_value = None
        result = get_fundamentals("NVDA")
        assert result is None


# ============================================================
# 4. technicals.py
# ============================================================

class TestTechnicals:
    @patch("data.technicals.api_client")
    def test_get_technicals_api(self, mock_client):
        """TC-005: API 기술지표 + 신호 판정."""
        mock_client.get_technicals.return_value = MOCK_TECHNICALS_RAW
        mock_client.get_quote.return_value = {"price": 120.5}

        result = get_technicals("NVDA")

        assert result is not None
        assert result["source"] == "twelvedata"
        assert result["rsi"]["value"] == 62.5
        assert result["rsi"]["signal"] == "neutral"
        assert result["macd"]["signal"] == "bullish"
        assert result["bollinger"]["signal"] in ("bullish", "neutral", "bearish")

    @patch("data.technicals.api_client")
    def test_get_technicals_force_fallback(self, mock_client):
        """TC-015: force_fallback=True → Python 직접 계산."""
        mock_client.get_history.return_value = _make_history_raw(252)

        result = get_technicals("NVDA", force_fallback=True)

        assert result is not None
        assert result["source"] == "python_calc"
        assert result["rsi"] is not None
        assert result["rsi"]["signal"] in ("bullish", "neutral", "bearish")
        assert result["macd"] is not None
        assert result["bollinger"] is not None

    @patch("data.technicals.api_client")
    def test_get_technicals_all_fail(self, mock_client):
        """TC-021: API + 폴백 모두 실패 → None."""
        mock_client.get_technicals.return_value = None
        mock_client.get_history.return_value = None

        result = get_technicals("NVDA")
        assert result is None

    def test_rsi_signal_boundaries(self):
        """TC-022: RSI 신호 판정 경계값."""
        assert _rsi_signal(75) == "bearish"
        assert _rsi_signal(25) == "bullish"
        assert _rsi_signal(50) == "neutral"
        assert _rsi_signal(70) == "bearish"   # 70 이상 → bearish
        assert _rsi_signal(30) == "bullish"   # 30 이하 → bullish
        assert _rsi_signal(31) == "neutral"
        assert _rsi_signal(69) == "neutral"

    def test_macd_signal(self):
        """MACD 신호 판정."""
        sig, _ = _macd_signal(1.5, 1.2, 0.3)
        assert sig == "bullish"
        sig, _ = _macd_signal(-1.5, -1.2, -0.3)
        assert sig == "bearish"

    def test_bbands_signal(self):
        """볼린저밴드 신호 판정."""
        sig, pos = _bbands_signal(131, 130, 110, 120)
        assert sig == "bearish" and pos == "upper"
        sig, pos = _bbands_signal(109, 130, 110, 120)
        assert sig == "bullish" and pos == "lower"
        sig, pos = _bbands_signal(125, 130, 110, 120)
        assert sig == "neutral" and pos == "upper_half"

    def test_ma_signal(self):
        """MA 신호 판정."""
        sig, vs = _ma_signal(120, 100)
        assert sig == "bullish" and "+" in vs
        sig, vs = _ma_signal(80, 100)
        assert sig == "bearish" and "-" in vs


# ============================================================
# 5. indicators.py (Python 직접 계산)
# ============================================================

class TestIndicators:
    def _make_close(self, n=100):
        np.random.seed(42)
        return pd.Series(100 + np.cumsum(np.random.randn(n) * 2))

    def test_calc_rsi(self):
        """TC-006: RSI 계산."""
        close = self._make_close(100)
        result = calc_rsi(close)

        assert isinstance(result, pd.Series)
        assert len(result) == 100
        valid = result.dropna()
        assert len(valid) > 0
        assert valid.between(0, 100).all()

    def test_calc_macd(self):
        """TC-007: MACD 계산."""
        close = self._make_close(100)
        result = calc_macd(close)

        assert result is not None
        assert "macd" in result
        assert "signal" in result
        assert "histogram" in result
        assert isinstance(result["macd"], pd.Series)

    def test_calc_bbands(self):
        """TC-008: 볼린저밴드 계산."""
        close = self._make_close(100)
        result = calc_bbands(close)

        assert result is not None
        assert "upper" in result
        assert "middle" in result
        assert "lower" in result
        # upper > middle > lower (유효 구간)
        u = result["upper"].dropna().iloc[-1]
        m = result["middle"].dropna().iloc[-1]
        l = result["lower"].dropna().iloc[-1]
        assert u > m > l

    def test_calc_rsi_insufficient_data(self):
        """TC-016: 데이터 부족 시 None."""
        short = pd.Series([100, 101, 102, 103, 104])
        assert calc_rsi(short) is None

    def test_calc_macd_insufficient_data(self):
        """TC-016: MACD 데이터 부족."""
        short = pd.Series([100, 101, 102, 103, 104])
        assert calc_macd(short) is None

    def test_calc_bbands_insufficient_data(self):
        """TC-016: 볼린저밴드 데이터 부족."""
        short = pd.Series([100, 101, 102])
        assert calc_bbands(short) is None

    def test_calc_ma(self):
        """이동평균 계산."""
        close = self._make_close(100)
        result = calc_ma(close, period=50)
        assert isinstance(result, pd.Series)
        assert len(result) == 100


# ============================================================
# 6. chart_builder.py
# ============================================================

class TestChartBuilder:
    def _make_chart_df(self):
        df = _make_ohlcv_df(50)
        df["MA50"] = df["Close"].rolling(50, min_periods=1).mean()
        df["MA200"] = df["Close"].rolling(50, min_periods=1).mean()
        return df

    def test_line_chart(self):
        """TC-009: 라인 차트 생성."""
        df = self._make_chart_df()
        fig = build_price_chart(df, chart_type="line")

        assert isinstance(fig, go.Figure)
        assert len(fig.data) >= 1

    def test_candlestick_chart(self):
        """TC-010: 캔들스틱 차트 생성."""
        df = self._make_chart_df()
        fig = build_price_chart(df, chart_type="candlestick")

        assert isinstance(fig, go.Figure)
        assert isinstance(fig.data[0], go.Candlestick)

    def test_empty_df_returns_none(self):
        """TC-017: 빈 DataFrame → None."""
        assert build_price_chart(pd.DataFrame()) is None
        assert build_price_chart(None) is None


# ============================================================
# 7. tooltips.py
# ============================================================

class TestTooltips:
    def test_known_keys(self):
        """TC-011: 등록된 키 조회."""
        pe = get_tooltip("pe")
        assert len(pe) > 0
        assert "주가수익비율" in pe

        rsi = get_tooltip("rsi")
        assert len(rsi) > 0
        assert "상대강도지수" in rsi

    def test_unknown_key(self):
        """TC-018: 존재하지 않는 키 → 빈 문자열."""
        assert get_tooltip("nonexistent_key") == ""

    def test_tooltips_count(self):
        """TOOLTIPS 딕셔너리에 22개 항목 등록."""
        assert len(TOOLTIPS) == 22

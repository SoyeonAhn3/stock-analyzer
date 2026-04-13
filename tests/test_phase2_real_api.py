"""Phase 2 실제 API 테스트 -Quick Look 데이터 수집 계층.

실제 API를 호출하여 데이터 파이프라인 전체를 검증한다.

실행: pytest tests/test_phase2_real_api.py -v -s
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pandas as pd
import plotly.graph_objects as go
import pytest

from data.quote import get_quote, get_premarket
from data.history import get_history
from data.fundamentals import get_fundamentals
from data.technicals import get_technicals
from utils.chart_builder import build_price_chart
from utils.tooltips import TOOLTIPS, get_tooltip
from data.cache import cache

TICKER = "AAPL"


# ============================================================
# 1. quote.py -실제 시세 조회
# ============================================================

class TestQuoteReal:
    def test_get_quote(self):
        """시세 조회 -정상 반환."""
        result = get_quote(TICKER)
        assert result is not None, "get_quote returned None"
        assert result["ticker"] == TICKER
        assert result["price"] > 0
        assert result["volume"] is None or result["volume"] > 0
        assert result["source"] in ("finnhub", "yfinance")
        vol_str = f"{result['volume']:,}" if result['volume'] else "N/A"
        print(f"  quote: ${result['price']}, change={result['change_percent']:+.2f}%, "
              f"vol={vol_str}, source={result['source']}")

    def test_get_quote_has_all_fields(self):
        """시세 결과에 필수 필드 존재."""
        result = get_quote(TICKER)
        assert result is not None
        for key in ["ticker", "price", "change", "change_percent", "volume", "source"]:
            assert key in result, f"missing key: {key}"

    def test_get_quote_invalid_ticker(self):
        """존재하지 않는 티커 → None."""
        result = get_quote("ZZZZZZ999")
        assert result is None
        print(f"  invalid ticker: None (correct)")

    def test_get_premarket(self):
        """장전/장후 시세 -장중이면 None 가능."""
        result = get_premarket(TICKER)
        # 장중에는 pre/post market 데이터가 없을 수 있음
        if result is not None:
            print(f"  premarket: pre=${result.get('pre_market_price')}, "
                  f"post=${result.get('post_market_price')}")
        else:
            print(f"  premarket: None (정상 -장중이거나 데이터 없음)")


# ============================================================
# 2. history.py -실제 히스토리 조회
# ============================================================

class TestHistoryReal:
    def test_get_history_1Y(self):
        """1Y 히스토리 -DataFrame 반환 + OHLCV 컬럼."""
        df = get_history(TICKER, "1Y")
        assert df is not None, "get_history returned None"
        assert isinstance(df, pd.DataFrame)
        assert len(df) > 200  # 1년 ≈ 252 거래일
        for col in ["Date", "Open", "High", "Low", "Close", "Volume"]:
            assert col in df.columns, f"missing column: {col}"
        print(f"  1Y history: {len(df)} rows, {df['Date'].iloc[0].date()} ~ {df['Date'].iloc[-1].date()}")

    def test_get_history_has_ma(self):
        """1Y 히스토리에 MA50/MA200 컬럼 포함."""
        df = get_history(TICKER, "1Y")
        assert df is not None
        assert "MA50" in df.columns
        assert "MA200" in df.columns
        ma50_last = df["MA50"].iloc[-1]
        ma200_last = df["MA200"].iloc[-1]
        print(f"  MA50={ma50_last:.2f}, MA200={ma200_last:.2f}")

    def test_get_history_1M(self):
        """1M 히스토리."""
        df = get_history(TICKER, "1M")
        assert df is not None
        assert len(df) >= 15  # 한 달 ≈ 20~22 거래일
        print(f"  1M history: {len(df)} rows")

    def test_get_history_1W(self):
        """1W 히스토리 (15분봉)."""
        df = get_history(TICKER, "1W")
        assert df is not None
        assert len(df) > 0
        print(f"  1W history: {len(df)} rows (intraday)")

    def test_get_history_5Y(self):
        """5Y 히스토리 (주봉)."""
        df = get_history(TICKER, "5Y")
        assert df is not None
        assert len(df) > 200
        print(f"  5Y history: {len(df)} rows (weekly)")

    def test_get_history_all_periods(self):
        """모든 기간 매핑이 정상 동작."""
        for period in ["1W", "1M", "3M", "6M", "1Y", "5Y"]:
            df = get_history(TICKER, period)
            assert df is not None, f"get_history failed for period={period}"
            assert len(df) > 0, f"empty DataFrame for period={period}"
        print(f"  all periods (1W~5Y): OK")


# ============================================================
# 3. fundamentals.py -실제 재무 지표
# ============================================================

class TestFundamentalsReal:
    def test_get_fundamentals(self):
        """재무 지표 -정상 반환."""
        result = get_fundamentals(TICKER)
        assert result is not None, "get_fundamentals returned None"
        assert result["ticker"] == TICKER
        assert result["sector"] is not None
        assert result["pe"] is not None or result["market_cap"] is not None
        print(f"  fundamentals: sector={result['sector']}, PE={result['pe']}, "
              f"EPS={result['eps']}, source={result['source']}")

    def test_get_fundamentals_has_key_fields(self):
        """재무 결과에 Phase 5 비교 모드용 필수 필드 존재."""
        result = get_fundamentals(TICKER)
        assert result is not None
        # sector, industry는 Phase 5 Compare Mode에서 필수
        assert result["sector"] is not None, "sector is None"
        assert result["industry"] is not None, "industry is None"
        print(f"  sector={result['sector']}, industry={result['industry']}")

    def test_get_fundamentals_force_fallback(self):
        """force_fallback=True -> Finviz 직접 호출."""
        result = get_fundamentals(TICKER, force_fallback=True)
        assert result is not None, "Finviz get_fundamentals returned None"
        assert result["source"] == "finviz"
        print(f"  Finviz fallback: sector={result['sector']}, PE={result['pe']}")


# ============================================================
# 4. technicals.py -실제 기술지표
# ============================================================

class TestTechnicalsReal:
    def test_get_technicals_api(self):
        """기술지표 -Twelve Data API 경유."""
        result = get_technicals(TICKER)
        assert result is not None, "get_technicals returned None"
        assert result["source"] in ("twelvedata", "python_calc")
        print(f"  technicals source: {result['source']}")

        # RSI
        if result["rsi"]:
            rsi = result["rsi"]
            assert 0 <= rsi["value"] <= 100
            assert rsi["signal"] in ("bullish", "neutral", "bearish")
            print(f"  RSI: {rsi['value']} ({rsi['signal']})")

        # MACD
        if result["macd"]:
            assert result["macd"]["signal"] in ("bullish", "neutral", "bearish")
            print(f"  MACD: {result['macd']['signal']} -{result['macd']['detail']}")

        # 볼린저밴드
        if result["bollinger"]:
            assert result["bollinger"]["signal"] in ("bullish", "neutral", "bearish")
            print(f"  Bollinger: {result['bollinger']['position']} ({result['bollinger']['signal']})")

        # MA50, MA200
        if result["ma50"]:
            print(f"  MA50: {result['ma50']['vs_price']} ({result['ma50']['signal']})")
        if result["ma200"]:
            print(f"  MA200: {result['ma200']['vs_price']} ({result['ma200']['signal']})")

    def test_get_technicals_force_fallback(self):
        """force_fallback=True → Python 직접 계산."""
        result = get_technicals(TICKER, force_fallback=True)
        assert result is not None, "Python fallback calculation failed"
        assert result["source"] == "python_calc"
        assert result["rsi"] is not None
        assert result["macd"] is not None
        assert result["bollinger"] is not None
        print(f"  python_calc: RSI={result['rsi']['value']}, "
              f"MACD={result['macd']['signal']}, "
              f"Bollinger={result['bollinger']['position']}")

    def test_technicals_signal_consistency(self):
        """API vs Python 계산 결과 신호가 크게 다르지 않은지 확인."""
        api_result = get_technicals(TICKER)
        cache.clear()
        py_result = get_technicals(TICKER, force_fallback=True)

        if api_result and py_result and api_result["rsi"] and py_result["rsi"]:
            api_rsi = api_result["rsi"]["value"]
            py_rsi = py_result["rsi"]["value"]
            diff = abs(api_rsi - py_rsi)
            print(f"  RSI diff: API={api_rsi} vs Python={py_rsi} (diff={diff:.1f})")
            # 15 이내 차이면 합리적 (데이터 기간/소스 차이)
            assert diff < 15, f"RSI diff too large: {diff}"


# ============================================================
# 5. chart_builder.py -실제 데이터로 차트 생성
# ============================================================

class TestChartBuilderReal:
    def test_line_chart_from_real_data(self):
        """실제 히스토리 데이터로 라인 차트 생성."""
        df = get_history(TICKER, "1Y")
        assert df is not None
        fig = build_price_chart(df, chart_type="line")
        assert isinstance(fig, go.Figure)
        assert len(fig.data) >= 1
        print(f"  line chart: {len(fig.data)} traces")

    def test_candlestick_chart_from_real_data(self):
        """실제 히스토리 데이터로 캔들스틱 차트 생성."""
        df = get_history(TICKER, "1Y")
        assert df is not None
        fig = build_price_chart(df, chart_type="candlestick")
        assert isinstance(fig, go.Figure)
        assert isinstance(fig.data[0], go.Candlestick)
        print(f"  candlestick chart: {len(fig.data)} traces")


# ============================================================
# 6. 통합 -Quick Look 전체 파이프라인
# ============================================================

class TestQuickLookPipelineReal:
    def test_full_pipeline(self):
        """Quick Look 전체 파이프라인 -시세+히스토리+재무+기술지표+차트."""
        cache.clear()

        # 1. 시세
        quote = get_quote(TICKER)
        assert quote is not None, "quote failed"

        # 2. 히스토리
        history = get_history(TICKER, "1Y")
        assert history is not None, "history failed"

        # 3. 재무
        fundamentals = get_fundamentals(TICKER)
        assert fundamentals is not None, "fundamentals failed"

        # 4. 기술지표
        technicals = get_technicals(TICKER)
        assert technicals is not None, "technicals failed"

        # 5. 차트
        chart = build_price_chart(history, chart_type="candlestick")
        assert chart is not None, "chart failed"

        # Quick Look dict 조립 (Phase 3 Agent에 전달하는 형태)
        quick_look_data = {
            "ticker": TICKER,
            "quote": quote,
            "fundamentals": fundamentals,
            "technicals": technicals,
        }

        assert quick_look_data["quote"]["price"] > 0
        assert quick_look_data["fundamentals"]["sector"] is not None
        assert quick_look_data["technicals"]["rsi"] is not None

        print(f"\n  === Quick Look Pipeline Complete ===")
        print(f"  Ticker: {TICKER}")
        print(f"  Price: ${quote['price']} ({quote['change_percent']:+.2f}%)")
        print(f"  Sector: {fundamentals['sector']} / {fundamentals['industry']}")
        print(f"  PE: {fundamentals['pe']}, EPS: {fundamentals['eps']}")
        print(f"  RSI: {technicals['rsi']['value']} ({technicals['rsi']['signal']})")
        print(f"  History: {len(history)} rows")
        print(f"  Chart: OK ({len(chart.data)} traces)")
        print(f"  Sources: quote={quote['source']}, "
              f"fundamentals={fundamentals['source']}, "
              f"technicals={technicals['source']}")

"""기술적 지표 모듈 — RSI, MACD, 볼린저밴드, MA, 거래량 + 신호 판정.

사용법:
    from data.technicals import get_technicals
    t = get_technicals("NVDA")
    # {"rsi": {"value": 62, "signal": "neutral"}, "macd": {...}, ...}
"""

import logging
from typing import Any, Optional

import pandas as pd

from data.api_client import api_client
from utils.indicators import calc_rsi, calc_macd, calc_bbands

logger = logging.getLogger(__name__)


def _rsi_signal(value: float) -> str:
    if value >= 70:
        return "bearish"
    if value <= 30:
        return "bullish"
    return "neutral"


def _macd_signal(macd_val: float, signal_val: float, histogram: float) -> tuple[str, str]:
    if histogram > 0 and macd_val > signal_val:
        signal = "bullish"
        detail = "MACD가 시그널 위 (상승 추세)"
    elif histogram < 0 and macd_val < signal_val:
        signal = "bearish"
        detail = "MACD가 시그널 아래 (하락 추세)"
    else:
        signal = "neutral"
        detail = "MACD 중립"
    return signal, detail


def _bbands_signal(price: float, upper: float, lower: float, middle: float) -> tuple[str, str]:
    if price >= upper:
        return "bearish", "upper"
    if price <= lower:
        return "bullish", "lower"
    if price >= middle:
        return "neutral", "upper_half"
    return "neutral", "lower_half"


def _ma_signal(price: float, ma_value: float) -> tuple[str, str]:
    if ma_value == 0:
        return "neutral", "0.0%"
    diff_pct = round((price - ma_value) / ma_value * 100, 1)
    prefix = "+" if diff_pct > 0 else ""
    if diff_pct > 0:
        signal = "bullish"
    elif diff_pct < 0:
        signal = "bearish"
    else:
        signal = "neutral"
    return signal, f"{prefix}{diff_pct}%"


def get_technicals(ticker: str, force_fallback: bool = False) -> Optional[dict[str, Any]]:
    """기술적 지표 종합 조회. Twelve Data → Python 직접 계산 폴백.

    Args:
        ticker: 종목 코드
        force_fallback: True면 API 건너뛰고 Python 직접 계산

    Returns:
        {
            "ticker", "rsi", "macd", "bollinger", "ma50", "ma200",
            "volume", "source"
        }
        실패 시 None.
    """
    if not force_fallback:
        result = _try_api(ticker)
        if result is not None:
            return result

    # 폴백: yfinance 히스토리로 Python 직접 계산
    return _calc_from_history(ticker)


def _try_api(ticker: str) -> Optional[dict[str, Any]]:
    """Twelve Data API로 기술지표 조회."""
    raw = api_client.get_technicals(ticker)
    if raw is None:
        return None

    # 현재가 필요 (MA 대비 비교용)
    quote = api_client.get_quote(ticker)
    price = quote["price"] if quote else 0

    result = {"ticker": ticker, "source": "twelvedata"}

    # RSI
    rsi_data = raw.get("rsi")
    if rsi_data and rsi_data.get("values"):
        rsi_val = rsi_data["values"][0]["rsi"]
        result["rsi"] = {"value": round(rsi_val, 1), "signal": _rsi_signal(rsi_val)}
    else:
        result["rsi"] = None

    # MACD
    macd_data = raw.get("macd")
    if macd_data and macd_data.get("values"):
        mv = macd_data["values"][0]
        sig, detail = _macd_signal(mv["macd"], mv["signal"], mv["histogram"])
        result["macd"] = {
            "histogram": round(float(mv["histogram"]), 2),
            "signal": sig,
            "detail": detail,
        }
    else:
        result["macd"] = None

    # 볼린저밴드
    bb_data = raw.get("bbands")
    if bb_data and bb_data.get("values") and price:
        bv = bb_data["values"][0]
        sig, pos = _bbands_signal(price, bv["upper"], bv["lower"], bv["middle"])
        result["bollinger"] = {
            "upper": round(float(bv["upper"]), 2),
            "middle": round(float(bv["middle"]), 2),
            "lower": round(float(bv["lower"]), 2),
            "position": pos,
            "signal": sig,
        }
    else:
        result["bollinger"] = None

    # MA50
    ma50_data = raw.get("ma50")
    if ma50_data and ma50_data.get("values") and price:
        ma_val = ma50_data["values"][0]["ma"]
        sig, vs = _ma_signal(price, ma_val)
        result["ma50"] = {"value": ma_val, "vs_price": vs, "signal": sig}
    else:
        result["ma50"] = None

    # MA200
    ma200_data = raw.get("ma200")
    if ma200_data and ma200_data.get("values") and price:
        ma_val = ma200_data["values"][0]["ma"]
        sig, vs = _ma_signal(price, ma_val)
        result["ma200"] = {"value": ma_val, "vs_price": vs, "signal": sig}
    else:
        result["ma200"] = None

    result["volume"] = None  # API 폴백에서는 거래량 추이 생략
    return result


def _calc_from_history(ticker: str) -> Optional[dict[str, Any]]:
    """yfinance 히스토리 데이터로 기술지표 직접 계산."""
    raw = api_client.get_history(ticker, period="1y", interval="1d")
    if raw is None or not raw.get("data"):
        return None

    try:
        df = pd.DataFrame(raw["data"])

        # 컬럼명 정규화
        col_lower = {c: c.lower() for c in df.columns}
        df = df.rename(columns=col_lower)
        if "close" not in df.columns:
            return None

        close = df["close"].astype(float)
        price = close.iloc[-1]

        result = {"ticker": ticker, "source": "python_calc"}

        # RSI
        rsi_series = calc_rsi(close)
        if rsi_series is not None:
            rsi_val = rsi_series.dropna().iloc[-1]
            result["rsi"] = {"value": round(float(rsi_val), 1), "signal": _rsi_signal(rsi_val)}
        else:
            result["rsi"] = None

        # MACD
        macd_data = calc_macd(close)
        if macd_data is not None:
            m = float(macd_data["macd"].dropna().iloc[-1])
            s = float(macd_data["signal"].dropna().iloc[-1])
            h = float(macd_data["histogram"].dropna().iloc[-1])
            sig, detail = _macd_signal(m, s, h)
            result["macd"] = {
                "histogram": round(h, 2),
                "signal": sig,
                "detail": detail,
            }
        else:
            result["macd"] = None

        # 볼린저밴드
        bb_data = calc_bbands(close)
        if bb_data is not None:
            upper = float(bb_data["upper"].dropna().iloc[-1])
            lower = float(bb_data["lower"].dropna().iloc[-1])
            middle = float(bb_data["middle"].dropna().iloc[-1])
            sig, pos = _bbands_signal(price, upper, lower, middle)
            result["bollinger"] = {
                "upper": round(upper, 2),
                "middle": round(middle, 2),
                "lower": round(lower, 2),
                "position": pos,
                "signal": sig,
            }
        else:
            result["bollinger"] = None

        # MA50
        if len(close) >= 50:
            ma50_val = round(float(close.rolling(50).mean().iloc[-1]), 2)
            sig, vs = _ma_signal(price, ma50_val)
            result["ma50"] = {"value": ma50_val, "vs_price": vs, "signal": sig}
        else:
            result["ma50"] = None

        # MA200
        if len(close) >= 200:
            ma200_val = round(float(close.rolling(200).mean().iloc[-1]), 2)
            sig, vs = _ma_signal(price, ma200_val)
            result["ma200"] = {"value": ma200_val, "vs_price": vs, "signal": sig}
        else:
            result["ma200"] = None

        # 거래량 추이 (20일 평균 대비)
        if "volume" in df.columns and len(df) >= 20:
            vol = df["volume"].astype(float)
            avg_20d = vol.tail(20).mean()
            latest_vol = vol.iloc[-1]
            if avg_20d > 0:
                vol_diff_pct = round((latest_vol - avg_20d) / avg_20d * 100, 1)
                prefix = "+" if vol_diff_pct > 0 else ""
                result["volume"] = {
                    "vs_20d_avg": f"{prefix}{vol_diff_pct}%",
                    "signal": "neutral",
                }
            else:
                result["volume"] = None
        else:
            result["volume"] = None

        return result

    except Exception as e:
        logger.warning("_calc_from_history failed for %s: %s", ticker, e)
        return None

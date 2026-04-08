"""기술지표 Python 직접 계산 — Twelve Data API 폴백용.

yfinance 종가 데이터로 RSI, MACD, 볼린저밴드를 직접 계산한다.
Twelve Data API를 못 쓸 때 대체 경로로 사용.

사용법:
    from utils.indicators import calc_rsi, calc_macd, calc_bbands, calc_ma
    rsi_values = calc_rsi(close_prices)
"""

import logging
from typing import Optional

import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)


def calc_rsi(close: pd.Series, period: int = 14) -> Optional[pd.Series]:
    """RSI 계산.

    RSI = 100 - 100 / (1 + RS)
    RS = 평균상승 / 평균하락
    """
    if close is None or len(close) < period + 1:
        return None

    delta = close.diff()
    gain = delta.where(delta > 0, 0.0)
    loss = (-delta).where(delta < 0, 0.0)

    avg_gain = gain.rolling(window=period, min_periods=period).mean()
    avg_loss = loss.rolling(window=period, min_periods=period).mean()

    # Wilder's smoothing 적용
    for i in range(period, len(close)):
        avg_gain.iloc[i] = (avg_gain.iloc[i - 1] * (period - 1) + gain.iloc[i]) / period
        avg_loss.iloc[i] = (avg_loss.iloc[i - 1] * (period - 1) + loss.iloc[i]) / period

    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    return rsi.round(2)


def calc_macd(close: pd.Series, fast: int = 12, slow: int = 26, signal: int = 9) -> Optional[dict[str, pd.Series]]:
    """MACD 계산.

    MACD Line = EMA(fast) - EMA(slow)
    Signal Line = EMA(MACD, signal)
    Histogram = MACD - Signal
    """
    if close is None or len(close) < slow + signal:
        return None

    ema_fast = close.ewm(span=fast, adjust=False).mean()
    ema_slow = close.ewm(span=slow, adjust=False).mean()
    macd_line = ema_fast - ema_slow
    signal_line = macd_line.ewm(span=signal, adjust=False).mean()
    histogram = macd_line - signal_line

    return {
        "macd": macd_line.round(4),
        "signal": signal_line.round(4),
        "histogram": histogram.round(4),
    }


def calc_bbands(close: pd.Series, period: int = 20, std_dev: float = 2.0) -> Optional[dict[str, pd.Series]]:
    """볼린저밴드 계산.

    Middle = SMA(period)
    Upper = Middle + std_dev * StdDev
    Lower = Middle - std_dev * StdDev
    """
    if close is None or len(close) < period:
        return None

    middle = close.rolling(window=period).mean()
    std = close.rolling(window=period).std()
    upper = middle + std_dev * std
    lower = middle - std_dev * std

    return {
        "upper": upper.round(2),
        "middle": middle.round(2),
        "lower": lower.round(2),
    }


def calc_ma(close: pd.Series, period: int = 50) -> Optional[pd.Series]:
    """단순 이동평균 계산."""
    if close is None or len(close) < period:
        return None
    return close.rolling(window=period, min_periods=1).mean().round(2)

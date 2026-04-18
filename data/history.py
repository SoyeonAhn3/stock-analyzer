"""주가 히스토리 모듈 — 기간별 OHLCV + 이동평균.

사용법:
    from data.history import get_history
    df = get_history("NVDA", "1Y")
    # DataFrame: Date, Open, High, Low, Close, Volume, MA50, MA200
"""

import logging
from typing import Optional

import pandas as pd

from data.api_client import api_client

logger = logging.getLogger(__name__)

# 사용자 기간 → yfinance period 매핑
PERIOD_MAP = {
    "1D": ("1d", "5m"),
"1M": ("1mo", "1d"),
    "3M": ("3mo", "1d"),
    "6M": ("6mo", "1d"),
    "1Y": ("1y", "1d"),
    "5Y": ("5y", "1wk"),
}


def get_history(ticker: str, period: str = "1Y") -> Optional[pd.DataFrame]:
    """주가 히스토리 조회.

    Args:
        ticker: 종목 코드
        period: '1W', '1M', '3M', '6M', '1Y', '5Y'

    Returns:
        DataFrame (Date, Open, High, Low, Close, Volume, MA50, MA200)
        실패 시 None.
    """
    yf_period, yf_interval = PERIOD_MAP.get(period, ("1y", "1d"))

    raw = api_client.get_history(ticker, period=yf_period, interval=yf_interval)
    if raw is None or not raw.get("data"):
        return None

    try:
        df = pd.DataFrame(raw["data"])

        # 컬럼명 정규화
        col_map = {}
        for col in df.columns:
            lower = col.lower()
            if lower == "date" or lower == "datetime":
                col_map[col] = "Date"
            elif lower == "open":
                col_map[col] = "Open"
            elif lower == "high":
                col_map[col] = "High"
            elif lower == "low":
                col_map[col] = "Low"
            elif lower == "close":
                col_map[col] = "Close"
            elif lower == "volume":
                col_map[col] = "Volume"
        df = df.rename(columns=col_map)

        if "Date" in df.columns:
            df["Date"] = pd.to_datetime(df["Date"])
            df = df.sort_values("Date").reset_index(drop=True)

        # 이동평균 추가 (일봉일 때만)
        if yf_interval == "1d" and "Close" in df.columns:
            df["MA50"] = df["Close"].rolling(window=50, min_periods=1).mean().round(2)
            df["MA200"] = df["Close"].rolling(window=200, min_periods=1).mean().round(2)
        elif yf_interval == "1wk" and "Close" in df.columns:
            # 주봉: 10주/40주 이동평균 (≈50일/200일)
            df["MA50"] = df["Close"].rolling(window=10, min_periods=1).mean().round(2)
            df["MA200"] = df["Close"].rolling(window=40, min_periods=1).mean().round(2)

        return df

    except Exception as e:
        logger.warning("get_history DataFrame 변환 실패 for %s: %s", ticker, e)
        return None

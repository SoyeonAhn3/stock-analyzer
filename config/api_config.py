"""API 설정 모듈 — 키 로딩, 엔드포인트, 타임아웃, 일일 한도."""

import os
from dotenv import load_dotenv

load_dotenv()

# ---------------------------------------------------------------------------
# API Keys
# ---------------------------------------------------------------------------
FINNHUB_API_KEY = os.getenv("FINNHUB_API_KEY", "")
TWELVEDATA_API_KEY = os.getenv("TWELVEDATA_API_KEY", "")
FMP_API_KEY = os.getenv("FMP_API_KEY", "")
FRED_API_KEY = os.getenv("FRED_API_KEY", "")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")

# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------
FINNHUB_BASE_URL = "https://finnhub.io/api/v1"
TWELVEDATA_BASE_URL = "https://api.twelvedata.com"
FMP_BASE_URL = "https://financialmodelingprep.com/api/v3"
FRED_BASE_URL = "https://api.stlouisfed.org/fred"

# ---------------------------------------------------------------------------
# Timeouts & Retries
# ---------------------------------------------------------------------------
API_TIMEOUT = 15  # seconds
MAX_RETRIES = 1

# ---------------------------------------------------------------------------
# Daily Limits
# ---------------------------------------------------------------------------
DAILY_LIMITS = {
    "finnhub": 60,        # per minute
    "twelvedata": 800,    # per day
    "fmp": 250,           # per day
    "fred": None,         # unlimited
    "ai_agent": 100,      # per day
}

# ---------------------------------------------------------------------------
# Cache TTL (seconds)
# ---------------------------------------------------------------------------
CACHE_TTL = {
    "quote": 60,           # 1 min — 시세는 실시간 변동이므로 짧게
    "quick_look": 300,     # 5 min — 재무/차트/기술지표
    "ai_result": 3600,     # 1 hour
    "sector": 21600,       # 6 hours
    "market": 60,          # 1 min — 시장 지수
}

# ---------------------------------------------------------------------------
# Fallback Priority Table
# ---------------------------------------------------------------------------
FALLBACK_PRIORITY = {
    "quote":           ["finnhub", "yfinance"],
    "history":         ["yfinance", "twelvedata"],
    "fundamentals":    ["yfinance", "fmp", "finviz"],
    "technicals":      ["twelvedata", "python_calc"],
    "news":            ["finnhub"],
    "analyst":         ["finnhub"],
    "sector_screen":   ["finviz", "fmp"],
    "sector_pe":       ["finviz", "fmp"],
    "macro":           ["fred"],
}

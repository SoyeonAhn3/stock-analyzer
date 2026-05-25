"""API 설정 모듈 — 키 로딩, 엔드포인트, 타임아웃, 일일 한도."""

import os
import ssl
import urllib3
import requests as _requests

from dotenv import load_dotenv

load_dotenv()

# ---------------------------------------------------------------------------
# SSL — 사내 프록시(자체 서명 인증서) 환경에서 SSL 검증 비활성화
# ---------------------------------------------------------------------------
SSL_VERIFY = os.getenv("SSL_VERIFY", "false").lower() in ("true", "1", "yes")

if not SSL_VERIFY:
    # requests / urllib3
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

    # curl_cffi (yfinance) — 강제 덮어쓰기 (setdefault는 기존 값 유지)
    os.environ["CURL_CA_BUNDLE"] = ""
    os.environ["REQUESTS_CA_BUNDLE"] = ""

    # stdlib ssl
    ssl._create_default_https_context = ssl._create_unverified_context

    # requests.Session 글로벌 패치 — finvizfinance 등 서드파티 라이브러리 대응
    _orig_session_init = _requests.Session.__init__

    def _patched_session_init(self, *args, **kwargs):
        _orig_session_init(self, *args, **kwargs)
        self.verify = False

    _requests.Session.__init__ = _patched_session_init

    # curl_cffi 세션 패치 — yfinance 대응
    try:
        import curl_cffi.requests as _curl_requests

        _orig_curl_init = _curl_requests.Session.__init__

        def _patched_curl_init(self, *args, **kwargs):
            kwargs.setdefault("verify", False)
            _orig_curl_init(self, *args, **kwargs)

        _curl_requests.Session.__init__ = _patched_curl_init
    except ImportError:
        pass

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
    "quote": 300,          # 5 min — 실시간 트레이딩이 아니므로 여유 있게
    "quick_look": 600,     # 10 min — 재무/차트/기술지표
    "ai_result": 3600,     # 1 hour
    "sector": 21600,       # 6 hours
    "market": 300,         # 5 min — 시장 지수
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

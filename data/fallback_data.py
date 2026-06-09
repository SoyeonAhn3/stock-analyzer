"""사내망 차단 등 외부 데이터 소스 실패 시 사용하는 정적 더미 데이터.

회사 방화벽(KB Wiper)이 finviz/finnhub/yahoo finance를 차단하면
backend/routers/market.py 가 이 샘플 데이터를 반환해 UI가 깨지지 않게 한다.
실제 시세가 아니며 화면 구성/개발 확인용이다.
"""

from typing import Any

# /api/market/indices — get_market_indices() 와 동일한 형태
FALLBACK_INDICES: list[dict[str, Any]] = [
    {"symbol": "S&P 500", "yf_symbol": "^GSPC", "price": 5200.50, "change": 42.30, "change_percent": 0.82},
    {"symbol": "NASDAQ", "yf_symbol": "^IXIC", "price": 16300.20, "change": 177.40, "change_percent": 1.10},
    {"symbol": "DOW", "yf_symbol": "^DJI", "price": 39100.80, "change": -85.20, "change_percent": -0.22},
    {"symbol": "BTC", "yf_symbol": "BTC-USD", "price": 67200.00, "change": 1450.00, "change_percent": 2.21},
    {"symbol": "ETH", "yf_symbol": "ETH-USD", "price": 3520.00, "change": -48.00, "change_percent": -1.35},
    {"symbol": "VIX", "yf_symbol": "^VIX", "price": 13.45, "change": -0.62, "change_percent": -4.41},
]

# /api/market/movers — get_top_movers() 와 동일한 형태
FALLBACK_MOVERS: dict[str, Any] = {
    "gainers": [
        {"ticker": "NVDA", "name": "NVIDIA Corp.", "change_pct": 6.84, "price": 121.40, "volume": 412000000},
        {"ticker": "AMD", "name": "Advanced Micro Devices", "change_pct": 5.12, "price": 168.30, "volume": 88000000},
        {"ticker": "TSLA", "name": "Tesla Inc.", "change_pct": 4.37, "price": 248.90, "volume": 134000000},
        {"ticker": "AVGO", "name": "Broadcom Inc.", "change_pct": 3.95, "price": 1620.00, "volume": 4200000},
        {"ticker": "META", "name": "Meta Platforms", "change_pct": 3.21, "price": 502.10, "volume": 19000000},
    ],
    "losers": [
        {"ticker": "INTC", "name": "Intel Corp.", "change_pct": -4.88, "price": 30.20, "volume": 61000000},
        {"ticker": "PFE", "name": "Pfizer Inc.", "change_pct": -3.74, "price": 27.85, "volume": 42000000},
        {"ticker": "BA", "name": "Boeing Co.", "change_pct": -3.10, "price": 178.40, "volume": 9800000},
        {"ticker": "NKE", "name": "Nike Inc.", "change_pct": -2.66, "price": 92.30, "volume": 12000000},
        {"ticker": "DIS", "name": "Walt Disney Co.", "change_pct": -2.05, "price": 101.70, "volume": 11000000},
    ],
}

# /api/market/news — get_market_news() 와 동일한 형태 (datetime: epoch seconds)
FALLBACK_NEWS: list[dict[str, Any]] = [
    {"headline": "[샘플] Fed holds rates steady, signals possible cut later this year",
     "source": "Sample Wire", "url": "https://example.com/news/1", "datetime": 1717900000},
    {"headline": "[샘플] Tech megacaps rally as AI spending forecasts climb",
     "source": "Sample Wire", "url": "https://example.com/news/2", "datetime": 1717890000},
    {"headline": "[샘플] Oil prices ease on demand concerns ahead of OPEC meeting",
     "source": "Sample Wire", "url": "https://example.com/news/3", "datetime": 1717880000},
    {"headline": "[샘플] Treasury yields dip after softer-than-expected jobs data",
     "source": "Sample Wire", "url": "https://example.com/news/4", "datetime": 1717870000},
    {"headline": "[샘플] Dollar steadies as traders weigh global rate paths",
     "source": "Sample Wire", "url": "https://example.com/news/5", "datetime": 1717860000},
]

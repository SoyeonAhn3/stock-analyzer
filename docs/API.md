# API Reference

Base URL: `http://localhost:8000/api`

## Health Check

| Method | Endpoint | Description |
|---|---|---|
| GET | `/` | Server health check |

**Response:**
```json
{"status": "ok", "service": "AI Stock Analyzer API"}
```

---

## Quote

| Method | Endpoint | Description |
|---|---|---|
| GET | `/api/quote/{ticker}` | Current stock quote |
| GET | `/api/fundamentals/{ticker}` | Financial metrics (PE, EPS, Market Cap, etc.) |
| GET | `/api/technicals/{ticker}` | Technical indicators (RSI, MACD, Bollinger, MA) |
| GET | `/api/history/{ticker}?period={period}` | Price history (OHLCV + MA) |
| GET | `/api/premarket/{ticker}` | Pre-market / after-hours data |

**History period options:** `1D`, `1W`, `1M`, `3M`, `6M`, `1Y` (default), `5Y`

### Example

```
GET /api/quote/NVDA
```

```json
{
  "ticker": "NVDA",
  "price": 135.42,
  "change": 2.15,
  "change_pct": 1.61,
  "volume": 45230100,
  ...
}
```

---

## Market

| Method | Endpoint | Description |
|---|---|---|
| GET | `/api/market/indices` | Major market indices (SPY, QQQ, DIA, BTC, ETH, VIX) |
| GET | `/api/market/movers` | Top 5 gainers + Top 5 losers |
| GET | `/api/market/news?limit={n}` | Market news headlines (default: 5) |

---

## AI Analysis

| Method | Endpoint | Description |
|---|---|---|
| POST | `/api/analysis/{ticker}?force={bool}` | Run 5-agent AI deep analysis (1-2 min) |
| GET | `/api/analysis/{ticker}/cache` | Get cached analysis result (no AI call) |

**POST /api/analysis/{ticker}**

Collects Quick Look data, then runs the 5-agent pipeline (News → Data → Macro → Cross-Validation → Analyst). Results are cached for 24 hours.

- `force=true`: Skip cache, re-run analysis
- `force=false` (default): Return cached result if available

### Response structure

```json
{
  "ticker": "NVDA",
  "agent_results": {
    "news": { "sentiment": "positive", "score": 0.72, ... },
    "data": { "assessment": "strong", ... },
    "macro": { "impact": "favorable", ... }
  },
  "agent_status": {
    "news": "success",
    "data": "success",
    "macro": "success"
  },
  "cross_validation": { "consensus": true, ... },
  "analyst": {
    "verdict": "BUY",
    "confidence": "high",
    "rationale": "..."
  },
  "errors": []
}
```

---

## Sector Screening

| Method | Endpoint | Description |
|---|---|---|
| POST | `/api/sector/{name}` | Run AI sector/theme screening (2-3 min) |
| GET | `/api/themes` | List all themes |
| POST | `/api/themes` | Create a new theme |
| DELETE | `/api/themes/{name}` | Delete a theme |

### Create theme request body

```json
{
  "name": "ev_battery",
  "tickers": ["TSLA", "RIVN", "LCID", "QS"],
  "preset": "mid_growth"
}
```

**Available presets:** `large_stable`, `mid_growth`, `early_growth`, `value`

---

## Compare

| Method | Endpoint | Description |
|---|---|---|
| POST | `/api/compare` | Compare 2-3 tickers (data only) |
| POST | `/api/compare/analyze` | AI comparison analysis |

### Request body

```json
{
  "tickers": ["NVDA", "AMD", "INTC"]
}
```

Automatically detects comparison type (`same_sector` or `cross_sector`) and adjusts analysis accordingly.

---

## Watchlist

| Method | Endpoint | Description |
|---|---|---|
| GET | `/api/watchlist` | Get watchlist tickers + quotes |
| POST | `/api/watchlist/{ticker}` | Add ticker to watchlist |
| DELETE | `/api/watchlist/{ticker}` | Remove ticker from watchlist |

---

## Guide

| Method | Endpoint | Description |
|---|---|---|
| GET | `/api/guide/categories` | List guide categories |
| GET | `/api/guide/{category}` | List topics in a category |
| GET | `/api/guide/{category}/{index}` | Get topic detail |

---

## Search

| Method | Endpoint | Description |
|---|---|---|
| GET | `/api/search?q={query}&limit={n}` | Ticker/company name autocomplete (default limit: 8, max: 20) |

---

## Alerts

| Method | Endpoint | Description |
|---|---|---|
| POST | `/api/alerts` | Create price alert |
| GET | `/api/alerts` | List active alerts |
| GET | `/api/alerts/triggered` | Check triggered alerts (checks current price) |
| DELETE | `/api/alerts/{alert_id}` | Delete an alert |

### Create alert request body

```json
{
  "ticker": "AAPL",
  "target_price": 200.00,
  "direction": "above"
}
```

**Direction options:** `above`, `below`

---

## Error Responses

All endpoints return standard HTTP error codes:

| Status | Meaning |
|---|---|
| 404 | Resource not found (invalid ticker, missing cache, etc.) |
| 422 | Validation error (invalid input) |
| 500 | Internal server error (agent failure, etc.) |
| 503 | Service temporarily unavailable (external API down) |

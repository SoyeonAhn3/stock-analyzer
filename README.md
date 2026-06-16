🌐 [한국어](./README_ko.md) | [English](./README.md)

# QuantAI — AI Stock Analyzer

[![Live Demo](https://img.shields.io/badge/Live%20Demo-QuantAI-blue?style=for-the-badge&logo=netlify)](https://stock-analyzer-ai.netlify.app/)

> Multi-agent US stock analysis system that aggregates real-time data from 6 financial APIs and delivers AI-powered buy/hold/sell recommendations through a 5-agent pipeline with cross-validation.

## Overview

Stock research is fragmented across dozens of platforms, and interpreting raw financial data is a barrier for many investors. QuantAI consolidates real-time quotes, charts, fundamentals, technicals, and macro indicators into a single dashboard, then runs 5 specialized AI agents in parallel to cross-validate and produce an actionable verdict. Built as a portfolio/demo project.

### Demo

https://github.com/user-attachments/assets/42a6e030-33c8-4f04-b49e-dd72c07ae4ab

## Manual

| Language | Link |
|---|---|
| English | [User Manual](./manuals/20260512_QuantAI_Manual.md) |

## Table of Contents

- [How It Works](#how-it-works)
- [Tech Stack](#tech-stack)
- [AI Components](#ai-components)
- [Quick Start](#quick-start)
- [Project Structure](#project-structure)
- [Tests](#tests)
- [Documentation](#documentation)
- [Current Status](#current-status)
- [Limitations](#limitations)

## How It Works

```
User enters ticker (e.g. NVDA)
        │
        ▼
  React SPA (Vite)
        │  HTTP / JSON
        ▼
  FastAPI Backend (/api)
        │
        ├─ Quote / Fundamentals / Technicals / History
        │     └─ yfinance + Finnhub + TwelveData + FMP (fallback)
        │
        ├─ AI Deep Analysis  (Google login · 3 free analyses/account)
        │     ├─ [parallel] News Agent ──┐
        │     ├─ [parallel] Data Agent ──┼─→ Cross-Validation → Analyst Agent
        │     └─ [parallel] Macro Agent ─┘                        │
        │                                                   BUY / HOLD / SELL
        │
        ├─ Sector Screening
        │     └─ 3-stage filter → AI summary → Top 5
        │
        ├─ Compare Mode
        │     └─ Same/cross sector auto-detect → AI comparison
        │
        └─ Portfolio
              └─ Holdings tracking → AI portfolio analysis
```

## Tech Stack

| Technology | Role | Why |
|---|---|---|
| FastAPI + Uvicorn | Backend REST API | Async-native, auto OpenAPI docs, easy deployment |
| React 19 + TypeScript | Frontend SPA | Component reuse, type safety, large ecosystem |
| Vite | Build tool / dev server | Fast HMR, native ESM, simple proxy config |
| Claude API (Sonnet) | AI agent engine | Strong financial reasoning, structured JSON output |
| yfinance | Stock quotes & financials | Free, no API key, broad coverage |
| Finnhub | Real-time quotes & news | Free tier (60 req/min), WebSocket-ready |
| Twelve Data | Technical indicators | Pre-computed RSI/MACD/Bollinger, free tier (800/day) |
| Finviz | Sector screening | Free screener with financial filters |
| FMP | Fundamentals fallback | Supplements yfinance gaps (key-metrics-ttm) |
| FRED | Macroeconomic data | Fed Funds Rate, CPI, unemployment, GDP |
| SQLite (WAL) | Persistence | Zero-config, WAL mode for concurrent reads |
| Lightweight Charts | Candlestick charts | Lightweight (~40KB), TradingView quality |
| Python asyncio | Agent orchestration | Native parallel execution, timeout control |
| Google OAuth (`google-auth` + `@react-oauth/google`) | Free-trial login gate | Verified Google `sub` keys per-account AI credits; no password handling |

## AI Components

QuantAI uses Claude API (Sonnet) for interpretation, not data generation. All numbers come from financial APIs; AI only analyzes and summarizes.

| Agent | Input | Output |
|---|---|---|
| News Agent | Finnhub headlines for ticker | Sentiment score + key event summary |
| Data Agent | Fundamentals + technicals | Financial health assessment |
| Macro Agent | FRED indicators (rates, CPI, GDP) | Macro environment impact on ticker |
| Cross-Validation | All 3 agent results | Consensus check, contradiction flags |
| Analyst Agent | Cross-validated results | Final BUY/HOLD/SELL + confidence + rationale |
| Sector Analyzer | Filtered sector stocks | AI-condensed screening per stock |
| Compare Agent | 2-3 ticker data side by side | Winner pick + category breakdown |
| Portfolio Agent | Holdings + market data | Portfolio health analysis + rebalancing suggestions |

**Failure handling:** If 1-2 agents fail, analysis proceeds with available results (graceful degradation). If all 3 primary agents fail, analysis is aborted with an error.

**Disclaimer:** All AI outputs are for reference only. They do not constitute financial advice.

## Quick Start

### Prerequisites

- Python 3.11+
- Node.js 18+
- API keys: Finnhub, Twelve Data, FMP, FRED, Anthropic (Claude)
- Google OAuth client ID — for the free-trial login gate ([Google Cloud Console](https://console.cloud.google.com/apis/credentials))

### 1. Clone & install

```bash
git clone https://github.com/Ihatespeedlimit/stock-analyzer.git
cd stock-analyzer

# Backend
pip install -r requirements.txt

# Frontend
cd frontend
npm install
cd ..
```

### 2. Configure environment

```bash
cp .env.example .env
# Edit .env and fill in your API keys:
#   FINNHUB_API_KEY=...
#   TWELVEDATA_API_KEY=...
#   FMP_API_KEY=...
#   FRED_API_KEY=...
#   ANTHROPIC_API_KEY=...
#   GOOGLE_CLIENT_ID=...        # backend ID-token verification (free-trial login)

# Frontend also needs the same client ID for the login button:
#   echo "VITE_GOOGLE_CLIENT_ID=..." > frontend/.env
```

### 3. Run

```bash
# Terminal 1 — Backend (port 8001)
uvicorn backend.main:app --reload --port 8001

# Terminal 2 — Frontend (port 5173)
cd frontend
npm run dev
```

Open `http://localhost:5173` in your browser. The Vite dev server proxies `/api` requests to the FastAPI backend.

### Production deployment

- **Backend:** Render (see `render.yaml`)
- **Frontend:** Netlify (see `netlify.toml`) — set `VITE_API_BASE` to your Render backend URL

## Project Structure

```
stock-analyzer/
├── backend/                    # FastAPI REST API
│   ├── main.py                 # App entry, CORS, router registration
│   ├── auth.py                 # Google ID token verification (free-trial login)
│   └── routers/                # 12 route modules
│       ├── quote.py            # /api/quote, fundamentals, technicals, history
│       ├── market.py           # /api/market (indices, movers, news)
│       ├── analysis.py         # /api/analysis (5-agent AI pipeline)
│       ├── sector.py           # /api/sector, themes CRUD
│       ├── compare.py          # /api/compare (2-3 ticker comparison)
│       ├── watchlist.py        # /api/watchlist CRUD
│       ├── guide.py            # /api/guide (beginner education)
│       ├── search.py           # /api/search (ticker autocomplete)
│       ├── alerts.py           # /api/alerts (price alerts)
│       ├── portfolio.py        # /api/portfolio CRUD + AI analysis
│       ├── sync.py             # /api/sync (data sync)
│       └── trial.py            # /api/trial (free-trial credit status)
│
├── agents/                     # AI agent layer
│   ├── orchestrator.py         # Parallel execution + retry + timeout
│   ├── news_agent.py           # News sentiment analysis
│   ├── data_agent.py           # Financial data interpretation
│   ├── macro_agent.py          # Macroeconomic analysis
│   ├── cross_validation.py     # Inter-agent cross-validation
│   ├── analyst_agent.py        # Final verdict generation
│   ├── sector_analyzer.py      # Sector AI screening
│   ├── compare_agent.py        # AI comparison analysis
│   ├── portfolio_agent.py      # Portfolio AI analysis
│   └── claude_client.py        # Claude API wrapper
│
├── data/                       # Data layer (API clients + business logic)
│   ├── api_client.py           # Unified API client with fallback
│   ├── database.py             # SQLite connection + table init
│   ├── cache.py                # In-memory cache with TTL
│   ├── portfolio.py            # Portfolio data management
│   └── ...                     # 20+ modules (quote, history, etc.)
│
├── services/                   # Business logic services
│   ├── sync_service.py         # Data synchronization
│   └── portfolio_calculator.py # Portfolio calculations
│
├── frontend/                   # React SPA
│   ├── package.json
│   ├── vite.config.ts          # Dev proxy to FastAPI
│   └── src/
│       ├── App.tsx             # Router + layout (Google OAuth + Auth providers)
│       ├── auth/               # AuthProvider + useAuth (Google login state)
│       ├── pages/              # 8 pages (MarketOverview, QuickLook, Portfolio, etc.)
│       ├── components/         # 20+ reusable components (incl. LoginButton, TrialBanner, TrialLimitModal)
│       ├── hooks/              # Data-fetching hooks
│       ├── services/           # API service modules
│       ├── theme/              # Dark/Light theme system
│       └── types/              # API response types
│
├── tests/                      # pytest test suite
├── Phase/                      # Phase development docs (15 phases, incl. 13.5)
├── utils/                      # Shared utilities
├── config/                     # Configuration files
├── requirements.txt            # Python dependencies
├── render.yaml                 # Render deployment config
└── netlify.toml                # Netlify deployment config
```

## Tests

```bash
# Run all tests
pytest

# Run specific phase tests
pytest tests/test_phase1_api.py
pytest tests/test_phase3_ai_analysis.py
```

Tests cover API integration (real API calls), data processing, AI agent pipeline logic, and the free-trial credit wallet (`test_phase14_trial.py`) across 9 test files.

## Documentation

| Document | Path | Description |
|---|---|---|
| Phase docs (1-15) | `Phase/Phase*.md` | Detailed development log per phase (incl. 13.5) |
| Design spec | `pre-requirement/design-spec.md` | Color tokens, layout, theme system |
| Portfolio spec | `pre-requirement/portfolio-design-spec.md` | Portfolio feature design |
| Feature spec | `pre-requirement/draft.txt` | Original feature specification |
| Data flow | `pre-requirement/data_flow.txt` | End-to-end data flow diagram |
| API reference | `docs/API.md` | REST API endpoint documentation |

## Current Status

### Feature Development (Phase 1-5)

| Phase | Name | Status | Deliverable |
|:---:|---|:---:|---|
| 1 | API Integration | ✅ Done | 6 API wrappers + fallback + caching |
| 2 | Quick Look | ✅ Done | Quote + chart + fundamentals + technicals |
| 3 | AI Deep Analysis | ✅ Done | 5-agent pipeline + graceful degradation |
| 4 | Sector Screening | ✅ Done | 3-stage filter + AI summary + Top 5 |
| 5 | Compare + Watchlist + Guide + Overview | ✅ Done | Remaining data logic |

### Backend + Frontend (Phase 6-9)

| Phase | Name | Status | Deliverable |
|:---:|---|:---:|---|
| 6 | FastAPI Backend | ✅ Done | 9 REST routers + CORS + SQLite init |
| 7 | React Setup + Design System | ✅ Done | Vite + theme + sidebar + routing |
| 8 | QuickLook + AI Analysis UI | ✅ Done | Candlestick chart + tech indicator cards |
| 9 | Remaining Pages + Integration | ✅ Done | Market Overview + Sector + Compare + Guide |

### Polish (Phase 10-13)

| Phase | Name | Status | Deliverable |
|:---:|---|:---:|---|
| 10 | UX + Data Persistence | ✅ Done | Search autocomplete + Watchlist UI + SQLite + alerts |
| 11 | Code Quality | ✅ Done | API key masking + singletons + parallelization |
| 12 | UI/UX + Mobile Optimization | ✅ Done | Mobile responsive + bottom nav + touch UX |
| 13 | Portfolio | ✅ Done | Holdings tracking + AI portfolio analysis |
| 13.5 | Portfolio Authentication | ✅ Done | Code+PIN auth gate + server-side storage |

### Free Trial & Internationalization (Phase 14-15)

| Phase | Name | Status | Deliverable |
|:---:|---|:---:|---|
| 14 | Free Trial (Google Login Gate) | 🔶 In Progress | Google-login-gated free trial — 3 AI analyses/account; credit wallet + ledger + reserve/commit (hold) pattern. Backend + frontend implemented (2026-06-16); browser manual QA pending |
| 15 | Internationalization (i18n) | 🔲 Not Started | KO/EN toggle for UI + AI results + guide content |

## Limitations

- Free API tiers have rate limits (Finnhub 60/min, Twelve Data 800/day, FMP 250/day)
- AI analysis takes 1-2 minutes per ticker due to sequential agent validation
- S&P 500 stocks only for autocomplete (other tickers can be entered manually)
- AI analysis is gated by Google login (3 free analyses per account); quotes, charts, sectors, and compare stay public. Payments / paid credits are not implemented yet (planned in BACKLOG V2-2)
- No WebSocket real-time updates — data refreshes on user action

---

<p align="center">Made with AI-assisted development</p>

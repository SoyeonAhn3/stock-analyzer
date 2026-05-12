# QuantAI — AI Stock Analyzer

> Multi-agent US stock analysis system that aggregates real-time data from 6 financial APIs and delivers AI-powered buy/hold/sell recommendations through a 5-agent pipeline with cross-validation.

| Item | Details |
|---|---|
| Version | v1.0 |
| Date | 2026-05-12 |
| Audience | Individual investors, developers, portfolio reviewers |

---

## Table of Contents

- [1. Overview](#1-overview)
- [2. Prerequisites](#2-prerequisites)
- [3. Getting Started](#3-getting-started)
- [4. Key Features](#4-key-features)
- [5. Data Storage](#5-data-storage)
- [6. Cautions & Limitations](#6-cautions--limitations)
- [7. Troubleshooting (FAQ)](#7-troubleshooting-faq)

---

## 1. Overview

QuantAI is a full-stack web application that consolidates US stock data from multiple financial APIs into a single dashboard and applies AI-driven analysis to generate actionable investment insights. Five specialized AI agents run in parallel, cross-validate each other's findings, and produce a final BUY / HOLD / SELL recommendation with confidence scores and rationale.

| Item | Details |
|---|---|
| Architecture | React 19 SPA + FastAPI REST API |
| AI Engine | Claude API (Sonnet) — 5-agent pipeline |
| Data Sources | yfinance, Finnhub, Twelve Data, FMP, Finviz, FRED |
| Database | SQLite (WAL mode) |
| Deployment | Netlify (frontend) + Render (backend) |
| Live Demo | [https://stock-analyzer-ai.netlify.app/](https://stock-analyzer-ai.netlify.app/) |

---

## 2. Prerequisites

- [ ] **Python 3.11+** installed
- [ ] **Node.js 18+** installed
- [ ] **Finnhub API key** — [https://finnhub.io/](https://finnhub.io/) (free tier: 60 req/min)
- [ ] **Twelve Data API key** — [https://twelvedata.com/](https://twelvedata.com/) (free tier: 800 req/day)
- [ ] **FMP API key** — [https://financialmodelingprep.com/](https://financialmodelingprep.com/) (free tier: 250 req/day)
- [ ] **FRED API key** — [https://fred.stlouisfed.org/](https://fred.stlouisfed.org/) (free, registration required)
- [ ] **Anthropic API key** — [https://console.anthropic.com/](https://console.anthropic.com/) (Claude API access)

---

## 3. Getting Started

1. **Clone the repository**

   ```bash
   git clone https://github.com/Ihatespeedlimit/stock-analyzer.git
   cd stock-analyzer
   ```

2. **Install backend dependencies**

   ```bash
   pip install -r requirements.txt
   ```

3. **Install frontend dependencies**

   ```bash
   cd frontend
   npm install
   cd ..
   ```

4. **Configure environment variables**

   ```bash
   cp .env.example .env
   ```

   Open `.env` and fill in your API keys:

   ```
   FINNHUB_API_KEY=your_key_here
   TWELVEDATA_API_KEY=your_key_here
   FMP_API_KEY=your_key_here
   FRED_API_KEY=your_key_here
   ANTHROPIC_API_KEY=your_key_here
   ```

5. **Start the backend** (Terminal 1)

   ```bash
   uvicorn backend.main:app --reload
   ```

   The API server starts on `http://localhost:8000`.

6. **Start the frontend** (Terminal 2)

   ```bash
   cd frontend
   npm run dev
   ```

   Open `http://localhost:5173` in your browser. The Vite dev server proxies `/api` requests to the FastAPI backend automatically.

7. **Production deployment**

   | Component | Platform | Config File |
   |---|---|---|
   | Backend | Render | `render.yaml` |
   | Frontend | Netlify | `netlify.toml` |

   Set the `VITE_API_BASE` environment variable on Netlify to your Render backend URL.

---

## 4. Key Features

### 4.1 Market Overview

The landing page displays a real-time snapshot of major market indices (S&P 500, NASDAQ, Dow Jones), top gainers/losers, and latest financial news headlines sourced from Finnhub.

| Data | Source | Refresh |
|---|---|---|
| Market indices | yfinance | On page load |
| Top movers | yfinance | On page load |
| News headlines | Finnhub | On page load |

---

### 4.2 QuickLook (Stock Dashboard)

Enter any US stock ticker to view a comprehensive single-stock dashboard including real-time quotes, interactive candlestick charts, fundamental metrics (P/E, EPS, market cap), and technical indicators (RSI, MACD, Bollinger Bands).

| Data | Source | Fallback |
|---|---|---|
| Quote & price | yfinance | Finnhub |
| Fundamentals | yfinance | FMP (key-metrics-ttm) |
| Technical indicators | Twelve Data | — |
| Price history | yfinance | Twelve Data |

---

### 4.3 AI Deep Analysis (5-Agent Pipeline)

The core feature. When you request an AI analysis for a ticker, five specialized agents execute in parallel:

| Agent | Role | Input |
|---|---|---|
| News Agent | Sentiment analysis | Finnhub headlines |
| Data Agent | Financial health check | Fundamentals + technicals |
| Macro Agent | Economic context | FRED indicators (rates, CPI, GDP) |
| Cross-Validator | Consensus check | All 3 agent outputs |
| Analyst Agent | Final verdict | Cross-validated results |

The final output is a **BUY / HOLD / SELL** recommendation with a confidence score (0-100%) and detailed rationale.

> **Warning:** AI analysis takes 1-2 minutes per ticker due to sequential agent validation. If 1-2 agents fail, the analysis proceeds with available results (graceful degradation). If all 3 primary agents fail, the analysis is aborted.

---

### 4.4 Sector Screening

Browse stocks by sector (Technology, Healthcare, Financial, etc.) with a 3-stage filtering pipeline:

1. **Stage 1** — Sector stock list from Finviz
2. **Stage 2** — Financial metric filtering (market cap, P/E, volume)
3. **Stage 3** — AI summary and ranking of top 5 picks

You can also create and manage custom screening themes.

---

### 4.5 Compare Mode

Select 2-3 tickers for side-by-side comparison. The system auto-detects whether the stocks belong to the same or different sectors and adjusts the comparison criteria accordingly. An AI Compare Agent evaluates each category and picks a winner.

---

### 4.6 Portfolio Tracker

Track your stock holdings with buy price, quantity, and date. The portfolio page displays:

- Current value and total gain/loss
- Individual position performance
- AI-powered portfolio health analysis with rebalancing suggestions

---

### 4.7 Watchlist

Add tickers to your watchlist for quick access. Watchlist data is persisted in SQLite, so your selections survive across sessions.

---

### 4.8 Price Alerts

Set price target alerts for any ticker. When checking a stock in QuickLook, triggered alerts are displayed if the current price crosses your target.

---

### 4.9 Beginner's Guide

An educational page with curated content explaining fundamental stock market concepts, key financial metrics, and how to interpret the data shown in QuantAI.

---

### 4.10 Ticker Search (Autocomplete)

A search bar with autocomplete suggestions drawn from S&P 500 constituents. Tickers outside the S&P 500 can still be entered manually.

---

## 5. Data Storage

- **SQLite (WAL mode)** is used for all persistent data (watchlists, portfolios, alerts, themes)
- WAL (Write-Ahead Logging) mode enables concurrent reads without blocking
- The database file is created automatically on first run — no manual setup required
- **In-memory cache** with TTL is used for frequently accessed API data to reduce external API calls and improve response times

---

## 6. Cautions & Limitations

> **Warning:** All AI outputs are for informational and educational purposes only. They do not constitute financial advice. Always consult a qualified financial advisor before making investment decisions.

> **Warning:** Free API tiers have rate limits — Finnhub (60 req/min), Twelve Data (800 req/day), FMP (250 req/day). Heavy usage may result in temporary API errors or degraded data.

> **Warning:** AI analysis takes 1-2 minutes per ticker due to the sequential agent validation pipeline. This is by design to ensure cross-validated results.

> **Warning:** Autocomplete only covers S&P 500 stocks. Other US tickers can be entered manually but will not appear in suggestions.

> **Warning:** No user authentication is implemented. The application operates as a single-user instance — all data (watchlists, portfolios) is shared across all visitors of the same deployment.

> **Warning:** Data is refreshed on user action (page load, button click). There are no WebSocket-based real-time updates.

---

## 7. Troubleshooting (FAQ)

**Q. The backend fails to start with a module import error.**
A. Make sure you have installed all dependencies with `pip install -r requirements.txt` using Python 3.11+. Check that you are running the command from the project root directory.

**Q. The frontend shows "Network Error" or "Failed to fetch" for all API calls.**
A. Verify that the backend is running on port 8000. Check `frontend/vite.config.ts` to confirm the proxy target matches your backend URL. If deploying to production, set the `VITE_API_BASE` environment variable.

**Q. AI analysis returns an error or times out.**
A. Confirm your `ANTHROPIC_API_KEY` is valid and has sufficient credits. The 5-agent pipeline requires multiple API calls to Claude, which may take 1-2 minutes. If the issue persists, check backend logs for specific agent failure messages.

**Q. Technical indicators (RSI, MACD) show as "N/A" or are missing.**
A. This typically means the Twelve Data API rate limit has been reached (800 requests/day on the free tier). Wait until the daily limit resets or upgrade your Twelve Data plan.

**Q. Sector screening returns no results.**
A. Finviz screener results depend on market conditions and filter criteria. Try adjusting the screening parameters or check if Finviz is accessible from your network.

**Q. The database seems corrupted or watchlist data is lost.**
A. Delete the SQLite database file and restart the backend — the tables will be recreated automatically. Note that this will erase all saved watchlists, portfolios, and alerts.

---

> This manual was automatically generated on 2026-05-12.

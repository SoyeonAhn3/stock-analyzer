/** FastAPI 응답 타입 — backend/routers 엔드포인트와 1:1 매핑 */

export interface QuoteResponse {
  ticker: string;
  price: number;
  change: number;
  change_percent: number;
  volume: number | null;
  day_high: number | null;
  day_low: number | null;
  open: number | null;
  previous_close: number | null;
  market_cap: number | null;
  source: string;
}

export interface FundamentalsResponse {
  ticker: string;
  pe: number | null;
  forward_pe: number | null;
  eps: number | null;
  peg: number | null;
  market_cap: number | null;
  week52_high: number | null;
  week52_low: number | null;
  dividend_yield: number | null;
  de_ratio: number | null;
  sector: string | null;
  industry: string | null;
  source: string;
}

export interface TechnicalsResponse {
  ticker: string;
  rsi: { value: number; signal: string } | null;
  macd: { histogram: number; signal: string; detail: string } | null;
  bollinger: {
    upper: number;
    middle: number;
    lower: number;
    position: string;
    signal: string;
  } | null;
  ma50: { value: number; vs_price: string; signal: string } | null;
  ma200: { value: number; vs_price: string; signal: string } | null;
  source: string;
}

export interface HistoryRecord {
  Date: string;
  Open: number;
  High: number;
  Low: number;
  Close: number;
  Volume: number;
  MA50?: number;
  MA200?: number;
}

export interface MarketIndex {
  symbol: string;
  yf_symbol: string;
  price: number | null;
  change: number | null;
  change_percent: number | null;
}

export interface WatchlistQuote {
  ticker: string;
  price: number | null;
  change: number | null;
  change_percent: number | null;
  highlight: boolean;
  source: string;
}

export interface WatchlistResponse {
  tickers: string[];
  quotes: WatchlistQuote[];
}

export interface AnalysisResult {
  agent: string;
  status: string;
  verdict: string;
  confidence: string;
  bull_case?: string;
  bear_case?: string;
  key_factors?: string[];
  summary: string;
  disclaimer?: string;
}

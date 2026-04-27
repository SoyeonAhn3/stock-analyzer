"""포트폴리오 정량 분석 파이프라인.

모든 계산은 Python(numpy)이 수행한다. AI 호출 없음.

사용법:
    from services.portfolio_calculator import run_analysis
    result = run_analysis(holdings)
"""

import logging
import math
from concurrent.futures import ThreadPoolExecutor, as_completed
from itertools import combinations
from typing import Any, Optional

import numpy as np
import pandas as pd

from data.quote import get_quote
from data.fundamentals import get_fundamentals
from data.yfinance_client import YFinanceClient
from data.fred_client import FREDClient

logger = logging.getLogger(__name__)

_yf = YFinanceClient()
_fred = FREDClient()

TRADING_DAYS = 252

CYCLICAL_SECTORS = {
    "Technology", "Consumer Cyclical", "Consumer Discretionary",
    "Financial Services", "Financials", "Basic Materials",
    "Materials", "Energy",
}

DEFENSIVE_SECTORS = {
    "Healthcare", "Utilities", "Consumer Defensive",
    "Consumer Staples", "Real Estate", "Communication Services",
    "Industrials",
}

GICS_SECTOR_COUNT = 11


# ── 메인 파이프라인 ─────────────────────────────────────────────

def run_analysis(holdings: list[dict[str, Any]]) -> dict[str, Any]:
    """포트폴리오 전체 분석을 실행한다.

    Args:
        holdings: [{"ticker": "AAPL", "shares": 45, "avg_cost": 142.30, ...}, ...]

    Returns:
        분석 결과 JSON (summary, holdings, analysis)
    """
    tickers = [h["ticker"] for h in holdings]

    # 1. 데이터 수집 (병렬)
    stock_data = _collect_data(tickers)

    # 2. 평가금액 / 비중
    valuations = _calc_valuations(holdings, stock_data)

    # 3. 집중도
    concentration = _calc_concentration(valuations)

    # 4. 가중평균 펀더멘털
    fundamentals = _calc_fundamentals(valuations, stock_data)

    # 5. 성과 (Alpha, 기여도)
    performance = _calc_performance(valuations, holdings, stock_data)

    # 6. 위험 (변동성, Beta, MDD, Sharpe, VaR, 상관관계, 유동성)
    risk = _calc_risk(valuations, stock_data)

    # 7. 스타일 분류
    style = _calc_style(valuations, stock_data)

    # 8. 거시 노출도
    macro = _calc_macro_exposure(valuations, stock_data, risk)

    # 9. 점수화
    scores = _calc_scores(concentration, risk, performance, fundamentals, valuations)

    return {
        "concentration": concentration,
        "fundamentals": fundamentals,
        "performance": performance,
        "risk": risk,
        "style": style,
        "macro": macro,
        "scores": scores,
    }


# ── 1. 데이터 수집 ──────────────────────────────────────────────

def _collect_data(tickers: list[str]) -> dict[str, dict[str, Any]]:
    """종목별 현재가 + 재무 + 1년 히스토리를 병렬 수집한다."""
    result: dict[str, dict[str, Any]] = {}

    with ThreadPoolExecutor(max_workers=10) as pool:
        futures = {}
        for t in tickers:
            futures[pool.submit(_fetch_single_stock, t)] = t
        futures[pool.submit(_fetch_benchmark)] = "__BENCHMARK__"
        futures[pool.submit(_fetch_risk_free_rate)] = "__RISK_FREE__"

        for future in as_completed(futures):
            key = futures[future]
            try:
                data = future.result()
                if data:
                    result[key] = data
            except Exception as e:
                logger.warning("Data collection failed for %s: %s", key, e)

    return result


def _fetch_single_stock(ticker: str) -> Optional[dict[str, Any]]:
    """한 종목의 시세 + 재무 + 히스토리를 가져온다."""
    quote = get_quote(ticker)
    fund = get_fundamentals(ticker)
    hist_raw = _yf.get_history(ticker, period="1y", interval="1d")

    daily_returns = None
    avg_volume = None
    if hist_raw and hist_raw.get("data"):
        df = pd.DataFrame(hist_raw["data"])
        if "Close" in df.columns and len(df) > 1:
            closes = df["Close"].dropna().values
            daily_returns = np.diff(closes) / closes[:-1]
        if "Volume" in df.columns:
            avg_volume = float(df["Volume"].tail(20).mean())

    return {
        "quote": quote,
        "fundamentals": fund,
        "daily_returns": daily_returns,
        "avg_volume": avg_volume,
    }


def _fetch_benchmark() -> Optional[dict[str, Any]]:
    """S&P500 1년 히스토리를 가져온다."""
    hist_raw = _yf.get_history("^GSPC", period="1y", interval="1d")
    if not hist_raw or not hist_raw.get("data"):
        return None
    df = pd.DataFrame(hist_raw["data"])
    if "Close" not in df.columns or len(df) < 2:
        return None
    closes = df["Close"].dropna().values
    daily_returns = np.diff(closes) / closes[:-1]
    first_close = float(closes[0])
    last_close = float(closes[-1])
    return {
        "daily_returns": daily_returns,
        "first_close": first_close,
        "last_close": last_close,
        "total_return": (last_close - first_close) / first_close * 100,
    }


def _fetch_risk_free_rate() -> Optional[dict[str, Any]]:
    """FRED에서 3개월 T-bill 금리를 가져온다."""
    try:
        data = _fred._get_series("DTB3", limit=1)
        if data:
            annual_rate = data[0]["value"] / 100
            return {"annual": annual_rate, "daily": annual_rate / TRADING_DAYS}
    except Exception as e:
        logger.warning("Risk-free rate fetch failed: %s", e)
    return {"annual": 0.05, "daily": 0.05 / TRADING_DAYS}


# ── 2. 평가금액 / 비중 ─────────────────────────────────────────

def _calc_valuations(
    holdings: list[dict], stock_data: dict
) -> list[dict[str, Any]]:
    """종목별 평가금액, 수익률, 비중을 계산한다."""
    results = []
    for h in holdings:
        t = h["ticker"]
        sd = stock_data.get(t, {})
        q = sd.get("quote") or {}
        fund = sd.get("fundamentals") or {}
        price = q.get("price")

        cost_basis = h["avg_cost"] * h["shares"]
        market_value = price * h["shares"] if price else None
        pnl = (market_value - cost_basis) if market_value else None
        pnl_pct = (pnl / cost_basis * 100) if (pnl is not None and cost_basis) else None

        results.append({
            "ticker": t,
            "shares": h["shares"],
            "avg_cost": h["avg_cost"],
            "currency": h.get("currency", "USD"),
            "purchase_date": h.get("purchase_date"),
            "current_price": price,
            "market_value": _r2(market_value),
            "cost_basis": _r2(cost_basis),
            "pnl": _r2(pnl),
            "pnl_pct": _r2(pnl_pct),
            "weight": None,
            "sector": fund.get("sector"),
            "country": fund.get("country"),
            "market_cap": fund.get("market_cap"),
            "beta": fund.get("beta"),
            "pe": fund.get("pe"),
            "roe": fund.get("roe"),
            "de_ratio": fund.get("de_ratio"),
            "operating_margin": fund.get("operating_margin"),
            "dividend_yield": fund.get("dividend_yield"),
            "profit_margin": fund.get("profit_margin"),
        })

    total_mv = sum(v["market_value"] for v in results if v["market_value"])
    for v in results:
        if v["market_value"] and total_mv:
            v["weight"] = _r2(v["market_value"] / total_mv * 100)

    return results


# ── 3. 집중도 ───────────────────────────────────────────────────

def _calc_concentration(valuations: list[dict]) -> dict[str, Any]:
    weights = sorted(
        [(v["ticker"], v["weight"]) for v in valuations if v["weight"]],
        key=lambda x: x[1],
        reverse=True,
    )
    weight_values = [w for _, w in weights]

    hhi = sum((w / 100) ** 2 for w in weight_values)
    effective_n = (1 / hhi) if hhi > 0 else len(weights)

    top_1 = weight_values[0] if len(weight_values) >= 1 else 0
    top_3 = sum(weight_values[:3]) if len(weight_values) >= 3 else sum(weight_values)
    top_5 = sum(weight_values[:5]) if len(weight_values) >= 5 else sum(weight_values)

    sector_weights: dict[str, float] = {}
    country_weights: dict[str, float] = {}
    for v in valuations:
        if not v["weight"]:
            continue
        s = v.get("sector") or "Unknown"
        sector_weights[s] = sector_weights.get(s, 0) + v["weight"]
        c = v.get("country") or "Unknown"
        country_weights[c] = country_weights.get(c, 0) + v["weight"]

    sector_weights = dict(sorted(sector_weights.items(), key=lambda x: x[1], reverse=True))
    country_weights = dict(sorted(country_weights.items(), key=lambda x: x[1], reverse=True))

    return {
        "hhi": _r4(hhi),
        "effective_n": _r2(effective_n),
        "top_1": {"ticker": weights[0][0], "weight": top_1} if weights else None,
        "top_3_weight": _r2(top_3),
        "top_5_weight": _r2(top_5),
        "sector_weights": {k: _r2(v) for k, v in sector_weights.items()},
        "sector_count": len(sector_weights),
        "country_weights": {k: _r2(v) for k, v in country_weights.items()},
        "missing_sectors": _get_missing_sectors(sector_weights),
    }


def _get_missing_sectors(sector_weights: dict) -> list[str]:
    all_gics = {
        "Technology", "Healthcare", "Financials", "Consumer Discretionary",
        "Consumer Staples", "Energy", "Utilities", "Real Estate",
        "Materials", "Industrials", "Communication Services",
    }
    present = set()
    for s in sector_weights:
        for g in all_gics:
            if g.lower() in s.lower() or s.lower() in g.lower():
                present.add(g)
    return sorted(all_gics - present)


# ── 4. 가중평균 펀더멘털 ────────────────────────────────────────

def _calc_fundamentals(
    valuations: list[dict], stock_data: dict
) -> dict[str, Any]:
    metrics = ["pe", "roe", "de_ratio", "operating_margin", "dividend_yield", "profit_margin"]
    weighted: dict[str, Optional[float]] = {}

    for m in metrics:
        total_w = 0
        total_val = 0
        for v in valuations:
            val = v.get(m)
            w = v.get("weight")
            if val is not None and w is not None and w > 0:
                total_val += val * w
                total_w += w
        weighted[f"weighted_{m}"] = _r4(total_val / total_w) if total_w > 0 else None

    annual_dividend = 0
    for v in valuations:
        dy = v.get("dividend_yield")
        price = v.get("current_price")
        shares = v.get("shares")
        if dy and price and shares:
            annual_dividend += dy * price * shares
    total_cost = sum(v["cost_basis"] for v in valuations if v["cost_basis"])
    yield_on_cost = (annual_dividend / total_cost * 100) if total_cost else 0

    return {
        **weighted,
        "annual_dividend": _r2(annual_dividend),
        "yield_on_cost": _r4(yield_on_cost),
    }


# ── 5. 성과 분석 ───────────────────────────────────────────────

def _calc_performance(
    valuations: list[dict],
    holdings: list[dict],
    stock_data: dict,
) -> dict[str, Any]:
    total_cost = sum(v["cost_basis"] for v in valuations if v["cost_basis"])
    total_mv = sum(v["market_value"] for v in valuations if v["market_value"])
    total_pnl = total_mv - total_cost
    total_return = (total_pnl / total_cost * 100) if total_cost else 0

    contributions = []
    for v in valuations:
        pnl = v.get("pnl") or 0
        contrib_pct = (pnl / total_cost * 100) if total_cost else 0
        pnl_share = (pnl / total_pnl * 100) if total_pnl else 0
        contributions.append({
            "ticker": v["ticker"],
            "pnl": v.get("pnl"),
            "contribution_pct": _r2(contrib_pct),
            "pnl_share": _r2(pnl_share),
        })
    contributions.sort(key=lambda x: x.get("pnl") or 0, reverse=True)

    bm = stock_data.get("__BENCHMARK__", {})
    benchmark_return = bm.get("total_return", 0)
    alpha = total_return - benchmark_return

    return {
        "total_return": _r2(total_return),
        "benchmark_return": _r2(benchmark_return),
        "alpha": _r2(alpha),
        "contributions": contributions,
        "summary": {
            "total_market_value": _r2(total_mv),
            "total_cost_basis": _r2(total_cost),
            "total_pnl": _r2(total_pnl),
        },
    }


# ── 6. 위험 분석 ───────────────────────────────────────────────

def _calc_risk(
    valuations: list[dict], stock_data: dict
) -> dict[str, Any]:
    tickers = [v["ticker"] for v in valuations if v["weight"]]
    weights_arr = np.array([v["weight"] / 100 for v in valuations if v["weight"]])

    returns_map: dict[str, np.ndarray] = {}
    for t in tickers:
        sd = stock_data.get(t, {})
        dr = sd.get("daily_returns")
        if dr is not None and len(dr) > 0:
            returns_map[t] = dr

    bm = stock_data.get("__BENCHMARK__", {})
    bm_returns = bm.get("daily_returns")

    rf = stock_data.get("__RISK_FREE__", {})
    rf_daily = rf.get("daily", 0.05 / TRADING_DAYS)

    # 공통 길이 맞추기
    valid_tickers = [t for t in tickers if t in returns_map]
    if not valid_tickers:
        return _empty_risk()

    min_len = min(len(returns_map[t]) for t in valid_tickers)
    if bm_returns is not None:
        min_len = min(min_len, len(bm_returns))

    trimmed = {t: returns_map[t][-min_len:] for t in valid_tickers}
    valid_weights = np.array([
        v["weight"] / 100 for v in valuations
        if v["ticker"] in valid_tickers and v["weight"]
    ])
    if valid_weights.sum() > 0:
        valid_weights = valid_weights / valid_weights.sum()

    returns_matrix = np.array([trimmed[t] for t in valid_tickers])
    port_returns = np.dot(valid_weights, returns_matrix)

    # 변동성
    volatility = float(np.std(port_returns, ddof=1) * math.sqrt(TRADING_DAYS))

    # Beta
    portfolio_beta = None
    if bm_returns is not None and len(bm_returns) >= min_len:
        bm_trimmed = bm_returns[-min_len:]
        cov_matrix = np.cov(port_returns, bm_trimmed)
        var_bm = np.var(bm_trimmed, ddof=1)
        portfolio_beta = float(cov_matrix[0][1] / var_bm) if var_bm > 0 else None

    # MDD
    cumulative = np.cumprod(1 + port_returns)
    running_max = np.maximum.accumulate(cumulative)
    drawdowns = (cumulative - running_max) / running_max
    mdd = float(np.min(drawdowns))

    # Sharpe
    excess = port_returns - rf_daily
    sharpe = float(np.mean(excess) / np.std(excess, ddof=1) * math.sqrt(TRADING_DAYS)) if np.std(excess, ddof=1) > 0 else 0

    # VaR (95%, 30일)
    var_95_daily = float(np.percentile(port_returns, 5))
    total_mv = sum(v["market_value"] for v in valuations if v["market_value"])
    var_95_30d = var_95_daily * math.sqrt(30) * total_mv

    # 상관관계 행렬
    correlation = {}
    if len(valid_tickers) >= 2:
        corr_matrix = np.corrcoef(returns_matrix)
        avg_corr_values = []
        for i, t1 in enumerate(valid_tickers):
            correlation[t1] = {}
            for j, t2 in enumerate(valid_tickers):
                val = float(corr_matrix[i][j])
                correlation[t1][t2] = _r4(val)
                if i < j:
                    avg_corr_values.append(val)
        avg_corr = float(np.mean(avg_corr_values)) if avg_corr_values else 0
    else:
        avg_corr = 0

    high_corr_pairs = []
    for (t1, t2) in combinations(valid_tickers, 2):
        if t1 in correlation and t2 in correlation.get(t1, {}):
            c = correlation[t1][t2]
            if c > 0.75:
                high_corr_pairs.append({"pair": [t1, t2], "correlation": c})

    # 유동성
    liquidity = []
    for v in valuations:
        t = v["ticker"]
        sd = stock_data.get(t, {})
        avg_vol = sd.get("avg_volume")
        price = v.get("current_price")
        mv = v.get("market_value")
        mcap = v.get("market_cap")

        if avg_vol and price and avg_vol > 0:
            ratio = mv / (avg_vol * price) if mv else 0
            flag = "danger" if ratio > 0.5 else "caution" if ratio > 0.1 else "safe"
        else:
            ratio = None
            flag = "unknown"

        cap_tier = "large" if (mcap and mcap > 10_000_000_000) else \
                   "mid" if (mcap and mcap > 2_000_000_000) else "small"

        liquidity.append({
            "ticker": t,
            "avg_volume_20d": int(avg_vol) if avg_vol else None,
            "holding_volume_ratio": _r4(ratio) if ratio else None,
            "flag": flag,
            "cap_tier": cap_tier,
        })

    return {
        "volatility": _r4(volatility),
        "portfolio_beta": _r4(portfolio_beta),
        "mdd": _r4(mdd),
        "sharpe": _r4(sharpe),
        "var_95_30d": _r2(var_95_30d),
        "var_95_30d_pct": _r2(var_95_30d / total_mv * 100) if total_mv else None,
        "correlation": correlation,
        "avg_correlation": _r4(avg_corr),
        "high_corr_pairs": high_corr_pairs,
        "liquidity": liquidity,
    }


def _empty_risk() -> dict[str, Any]:
    return {
        "volatility": None, "portfolio_beta": None, "mdd": None,
        "sharpe": None, "var_95_30d": None, "var_95_30d_pct": None,
        "correlation": {}, "avg_correlation": None, "high_corr_pairs": [],
        "liquidity": [],
    }


# ── 7. 스타일 분류 ──────────────────────────────────────────────

def _calc_style(
    valuations: list[dict], stock_data: dict
) -> dict[str, Any]:
    growth_w, value_w = 0.0, 0.0
    large_w, mid_w, small_w = 0.0, 0.0, 0.0
    dividend_w, non_dividend_w = 0.0, 0.0
    cyclical_w, defensive_w = 0.0, 0.0

    per_stock = []

    for v in valuations:
        w = v.get("weight") or 0
        pe = v.get("pe")
        mcap = v.get("market_cap")
        dy = v.get("dividend_yield")
        sector = v.get("sector") or ""

        # 성장 vs 가치
        is_growth = (pe is not None and pe > 25) or (pe is None)
        if is_growth:
            growth_w += w
        else:
            value_w += w

        # 시총
        if mcap and mcap > 10_000_000_000:
            large_w += w
            cap_label = "large"
        elif mcap and mcap > 2_000_000_000:
            mid_w += w
            cap_label = "mid"
        else:
            small_w += w
            cap_label = "small"

        # 배당
        if dy and dy > 0.01:
            dividend_w += w
            div_label = "dividend"
        else:
            non_dividend_w += w
            div_label = "non-dividend"

        # 경기 민감도
        if any(cs.lower() in sector.lower() for cs in CYCLICAL_SECTORS):
            cyclical_w += w
            cycle_label = "cyclical"
        else:
            defensive_w += w
            cycle_label = "defensive"

        per_stock.append({
            "ticker": v["ticker"],
            "style": "growth" if is_growth else "value",
            "cap": cap_label,
            "dividend": div_label,
            "cycle": cycle_label,
        })

    return {
        "growth_pct": _r2(growth_w),
        "value_pct": _r2(value_w),
        "large_pct": _r2(large_w),
        "mid_pct": _r2(mid_w),
        "small_pct": _r2(small_w),
        "dividend_pct": _r2(dividend_w),
        "non_dividend_pct": _r2(non_dividend_w),
        "cyclical_pct": _r2(cyclical_w),
        "defensive_pct": _r2(defensive_w),
        "per_stock": per_stock,
    }


# ── 8. 거시 노출도 ─────────────────────────────────────────────

def _calc_macro_exposure(
    valuations: list[dict],
    stock_data: dict,
    risk: dict,
) -> dict[str, Any]:
    # 금리 민감도: PER 30+ 종목 비중
    high_per_tickers = []
    high_per_weight = 0
    for v in valuations:
        pe = v.get("pe")
        w = v.get("weight") or 0
        if pe and pe > 30:
            high_per_weight += w
            high_per_tickers.append({"ticker": v["ticker"], "pe": pe, "weight": w})

    # 동일 매크로 베팅 감지
    same_bets = []
    corr = risk.get("correlation", {})
    tickers_with_sector = {v["ticker"]: v.get("sector") for v in valuations}

    for pair_info in risk.get("high_corr_pairs", []):
        t1, t2 = pair_info["pair"]
        s1 = tickers_with_sector.get(t1)
        s2 = tickers_with_sector.get(t2)
        if s1 and s2 and s1 == s2:
            same_bets.append({
                "tickers": [t1, t2],
                "sector": s1,
                "correlation": pair_info["correlation"],
            })

    # 섹터 클러스터 (같은 섹터 종목 3개+면 경고)
    sector_clusters = []
    sector_tickers: dict[str, list[dict]] = {}
    for v in valuations:
        s = v.get("sector")
        if s and v.get("weight"):
            if s not in sector_tickers:
                sector_tickers[s] = []
            sector_tickers[s].append({"ticker": v["ticker"], "weight": v["weight"]})

    for sector, tlist in sector_tickers.items():
        if len(tlist) >= 3:
            total_w = sum(t["weight"] for t in tlist)
            sector_clusters.append({
                "sector": sector,
                "tickers": [t["ticker"] for t in tlist],
                "combined_weight": _r2(total_w),
            })

    return {
        "rate_sensitivity": {
            "high_per_weight": _r2(high_per_weight),
            "high_per_tickers": high_per_tickers,
            "level": "high" if high_per_weight > 50 else "medium" if high_per_weight > 25 else "low",
        },
        "same_macro_bets": same_bets,
        "sector_clusters": sector_clusters,
    }


# ── 9. 점수화 ──────────────────────────────────────────────────

def _calc_scores(
    concentration: dict,
    risk: dict,
    performance: dict,
    fundamentals: dict,
    valuations: list[dict],
) -> dict[str, Any]:

    # 분산 점수 (0~100, 높을수록 잘 분산)
    hhi = concentration.get("hhi") or 0
    sector_count = concentration.get("sector_count") or 1
    avg_corr = risk.get("avg_correlation") or 0

    div_hhi = (1 - min(hhi, 1)) * 40
    div_sector = min(sector_count / GICS_SECTOR_COUNT, 1) * 30
    div_corr = (1 - min(abs(avg_corr), 1)) * 30
    diversification = _clamp(div_hhi + div_sector + div_corr)

    # 위험 점수 (0~100, 높을수록 위험)
    vol = risk.get("volatility") or 0
    beta = risk.get("portfolio_beta") or 0
    mdd = abs(risk.get("mdd") or 0)

    risk_vol = min(vol / 0.4, 1) * 30
    risk_beta = min(abs(beta) / 2.0, 1) * 30
    risk_mdd = min(mdd / 0.3, 1) * 20
    risk_conc = min(hhi / 0.5, 1) * 20
    risk_score = _clamp(risk_vol + risk_beta + risk_mdd + risk_conc)

    # 성과 점수 (0~100)
    total_ret = performance.get("total_return") or 0
    alpha = performance.get("alpha") or 0
    sharpe = risk.get("sharpe") or 0

    perf_ret = min(max(total_ret, 0) / 50, 1) * 40
    perf_alpha = min(max(alpha, 0) / 20, 1) * 30
    perf_sharpe = min(max(sharpe, 0) / 2.0, 1) * 30
    performance_score = _clamp(perf_ret + perf_alpha + perf_sharpe)

    # 퀄리티 점수 (0~100)
    w_roe = fundamentals.get("weighted_roe") or 0
    w_debt = fundamentals.get("weighted_de_ratio") or 0
    w_margin = fundamentals.get("weighted_operating_margin") or 0

    qual_roe = min(max(w_roe, 0) / 0.3, 1) * 30 if w_roe else 0
    qual_debt = (1 - min(abs(w_debt) / 200, 1)) * 30
    qual_margin = min(max(w_margin, 0) / 0.3, 1) * 20 if w_margin else 0

    safe_count = sum(1 for v in (risk.get("liquidity") or []) if v.get("flag") == "safe")
    total_count = len(risk.get("liquidity") or []) or 1
    qual_liq = (safe_count / total_count) * 20
    quality = _clamp(qual_roe + qual_debt + qual_margin + qual_liq)

    return {
        "diversification": round(diversification),
        "risk": round(risk_score),
        "risk_rating": _r2(risk_score / 10),
        "performance": round(performance_score),
        "quality": round(quality),
    }


# ── 유틸 ────────────────────────────────────────────────────────

def _r2(val) -> Optional[float]:
    return round(float(val), 2) if val is not None else None

def _r4(val) -> Optional[float]:
    return round(float(val), 4) if val is not None else None

def _clamp(val: float, lo: float = 0, hi: float = 100) -> float:
    return max(lo, min(hi, val))

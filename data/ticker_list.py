"""S&P 500 + 주요 ETF 종목 리스트 — 검색 자동완성용.

사용법:
    from data.ticker_list import search_tickers
    results = search_tickers("NV", limit=8)
"""

# S&P 500 주요 종목 + ETF (ticker, name)
# 전체 500개를 하드코딩하면 파일이 너무 크므로, 주요 150개 + ETF 포함
TICKER_DB: list[tuple[str, str]] = [
    # Mega Cap
    ("AAPL", "Apple Inc."),
    ("MSFT", "Microsoft Corp."),
    ("GOOGL", "Alphabet Inc. Class A"),
    ("GOOG", "Alphabet Inc. Class C"),
    ("AMZN", "Amazon.com Inc."),
    ("NVDA", "NVIDIA Corp."),
    ("META", "Meta Platforms Inc."),
    ("TSLA", "Tesla Inc."),
    ("BRK.B", "Berkshire Hathaway Class B"),
    ("TSM", "Taiwan Semiconductor"),
    # Large Cap Tech
    ("AVGO", "Broadcom Inc."),
    ("ORCL", "Oracle Corp."),
    ("CRM", "Salesforce Inc."),
    ("AMD", "Advanced Micro Devices"),
    ("ADBE", "Adobe Inc."),
    ("INTC", "Intel Corp."),
    ("QCOM", "Qualcomm Inc."),
    ("TXN", "Texas Instruments"),
    ("IBM", "IBM Corp."),
    ("NOW", "ServiceNow Inc."),
    ("AMAT", "Applied Materials"),
    ("MU", "Micron Technology"),
    ("LRCX", "Lam Research"),
    ("KLAC", "KLA Corp."),
    ("SNPS", "Synopsys Inc."),
    ("CDNS", "Cadence Design Systems"),
    ("MRVL", "Marvell Technology"),
    ("PANW", "Palo Alto Networks"),
    ("CRWD", "CrowdStrike Holdings"),
    ("FTNT", "Fortinet Inc."),
    ("ZS", "Zscaler Inc."),
    ("NET", "Cloudflare Inc."),
    ("DDOG", "Datadog Inc."),
    ("SNOW", "Snowflake Inc."),
    ("PLTR", "Palantir Technologies"),
    ("SHOP", "Shopify Inc."),
    ("SQ", "Block Inc."),
    ("UBER", "Uber Technologies"),
    ("ABNB", "Airbnb Inc."),
    ("COIN", "Coinbase Global"),
    # Healthcare
    ("UNH", "UnitedHealth Group"),
    ("JNJ", "Johnson & Johnson"),
    ("LLY", "Eli Lilly and Co."),
    ("ABBV", "AbbVie Inc."),
    ("MRK", "Merck & Co."),
    ("PFE", "Pfizer Inc."),
    ("TMO", "Thermo Fisher Scientific"),
    ("ABT", "Abbott Laboratories"),
    ("DHR", "Danaher Corp."),
    ("BMY", "Bristol-Myers Squibb"),
    ("AMGN", "Amgen Inc."),
    ("GILD", "Gilead Sciences"),
    ("ISRG", "Intuitive Surgical"),
    ("VRTX", "Vertex Pharmaceuticals"),
    ("REGN", "Regeneron Pharma"),
    ("MDT", "Medtronic PLC"),
    # Financials
    ("JPM", "JPMorgan Chase"),
    ("V", "Visa Inc."),
    ("MA", "Mastercard Inc."),
    ("BAC", "Bank of America"),
    ("WFC", "Wells Fargo"),
    ("GS", "Goldman Sachs"),
    ("MS", "Morgan Stanley"),
    ("BLK", "BlackRock Inc."),
    ("SCHW", "Charles Schwab"),
    ("AXP", "American Express"),
    ("C", "Citigroup Inc."),
    ("PYPL", "PayPal Holdings"),
    # Consumer
    ("WMT", "Walmart Inc."),
    ("PG", "Procter & Gamble"),
    ("KO", "Coca-Cola Co."),
    ("PEP", "PepsiCo Inc."),
    ("COST", "Costco Wholesale"),
    ("MCD", "McDonald's Corp."),
    ("NKE", "Nike Inc."),
    ("SBUX", "Starbucks Corp."),
    ("TGT", "Target Corp."),
    ("HD", "Home Depot"),
    ("LOW", "Lowe's Companies"),
    ("TJX", "TJX Companies"),
    ("LULU", "Lululemon Athletica"),
    # Industrials
    ("CAT", "Caterpillar Inc."),
    ("DE", "Deere & Company"),
    ("UPS", "United Parcel Service"),
    ("BA", "Boeing Co."),
    ("HON", "Honeywell International"),
    ("RTX", "RTX Corp."),
    ("LMT", "Lockheed Martin"),
    ("NOC", "Northrop Grumman"),
    ("GD", "General Dynamics"),
    ("GE", "GE Aerospace"),
    # Energy
    ("XOM", "Exxon Mobil"),
    ("CVX", "Chevron Corp."),
    ("COP", "ConocoPhillips"),
    ("SLB", "Schlumberger"),
    ("EOG", "EOG Resources"),
    # Communication
    ("DIS", "Walt Disney Co."),
    ("NFLX", "Netflix Inc."),
    ("CMCSA", "Comcast Corp."),
    ("T", "AT&T Inc."),
    ("VZ", "Verizon Communications"),
    ("TMUS", "T-Mobile US"),
    # Real Estate
    ("AMT", "American Tower"),
    ("PLD", "Prologis Inc."),
    ("CCI", "Crown Castle"),
    ("EQIX", "Equinix Inc."),
    ("SPG", "Simon Property Group"),
    # Utilities
    ("NEE", "NextEra Energy"),
    ("DUK", "Duke Energy"),
    ("SO", "Southern Company"),
    # Materials
    ("LIN", "Linde PLC"),
    ("APD", "Air Products"),
    ("SHW", "Sherwin-Williams"),
    ("FCX", "Freeport-McMoRan"),
    # Clean Energy / Space / Cybersecurity (Phase 4-5 themes)
    ("ENPH", "Enphase Energy"),
    ("SEDG", "SolarEdge Technologies"),
    ("FSLR", "First Solar"),
    ("PLUG", "Plug Power"),
    ("RUN", "Sunrun Inc."),
    ("RKLB", "Rocket Lab USA"),
    ("ASTS", "AST SpaceMobile"),
    ("LUNR", "Intuitive Machines"),
    ("OKTA", "Okta Inc."),
    ("LHX", "L3Harris Technologies"),
    ("HII", "HII (Huntington Ingalls)"),
    # Major ETFs
    ("SPY", "SPDR S&P 500 ETF"),
    ("QQQ", "Invesco QQQ Trust"),
    ("IWM", "iShares Russell 2000"),
    ("DIA", "SPDR Dow Jones ETF"),
    ("VOO", "Vanguard S&P 500 ETF"),
    ("VTI", "Vanguard Total Stock Market"),
    ("ARKK", "ARK Innovation ETF"),
    ("XLK", "Technology Select Sector SPDR"),
    ("XLF", "Financial Select Sector SPDR"),
    ("XLE", "Energy Select Sector SPDR"),
    ("XLV", "Health Care Select Sector SPDR"),
    ("SOXX", "iShares Semiconductor ETF"),
    ("SMH", "VanEck Semiconductor ETF"),
    # Crypto-related
    ("MSTR", "MicroStrategy Inc."),
    ("MARA", "Marathon Digital"),
    ("RIOT", "Riot Platforms"),
]


def search_tickers(query: str, limit: int = 8) -> list[dict[str, str]]:
    """쿼리 문자열로 종목 검색. ticker prefix 우선, name 포함 차순.

    Returns:
        [{"ticker": "NVDA", "name": "NVIDIA Corp."}, ...]
    """
    q = query.strip().upper()
    if not q:
        return []

    prefix_matches = []
    name_matches = []

    for ticker, name in TICKER_DB:
        if ticker.upper().startswith(q):
            prefix_matches.append({"ticker": ticker, "name": name})
        elif q.lower() in name.lower():
            name_matches.append({"ticker": ticker, "name": name})

    results = prefix_matches + name_matches
    return results[:limit]

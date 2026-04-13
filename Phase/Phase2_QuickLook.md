# Phase 2 — Quick Look `✅ 완료`

> 티커 입력 시 시세, 차트, 재무 지표, 기술적 지표를 즉시 반환하는 데이터 수집 계층 완성

**상태**: ✅ 완료
**선행 조건**: Phase 1 완료 (API 래퍼 + 캐싱 사용 가능)

---

## 개요

Quick Look은 AI를 사용하지 않는 순수 데이터 조회 기능이다. 티커를 받으면 4개 API에서 병렬로 시세, 히스토리, 재무, 기술지표를 수집하여 dict/DataFrame으로 반환한다. 이 데이터는 Phase 3(AI Agent)에서 재사용되므로 **이 Phase가 전체 프로젝트의 데이터 기반**이 된다. 화면 렌더링은 UI Phase에서 처리하고, 여기서는 데이터 수집 함수만 개발한다.

---

## 완료 예정 / 완료 항목

| # | 모듈 | 상태 | 설명 |
|---|---|---|---|
| 1 | `data/quote.py` | ✅ | 시세 수집 (`get_quote`, `get_premarket`) |
| 2 | `data/history.py` | ✅ | 주가 히스토리 (`get_history`) |
| 3 | `data/fundamentals.py` | ✅ | 재무 지표 (`get_fundamentals`) |
| 4 | `data/technicals.py` | ✅ | 기술적 지표 (`get_technicals`) |
| 5 | `utils/indicators.py` | ✅ | 기술지표 Python 직접 계산 (Twelve Data 폴백) |
| 6 | `utils/chart_builder.py` | ✅ | Plotly figure 객체 생성 |
| 7 | `utils/tooltips.py` | ✅ | 지표별 인라인 설명 텍스트 |

---

## 시세 수집 (quote.py)

### 목적
현재가, 등락, 거래량, 일중 범위, 장 전/후 시세 수집

### 핵심 함수
```python
def get_quote(ticker: str) -> dict | None:
    """Finnhub → yfinance 폴백"""
    return {
        "price": 142.50,
        "change": 3.20,
        "change_percent": 2.3,
        "volume": 45_000_000,
        "day_high": 144.00,
        "day_low": 140.10,
        "source": "finnhub"
    }

def get_premarket(ticker: str) -> dict | None:
    """장 전/장 후 시세. 없으면 None"""
```

### 설계 결정 사항
- Finnhub이 1순위 (준실시간), yfinance가 폴백
- 잘못된 티커 입력 시 None 반환 (에러 raise 하지 않음)
- 결과에 `source` 필드 포함 (어디서 가져왔는지 추적)
- **캐시 TTL 60초** — 시세는 실시간 변동하므로 다른 데이터(5분)보다 짧게 설정. 재무/차트/기술지표는 1분 내 거의 변하지 않으므로 TTL 5분 유지

---

## 주가 히스토리 (history.py)

### 목적
기간별 OHLCV 데이터프레임 반환 (차트용)

### 핵심 함수
```python
def get_history(ticker: str, period: str) -> pd.DataFrame | None:
    """period: '1W','1M','3M','6M','1Y','5Y'"""
    # 반환: Date, Open, High, Low, Close, Volume 컬럼
```

### 설계 결정 사항
- 소스: yfinance (히스토리 데이터는 yfinance가 가장 풍부)
- 50일/200일 이동평균은 DataFrame에 컬럼 추가하여 반환
- 기간 문자열을 yfinance period 파라미터로 매핑

---

## 재무 지표 (fundamentals.py)

### 목적
PE, Forward PE, EPS, PEG, 시가총액, 52주 고저, 배당률, D/E, 섹터, 산업 등

### 핵심 함수
```python
def get_fundamentals(ticker: str, force_fallback=False) -> dict | None:
    """yfinance (.info) → Finviz 폴백"""
    return {
        "pe": 35.2, "forward_pe": 28.1, "eps": 4.05,
        "peg": 1.8, "market_cap": 3_500_000_000_000,
        "week52_high": 153.0, "week52_low": 76.0,
        "dividend_yield": 0.0003, "de_ratio": 0.41,
        "sector": "Technology", "industry": "Semiconductors",
        "source": "yfinance"
    }
```

### 설계 결정 사항
- yfinance 1순위, Finviz 폴백 (FMP 무료 플랜 403 제한으로 대체)
- `force_fallback=True` 파라미터: 테스트에서 Finviz 폴백 경로 강제 확인용
- sector, industry 필드는 Phase 5(Compare Mode)의 섹터 판정에 재사용

---

## 기술적 지표 (technicals.py)

### 목적
RSI, MACD, 볼린저밴드, MA, 거래량 추이 + 신호 판정

### 핵심 함수
```python
def get_technicals(ticker: str, force_fallback=False) -> dict | None:
    """Twelve Data → Python 직접 계산 폴백"""
    return {
        "rsi": {"value": 62, "signal": "neutral"},
        "macd": {"signal": "bullish", "detail": "bullish crossover 3일째"},
        "bollinger": {"position": "middle", "signal": "neutral"},
        "ma50": {"vs_price": "+3.1%", "signal": "bullish"},
        "ma200": {"vs_price": "+17.3%", "signal": "bullish"},
        "volume": {"vs_20d_avg": "+15%", "signal": "neutral"}
    }
```

### 설계 결정 사항
- Twelve Data 1순위 (API가 지표를 직접 계산하여 반환)
- 폴백: `indicators.py`에서 yfinance 가격 데이터로 Python 직접 계산
- 각 지표에 `signal` 필드: "bullish" / "neutral" / "bearish"
- RSI 70+ → bearish(과매수), 30- → bullish(과매도), 사이 → neutral

---

## 차트 빌더 (chart_builder.py)

### 목적
Plotly figure 객체 생성 (렌더링은 UI Phase)

### 핵심 함수
```python
def build_price_chart(df, chart_type="line", show_ma=True) -> go.Figure:
    """chart_type: 'line' | 'candlestick'"""
```

### 설계 결정 사항
- 라인 / 캔들스틱 전환 가능
- MA 오버레이 (50일, 200일)
- 하단 거래량 바 차트 (subplot)
- Plotly figure 객체를 반환. `st.plotly_chart(fig)`는 UI Phase에서 호출

---

## 툴팁 데이터 (tooltips.py)

### 목적
지표별 인라인 설명 텍스트 딕셔너리

### 핵심 구조
```python
TOOLTIPS = {
    "pe": "주가수익비율. 주가 / 주당순이익. 높으면 비싸거나 성장 기대.",
    "rsi": "상대강도지수. 70+ 과매수, 30- 과매도.",
    "macd": "이동평균 수렴확산. 골든크로스 = 상승 신호.",
    "market_cap": "시가총액. 주가 x 발행주식수.",
    ...
}
```

---

## 선행 조건 및 의존성

- Phase 1 완료: API 래퍼, 캐싱, api_config 사용 가능
- pip: `yfinance`, `plotly`, `pandas`, `requests`

---

## 캐시 TTL 분리 정책

시세(quote)와 나머지 데이터는 갱신 빈도가 다르므로 TTL을 분리한다.

| 데이터 종류 | TTL | 이유 |
|------------|-----|------|
| 시세 (quote) | 60초 | 주가는 실시간 변동. 1분 이상 지난 시세는 의미 감소 |
| 재무/차트/기술지표 | 5분 | PER, RSI, 차트 히스토리는 1분 내 거의 변하지 않음 |
| AI 분석 결과 | 1시간 | AI 해석은 단기간에 바뀌지 않음 |
| 섹터 정보 | 6시간 | 섹터 구성은 거의 변하지 않음 |

---

## 개발 시 주의사항

- 모든 함수는 Streamlit 의존 없이 순수 Python으로 작성
- 에러 시 None 반환. 화면에서 "N/A" 표시하는 건 UI Phase의 책임
- get_fundamentals의 sector/industry 필드는 Phase 5에서 Compare Mode 판정에 사용됨 — 키 이름 변경 금지
- Quick Look 데이터 전체를 dict로 묶어서 Phase 3 Agent에 전달하는 구조 고려

---

## 변경 이력

| 날짜 | 내용 |
|---|---|
| 2026-04-06 | 최초 작성 |
| 2026-04-08 | Phase 2 전체 완료 — 7개 모듈 구현, 31개 테스트 PASSED |
| 2026-04-10 | 캐시 TTL 분리 정책 추가 — 시세(60초) vs 나머지(5분) |
| 2026-04-13 | fundamentals.py force_fallback 대상을 FMP → Finviz로 변경 |
| 2026-04-13 | 실제 API 테스트 수행 — 19개 테스트 중 18 PASSED, 1 SKIPPED(FMP) → 코드 수정 후 19 PASSED |

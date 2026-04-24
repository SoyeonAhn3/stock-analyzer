# Phase 11 — 코드 품질 개선 (Code Review 기반) `🔲 미시작`

> 4-Agent Code Review Pipeline 리뷰 결과(70/100, C등급) 기반 Top 10 이슈 수정

**상태**: 🔲 미시작
**선행 조건**: Phase 10 완료 (UX 개선 + 데이터 영속화)
**리뷰 리포트**: `code-review-pipeline/output/stock-analyzer_review_report.md`

---

## 개요

4-Agent Code Review Pipeline으로 백엔드 코드 전체(30+ 파일, ~3,300줄)를 분석한 결과 68건의 이슈가 발견되었다 (Critical 12, Warning 52, Info 4). 이 Phase에서는 영향 범위 × ROI 기준 Top 10 이슈를 3단계(보안 → 성능 → 품질)로 수정한다.

---

## 완료 예정 항목

| # | 항목 | 상태 | 심각도 | 난이도 | 예상 소요 |
|---|---|---|---|---|---|
| 1 | API 키 인스턴스 변수 노출 방지 | 🔲 | Critical | 하 | 30분 |
| 2 | API 키 URL 쿼리 파라미터 로그 마스킹 | 🔲 | Critical | 중 | 1시간 |
| 3 | watchlist DELETE+INSERT 트랜잭션 래핑 | 🔲 | Critical | 하 | 30분 |
| 4 | AI 응답 `**result['data']` 무검증 언패킹 수정 | 🔲 | Warning | 하 | 30분 |
| 5 | Anthropic 클라이언트 싱글턴 전환 | 🔲 | Critical | 하 | 30분 |
| 6 | `analyze()` 3개 독립 호출 병렬화 | 🔲 | Critical | 중 | 1시간 |
| 7 | `get_technicals()` 5개 API 호출 병렬화 | 🔲 | Critical | 중 | 1시간 |
| 8 | async Agent 내 동기 `call_claude()` 블로킹 해소 | 🔲 | Critical | 상 | 1시간 |
| 9 | `get_market_indices()` 6개 지수 순차 호출 병렬화 | 🔲 | Critical | 중 | 1시간 |
| 10 | `get_macro_summary()` 4개 HTTP 요청 병렬화 | 🔲 | Critical | 중 | 1시간 |

---

## Step 1: 보안 (항목 #1 ~ #4)

### 1-1. API 키 인스턴스 변수 노출 방지

**현재 상태**: `config/api_config.py`는 이미 `.env` + `os.getenv()` 구조를 사용 중 (L11-15). `.gitignore`에 `.env` 패턴 등록 완료. 리뷰 리포트 Critical #1의 "하드코딩" 지적은 실제와 다르나, **인스턴스 변수 저장** 문제는 유효함.

| 파일 | 라인 | 현재 코드 | 문제 |
|---|---|---|---|
| `data/finnhub_client.py` | L18 | `self._headers = {"X-Finnhub-Token": FINNHUB_API_KEY}` | 객체 직렬화/로그 시 키 노출 |
| `data/fmp_client.py` | L30 | `params["apikey"] = FMP_API_KEY` | 요청 시 dict에 키 삽입 |
| `data/fred_client.py` | L8 | `from config.api_config import FRED_API_KEY` | 모듈 변수 직접 참조 |

**개선 방향**:
- 각 클라이언트 클래스에 `__repr__` 마스킹 추가
- 로그 출력 시 API 키 포함 가능성 있는 dict 마스킹 유틸 함수 작성

### 1-2. API 키 URL 쿼리 파라미터 로그 마스킹

**현재 상태**: FMP, FRED, TwelveData는 API 설계상 쿼리 파라미터로 키를 전송해야 함 (HTTP 헤더 인증 미지원).

| 파일 | 라인 | 전송 방식 |
|---|---|---|
| `data/fmp_client.py` | L30 | `params["apikey"] = FMP_API_KEY` |
| `data/fred_client.py` | 요청 시 | `params["api_key"] = FRED_API_KEY` |
| `data/twelvedata_client.py` | 요청 시 | `params["apikey"] = TWELVEDATA_API_KEY` |

**개선 방향**:
- API 자체가 헤더 인증을 지원하지 않으므로, **로그/에러 출력에서 URL 마스킹** 적용
- 공통 `_sanitize_url()` 유틸 함수 작성 (apikey=xxx → apikey=****)
- Exception 핸들러에서 URL 로깅 시 마스킹 적용

### 1-3. watchlist DELETE+INSERT 트랜잭션 래핑

**현재 상태**: `data/watchlist.py` L117-128

```python
# 현재: DELETE 후 INSERT — 중간에 예외 시 데이터 전체 손실
conn.execute("DELETE FROM watchlist")
for ticker in watchlist:
    conn.execute("INSERT INTO watchlist ...")
conn.commit()
```

**개선 방향**:
- `with conn:` 컨텍스트 매니저로 원자적 트랜잭션 보장
- DB는 이미 WAL 모드 활성화 (`database.py` L84)

### 1-4. AI 응답 무검증 언패킹 수정

**현재 상태**: 5개 Agent가 Claude 응답의 `result['data']`를 검증 없이 `**` 언패킹하여 반환. Prompt Injection 시 임의 키가 주입될 수 있음.

| 파일 | 라인 | 패턴 |
|---|---|---|
| `agents/analyst_agent.py` | ~L175 | `**result['data']` 무검증 |
| `agents/cross_validation.py` | ~L232 | 동일 패턴 |
| `agents/news_agent.py` | ~L59 | 동일 패턴 |
| `agents/data_agent.py` | ~L60 | 동일 패턴 |
| `agents/macro_agent.py` | ~L62 | 동일 패턴 |

**개선 방향**:
- Agent별 허용 키 화이트리스트 정의
- `{k: v for k, v in result['data'].items() if k in ALLOWED_KEYS}` 패턴 적용

---

## Step 2: 성능 (항목 #5 ~ #10)

### 2-1. Anthropic 클라이언트 싱글턴 전환

**현재 상태**: `agents/claude_client.py` L55 — `call_claude()` 호출마다 `Anthropic()` 인스턴스 새로 생성. 매번 TCP handshake 반복.

**개선 방향**:
- 모듈 레벨에서 `_client = None` 선언
- 첫 호출 시 1회 초기화 후 재사용 (lazy singleton)

### 2-2. analyze() 3개 독립 호출 병렬화

**현재 상태**: `backend/routers/analysis.py` L29-34 — `get_quote()`, `get_fundamentals()`, `get_technicals()` 3개를 순차 실행.

**개선 방향**:
```python
# Before: 직렬 (~1.5초+)
quote = client.get_quote(ticker)
fundamentals = client.get_fundamentals(ticker)
technicals = client.get_technicals(ticker)

# After: 병렬 (~0.5초)
quote, fundamentals, technicals = await asyncio.gather(
    asyncio.to_thread(client.get_quote, ticker),
    asyncio.to_thread(client.get_fundamentals, ticker),
    asyncio.to_thread(client.get_technicals, ticker),
)
```

### 2-3. get_technicals() 5개 API 호출 병렬화

**현재 상태**: `data/api_client.py` L142-146 — RSI, MACD, Bollinger, MA50, MA200 5개 TwelveData 호출 순차 실행.

**개선 방향**:
- `concurrent.futures.ThreadPoolExecutor`로 5개 요청 병렬 실행
- 개별 실패 시 해당 지표만 None 처리 (부분 실패 허용)

### 2-4. async Agent 내 동기 call_claude() 블로킹 해소

**현재 상태**: 3개 Agent의 `async def run()` 내에서 동기 `call_claude()`를 직접 호출하여 이벤트 루프 블로킹.

| 파일 | 라인 |
|---|---|
| `agents/news_agent.py` | L57 |
| `agents/data_agent.py` | L60 |
| `agents/macro_agent.py` | L62 |

**개선 방향**:
- `result = await asyncio.to_thread(call_claude, SYSTEM_PROMPT, user_message)` 로 전환
- 또는 `call_claude()` 자체를 `async` + `AsyncAnthropic`으로 전환 (싱글턴 전환과 동시 적용)

### 2-5. get_market_indices() 6개 지수 병렬화

**현재 상태**: `data/yfinance_client.py` L109-126 — SPY, NASDAQ, DOW, BTC, ETH, VIX를 for 루프에서 순차 조회. 하나 실패 시 전체 None 반환.

**개선 방향**:
- `ThreadPoolExecutor`로 6개 지수 병렬 조회
- 부분 실패 허용: 성공한 지수만 포함하여 반환

### 2-6. get_macro_summary() 4개 HTTP 요청 병렬화

**현재 상태**: `data/fred_client.py` L93-98 — `get_fed_rate()`, `get_cpi()`, `get_unemployment()`, `get_treasury_spread()` 4개 순차 호출.

**개선 방향**:
- `ThreadPoolExecutor`로 4개 FRED API 요청 병렬 실행
- `get_treasury_spread()` 내부의 10Y/2Y 2개 호출도 병렬화

---

## Step 3: 코드 품질 (추가 개선)

> Top 10 수정 과정에서 자연스럽게 함께 적용할 Warning 수준 개선 사항

| # | 파일 | 이슈 | 개선 |
|---|---|---|---|
| 1 | `agents/sector_analyzer.py` L215 | `time.sleep(3)` → async 컨텍스트 블로킹 | `await asyncio.sleep(3)` 전환 |
| 2 | `data/finnhub_client.py` L59 | `datetime.now()` 2회 호출 → 날짜 불일치 가능 | 1회 저장 후 재사용 |
| 3 | `data/finnhub_client.py` L55 | 함수 내부 `import datetime` | 모듈 최상단으로 이동 |
| 4 | `data/fmp_client.py` L93 | 수동 중앙값 계산 | `statistics.median()` 사용 |
| 5 | `backend/routers/alerts.py` L270 | 정적 경로(`/triggered`) vs 동적 경로(`/{alert_id}`) 충돌 | 정적 경로 먼저 등록 |

---

## 예상 효과

| 지표 | Before | After (예상) |
|---|---|---|
| 리뷰 점수 | 70/100 (C) | 85+ (B) |
| Critical 이슈 | 12건 | 2건 이하 |
| 단일 종목 분석 응답 시간 | ~4초+ | ~1.5초 |
| 메인 페이지 로딩 (지수) | ~3초+ | ~0.8초 |
| 매크로 데이터 조회 | ~1.2초+ | ~0.4초 |

---

## 관련 파일

| 위치 | 파일 | 역할 |
|---|---|---|
| Config | `config/api_config.py` | API 키 + 엔드포인트 설정 |
| Core | `agents/claude_client.py` | Anthropic API 래퍼 |
| Core | `data/api_client.py` | 통합 API 클라이언트 (Fallback) |
| Core | `data/database.py` | SQLite 관리 |
| Core | `data/watchlist.py` | Watchlist CRUD |
| Agent | `agents/news_agent.py` | 뉴스 감성 분석 Agent |
| Agent | `agents/data_agent.py` | 재무/기술 분석 Agent |
| Agent | `agents/macro_agent.py` | 매크로 분석 Agent |
| Agent | `agents/analyst_agent.py` | 애널리스트 Agent |
| Agent | `agents/cross_validation.py` | 교차 검증 Agent |
| Agent | `agents/sector_analyzer.py` | 섹터 스크리닝 |
| Data | `data/finnhub_client.py` | Finnhub API |
| Data | `data/fmp_client.py` | FMP API |
| Data | `data/fred_client.py` | FRED API |
| Data | `data/yfinance_client.py` | yfinance |
| Router | `backend/routers/analysis.py` | 분석 엔드포인트 |
| Router | `backend/routers/alerts.py` | 알림 엔드포인트 |

---

## 설계 결정 사항

| 결정 | 선택 | 이유 |
|---|---|---|
| API 키 관리 | `.env` + `os.getenv()` 유지 | 이미 적용된 구조, 추가 전환 불필요 |
| 병렬화 방식 | `asyncio.to_thread()` + `ThreadPoolExecutor` | 기존 동기 클라이언트를 async로 전면 재작성하지 않고 점진적 개선 |
| Claude 클라이언트 | 동기 싱글턴 + `to_thread()` | AsyncAnthropic 전환은 전면 리팩토링 필요, 현 단계에서는 과도 |
| 트랜잭션 | `with conn:` 컨텍스트 매니저 | SQLite 내장 트랜잭션 지원 활용 |

---

## 변경 이력

| 날짜 | 내용 |
|---|---|
| 2026-04-24 | Phase 11 문서 신규 생성 (Code Review 기반 품질 개선) |

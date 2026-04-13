# Phase 1 — 프로젝트 기반 + API 연동 `✅ 완료`

> 프로젝트 구조 세팅, 5개 외부 API 래퍼 개발, 폴백 로직, 캐싱 모듈 완성

**상태**: ✅ 완료
**선행 조건**: 없음 (최초 Phase)

---

## 개요

프로젝트 디렉토리 구조를 잡고, 5개 금융 데이터 API(yfinance, Finnhub, Twelve Data, FMP, FRED)의 래퍼 클래스를 개발한다. API 실패 시 자동으로 대체 소스를 시도하는 폴백 로직과, 중복 호출을 방지하는 캐싱 모듈을 포함한다. 이 Phase가 완료되면 이후 모든 Phase에서 `api_client.get_quote("NVDA")` 한 줄로 안정적인 데이터를 받을 수 있다.

---

## 완료 예정 / 완료 항목

| # | 모듈 | 상태 | 설명 |
|---|---|---|---|
| 1 | `config/api_config.py` | ✅ | API 키 로딩, 엔드포인트, 타임아웃 |
| 2 | `config/themes.json` | ✅ | 커스텀 테마 종목 리스트 |
| 3 | `config/related_industries.json` | ✅ | 관련 업종 매핑 테이블 |
| 4 | `data/yfinance_client.py` | ✅ | yfinance 래퍼 |
| 5 | `data/finnhub_client.py` | ✅ | Finnhub 래퍼 |
| 6 | `data/twelvedata_client.py` | ✅ | Twelve Data 래퍼 |
| 7 | `data/fmp_client.py` | ✅ | FMP 래퍼 (무료 플랜 제한으로 폴백 전용) |
| 8 | `data/fred_client.py` | ✅ | FRED 래퍼 |
| 9 | `data/finviz_client.py` | ✅ | Finviz 래퍼 (FMP 대체 — 섹터 스크리닝/PE) |
| 10 | `data/api_client.py` | ✅ | 통합 API 클라이언트 (폴백 로직) |
| 11 | `data/cache.py` | ✅ | 캐싱 모듈 |
| 12 | `utils/usage_tracker.py` | ✅ | AI 일일 사용량 추적 |

---

## 프로젝트 구조

### 목적
전체 프로젝트의 디렉토리 구조를 확정한다.

### 구현 파일
```
stock-analyzer/
├── app.py                        # Streamlit 메인 엔트리 (UI Phase에서 작성)
├── requirements.txt
├── .env                          # API 키 (gitignore)
├── config/
│   ├── api_config.py
│   ├── themes.json
│   └── related_industries.json
├── data/
│   ├── api_client.py
│   ├── yfinance_client.py
│   ├── finnhub_client.py
│   ├── twelvedata_client.py
│   ├── fmp_client.py
│   ├── fred_client.py
│   └── cache.py
├── agents/
│   ├── orchestrator.py
│   ├── news_agent.py
│   ├── data_agent.py
│   ├── macro_agent.py
│   ├── cross_validation.py
│   └── analyst_agent.py
├── screens/                      # UI Phase에서 작성
├── utils/
│   ├── tooltips.py
│   ├── indicators.py
│   └── usage_tracker.py
├── tests/
│   ├── test_phase1_api.py
│   ├── test_phase2_quick_look.py
│   ├── test_phase3_ai_analysis.py
│   ├── test_phase4_sector.py
│   └── test_phase5_compare.py
└── Phase/                        # Phase 문서
```

---

## API 클라이언트

### 목적
5개 API 각각의 래퍼 클래스 + 통합 클라이언트 (폴백 포함)

### 설계 결정 사항
- 각 래퍼는 공통 인터페이스: `get_quote()`, `get_history()`, `get_fundamentals()` 등
- 타임아웃: 15초
- 에러 시 None 반환 (호출자가 폴백 판단)
- 호출 카운터 내장 (일일 제한 추적용)
- 통합 클라이언트가 API 우선순위 테이블에 따라 폴백 자동 실행
- 성공한 소스명을 결과에 포함 (`"source": "finnhub"`)
- FMP 무료 플랜 403 제한 → Finviz(finvizfinance)로 섹터 스크리닝/PE 대체 (2026-04-13)

---

## 캐싱 모듈

### 목적
동일 데이터 중복 호출 방지

### 설계 결정 사항
- 키: (함수명, 티커, 파라미터) 조합
- TTL: 시세(quote) 60초, Quick Look(재무/차트/기술지표) 5분, AI 결과 1시간, Sector 6시간
- 저장: 딕셔너리 (메모리 캐시). 영구 저장 불필요
- 수동 무효화: `cache.invalidate(ticker)` 지원
- `cache.force_expire()`: 테스트용 강제 만료

---

## 선행 조건 및 의존성

- .env에 API 키 5개 세팅 필요:
  - `FINNHUB_API_KEY`
  - `TWELVEDATA_API_KEY`
  - `FMP_API_KEY` (무료 플랜 제한으로 폴백 전용)
  - `FRED_API_KEY`
  - `ANTHROPIC_API_KEY`
- yfinance, Finviz는 API 키 불필요

---

## 네트워크 제약 대비

> 네트워크 환경에 따라 금융 API가 차단될 가능성이 있어, 이에 대비한 테스트 전략을 기록한다.

- 금융 데이터 API(Yahoo Finance, Finnhub, TwelveData, FMP)는 네트워크 정책에 따라 접속이 차단될 수 있음
- FRED(api.stlouisfed.org)는 정부 경제데이터로 대부분 환경에서 접속 가능

### 테스트 전략

네트워크 차단 가능성에 대비하여 실제 API 테스트 + 단위 테스트 방식을 채택:

| 구분 | 방식 | 비고 |
|------|------|------|
| yfinance / Finnhub / TwelveData / FMP | **실제 API 테스트** | 접속 가능한 환경에서 수행 |
| FRED | **실제 API 테스트** | 대부분 환경에서 접속 가능 |
| 캐시 / 폴백 / 사용량 추적 | **단위 테스트** | 네트워크 무관, 순수 로직 검증 |

테스트 파일:
- `tests/test_phase1_real_api.py` — 27개 실제 API 테스트: 24 PASSED, 3 SKIPPED (FMP 403) (2026-04-13)

---

## 개발 시 주의사항

- yfinance는 비공식 라이브러리. 메인 의존하지 말고 1순위 시도 소스로만 사용
- Finnhub 무료 티어 시세는 약 15분 지연. "실시간"이라 표현하지 않기
- FMP 무료 일 250회, Twelve Data 일 800회 — 테스트 중 과다 호출 주의
- .env 파일은 반드시 .gitignore에 추가
- 네트워크 환경에 따라 금융 API 접속이 차단될 수 있음 — 실제 연동 테스트는 접속 가능한 환경에서 수행

---

## 변경 이력

| 날짜 | 내용 |
|---|---|
| 2026-04-06 | 최초 작성 |
| 2026-04-08 | 네트워크 제약 대비 및 테스트 전략 기록 |
| 2026-04-08 | Phase 1 전체 완료 — 11개 모듈 구현, 19개 테스트 PASSED |
| 2026-04-13 | FMP 무료 플랜 403 제한 발견 → Finviz(finvizfinance) 래퍼 추가, 폴백 우선순위 변경 |
| 2026-04-13 | 실제 API 테스트 수행 — 27개 테스트 중 24 PASSED, 3 SKIPPED (FMP) |

# AI Stock Analyzer

> Multi-Agent 미국 주식 종합 분석 시스템

미국 주식 티커를 입력하면 실시간 시세, 차트, 재무 지표를 즉시 보여주고, AI Agent 5명이 뉴스, 데이터, 매크로를 병렬 수집하여 교차 검증 후 매수/중립/매도 의견을 제시하는 시스템.

---

## 핵심 기능

| 모드 | 설명 | AI 사용 | 소요 시간 |
|------|------|:-------:|:---------:|
| **Quick Look** | 시세 + 차트 + 재무 + 기술지표 조회 | X | ~1초 |
| **AI Deep Analysis** | 5개 Agent 병렬 분석 + 교차 검증 + 종합 판단 | O | 1~2분 |
| **Sector Screening** | 섹터별 3단계 필터 + AI 축약 분석 + Top 5 추천 | O | 2~3분 |
| **Compare Mode** | 2~3 종목 비교 (same/cross sector 자동 감지) | O | ~1분 |
| **Beginner's Guide** | 주식 용어/지표/차트 교육 페이지 | X | - |

---

## 시스템 아키텍처

```
[사용자] → React (브라우저)
               │ HTTP/JSON
               ▼
          FastAPI 백엔드 (localhost:8000)
               │
               ├── /api/quote/* ──→ [데이터 계층] ──→ 시세/차트/재무/기술지표
               │                        │
               │                        ├── yfinance (주가/재무)
               │                        ├── Finnhub (시세/뉴스)
               │                        ├── Twelve Data (기술지표)
               │                        ├── Finviz (섹터 스크리닝)
               │                        ├── FMP (재무 폴백)
               │                        └── FRED (매크로 경제)
               │
               ├── /api/analysis/* ──→ AI Agent 계층
               │                        │
               │                        ├──[병렬]── News Agent ──┐
               │                        ├──[병렬]── Data Agent ──┼──→ Cross-validation ──→ Analyst
               │                        └──[병렬]── Macro Agent ─┘        Agent               Agent
               │                                                                                │
               │                                                                        BUY / HOLD / SELL
               │
               ├── /api/sector/* ──→ 3단계 필터 ──→ AI 축약 분석 ──→ Top 5
               │
               └── /api/compare/* ──→ 비교 유형 판정 ──→ AI 비교 분석
```

---

## 기술 스택

| 역할 | 도구 | 비용 |
|------|------|------|
| AI Agent | Claude API (Sonnet) | 월 ~$15-20 |
| 주가/재무 | yfinance | 무료 |
| 시세/뉴스 | Finnhub | 무료 (분당 60회) |
| 기술적 지표 | Twelve Data | 무료 (일 800회) |
| 섹터 스크리닝 | Finviz (finvizfinance) | 무료 |
| 재무 폴백 | FMP | 무료 (일 250회, 일부 엔드포인트 제한) |
| 매크로 경제 | FRED API | 무료 |
| 백엔드 API | FastAPI + Uvicorn | 무료 |
| 프론트엔드 | React + TypeScript + Vite | 무료 |
| 차트 | Lightweight Charts (또는 Plotly React) | 무료 |
| 오케스트레이터 | Python asyncio | 무료 |

---

## 프로젝트 구조

```
stock-analyzer/
├── requirements.txt
├── .env                            # API 키 (gitignore)
│
├── config/                         # 설정
│   ├── api_config.py               # API 키 로딩, 엔드포인트, 타임아웃
│   ├── themes.json                 # 커스텀 테마 종목 리스트
│   └── related_industries.json     # 관련 업종 매핑 테이블
│
├── data/                           # 데이터 계층 (Phase 1~5)
│   ├── api_client.py               # 통합 API 클라이언트 (폴백 로직)
│   ├── yfinance_client.py          # yfinance 래퍼
│   ├── finnhub_client.py           # Finnhub 래퍼
│   ├── twelvedata_client.py        # Twelve Data 래퍼
│   ├── fmp_client.py               # FMP 래퍼 (폴백 전용)
│   ├── finviz_client.py            # Finviz 래퍼 (섹터 스크리닝/PE)
│   ├── fred_client.py              # FRED 래퍼
│   ├── cache.py                    # 캐싱 모듈
│   ├── quote.py                    # 시세 수집
│   ├── history.py                  # 주가 히스토리
│   ├── fundamentals.py             # 재무 지표
│   ├── technicals.py               # 기술적 지표
│   ├── sector_data.py              # GICS 섹터 종목 조회
│   ├── stock_filter.py             # 3단계 필터
│   ├── theme_manager.py            # themes.json CRUD
│   ├── compare.py                  # 비교 유형 판정
│   ├── style_classifier.py         # 투자 스타일 분류
│   ├── watchlist.py                # Watchlist 관리
│   ├── guide_content.py            # 가이드 콘텐츠
│   └── market_overview.py          # 시장 지수/급등락/뉴스
│
├── agents/                         # AI Agent 계층 (Phase 3~5)
│   ├── claude_client.py            # Claude API 기본 호출
│   ├── orchestrator.py             # Agent 오케스트레이터
│   ├── news_agent.py               # 뉴스 감성 분석
│   ├── data_agent.py               # 재무/기술지표 해석
│   ├── macro_agent.py              # 거시경제 분석
│   ├── cross_validation.py         # Agent 간 교차 검증
│   ├── analyst_agent.py            # 종합 판단
│   ├── sector_analyzer.py          # 섹터 AI 축약 분석
│   └── compare_agent.py            # AI 비교 분석
│
├── backend/                        # FastAPI 백엔드 (Phase 6)
│   ├── main.py                     # 서버 시작점 + CORS
│   ├── schemas.py                  # Pydantic 요청/응답 모델
│   └── routers/
│       ├── quote.py                # /api/quote, fundamentals, technicals, history
│       ├── market.py               # /api/market/indices, movers, news
│       ├── analysis.py             # /api/analysis (AI 5-Agent)
│       ├── sector.py               # /api/sector, themes
│       ├── compare.py              # /api/compare
│       ├── watchlist.py            # /api/watchlist CRUD
│       └── guide.py                # /api/guide
│
├── frontend/                       # React 프론트엔드 (Phase 7~9)
│   ├── package.json
│   ├── vite.config.ts
│   └── src/
│       ├── App.tsx                 # 앱 시작점 + 라우팅
│       ├── theme/                  # 디자인 시스템 (Dark/Light)
│       ├── components/             # 재사용 UI 컴포넌트
│       ├── pages/                  # 화면별 페이지
│       ├── hooks/                  # API 호출 로직
│       └── types/                  # TypeScript 타입
│
├── utils/
│   ├── tooltips.py                 # 지표별 설명 텍스트
│   ├── indicators.py               # 기술지표 Python 계산 (폴백)
│   └── usage_tracker.py            # AI 일일 사용량 추적
│
├── tests/
│   ├── test_phase1_real_api.py     # Phase 1 실제 API 테스트 (27개)
│   ├── test_phase2_real_api.py     # Phase 2 실제 API 테스트 (19개)
│   ├── test_phase3_real_api.py     # Phase 3 실제 API 테스트 (9개)
│   ├── test_phase4_sector.py
│   └── test_phase5_compare.py
│
├── Phase/                          # Phase 개발 문서
│   ├── Phase1_프로젝트기반_API연동.md              # ✅ 완료
│   ├── Phase2_QuickLook.md                        # ✅ 완료
│   ├── Phase3_AI_DeepAnalysis.md                  # ✅ 완료
│   ├── Phase4_SectorScreening.md                  # ✅ 완료
│   ├── Phase5_Compare_Watchlist_Guide_Overview.md # ✅ 완료
│   ├── Phase6_FastAPI_백엔드.md                    # 🔲 미시작
│   ├── Phase7_React_셋업_디자인_레이아웃.md         # 🔲 미시작
│   ├── Phase8_QuickLook_AI분석_화면.md             # 🔲 미시작
│   ├── Phase9_나머지화면_최종통합.md                # 🔲 미시작
│   └── Phase10_UX개선_데이터영속화.md              # 🔲 미시작
│
└── pre-requirement/                # 기획 문서
    ├── draft.txt                   # 기능 기술서
    ├── design-spec.md              # 디자인 스펙 (권위 문서)
    └── Stock Analyzer UI.png       # UI 레퍼런스 이미지
```

---

## Phase별 개발 계획

### 기능 개발 (Phase 1~5)

| Phase | 이름 | 상태 | 핵심 산출물 |
|:-----:|------|:----:|-----------|
| 1 | 프로젝트 기반 + API 연동 | ✅ | 6개 API 래퍼 + 폴백 + 캐싱 |
| 2 | Quick Look | ✅ | 시세 + 차트 + 재무 + 기술지표 |
| 3 | AI Deep Analysis | ✅ | 5 Agent 파이프라인 + Graceful Degradation |
| 4 | Sector Screening | ✅ | 3단계 필터 + AI 축약 + Top 5 |
| 5 | Compare + Watchlist + Guide + Overview | ✅ | 나머지 데이터 로직 전부 |

### 백엔드 + 프론트엔드 (Phase 6~9) — React 전환

| Phase | 이름 | 상태 | 핵심 산출물 |
|:-----:|------|:----:|-----------|
| 6 | FastAPI 백엔드 | 🔲 | REST API 15개 엔드포인트 + CORS + Pydantic |
| 7 | React 셋업 + 디자인 시스템 + 레이아웃 | 🔲 | 프로젝트 초기화 + 테마 + 사이드바 + 라우팅 + 하단 바 |
| 8 | Quick Look + AI 분석 화면 | 🔲 | 핵심 화면 2개 + 캔들스틱 차트 + 기술 지표 카드 |
| 9 | 나머지 화면 + 최종 통합 | 🔲 | Market Overview + Sector + Compare + Guide + 면책 조항 |

### UX 개선 + 영속화 (Phase 10)

| Phase | 이름 | 상태 | 핵심 산출물 |
|:-----:|------|:----:|-----------|
| 10 | UX 개선 + 데이터 영속화 | 🔲 | 검색 자동완성 + Watchlist UI + SQLite + 가격 알림 + 반응형 |

---

## 설계 특징

- **데이터 재사용**: Quick Look 데이터를 AI Agent가 그대로 사용하여 API 호출 최소화
- **캐시 TTL 분리**: 시세(60초)는 짧게, 재무/차트/기술지표(5분)는 길게 — 데이터 특성에 맞춘 갱신 주기
- **Graceful Degradation**: Agent 3개 중 일부 실패해도 나머지로 분석 진행
- **3단계 필터**: 공통 필터 + 유형별 프리셋 4종 + 적응형 완화 (빈 결과 방지)
- **비교 유형 자동 감지**: same_sector / cross_sector를 판정하여 분석 방식 분기
- **AI 환각 방지**: 숫자는 API에서만. AI는 해석만 담당
- **API 폴백 체인**: 1순위 실패 시 자동으로 대체 소스 시도
- **법적 면책**: 모든 AI 분석 결과에 면책 조항 표시

---

## 참조 문서

| 문서 | 위치 | 내용 |
|------|------|------|
| 기능 기술서 | `pre-requirement/draft.txt` | 전체 기능 상세 설계 |
| UI 디자인 계획서 | `pre-requirement/UI.txt` | 컬러/타이포/레이아웃/화면별 디자인 |
| **디자인 스펙 (권위 문서)** | `pre-requirement/design-spec.md` | 컬러 토큰, 레이아웃 구조, Plotly 테마, Settings |
| 데이터 흐름 정리 | `pre-requirement/data_flow.txt` | 사용자 입력 → Quick Look → Deep Analysis 전체 흐름 |
| Phase 문서 | `Phase/Phase*.md` | Phase별 개발 상세 + 테스트 |

---

## 변경 이력

| 날짜 | 내용 |
|------|------|
| 2026-04-06 | 최초 작성. Phase 1~8 문서 생성. |
| 2026-04-08 | Phase 1 완료. 11개 모듈 구현, 19개 테스트 PASSED. |
| 2026-04-08 | Phase 2 완료. 7개 모듈 구현, 31개 테스트 PASSED. |
| 2026-04-10 | 캐시 TTL 분리 정책 적용 — 시세(60초) vs 나머지(5분). |
| 2026-04-10 | Phase 3 완료. 7개 모듈 구현, 29개 테스트 PASSED. |
| 2026-04-13 | FMP 무료 플랜 403 제한 → Finviz 래퍼 추가, 폴백 우선순위 변경. |
| 2026-04-13 | Phase 1 실제 API 테스트 수행 - 27개 중 24 PASSED, 3 SKIPPED (FMP). |
| 2026-04-13 | Phase 2 실제 API 테스트 수행 - 19개 전체 PASSED. |
| 2026-04-13 | Phase 3 실제 API 테스트 수행 - 9개 전체 PASSED (Claude + 금융 API 실호출). |
| 2026-04-14 | Phase 4-5 구현 완료 (원격 병합). Sector Screening + Compare/Watchlist/Guide/Overview. |
| 2026-04-14 | technicals.py — Bollinger 수치 + MACD 히스토그램 값 추가. |
| 2026-04-14 | market_overview — BTC/ETH 추가 (하단 지수 바 6개 항목). |
| 2026-04-14 | design-spec.md 전면 개정 — Dark/Light 동시 지원, Settings 패널, 사이드바 메뉴 5개 확정. |
| 2026-04-14 | Phase 4-8 문서 업데이트 — 최신 설계 결정사항 반영. |
| 2026-04-14 | **React 전환 결정** — Streamlit → FastAPI + React + TypeScript. |
| 2026-04-14 | Phase 6~9 문서 재구성 — Phase 6(FastAPI), 7(React 셋업), 8(핵심 화면), 9(나머지+통합). |

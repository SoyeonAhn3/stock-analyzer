🌐 [한국어](./README_ko.md) | [English](./README.md)

# QuantAI — AI Stock Analyzer

[![Live Demo](https://img.shields.io/badge/Live%20Demo-QuantAI-blue?style=for-the-badge&logo=netlify)](https://stock-analyzer-ai.netlify.app/)

> 6개 금융 API에서 실시간 데이터를 수집하고, 5개 AI 에이전트가 교차 검증을 거쳐 매수/보유/매도 의견을 제시하는 미국 주식 분석 시스템.

## 개요

주식 분석 정보가 여러 플랫폼에 분산되어 있고, 초보자에게는 원시 금융 데이터 해석 자체가 진입 장벽입니다. QuantAI는 실시간 시세, 차트, 재무 지표, 기술 지표, 거시경제 지표를 하나의 대시보드에 통합하고, 5개의 전문 AI 에이전트가 병렬로 분석 후 교차 검증하여 실행 가능한 판단을 도출합니다. 포트폴리오/데모 프로젝트로 제작되었습니다.

### 데모

https://github.com/user-attachments/assets/42a6e030-33c8-4f04-b49e-dd72c07ae4ab

## Manual

| Language | Link |
|---|---|
| English | [User Manual](./manuals/20260512_QuantAI_Manual.md) |

## 목차

- [동작 흐름](#동작-흐름)
- [기술 스택](#기술-스택)
- [AI 구성 요소](#ai-구성-요소)
- [빠른 시작](#빠른-시작)
- [프로젝트 구조](#프로젝트-구조)
- [테스트](#테스트)
- [문서](#문서)
- [현재 상태](#현재-상태)
- [한계점](#한계점)

## 동작 흐름

```
사용자가 티커 입력 (예: NVDA)
        │
        ▼
  React SPA (Vite)
        │  HTTP / JSON
        ▼
  FastAPI 백엔드 (/api)
        │
        ├─ 시세 / 재무 / 기술지표 / 히스토리
        │     └─ yfinance + Finnhub + TwelveData + FMP (폴백)
        │
        ├─ AI Deep Analysis
        │     ├─ [병렬] News Agent ──┐
        │     ├─ [병렬] Data Agent ──┼─→ 교차 검증 → Analyst Agent
        │     └─ [병렬] Macro Agent ─┘                   │
        │                                          BUY / HOLD / SELL
        │
        ├─ Sector Screening
        │     └─ 3단계 필터 → AI 요약 → Top 5
        │
        └─ Compare Mode
              └─ 동일/교차 섹터 자동 감지 → AI 비교 분석
```

## 기술 스택

| Technology | Role | Why |
|---|---|---|
| FastAPI + Uvicorn | 백엔드 REST API | Async 네이티브, OpenAPI 자동 생성, 배포 용이 |
| React 19 + TypeScript | 프론트엔드 SPA | 컴포넌트 재사용, 타입 안전성, 생태계 |
| Vite | 빌드 도구 / 개발 서버 | 빠른 HMR, 네이티브 ESM, 프록시 설정 간편 |
| Claude API (Sonnet) | AI 에이전트 엔진 | 금융 추론 능력, 구조화된 JSON 출력 |
| yfinance | 주가/재무 데이터 | 무료, API 키 불필요, 넓은 커버리지 |
| Finnhub | 실시간 시세/뉴스 | 무료 (분당 60회), WebSocket 지원 |
| Twelve Data | 기술적 지표 | RSI/MACD/Bollinger 사전 계산, 무료 (일 800회) |
| Finviz | 섹터 스크리닝 | 무료 스크리너, 재무 필터 제공 |
| FMP | 재무 폴백 | yfinance 누락 보완 (key-metrics-ttm) |
| FRED | 거시경제 데이터 | 기준금리, CPI, 실업률, GDP |
| SQLite (WAL) | 데이터 영속화 | 설정 불필요, WAL 모드로 동시 읽기 지원 |
| Lightweight Charts | 캔들스틱 차트 | 경량 (~40KB), TradingView 수준 품질 |
| Python asyncio | Agent 오케스트레이션 | 네이티브 병렬 실행, 타임아웃 제어 |

## AI 구성 요소

QuantAI는 Claude API (Sonnet)를 데이터 생성이 아닌 해석에 사용합니다. 모든 수치는 금융 API에서 가져오며, AI는 분석과 요약만 담당합니다.

| Agent | 입력 | 출력 |
|---|---|---|
| News Agent | 해당 종목 Finnhub 헤드라인 | 감성 점수 + 주요 이벤트 요약 |
| Data Agent | 재무 + 기술지표 | 재무 건전성 평가 |
| Macro Agent | FRED 지표 (금리, CPI, GDP) | 거시경제 환경이 종목에 미치는 영향 |
| Cross-Validation | 3개 Agent 결과 전체 | 합의 확인, 모순 플래그 |
| Analyst Agent | 교차 검증 결과 | 최종 BUY/HOLD/SELL + 신뢰도 + 근거 |
| Sector Analyzer | 필터링된 섹터 종목 | 종목별 AI 축약 분석 |
| Compare Agent | 2-3개 종목 데이터 비교 | 우위 종목 선정 + 항목별 분석 |

**실패 처리:** 1-2개 Agent가 실패해도 가용한 결과로 분석을 진행합니다 (Graceful Degradation). 3개 Agent 모두 실패 시 에러와 함께 분석이 중단됩니다.

**면책 조항:** 모든 AI 분석 결과는 참고용이며, 투자 조언이 아닙니다.

## 빠른 시작

### 사전 요구사항

- Python 3.11+
- Node.js 18+
- API 키: Finnhub, Twelve Data, FMP, FRED, Anthropic (Claude)

### 1. 클론 & 설치

```bash
git clone https://github.com/Ihatespeedlimit/stock-analyzer.git
cd stock-analyzer

# 백엔드
pip install -r requirements.txt

# 프론트엔드
cd frontend
npm install
cd ..
```

### 2. 환경변수 설정

```bash
cp .env.example .env
# .env 파일을 열고 API 키를 입력:
#   FINNHUB_API_KEY=...
#   TWELVEDATA_API_KEY=...
#   FMP_API_KEY=...
#   FRED_API_KEY=...
#   ANTHROPIC_API_KEY=...
```

### 3. 실행

```bash
# 터미널 1 — 백엔드 (포트 8000)
uvicorn backend.main:app --reload

# 터미널 2 — 프론트엔드 (포트 5173)
cd frontend
npm run dev
```

브라우저에서 `http://localhost:5173`을 엽니다. Vite 개발 서버가 `/api` 요청을 FastAPI 백엔드로 프록시합니다.

### 프로덕션 배포

- **백엔드:** Render (`render.yaml` 참조)
- **프론트엔드:** Netlify (`netlify.toml` 참조) — `VITE_API_BASE`를 Render 백엔드 URL로 설정

## 프로젝트 구조

```
stock-analyzer/
├── backend/                    # FastAPI REST API
│   ├── main.py                 # 앱 진입점, CORS, 라우터 등록
│   └── routers/                # 9개 라우트 모듈
│       ├── quote.py            # /api/quote, fundamentals, technicals, history
│       ├── market.py           # /api/market (지수, 급등락, 뉴스)
│       ├── analysis.py         # /api/analysis (5-Agent AI 파이프라인)
│       ├── sector.py           # /api/sector, 테마 CRUD
│       ├── compare.py          # /api/compare (2-3 종목 비교)
│       ├── watchlist.py        # /api/watchlist CRUD
│       ├── guide.py            # /api/guide (초보자 가이드)
│       ├── search.py           # /api/search (티커 자동완성)
│       └── alerts.py           # /api/alerts (가격 알림)
│
├── agents/                     # AI Agent 계층
│   ├── orchestrator.py         # 병렬 실행 + 재시도 + 타임아웃
│   ├── news_agent.py           # 뉴스 감성 분석
│   ├── data_agent.py           # 재무 데이터 해석
│   ├── macro_agent.py          # 거시경제 분석
│   ├── cross_validation.py     # Agent 간 교차 검증
│   ├── analyst_agent.py        # 최종 판단 생성
│   ├── sector_analyzer.py      # 섹터 AI 스크리닝
│   ├── compare_agent.py        # AI 비교 분석
│   └── claude_client.py        # Claude API 래퍼
│
├── data/                       # 데이터 계층 (API 클라이언트 + 비즈니스 로직)
│   ├── api_client.py           # 통합 API 클라이언트 (폴백 로직)
│   ├── yfinance_client.py      # yfinance 래퍼
│   ├── finnhub_client.py       # Finnhub 래퍼
│   ├── twelvedata_client.py    # Twelve Data 래퍼
│   ├── fmp_client.py           # FMP 래퍼 (폴백 전용)
│   ├── finviz_client.py        # Finviz 래퍼 (섹터 스크리닝)
│   ├── fred_client.py          # FRED 래퍼 (매크로 데이터)
│   ├── database.py             # SQLite 연결 + 테이블 초기화
│   ├── cache.py                # 인메모리 캐시 (TTL 기반)
│   └── ...                     # 15개 추가 모듈 (quote, history 등)
│
├── frontend/                   # React SPA
│   ├── package.json
│   ├── vite.config.ts          # FastAPI 개발 프록시 설정
│   └── src/
│       ├── App.tsx             # 라우터 + 레이아웃
│       ├── pages/              # 7개 페이지 (MarketOverview, QuickLook 등)
│       ├── components/         # 16개 재사용 컴포넌트
│       ├── hooks/              # 데이터 호출 hooks
│       ├── theme/              # Dark/Light 테마 시스템
│       └── types/              # API 응답 TypeScript 타입
│
├── tests/                      # pytest 테스트 모음
├── Phase/                      # Phase 개발 문서 (14개 Phase, 13.5 포함)
├── utils/                      # 공용 유틸리티
├── config/                     # 설정 파일
├── requirements.txt            # Python 의존성
├── render.yaml                 # Render 배포 설정
└── netlify.toml                # Netlify 배포 설정
```

## 테스트

```bash
# 전체 테스트 실행
pytest

# 특정 Phase 테스트 실행
pytest tests/test_phase1_api.py
pytest tests/test_phase3_ai_analysis.py
```

8개 테스트 파일에서 API 통합(실제 API 호출), 데이터 처리, AI Agent 파이프라인 로직을 검증합니다.

## 문서

| 문서 | 경로 | 설명 |
|---|---|---|
| Phase 문서 (1-14) | `Phase/Phase*.md` | Phase별 상세 개발 기록 (13.5 포함) |
| 디자인 스펙 | `pre-requirement/design-spec.md` | 컬러 토큰, 레이아웃, 테마 시스템 |
| 기능 기술서 | `pre-requirement/draft.txt` | 전체 기능 상세 설계 |
| 데이터 흐름 | `pre-requirement/data_flow.txt` | 엔드투엔드 데이터 흐름도 |
| API 레퍼런스 | `docs/API.md` | REST API 엔드포인트 문서 |

## 현재 상태

### 기능 개발 (Phase 1-5)

| Phase | 이름 | 상태 | 핵심 산출물 |
|:---:|---|:---:|---|
| 1 | API 연동 | ✅ 완료 | 6개 API 래퍼 + 폴백 + 캐싱 |
| 2 | Quick Look | ✅ 완료 | 시세 + 차트 + 재무 + 기술지표 |
| 3 | AI Deep Analysis | ✅ 완료 | 5 Agent 파이프라인 + Graceful Degradation |
| 4 | Sector Screening | ✅ 완료 | 3단계 필터 + AI 요약 + Top 5 |
| 5 | Compare + Watchlist + Guide + Overview | ✅ 완료 | 나머지 데이터 로직 전체 |

### 백엔드 + 프론트엔드 (Phase 6-9)

| Phase | 이름 | 상태 | 핵심 산출물 |
|:---:|---|:---:|---|
| 6 | FastAPI 백엔드 | ✅ 완료 | 9개 REST 라우터 + CORS + SQLite 초기화 |
| 7 | React 셋업 + 디자인 시스템 | ✅ 완료 | Vite + 테마 + 사이드바 + 라우팅 |
| 8 | QuickLook + AI 분석 화면 | ✅ 완료 | 캔들스틱 차트 + 기술 지표 카드 |
| 9 | 나머지 화면 + 최종 통합 | ✅ 완료 | Market Overview + Sector + Compare + Guide |

### 개선 (Phase 10-13.5)

| Phase | 이름 | 상태 | 핵심 산출물 |
|:---:|---|:---:|---|
| 10 | UX + 데이터 영속화 | ✅ 완료 | 검색 자동완성 + Watchlist UI + SQLite + 알림 |
| 11 | 코드 품질 | ✅ 완료 | API 키 마스킹 + 싱글턴 + 병렬화 |
| 12 | UI/UX + 모바일 최적화 | ✅ 완료 | 모바일 반응형 + 바텀 네비 + 터치 UX |
| 13 | Portfolio | ✅ 완료 | 보유 종목 관리 + AI 포트폴리오 분석 |
| 13.5 | 포트폴리오 인증 | 🔲 예정 | 코드+PIN 인증 게이트 + 서버 측 저장 |

## 한계점

- 무료 API 요금제에 호출 제한 존재 (Finnhub 60/분, Twelve Data 800/일, FMP 250/일)
- AI 분석에 종목당 1-2분 소요 (순차적 Agent 검증 때문)
- 자동완성은 S&P 500 종목만 지원 (다른 티커는 직접 입력 가능)
- 사용자 인증 없음 — 단일 사용자 로컬 또는 배포 인스턴스
- WebSocket 실시간 업데이트 없음 — 사용자 액션 시 데이터 갱신

---

<p align="center">Made with AI-assisted development</p>

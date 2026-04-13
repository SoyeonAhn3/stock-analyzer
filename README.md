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
[사용자] → Streamlit UI
               │
               ├── Quick Look ──→ [API 계층] ──→ 시세/차트/재무/기술지표
               │                    │
               │                    ├── yfinance (주가/재무)
               │                    ├── Finnhub (시세/뉴스)
               │                    ├── Twelve Data (기술지표)
               │                    ├── Finviz (섹터 스크리닝)
               │                    ├── FMP (재무 폴백)
               │                    └── FRED (매크로 경제)
               │
               ├── AI Deep Analysis
               │     │
               │     ├──[병렬]── News Agent ──┐
               │     ├──[병렬]── Data Agent ──┼──→ Cross-validation ──→ Analyst
               │     └──[병렬]── Macro Agent ─┘        Agent               Agent
               │                                                            │
               │                                                    BUY / HOLD / SELL
               │
               ├── Sector Screening ──→ 3단계 필터 ──→ AI 축약 분석 ──→ Top 5
               │
               └── Compare Mode ──→ 비교 유형 판정 ──→ AI 비교 분석
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
| 웹 UI | Streamlit | 무료 |
| 차트 | Plotly | 무료 |
| 오케스트레이터 | Python asyncio | 무료 |

---

## 프로젝트 구조

```
stock-analyzer/
├── app.py                          # Streamlit 메인 엔트리
├── requirements.txt
├── .env                            # API 키 (gitignore)
│
├── config/
│   ├── api_config.py               # API 키 로딩, 엔드포인트, 타임아웃
│   ├── themes.json                 # 커스텀 테마 종목 리스트
│   └── related_industries.json     # 관련 업종 매핑 테이블
│
├── data/
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
├── agents/
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
├── screens/
│   ├── styles.py                   # CSS 디자인 시스템
│   ├── sidebar.py                  # 사이드바
│   ├── state.py                    # session_state + 화면 전환
│   ├── market_overview.py          # 기본 화면 UI
│   ├── quick_look.py               # Quick Look UI
│   ├── ai_analysis.py              # AI 분석 결과 UI
│   ├── sector_screening.py         # Sector Screening UI
│   ├── compare_mode.py             # Compare Mode UI
│   ├── guide.py                    # Beginner's Guide UI
│   └── components/
│       ├── tooltip.py              # 인라인 툴팁
│       ├── signal_badge.py         # 신호 뱃지
│       ├── agent_status.py         # Agent 진행 표시
│       ├── loading.py              # 로딩 상태
│       └── error_banner.py         # 에러 배너
│
├── utils/
│   ├── tooltips.py                 # 지표별 설명 텍스트
│   ├── indicators.py               # 기술지표 Python 계산 (폴백)
│   ├── chart_builder.py            # Plotly figure 생성
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
│   ├── Phase1_프로젝트기반_API연동.md      # ✅ 완료
│   ├── Phase2_QuickLook.md                # ✅ 완료
│   ├── Phase3_AI_DeepAnalysis.md          # ✅ 완료
│   ├── Phase4_SectorScreening.md          # 🔲 미시작
│   ├── Phase5_Compare_Watchlist_Guide_Overview.md  # 🔲 미시작
│   ├── Phase6_UI기반_사이드바_화면전환.md    # 🔲 미시작
│   ├── Phase7_QuickLook_AI결과_UI.md       # 🔲 미시작
│   └── Phase8_나머지UI_최종통합.md          # 🔲 미시작
│
└── pre-requirement/                # 기획 문서
    ├── draft.txt                   # 기능 기술서
    └── UI.txt                      # UI 디자인 계획서
```

---

## Phase별 개발 계획

### 기능 개발 (Phase 1~5)

| Phase | 이름 | 상태 | 핵심 산출물 |
|:-----:|------|:----:|-----------|
| 1 | 프로젝트 기반 + API 연동 | ✅ | 6개 API 래퍼 + 폴백 + 캐싱 |
| 2 | Quick Look | ✅ | 시세 + 차트 + 재무 + 기술지표 |
| 3 | AI Deep Analysis | ✅ | 5 Agent 파이프라인 + Graceful Degradation |
| 4 | Sector Screening | 🔲 | 3단계 필터 + AI 축약 + Top 5 |
| 5 | Compare + Watchlist + Guide + Overview | 🔲 | 나머지 데이터 로직 전부 |

### UI 개발 (Phase 6~8) — 수동 확인

| Phase | 이름 | 상태 | 핵심 산출물 | 확인 항목 |
|:-----:|------|:----:|-----------|:---------:|
| 6 | UI 기반 + 사이드바 + 화면 전환 | 🔲 | CSS + 레이아웃 + 모드 라우팅 | 11개 |
| 7 | Quick Look + AI 결과 UI | 🔲 | 핵심 화면 디자인 적용 | 12개 |
| 8 | 나머지 UI + 최종 통합 | 🔲 | 전체 완성 + 시나리오 테스트 | 18개 |

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

# Phase 3 — AI Deep Analysis `✅ Completed`

> 5-agent parallel pipeline with cross-validation producing BUY/HOLD/SELL verdicts

**Completed**: 2026-04-10
**Status**: ✅ Completed
**Prerequisites**: Phase 2 completion (Quick Look data passed to agents)

---

## Overview

Orchestrates 5 AI Agents (News, Data, Macro, Cross-validation, Analyst) using the Claude API. Three agents run in parallel to collect and analyze data, followed by cross-validation and a final BUY/HOLD/SELL verdict. Implements graceful degradation when agents fail. All logic is pure Python with no Streamlit dependency.

---

## Deliverables

| # | Module | Status | Type |
|---|---|---|---|
| 1 | `agents/claude_client.py` | ✅ | general |
| 2 | `agents/news_agent.py` | ✅ | project-specific |
| 3 | `agents/data_agent.py` | ✅ | project-specific |
| 4 | `agents/macro_agent.py` | ✅ | project-specific |
| 5 | `agents/cross_validation.py` | ✅ | project-specific |
| 6 | `agents/analyst_agent.py` | ✅ | project-specific |
| 7 | `agents/orchestrator.py` | ✅ | general |
| 8 | `utils/usage_tracker.py` (integration) | ✅ | general |

---

## Claude API Connection (claude_client.py)

### Purpose

Common function for calling Claude Sonnet + JSON response parsing.

### Implementation Files

- `agents/claude_client.py`

### Core Structure

```python
def call_claude(system_prompt: str, user_message: str) -> dict:
    """
    Returns: {"parsed": True, "data": {...}} or
             {"parsed": False, "raw_output": "...", "error": "..."}
    """
```

### Design Decisions

| Decision | Reason |
|---|---|
| Model: Claude Sonnet | Cost efficiency |
| JSON parse failure → save raw_output | Analyst Agent can still process unstructured data |
| `usage_tracker.increment()` on each call | Track daily usage toward 100-call limit |

---

## Agent Implementations

### News Agent (news_agent.py)

- **Input**: Ticker + Quick Look data
- **Data sources**: Finnhub Company News + Analyst Recommendations + Web Search
- **Web Search quality**: 7-day filter, Reuters/Bloomberg/CNBC/WSJ priority
- **Output**: overall_sentiment, recent_news[], earnings, analyst_consensus, key_events_upcoming

### Data Agent (data_agent.py)

- **Input**: Quick Look data reused (no additional API calls)
- **Additional**: Sector average PE (FMP or top 10 peers median)
- **Output**: price_position, valuation, technicals_summary, financial_health

### Macro Agent (macro_agent.py)

- **Input**: FRED API (fed rate, CPI, unemployment) + Web Search + VIX
- **Output**: fed_rate, rate_outlook, inflation, sector_trend, market_sentiment, risk_factors[]

---

## Orchestrator (orchestrator.py)

### Purpose

Controls agent execution order, parallel execution, state management, and failure handling.

### Implementation Files

- `agents/orchestrator.py`

### Core Structure

```python
def run(quick_look_data: dict, agent_overrides: dict = None) -> dict:
    """
    Returns: analysis_state = {
        "ticker": "NVDA",
        "quick_look_data": {...},
        "agent_results": {"news": {...}, "data": {...}, "macro": {...}},
        "agent_status": {"news": "success", "data": "success", "macro": "failed"},
        "cross_validation": {...},
        "analyst": {...},
        "errors": []
    }
    """
```

### Execution Flow

```
Quick Look data received
    ↓
[Parallel] News + Data + Macro Agent (asyncio.gather)
    ↓  30s timeout per agent, 1 retry on failure (15s delay)
    ↓
Graceful Degradation check
    ↓
Cross-validation Agent
    ↓
Analyst Agent
    ↓
Return analysis_state
```

### Graceful Degradation Policy

| Success Count | Action | Confidence Impact |
|---|---|---|
| 3/3 | Normal execution | Maintained |
| 2/3 | Proceed; failed area marked "no data" | Downgrade 1 level |
| 1/3 | Proceed; fixed at low confidence | Fixed at low |
| 0/3 | Abort with error message | No analysis |

### Agent Failure Impact

| Failed Agent | Missing Information | Mitigation |
|---|---|---|
| News | News sentiment, earnings, analyst opinions | Judge from Data + Macro |
| Data | Financial interpretation | Fall back to Quick Look level |
| Macro | Interest rates, CPI, sector trends | Not reflected |

### Design Decisions

| Decision | Reason |
|---|---|
| State management via pure dict | No Streamlit session_state dependency |
| `agent_overrides` parameter | Test convenience — inject agent results directly |
| Prompt includes "interpret data below; do not invent numbers" | Hallucination prevention |

---

## Test Results

### Unit Tests

Test file: `tests/test_phase3_ai_analysis.py` — 29 tests all PASSED (2026-04-10)

| Module | Test Count | Key Verifications |
|---|---|---|
| claude_client | 6 | JSON parsing (pure/code block/embedded/failure), missing API key, daily limit |
| News Agent | 4 | Normal execution, no news handling, Claude failure, partial return |
| Data Agent | 3 | Normal execution, quick_look_data reuse, Claude failure |
| Macro Agent | 2 | Normal execution, FRED data unavailable |
| Cross-validation | 4 | Normal cross-check, partial agents, empty results, Claude failure default |
| Analyst Agent | 4 | Normal verdict, confidence downgrade (2/3), low fixed (1/3), Claude failure |
| Orchestrator | 5 | Full pipeline, full failure abort, partial continue, graceful degradation, timeout |
| Usage Tracker | 1 | Claude call increments counter |

### Real API Tests (2026-04-13)

Test file: `tests/test_phase3_real_api.py` — 9 tests all PASSED (~220 seconds)

| Test | Result | Key Validation |
|---|---|---|
| Claude API basic 3 calls | PASSED | JSON parsing, stock analysis, usage_tracker |
| News Agent live run | PASSED | sentiment=mixed, consensus=buy |
| Data Agent live run | PASSED | valuation=overvalued, trend=neutral |
| Macro Agent live run | PASSED | fed_rate=3.64%, sentiment=bullish |
| Cross-validation live | PASSED | 2 conflicts, confidence downgrade 1 level |
| Full Pipeline (AAPL) | PASSED | verdict=BUY, confidence=medium, 3/3 agents |
| Usage tracker final check | PASSED | 15/100 daily usage |

---

## Prerequisites & Dependencies

- Phase 2 complete: Quick Look data functions pass data to agents
- `.env`: `ANTHROPIC_API_KEY` required
- pip: `anthropic`, `asyncio`

---

## Development Notes

- AI interprets only — all numbers come from API data (hallucination prevention)
- Claude cost: Sonnet, Deep Analysis 1 run = 5 agent calls ≈ $0.05–0.10
- Monitor costs during testing with real API calls
- Cross-validation is currently a single AI Agent; future: split into rule-based (Python) + AI interpretation

---

## Phase 3 Skill Classification

| Skill | Classification | Reason |
|---|---|---|
| AI agent orchestration | General | Reusable multi-agent pipeline pattern |
| Graceful degradation | General | Applicable to any distributed agent system |
| Claude API wrapper | General | Reusable LLM client pattern |
| Financial agent prompts | Project-specific | Tied to stock analysis domain |

---

## Change Log

| Date | Description |
|---|---|
| 2026-04-06 | Initial creation |
| 2026-04-10 | Phase 3 implementation complete — 7 modules |
| 2026-04-13 | Real API tests — 9 tests PASSED (Claude + financial API live calls) |

---
---

# Phase 3 — AI 심층 분석 `✅ 완료`

> 5개 AI Agent 병렬 실행 → 교차 검증 → 종합 판단 파이프라인 완성

**완료일**: 2026-04-10
**상태**: ✅ 완료
**선행 조건**: Phase 2 완료 (Quick Look 데이터를 Agent에 전달)

---

## 개요

Claude API를 사용하여 5개 AI Agent(News, Data, Macro, Cross-validation, Analyst)를 오케스트레이션한다. 3개 Agent가 병렬로 데이터를 수집·분석하고, 교차 검증 후 종합 판단(BUY/HOLD/SELL)을 내린다. Agent 부분 실패 시 Graceful Degradation 정책으로 분석을 이어간다. 모든 로직은 순수 Python으로, Streamlit 의존 없이 개발한다.

---

## 완료 예정 / 완료 항목

| # | Skill / 모듈 | 상태 | 스킬 타입 |
|---|---|---|---|
| 1 | `agents/claude_client.py` | ✅ | general |
| 2 | `agents/news_agent.py` | ✅ | project-specific |
| 3 | `agents/data_agent.py` | ✅ | project-specific |
| 4 | `agents/macro_agent.py` | ✅ | project-specific |
| 5 | `agents/cross_validation.py` | ✅ | project-specific |
| 6 | `agents/analyst_agent.py` | ✅ | project-specific |
| 7 | `agents/orchestrator.py` | ✅ | general |
| 8 | `utils/usage_tracker.py` (연동) | ✅ | general |

---

## Claude API 연결 (claude_client.py)

### 목적

Claude Sonnet 호출 + JSON 응답 파싱의 공통 함수

### 구현 파일

- `agents/claude_client.py`

### 핵심 클래스 / 구조

```python
def call_claude(system_prompt: str, user_message: str) -> dict:
    """
    반환: {"parsed": True, "data": {...}} 또는
          {"parsed": False, "raw_output": "...", "error": "..."}
    """
```

### 설계 결정 사항

| 결정 | 이유 |
|---|---|
| 모델: Claude Sonnet | 비용 효율 |
| JSON 파싱 실패 시 raw_output 저장 | Analyst Agent가 비구조화 데이터도 처리 가능 |
| 호출마다 `usage_tracker.increment()` 실행 | 일일 100회 한도 추적 |

---

## Agent 개별 구현

### News Agent (news_agent.py)

- **입력**: 티커 + Quick Look 데이터
- **데이터 수집**: Finnhub Company News + Analyst Recommendations + Web Search
- **Web Search 품질 관리**: 7일 필터, Reuters/Bloomberg/CNBC/WSJ 우선
- **출력**: overall_sentiment, recent_news[], earnings, analyst_consensus, key_events_upcoming

### Data Agent (data_agent.py)

- **입력**: Quick Look 데이터 재사용 (API 재호출 없음)
- **추가**: 섹터 평균 PE (FMP 또는 동종 상위 10개 중앙값)
- **출력**: price_position, valuation, technicals_summary, financial_health

### Macro Agent (macro_agent.py)

- **입력**: FRED API (금리, CPI, 실업률) + Web Search + VIX
- **출력**: fed_rate, rate_outlook, inflation, sector_trend, market_sentiment, risk_factors[]

---

## 오케스트레이터 (orchestrator.py)

### 목적

Agent 실행 순서 제어, 병렬 실행, 상태 관리, 실패 처리

### 구현 파일

- `agents/orchestrator.py`

### 핵심 클래스 / 구조

```python
def run(quick_look_data: dict, agent_overrides: dict = None) -> dict:
    """
    반환: analysis_state = {
        "ticker": "NVDA",
        "quick_look_data": {...},
        "agent_results": {"news": {...}, "data": {...}, "macro": {...}},
        "agent_status": {"news": "success", "data": "success", "macro": "failed"},
        "cross_validation": {...},
        "analyst": {...},
        "errors": []
    }
    """
```

### 실행 흐름

```
Quick Look 데이터 수신
    ↓
[병렬] News + Data + Macro Agent (asyncio.gather)
    ↓  Agent당 30초 타임아웃, 실패 시 1회 재시도 (15초 대기)
    ↓
Graceful Degradation 판정
    ↓
Cross-validation Agent
    ↓
Analyst Agent
    ↓
analysis_state 반환
```

### Graceful Degradation 정책

| 성공 수 | 처리 | 신뢰도 영향 |
|---|---|---|
| 3/3 | 정상 진행 | 유지 |
| 2/3 | 진행. 실패 영역 "데이터 없음" | 1단계 하향 |
| 1/3 | 진행. low 고정 | low 고정 |
| 0/3 | 중단. 에러 메시지 반환 | 분석 없음 |

### Agent별 실패 시 영향

| Agent 실패 | 빠지는 정보 | 대체 |
|---|---|---|
| News | 뉴스 감성, 실적, 애널리스트 | Data+Macro로 판단 |
| Data | 재무 해석 | Quick Look 수준으로 대체 |
| Macro | 금리, CPI, 섹터 트렌드 | 미반영 |

### 설계 결정 사항

| 결정 | 이유 |
|---|---|
| 상태 관리는 순수 dict | Streamlit session_state 의존 없음 |
| `agent_overrides` 파라미터 | 테스트 시 Agent 결과 직접 주입 가능 |
| 프롬프트에 "아래 데이터를 해석하세요. 새 숫자를 만들지 마세요" 명시 | 환각 방지 |

---

## 테스트 결과

### 단위 테스트

테스트 파일: `tests/test_phase3_ai_analysis.py` — 29개 테스트 전체 PASSED (2026-04-10)

| 모듈 | 테스트 수 | 주요 검증 항목 |
|---|---|---|
| claude_client | 6개 | JSON 파싱(순수/코드블록/임베디드/실패), API 키 미설정, 일일 한도 초과 |
| News Agent | 4개 | 정상 실행, 뉴스 없음 처리, Claude 실패, partial 반환 |
| Data Agent | 3개 | 정상 실행, quick_look_data 재사용 검증, Claude 실패 |
| Macro Agent | 2개 | 정상 실행, FRED 데이터 없음 처리 |
| Cross-validation | 4개 | 정상 교차검증, 부분 Agent, 빈 결과, Claude 실패 시 기본 반환 |
| Analyst Agent | 4개 | 정상 판단, 신뢰도 하향(2/3), 신뢰도 low 고정(1/3), Claude 실패 |
| Orchestrator | 5개 | 전체 파이프라인, 전체 실패 중단, 부분 실패 계속, Graceful Degradation, 타임아웃 |
| Usage Tracker 연동 | 1개 | Claude 호출 시 카운트 증가 |

### 실제 API 테스트 (2026-04-13)

테스트 파일: `tests/test_phase3_real_api.py` — 9개 테스트 전체 PASSED (약 220초)

| 테스트 | 결과 | 주요 확인 |
|---|---|---|
| Claude API 기본 호출 3개 | PASSED | JSON 파싱, 주식 분석, usage_tracker |
| News Agent 실제 실행 | PASSED | sentiment=mixed, consensus=buy |
| Data Agent 실제 실행 | PASSED | valuation=overvalued, trend=neutral |
| Macro Agent 실제 실행 | PASSED | fed_rate=3.64%, sentiment=bullish |
| Cross-validation 실제 실행 | PASSED | 2건 conflict, 신뢰도 1단계 하향 |
| Full Pipeline (AAPL) | PASSED | verdict=BUY, confidence=medium, 3/3 agents |
| Usage tracker 최종 확인 | PASSED | 15/100 일일 사용량 |

---

## 선행 조건 및 의존성

- Phase 2 완료: Quick Look 데이터 함수 재사용
- `.env`에 `ANTHROPIC_API_KEY` 추가
- pip: `anthropic`, `asyncio`

---

## 개발 시 주의사항

- AI는 숫자를 "해석"만. 숫자 자체는 API 데이터만 사용 (환각 방지)
- Claude 호출 비용: Sonnet 기준 Deep Analysis 1회 = Agent 5회 호출 ≈ $0.05~0.10
- 테스트 중 실제 API 호출 시 비용 주의
- Cross-validation은 현재 AI Agent 1개로 통합 처리. 추후 규칙 기반(Python) + AI 해석으로 분리 가능

---

## Phase 3 스킬 범용/전용 분류

| 스킬 | 분류 | 이유 |
|---|---|---|
| AI Agent 오케스트레이션 | 범용 | 다중 에이전트 파이프라인 패턴 재사용 가능 |
| Graceful Degradation | 범용 | 모든 분산 에이전트 시스템에 적용 가능 |
| Claude API 래퍼 | 범용 | LLM 클라이언트 패턴 재사용 가능 |
| 금융 분석 Agent 프롬프트 | 전용 | 주식 분석 도메인에 종속 |

---

## 변경 이력

| 날짜 | 내용 |
|---|---|
| 2026-04-06 | 최초 작성 |
| 2026-04-10 | Phase 3 구현 완료 — 7개 모듈 |
| 2026-04-13 | 실제 API 테스트 수행 — 9개 테스트 PASSED (Claude + 금융 API 실호출) |

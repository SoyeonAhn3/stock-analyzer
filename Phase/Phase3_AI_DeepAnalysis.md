# Phase 3 — AI Deep Analysis `🔲 미시작`

> 5개 AI Agent 병렬 실행 → 교차 검증 → 종합 판단 파이프라인 완성

**상태**: 🔲 미시작
**선행 조건**: Phase 2 완료 (Quick Look 데이터를 Agent에 전달)

---

## 개요

Claude API를 사용하여 5개 AI Agent(News, Data, Macro, Cross-validation, Analyst)를 오케스트레이션한다. 3개 Agent가 병렬로 데이터를 수집·분석하고, 교차 검증 후 종합 판단(BUY/HOLD/SELL)을 내린다. Agent 부분 실패 시 Graceful Degradation 정책으로 분석을 이어간다. 모든 로직은 순수 Python으로, Streamlit 의존 없이 개발한다.

---

## 완료 예정 / 완료 항목

| # | 모듈 | 상태 | 설명 |
|---|---|---|---|
| 1 | `agents/claude_client.py` | 🔲 | Claude API 기본 호출 + JSON 파싱 |
| 2 | `agents/news_agent.py` | 🔲 | 뉴스 감성 + 실적 + 애널리스트 의견 |
| 3 | `agents/data_agent.py` | 🔲 | 재무/기술지표 해석 |
| 4 | `agents/macro_agent.py` | 🔲 | 거시경제 + 섹터 트렌드 |
| 5 | `agents/cross_validation.py` | 🔲 | Agent 간 모순 탐지 |
| 6 | `agents/analyst_agent.py` | 🔲 | 종합 판단 (BUY/HOLD/SELL) |
| 7 | `agents/orchestrator.py` | 🔲 | 병렬 실행 + 상태 관리 + Graceful Degradation |
| 8 | `utils/usage_tracker.py` | 🔲 | 일일 AI 100회 하드 리밋 (Phase 1에서 생성, 여기서 연동) |

---

## Claude API 연결 (claude_client.py)

### 목적
Claude Sonnet 호출 + JSON 응답 파싱의 공통 함수

### 핵심 함수
```python
def call_claude(system_prompt: str, user_message: str) -> dict:
    """
    반환: {"parsed": True, "data": {...}} 또는
          {"parsed": False, "raw_output": "...", "error": "..."}
    """
```

### 설계 결정 사항
- 모델: Claude Sonnet (비용 효율)
- .env에 `ANTHROPIC_API_KEY` 추가
- JSON 파싱 실패 시 raw_output 저장 (Analyst Agent가 비구조화 데이터도 처리)
- 호출마다 `usage_tracker.increment()` 실행

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

### 핵심 구조
```python
def run(quick_look_data: dict, agent_overrides: dict = None) -> dict:
    """
    agent_overrides: 테스트용. Agent 결과를 mock으로 주입 가능.
    
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
    ↓ 각 Agent 타임아웃 30초, 실패 시 1회 재시도 (15초 대기)
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

| 성공 수 | 처리 | confidence 영향 |
|---------|------|----------------|
| 3/3 | 정상 진행 | 유지 |
| 2/3 | 진행. 실패 영역 "데이터 없음" | 1단계 하향 |
| 1/3 | 진행. low confidence 고정 | low 고정 |
| 0/3 | 중단. 에러 메시지 반환 | 분석 없음 |

### Agent별 실패 시 영향

| Agent 실패 | 빠지는 정보 | 대체 |
|-----------|-----------|------|
| News | 뉴스 감성, 실적, 애널리스트 | Data+Macro로 판단 |
| Data | 재무 해석 | Quick Look 수준으로 대체 |
| Macro | 금리, CPI, 섹터 트렌드 | 미반영 |

### 설계 결정 사항
- 상태 관리는 순수 dict. Streamlit session_state 연결은 UI Phase에서
- `agent_overrides` 파라미터로 테스트 시 mock 주입 가능
- 프롬프트에 "아래 데이터를 해석하세요. 새 숫자를 만들지 마세요" 명시 (환각 방지)

---

## 선행 조건 및 의존성

- Phase 2 완료: Quick Look 데이터를 Agent에 전달
- .env에 `ANTHROPIC_API_KEY` 추가
- pip: `anthropic`, `asyncio`

---

## 개발 시 주의사항

- AI는 숫자를 "해석"만. 숫자 자체는 API 데이터만 사용 (환각 방지)
- Claude 호출 비용: Sonnet 기준 Deep Analysis 1회 = Agent 5회 호출 ≈ $0.05~0.10
- 테스트 중 실제 API 호출 시 비용 주의. mock 테스트를 우선 통과시키고, api_call은 최종 확인용
- Cross-validation은 현재 AI Agent 1개로 통합 처리. 추후 확장 시 규칙 기반(Python) + AI 해석으로 분리

---

## 변경 이력

| 날짜 | 내용 |
|---|---|
| 2026-04-06 | 최초 작성 |

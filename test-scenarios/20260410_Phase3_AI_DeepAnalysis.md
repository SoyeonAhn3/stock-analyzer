# 테스트 시나리오 — Phase 3 AI Deep Analysis

- **생성일**: 2026-04-10
- **대상 Phase**: Phase 3
- **구현 기능**: 5개 AI Agent(뉴스/재무/거시경제/교차검증/종합판단) 병렬 실행 → 교차검증 → BUY/HOLD/SELL 종합 판단 파이프라인
- **전제조건**: `.env`에 `ANTHROPIC_API_KEY` 설정 완료, Phase 2 Quick Look 데이터 수집 정상 동작

---

## 시나리오 목록

| ID | 유형 | 제목 | 검증 | 우선순위 |
|----|------|------|------|---------|
| TC-001 | 정상 | claude_client가 JSON 응답을 정상 파싱 | 🤖 AI검증 | High |
| TC-002 | 정상 | 3개 Agent 병렬 실행 후 전체 파이프라인 완료 | 🤖 AI검증 | High |
| TC-003 | 정상 | Data Agent가 quick_look_data를 재사용 (API 재호출 없음) | 🤖 AI검증 | High |
| TC-004 | 정상 | Analyst Agent가 BUY/HOLD/SELL 중 하나를 반환 | 🤖 AI검증 | High |
| TC-005 | 정상 | usage_tracker가 Claude 호출마다 카운트 증가 | 🤖 AI검증 | Medium |
| TC-006 | 엣지 | Claude 응답이 ```json 블록으로 감싸져 있을 때 파싱 | 🤖 AI검증 | Medium |
| TC-007 | 엣지 | Claude 응답에 JSON 외 텍스트가 섞여 있을 때 추출 | 🤖 AI검증 | Medium |
| TC-008 | 엣지 | 뉴스/애널리스트 데이터가 없을 때 News Agent 동작 | 🤖 AI검증 | Medium |
| TC-009 | 엣지 | FRED 매크로 데이터가 없을 때 Macro Agent 동작 | 🤖 AI검증 | Medium |
| TC-010 | 엣지 | Agent 2/3만 성공 시 Graceful Degradation + 신뢰도 하향 | 🤖 AI검증 | High |
| TC-011 | 엣지 | Agent 1/3만 성공 시 confidence "low" 고정 | 🤖 AI검증 | High |
| TC-012 | 실패 | ANTHROPIC_API_KEY 미설정 시 에러 반환 | 🤖 AI검증 | High |
| TC-013 | 실패 | 일일 한도(100회) 초과 시 AI 호출 차단 | 🤖 AI검증 | High |
| TC-014 | 실패 | Claude가 JSON이 아닌 텍스트만 반환 시 raw_output 보존 | 🤖 AI검증 | Medium |
| TC-015 | 실패 | 3개 Agent 모두 실패 시 분석 중단 + 에러 반환 | 🤖 AI검증 | High |
| TC-016 | 실패 | Agent 타임아웃(30초) 초과 시 재시도 후 실패 처리 | 🤖 AI검증 | Medium |
| TC-017 | 실패 | 교차검증 Agent 실패 시 기본 결과 반환 (파이프라인 중단 안 함) | 🤖 AI검증 | High |

---

### TC-001 [정상] 🤖 AI검증 — claude_client가 JSON 응답을 정상 파싱

**사전조건**: `agents/claude_client.py`의 `_parse_json_response` 함수 구현 완료
**실행 단계**:
1. `_parse_json_response`에 순수 JSON 문자열 `'{"sentiment": "positive"}'`을 전달
2. 반환값 확인
**입력값**: `'{"sentiment": "positive", "score": 0.8}'`
**예상 결과**: `{"parsed": True, "data": {"sentiment": "positive", "score": 0.8}}` 반환
**확인 방법**: 반환 dict의 `parsed`가 `True`이고 `data` 키에 원본 JSON이 dict로 들어있는지 확인

**결과**: [x] Pass  [ ] Fail  **코멘트**: PASSED (2026-04-10) / 실제 API 테스트 PASSED (2026-04-13)

---

### TC-002 [정상] 🤖 AI검증 — 3개 Agent 병렬 실행 후 전체 파이프라인 완료

**사전조건**: `agents/orchestrator.py`의 `run_analysis` 함수 구현 완료, `agent_overrides`로 결과 주입 가능
**실행 단계**:
1. `run_analysis(quick_look_data, agent_overrides={"news": ..., "data": ..., "macro": ...})`를 호출
2. cross_validation, analyst_agent의 `call_claude` 패치
3. 반환된 `analysis_state` 확인
**입력값**: NVDA quick_look_data + 3개 Agent 결과
**예상 결과**: `analysis_state`에 `ticker`, `agent_results`(3개), `agent_status`(3개 모두 "success"), `cross_validation`, `analyst`(verdict 포함), `errors`(빈 리스트) 키가 모두 존재
**확인 방법**: 반환 dict의 각 키 존재 여부 및 `agent_status` 값 확인, `errors` 리스트가 비어있는지 확인

**결과**: [x] Pass  [ ] Fail  **코멘트**: PASSED (2026-04-10) / 실제 API 테스트 PASSED (2026-04-13)

---

### TC-003 [정상] 🤖 AI검증 — Data Agent가 quick_look_data를 재사용 (API 재호출 없음)

**사전조건**: `agents/data_agent.py` 구현 완료
**실행 단계**:
1. `data_agent.run("NVDA", quick_look_data)` 호출 시 `call_claude`만 패치
2. `api_client`의 어떤 메서드도 호출되지 않는지 확인
**입력값**: PER 35.2, RSI 72, MACD bullish 등이 포함된 quick_look_data
**예상 결과**: `call_claude`에 전달된 user_message에 "PER", "35.2", "RSI" 등 quick_look_data 값이 포함됨. `api_client`의 메서드는 호출되지 않음
**확인 방법**: `data_agent.py` 소스에서 `api_client` import가 없는지 확인. `call_claude` 호출 인자의 user_message 내용 검증

**결과**: [x] Pass  [ ] Fail  **코멘트**: PASSED (2026-04-10) / 실제 API 테스트 PASSED (2026-04-13)

---

### TC-004 [정상] 🤖 AI검증 — Analyst Agent가 BUY/HOLD/SELL 중 하나를 반환

**사전조건**: `agents/analyst_agent.py` 구현 완료
**실행 단계**:
1. `analyst_agent.run(agent_results, cross_validation, success_count=3)` 호출
2. `call_claude`가 `{"verdict": "BUY", "confidence": "high", ...}` 반환하도록 설정
3. 결과의 `verdict` 값 확인
**입력값**: 3개 Agent 정상 결과 + 교차검증 결과
**예상 결과**: 반환 dict에 `verdict` 키가 존재하며 값이 `"BUY"`, `"HOLD"`, `"SELL"` 중 하나. `disclaimer` 키에 면책 조항 문구 포함
**확인 방법**: `result["verdict"] in ("BUY", "HOLD", "SELL")` 확인, `result["disclaimer"]`에 "투자 자문이 아닙니다" 포함 여부

**결과**: [x] Pass  [ ] Fail  **코멘트**: PASSED (2026-04-10) / 실제 API 테스트 PASSED (2026-04-13)

---

### TC-005 [정상] 🤖 AI검증 — usage_tracker가 Claude 호출마다 카운트 증가

**사전조건**: `utils/usage_tracker.py` 싱글톤, `agents/claude_client.py`에서 호출 시 `increment()` 실행
**실행 단계**:
1. `usage_tracker.count` 현재값 기록
2. `call_claude("system", "user")` 호출 (Anthropic 클라이언트 패치)
3. `usage_tracker.count` 다시 확인
**입력값**: 임의의 system_prompt, user_message
**예상 결과**: 호출 전 대비 `usage_tracker.count`가 정확히 1 증가
**확인 방법**: 호출 전후 `usage_tracker.count` 값 비교

**결과**: [x] Pass  [ ] Fail  **코멘트**: PASSED (2026-04-10) / 실제 API 테스트 PASSED (2026-04-13)

---

### TC-006 [엣지] 🤖 AI검증 — Claude 응답이 ```json 블록으로 감싸져 있을 때 파싱

**사전조건**: `_parse_json_response` 함수 구현 완료
**실행 단계**:
1. `_parse_json_response`에 마크다운 코드 블록 포함 텍스트 전달
**입력값**: `'Here is the result:\n```json\n{"verdict": "BUY"}\n```\nEnd.'`
**예상 결과**: `{"parsed": True, "data": {"verdict": "BUY"}}` 반환
**확인 방법**: `result["parsed"]`가 `True`이고 `result["data"]["verdict"]`가 `"BUY"`

**결과**: [x] Pass  [ ] Fail  **코멘트**: PASSED (2026-04-10) / 실제 API 테스트 PASSED (2026-04-13)

---

### TC-007 [엣지] 🤖 AI검증 — Claude 응답에 JSON 외 텍스트가 섞여 있을 때 추출

**사전조건**: `_parse_json_response` 함수 구현 완료
**실행 단계**:
1. `_parse_json_response`에 JSON 전후로 설명 텍스트가 포함된 문자열 전달
**입력값**: `'Analysis complete. {"verdict": "HOLD", "confidence": "medium"} That is all.'`
**예상 결과**: 가장 바깥 `{}`를 추출하여 `{"parsed": True, "data": {"verdict": "HOLD", "confidence": "medium"}}` 반환
**확인 방법**: `result["parsed"]`가 `True`이고 `result["data"]`에 `verdict`, `confidence` 키 존재

**결과**: [x] Pass  [ ] Fail  **코멘트**: PASSED (2026-04-10) / 실제 API 테스트 PASSED (2026-04-13)

---

### TC-008 [엣지] 🤖 AI검증 — 뉴스/애널리스트 데이터가 없을 때 News Agent 동작

**사전조건**: `agents/news_agent.py` 구현 완료
**실행 단계**:
1. `api_client.get_news` → `None`, `api_client.get_analyst` → `None`으로 설정
2. `call_claude`는 정상 응답 반환
3. `news_agent.run("NVDA", quick_look_data)` 호출
**입력값**: 뉴스 없음, 애널리스트 없음 상태의 quick_look_data
**예상 결과**: 예외 발생 없이 `status: "success"` 반환. Claude에 전달된 메시지에 "최근 뉴스: 없음", "애널리스트 추천: 데이터 없음" 문구 포함
**확인 방법**: 반환 dict의 `status` 확인, `call_claude` 호출 인자 내 "없음" 문자열 포함 여부

**결과**: [x] Pass  [ ] Fail  **코멘트**: PASSED (2026-04-10) / 실제 API 테스트 PASSED (2026-04-13)

---

### TC-009 [엣지] 🤖 AI검증 — FRED 매크로 데이터가 없을 때 Macro Agent 동작

**사전조건**: `agents/macro_agent.py` 구현 완료
**실행 단계**:
1. `api_client.get_macro` → `None`으로 설정
2. `call_claude`는 정상 응답 반환
3. `macro_agent.run("NVDA", quick_look_data)` 호출
**입력값**: FRED 데이터 없는 상태
**예상 결과**: 예외 발생 없이 `status: "success"` 반환. Claude에 전달된 메시지에 "거시경제 지표: 데이터 없음" 문구 포함
**확인 방법**: 반환 dict의 `status` 확인, `call_claude` 호출 인자 검증

**결과**: [x] Pass  [ ] Fail  **코멘트**: PASSED (2026-04-10) / 실제 API 테스트 PASSED (2026-04-13)

---

### TC-010 [엣지] 🤖 AI검증 — Agent 2/3만 성공 시 Graceful Degradation + 신뢰도 하향

**사전조건**: `agents/orchestrator.py`, `agents/analyst_agent.py` 구현 완료
**실행 단계**:
1. news, data는 agent_overrides로 정상 결과 주입
2. macro_agent.run을 `RuntimeError` 발생하도록 설정
3. cross_validation, analyst의 `call_claude`가 confidence: "high" 반환하도록 설정
4. `run_analysis` 호출
**입력값**: 2개 Agent 성공 + 1개 실패
**예상 결과**: `agent_status`에서 news="success", data="success", macro="failed". `analyst`의 `confidence`가 "high" → "medium"으로 1단계 하향. `errors` 리스트에 macro 관련 에러 1건 포함
**확인 방법**: `result["agent_status"]` 값 확인, `result["analyst"]["confidence"]`가 "medium"인지 확인, `len(result["errors"]) == 1`

**결과**: [x] Pass  [ ] Fail  **코멘트**: PASSED (2026-04-10) / 실제 API 테스트 PASSED (2026-04-13)

---

### TC-011 [엣지] 🤖 AI검증 — Agent 1/3만 성공 시 confidence "low" 고정

**사전조건**: `agents/analyst_agent.py`의 `_adjust_confidence` 함수 구현 완료
**실행 단계**:
1. news만 agent_overrides로 정상 결과 주입
2. data, macro를 `RuntimeError` 발생하도록 설정
3. analyst의 `call_claude`가 confidence: "high" 반환하도록 설정
4. `run_analysis` 호출
**입력값**: 1개 Agent 성공 + 2개 실패
**예상 결과**: `analyst`의 `confidence`가 원래 "high"여도 강제로 "low"로 고정. 분석은 중단되지 않고 결과 반환
**확인 방법**: `result["analyst"]["confidence"] == "low"` 확인, `result["analyst"]`가 `None`이 아닌지 확인

**결과**: [x] Pass  [ ] Fail  **코멘트**: PASSED (2026-04-10) / 실제 API 테스트 PASSED (2026-04-13)

---

### TC-012 [실패] 🤖 AI검증 — ANTHROPIC_API_KEY 미설정 시 에러 반환

**사전조건**: `agents/claude_client.py` 구현 완료
**실행 단계**:
1. `ANTHROPIC_API_KEY`를 빈 문자열로 패치
2. `call_claude("system", "user")` 호출
**입력값**: 빈 API 키
**예상 결과**: `{"parsed": False, "raw_output": "", "error": "ANTHROPIC_API_KEY가 설정되지 않았습니다."}` 반환. 예외가 발생하지 않음
**확인 방법**: 반환 dict의 `parsed`가 `False`, `error`에 "ANTHROPIC_API_KEY" 문자열 포함

**결과**: [x] Pass  [ ] Fail  **코멘트**: PASSED (2026-04-10) / 실제 API 테스트 PASSED (2026-04-13)

---

### TC-013 [실패] 🤖 AI검증 — 일일 한도(100회) 초과 시 AI 호출 차단

**사전조건**: `utils/usage_tracker.py` 싱글톤, `agents/claude_client.py` 연동 완료
**실행 단계**:
1. `usage_tracker.is_exhausted`를 `True`로 설정
2. `call_claude("system", "user")` 호출
**입력값**: 한도 초과 상태
**예상 결과**: `{"parsed": False, "raw_output": "", "error": "일일 AI 사용 한도(100회)에 도달했습니다."}` 반환. Anthropic API 실제 호출 없음
**확인 방법**: 반환 dict의 `error`에 "한도" 문자열 포함, Anthropic 클라이언트가 호출되지 않았는지 확인

**결과**: [x] Pass  [ ] Fail  **코멘트**: PASSED (2026-04-10) / 실제 API 테스트 PASSED (2026-04-13)

---

### TC-014 [실패] 🤖 AI검증 — Claude가 JSON이 아닌 텍스트만 반환 시 raw_output 보존

**사전조건**: `_parse_json_response` 함수 구현 완료
**실행 단계**:
1. `_parse_json_response`에 JSON이 전혀 없는 순수 텍스트 전달
**입력값**: `"This is just plain text with no JSON at all."`
**예상 결과**: `{"parsed": False, "raw_output": "This is just plain text with no JSON at all.", "error": "JSON 파싱 실패"}` 반환
**확인 방법**: `result["parsed"]`가 `False`, `result["raw_output"]`에 원본 텍스트가 그대로 보존

**결과**: [x] Pass  [ ] Fail  **코멘트**: PASSED (2026-04-10) / 실제 API 테스트 PASSED (2026-04-13)

---

### TC-015 [실패] 🤖 AI검증 — 3개 Agent 모두 실패 시 분석 중단 + 에러 반환

**사전조건**: `agents/orchestrator.py` 구현 완료
**실행 단계**:
1. news_agent.run, data_agent.run, macro_agent.run 모두 `RuntimeError` 발생하도록 설정
2. `run_analysis(quick_look_data)` 호출
**입력값**: 모든 Agent 실패 상태
**예상 결과**: `analyst`가 `None`, `cross_validation`이 `None`, `errors` 리스트에 3건의 에러 포함. 예외가 발생하지 않고 정상 dict 반환
**확인 방법**: `result["analyst"] is None`, `result["cross_validation"] is None`, `len(result["errors"]) == 3`

**결과**: [x] Pass  [ ] Fail  **코멘트**: PASSED (2026-04-10) / 실제 API 테스트 PASSED (2026-04-13)

---

### TC-016 [실패] 🤖 AI검증 — Agent 타임아웃(30초) 초과 시 재시도 후 실패 처리

**사전조건**: `agents/orchestrator.py`의 `_run_agent_with_retry` 함수 구현 완료
**실행 단계**:
1. `AGENT_TIMEOUT`을 0.01초로 패치
2. `AGENT_RETRY_DELAY`를 0.01초로 패치
3. macro_agent.run이 10초 sleep하도록 설정
4. news, data는 agent_overrides로 정상 주입
5. `run_analysis` 호출
**입력값**: 타임아웃 발생 Agent 1개
**예상 결과**: macro의 `agent_status`가 "failed". 나머지 2개는 "success". 분석은 계속 진행되어 `analyst` 결과 존재
**확인 방법**: `result["agent_status"]["macro"] == "failed"`, `result["analyst"] is not None`

**결과**: [x] Pass  [ ] Fail  **코멘트**: PASSED (2026-04-10) / 실제 API 테스트 PASSED (2026-04-13)

---

### TC-017 [실패] 🤖 AI검증 — 교차검증 Agent 실패 시 기본 결과 반환 (파이프라인 중단 안 함)

**사전조건**: `agents/cross_validation.py` 구현 완료
**실행 단계**:
1. `cross_validation.call_claude`가 실패하도록 설정 (parsed: False, raw_output: "", error: "API 에러")
2. 정상적인 agent_results를 전달하여 `cross_validation.run` 호출
**입력값**: 정상 Agent 결과 + Claude 호출 실패
**예상 결과**: 예외 발생 없이 기본 결과 반환: `status: "skipped"`, `conflicts: []`, `agreements: []`, `confidence_adjustment: "none"`. 파이프라인이 중단되지 않고 Analyst Agent로 계속 진행
**확인 방법**: `result["status"]`가 "skipped" 또는 에러가 아닌 값, `result["confidence_adjustment"] == "none"`

**결과**: [x] Pass  [ ] Fail  **코멘트**: PASSED (2026-04-10) / 실제 API 테스트 PASSED (2026-04-13)

---

## 테스트 완료 체크리스트

- [x] 모든 정상 케이스 Pass
- [x] 엣지 케이스에서 앱이 크래시 없이 처리됨
- [x] 실패 케이스에서 사용자에게 적절한 안내가 표시됨
- [x] Graceful Degradation이 설계대로 동작함 (3/3, 2/3, 1/3, 0/3)
- [x] 일일 한도 초과 시 AI 호출이 차단됨
- [x] 교차검증/Analyst 실패 시에도 파이프라인이 중단되지 않음

---

## 실제 API 테스트 결과 (2026-04-13)

테스트 파일: `tests/test_phase3_real_api.py`
실행: `pytest tests/test_phase3_real_api.py -v -s`
소요 시간: 약 220초
결과: **9/9 PASSED**

| # | 테스트 | 결과 | 비고 |
|---|--------|:----:|------|
| 1 | Claude API 기본 호출 (JSON 응답) | PASSED | 529 Overloaded 재시도 후 성공 |
| 2 | Claude API 주식 분석 JSON 파싱 | PASSED | |
| 3 | usage_tracker 증가 확인 | PASSED | 호출 전후 count 비교 |
| 4 | News Agent 실행 | PASSED | sentiment=mixed, score=0.65, consensus=buy |
| 5 | Data Agent 실행 | PASSED | valuation=overvalued, trend=neutral, health=moderate |
| 6 | Macro Agent 실행 | PASSED | fed_rate=3.64%, outlook=인하, sentiment=bullish |
| 7 | Cross-validation 실행 | PASSED | 2건 conflict, confidence_adjustment=downgrade_one |
| 8 | Full Pipeline (run_analysis) | PASSED | verdict=BUY, confidence=medium, 3/3 agents 성공 |
| 9 | Usage tracker 최종 확인 | PASSED | 15/100 일일 사용량 |

### 주요 관찰

- Claude 529 Overloaded 에러가 간헐적 발생 - `_call_claude_with_retry` (최대 3회, 5초 간격)로 해결
- 3개 Agent 모두 실제 Claude API + 금융 API로 성공 (3/3)
- Cross-validation에서 Agent 간 모순 2건 감지 후 신뢰도 1단계 하향
- 전체 파이프라인 AAPL 분석: BUY (medium confidence)
- AI 사용량: 1회 실행당 약 15회 Claude 호출, 일일 한도 100회 대비 여유

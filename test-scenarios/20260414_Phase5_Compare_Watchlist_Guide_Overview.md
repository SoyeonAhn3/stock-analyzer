# 테스트 시나리오 — Phase 5 Compare + Watchlist + Guide + Overview

- **생성일**: 2026-04-14
- **대상 Phase**: Phase 5
- **구현 기능**: 비교 유형 판정, 스타일 분류, AI 비교 분석, Watchlist CRUD, 가이드 콘텐츠, 시장 개요
- **전제조건**: Phase 4까지 완료, API 키 설정 완료, `config/related_industries.json` 존재

---

## 시나리오 목록

| ID | 유형 | 제목 | 검증 | 우선순위 |
|----|------|------|------|---------|
| TC-001 | 정상 | 동일 섹터+동일 업종 비교 판정 | 🤖 AI검증 | High |
| TC-002 | 정상 | 다른 섹터 비교 판정 | 🤖 AI검증 | High |
| TC-003 | 정상 | 관련 업종 → same_sector 판정 | 🤖 AI검증 | High |
| TC-004 | 정상 | get_comparison_data 전체 데이터 구조 반환 | 🤖 AI검증 | High |
| TC-005 | 정상 | Growth 스타일 분류 (forward_pe >= 25) | 🤖 AI검증 | High |
| TC-006 | 정상 | Value 스타일 분류 (forward_pe < 18 + 배당) | 🤖 AI검증 | High |
| TC-007 | 정상 | AI 비교 분석 same_sector 호출 성공 | 🤖 AI검증 | High |
| TC-008 | 정상 | Watchlist 종목 추가 및 조회 | 🤖 AI검증 | High |
| TC-009 | 정상 | Watchlist 등락률 조회 + highlight 판정 | 🤖 AI검증 | High |
| TC-010 | 정상 | Guide 카테고리 및 주제 조회 | 🤖 AI검증 | Medium |
| TC-011 | 정상 | 시장 지수 4종 조회 | 🤖 AI검증 | High |
| TC-012 | 정상 | 급등/급락 Top 5 조회 | 🤖 AI검증 | Medium |
| TC-013 | 엣지 | 티커 1개만 비교 → same_sector | 🤖 AI검증 | Medium |
| TC-014 | 엣지 | sector/industry 빈값 → cross_sector | 🤖 AI검증 | Medium |
| TC-015 | 엣지 | Balanced 분류 (애매한 지표값) | 🤖 AI검증 | Medium |
| TC-016 | 엣지 | 데이터 전부 None → Balanced 기본값 | 🤖 AI검증 | Medium |
| TC-017 | 엣지 | Watchlist 중복 추가 시 무시 | 🤖 AI검증 | Medium |
| TC-018 | 엣지 | 빈 Watchlist에서 quotes 조회 | 🤖 AI검증 | Low |
| TC-019 | 엣지 | Guide 존재하지 않는 카테고리 조회 | 🤖 AI검증 | Low |
| TC-020 | 엣지 | Guide 범위 초과 인덱스 조회 | 🤖 AI검증 | Low |
| TC-021 | 엣지 | 시장 지수 캐시 히트 | 🤖 AI검증 | Medium |
| TC-022 | 실패 | fundamentals API 실패 → cross_sector | 🤖 AI검증 | High |
| TC-023 | 실패 | quote API 실패 → 비교 데이터에 None | 🤖 AI검증 | High |
| TC-024 | 실패 | AI 비교 분석 호출 실패 → error 반환 | 🤖 AI검증 | High |
| TC-025 | 실패 | AI 비교 분석 JSON 파싱 실패 | 🤖 AI검증 | High |
| TC-026 | 실패 | Watchlist 빈 문자열 추가 → ValueError | 🤖 AI검증 | Medium |
| TC-027 | 실패 | Watchlist 없는 종목 제거 → KeyError | 🤖 AI검증 | Medium |
| TC-028 | 실패 | 시장 지수 API 실패 → None 반환 | 🤖 AI검증 | High |
| TC-029 | 실패 | 시장 뉴스 API 실패 → None 반환 | 🤖 AI검증 | Medium |
| TC-030 | 실패 | top_movers Finviz 실패 → None 반환 | 🤖 AI검증 | Medium |

---

### TC-001 [정상] 🤖 AI검증 — 동일 섹터+동일 업종 비교 판정

**사전조건**: NVDA, AMD의 fundamentals에서 sector="Technology", industry="Semiconductors" 반환
**실행 단계**:
1. `detect_comparison_type(["NVDA", "AMD"])` 호출
2. 내부적으로 각 티커에 대해 `get_fundamentals()` 호출
3. sector 동일 + industry 동일 확인
**입력값**: `["NVDA", "AMD"]`
**예상 결과**: 반환값이 `"same_sector"` 문자열
**확인 방법**: `assert detect_comparison_type(["NVDA", "AMD"]) == "same_sector"` — 테스트 코드에서 fundamentals mock으로 sector/industry 동일하게 설정 후 확인

**결과**: [x] Pass  [ ] Fail  **코멘트**: test_same_sector_same_industry PASSED

---

### TC-002 [정상] 🤖 AI검증 — 다른 섹터 비교 판정

**사전조건**: NVDA(Technology)와 JNJ(Healthcare)의 fundamentals 반환
**실행 단계**:
1. `detect_comparison_type(["NVDA", "JNJ"])` 호출
2. sector가 다른 것 확인
**입력값**: `["NVDA", "JNJ"]`
**예상 결과**: 반환값이 `"cross_sector"` 문자열
**확인 방법**: `assert detect_comparison_type(["NVDA", "JNJ"]) == "cross_sector"` — 서로 다른 sector mock 설정 후 확인

**결과**: [x] Pass  [ ] Fail  **코멘트**: test_cross_sector PASSED

---

### TC-003 [정상] 🤖 AI검증 — 관련 업종 → same_sector 판정

**사전조건**: 두 종목이 같은 sector, 다른 industry이지만 `related_industries.json`에 관련 업종으로 등록
**실행 단계**:
1. `detect_comparison_type(["A", "B"])` 호출
2. sector 동일, industry 다름 확인
3. `related_industries.json` 참조 → 관련 업종이면 same_sector
**입력값**: sector="Technology", industry A="Semiconductors", industry B="Software—Infrastructure" (related_industries.json에 매핑됨)
**예상 결과**: 반환값이 `"same_sector"`
**확인 방법**: related_industries.json에 해당 매핑이 존재하는지 확인 후, mock 테스트에서 `"same_sector"` 반환 검증

**결과**: [x] Pass  [ ] Fail  **코멘트**: test_same_sector_related_industry PASSED

---

### TC-004 [정상] 🤖 AI검증 — get_comparison_data 전체 데이터 구조 반환

**사전조건**: NVDA, AAPL의 quote, fundamentals, technicals mock 데이터 준비
**실행 단계**:
1. `get_comparison_data(["NVDA", "AAPL"])` 호출
2. 내부적으로 detect_comparison_type + 각 티커별 quote/fundamentals/technicals 수집
**입력값**: `["NVDA", "AAPL"]`
**예상 결과**: `{"tickers": ["NVDA", "AAPL"], "comparison_type": "same_sector"|"cross_sector", "data": {"NVDA": {"quote": {...}, "fundamentals": {...}, "technicals": {...}}, "AAPL": {...}}}` 구조 반환
**확인 방법**: result["tickers"], result["comparison_type"], result["data"]["NVDA"]["quote"] 각 키 존재 및 값 검증

**결과**: [x] Pass  [ ] Fail  **코멘트**: test_get_comparison_data PASSED

---

### TC-005 [정상] 🤖 AI검증 — Growth 스타일 분류 (forward_pe >= 25)

**사전조건**: 없음 (순수 함수)
**실행 단계**:
1. `classify_style({"forward_pe": 35, "dividend_yield": 0.1})` 호출
**입력값**: `{"forward_pe": 35, "dividend_yield": 0.1}`
**예상 결과**: 반환값이 `"Growth"`
**확인 방법**: `assert classify_style({"forward_pe": 35, "dividend_yield": 0.1}) == "Growth"` — forward_pe >= 25 조건 충족

**결과**: [x] Pass  [ ] Fail  **코멘트**: test_growth_high_pe PASSED

---

### TC-006 [정상] 🤖 AI검증 — Value 스타일 분류 (forward_pe < 18 + 배당)

**사전조건**: 없음 (순수 함수)
**실행 단계**:
1. `classify_style({"forward_pe": 14, "dividend_yield": 3.0})` 호출
**입력값**: `{"forward_pe": 14, "dividend_yield": 3.0}`
**예상 결과**: 반환값이 `"Value"`
**확인 방법**: `assert classify_style({"forward_pe": 14, "dividend_yield": 3.0}) == "Value"` — forward_pe < 18 AND dividend_yield >= 2.0 충족

**결과**: [x] Pass  [ ] Fail  **코멘트**: test_value_low_pe_high_dividend PASSED

---

### TC-007 [정상] 🤖 AI검증 — AI 비교 분석 same_sector 호출 성공

**사전조건**: `call_claude` mock이 `{"parsed": True, "data": {"rankings": {...}, ...}}` 반환
**실행 단계**:
1. `run_compare_analysis(["NVDA", "AAPL"], "same_sector", ticker_data)` 호출
2. 내부적으로 `_build_same_sector_prompt()` 생성 + `call_claude()` 호출
**입력값**: tickers=["NVDA", "AAPL"], comparison_type="same_sector", ticker_data={...}
**예상 결과**: `{"status": "success", "comparison_type": "same_sector", "tickers": ["NVDA", "AAPL"], "analysis": {...}, "error": None}`
**확인 방법**: result["status"] == "success", result["analysis"]가 None이 아님, result["error"]가 None

**결과**: [x] Pass  [ ] Fail  **코멘트**: test_same_sector_success PASSED

---

### TC-008 [정상] 🤖 AI검증 — Watchlist 종목 추가 및 조회

**사전조건**: 빈 watchlist.json (또는 파일 없음)
**실행 단계**:
1. `add_to_watchlist("NVDA")` 호출
2. `add_to_watchlist("AAPL")` 호출
3. `load_watchlist()` 호출
**입력값**: "NVDA", "AAPL"
**예상 결과**: `load_watchlist()` 반환값이 `["NVDA", "AAPL"]`
**확인 방법**: 리스트 길이 2, 각 원소가 대문자 티커 문자열, 추가 순서 유지

**결과**: [x] Pass  [ ] Fail  **코멘트**: test_add_and_remove PASSED

---

### TC-009 [정상] 🤖 AI검증 — Watchlist 등락률 조회 + highlight 판정

**사전조건**: `get_quote` mock이 change_percent=6.5(NVDA), change_percent=1.2(AAPL) 반환
**실행 단계**:
1. `get_watchlist_quotes(["NVDA", "AAPL"])` 호출
**입력값**: `["NVDA", "AAPL"]`
**예상 결과**: NVDA의 `highlight=True` (|6.5| >= 5.0), AAPL의 `highlight=False` (|1.2| < 5.0)
**확인 방법**: 각 항목의 highlight 플래그 값 검증, HIGHLIGHT_THRESHOLD = 5.0 기준

**결과**: [x] Pass  [ ] Fail  **코멘트**: test_get_watchlist_quotes PASSED

---

### TC-010 [정상] 🤖 AI검증 — Guide 카테고리 및 주제 조회

**사전조건**: 없음 (정적 딕셔너리)
**실행 단계**:
1. `get_categories()` 호출
2. `get_topics("chart_basics")` 호출
3. `get_topic_detail("chart_basics", 0)` 호출
**입력값**: category="chart_basics", index=0
**예상 결과**: categories는 5개 항목 포함, topics는 3개 이상, topic_detail에 title/level/what/how/when/example 키 존재
**확인 방법**: `len(get_categories()) == 5`, `"chart_basics" in get_categories()`, topic_detail["title"] == "캔들스틱 차트"

**결과**: [x] Pass  [ ] Fail  **코멘트**: test_get_categories, test_get_topics, test_get_topic_detail PASSED

---

### TC-011 [정상] 🤖 AI검증 — 시장 지수 4종 조회

**사전조건**: `api_client.get_market_indices()` mock이 SPY, NASDAQ, DOW, VIX 데이터 반환
**실행 단계**:
1. `get_market_indices()` 호출
**입력값**: 없음
**예상 결과**: 리스트에 4개 항목, 각각 `symbol` 키가 "S&P 500", "NASDAQ", "DOW", "VIX" 중 하나, `price`와 `change_percent` 존재
**확인 방법**: `len(result) == 4`, 각 항목의 symbol/price/change_percent 키 존재 검증

**결과**: [x] Pass  [ ] Fail  **코멘트**: test_get_market_indices PASSED

---

### TC-012 [정상] 🤖 AI검증 — 급등/급락 Top 5 조회

**사전조건**: `finvizfinance` Overview mock이 gainers/losers DataFrame 반환
**실행 단계**:
1. `get_top_movers()` 호출
**입력값**: 없음
**예상 결과**: `{"gainers": [...], "losers": [...]}` 구조, 각 리스트에 ticker/name/change_pct/price 키 포함
**확인 방법**: result["gainers"]와 result["losers"] 키 존재, 각 항목에 ticker 키 존재

**결과**: [x] Pass  [ ] Fail  **코멘트**: 코드 구조 확인 — finvizfinance Overview 활용, Top 5 제한 (`head(5)`)

---

### TC-013 [엣지] 🤖 AI검증 — 티커 1개만 비교 → same_sector

**사전조건**: 없음
**실행 단계**:
1. `detect_comparison_type(["NVDA"])` 호출
**입력값**: `["NVDA"]`
**예상 결과**: 반환값이 `"same_sector"` — 비교 대상이 1개면 자기 자신과 같은 섹터
**확인 방법**: `assert detect_comparison_type(["NVDA"]) == "same_sector"` — `len(tickers) < 2` 조건 분기 확인

**결과**: [x] Pass  [ ] Fail  **코멘트**: test_single_ticker PASSED

---

### TC-014 [엣지] 🤖 AI검증 — sector/industry 빈값 → cross_sector

**사전조건**: `get_fundamentals` mock이 sector=None, industry=None 반환
**실행 단계**:
1. `detect_comparison_type(["XXX", "NVDA"])` 호출
2. XXX의 sector가 None → "Unknown"으로 변환
**입력값**: `["XXX", "NVDA"]`
**예상 결과**: 반환값이 `"cross_sector"` — Unknown 포함 시 안전하게 cross
**확인 방법**: `assert detect_comparison_type(...) == "cross_sector"` — `any(i["sector"] == "Unknown")` 조건 확인

**결과**: [x] Pass  [ ] Fail  **코멘트**: test_unknown_sector PASSED

---

### TC-015 [엣지] 🤖 AI검증 — Balanced 분류 (애매한 지표값)

**사전조건**: 없음 (순수 함수)
**실행 단계**:
1. `classify_style({"forward_pe": 22, "dividend_yield": 1.0})` 호출
**입력값**: `{"forward_pe": 22, "dividend_yield": 1.0}` — Growth 기준(25) 미달, Value 기준(18 미만) 미달
**예상 결과**: 반환값이 `"Balanced"`
**확인 방법**: forward_pe=22는 25 미만(Growth 아님), 18 이상(Value 아님) → Balanced 기본값 반환

**결과**: [x] Pass  [ ] Fail  **코멘트**: test_balanced_default PASSED

---

### TC-016 [엣지] 🤖 AI검증 — 데이터 전부 None → Balanced 기본값

**사전조건**: 없음 (순수 함수)
**실행 단계**:
1. `classify_style({})` 호출 — 모든 키 누락
**입력값**: `{}`
**예상 결과**: 반환값이 `"Balanced"` — `_to_float(None)` → None, Growth/Value 조건 모두 불충족
**확인 방법**: `assert classify_style({}) == "Balanced"`

**결과**: [x] Pass  [ ] Fail  **코멘트**: test_balanced_no_data PASSED

---

### TC-017 [엣지] 🤖 AI검증 — Watchlist 중복 추가 시 무시

**사전조건**: watchlist.json에 ["NVDA"] 저장 상태
**실행 단계**:
1. `add_to_watchlist("NVDA")` 호출 (이미 존재)
2. `load_watchlist()` 호출
**입력값**: "NVDA" (중복)
**예상 결과**: 리스트에 "NVDA"가 1개만 존재, 에러 발생하지 않음
**확인 방법**: `load_watchlist().count("NVDA") == 1` — 중복 추가 시 `if ticker in wl: return` 분기

**결과**: [x] Pass  [ ] Fail  **코멘트**: test_add_duplicate PASSED

---

### TC-018 [엣지] 🤖 AI검증 — 빈 Watchlist에서 quotes 조회

**사전조건**: 빈 watchlist
**실행 단계**:
1. `get_watchlist_quotes([])` 호출
**입력값**: `[]`
**예상 결과**: 빈 리스트 `[]` 반환, 에러 없음
**확인 방법**: `assert get_watchlist_quotes([]) == []`

**결과**: [x] Pass  [ ] Fail  **코멘트**: test_empty_watchlist_quotes PASSED

---

### TC-019 [엣지] 🤖 AI검증 — Guide 존재하지 않는 카테고리 조회

**사전조건**: 없음 (정적 딕셔너리)
**실행 단계**:
1. `get_topics("nonexistent_category")` 호출
**입력값**: `"nonexistent_category"`
**예상 결과**: 빈 리스트 `[]` 반환
**확인 방법**: `assert get_topics("nonexistent_category") == []`

**결과**: [x] Pass  [ ] Fail  **코멘트**: test_get_topics_invalid_category PASSED

---

### TC-020 [엣지] 🤖 AI검증 — Guide 범위 초과 인덱스 조회

**사전조건**: 없음 (정적 딕셔너리)
**실행 단계**:
1. `get_topic_detail("chart_basics", 999)` 호출
**입력값**: category="chart_basics", index=999
**예상 결과**: `None` 반환
**확인 방법**: `assert get_topic_detail("chart_basics", 999) is None` — `0 <= index < len(topics)` 조건 불충족

**결과**: [x] Pass  [ ] Fail  **코멘트**: test_get_topic_detail_invalid_index PASSED

---

### TC-021 [엣지] 🤖 AI검증 — 시장 지수 캐시 히트

**사전조건**: `cache.get("market_indices", "overview")`가 이전 저장 데이터 반환
**실행 단계**:
1. 캐시에 시장 지수 데이터 설정
2. `get_market_indices()` 호출
**입력값**: 없음
**예상 결과**: API 호출 없이 캐시된 데이터 반환, `api_client.get_market_indices()` 호출 안 됨
**확인 방법**: mock으로 `api_client.get_market_indices` 호출 횟수 = 0 검증

**결과**: [x] Pass  [ ] Fail  **코멘트**: test_indices_cache_hit PASSED

---

### TC-022 [실패] 🤖 AI검증 — fundamentals API 실패 → cross_sector

**사전조건**: `get_fundamentals` mock이 None 반환
**실행 단계**:
1. `detect_comparison_type(["XXX", "YYY"])` 호출
2. 두 종목 모두 fundamentals 실패 → sector="Unknown"
**입력값**: `["XXX", "YYY"]`
**예상 결과**: 반환값이 `"cross_sector"` — Unknown 포함 시 안전하게 cross
**확인 방법**: `assert detect_comparison_type(["XXX", "YYY"]) == "cross_sector"` — None → "Unknown" 변환 로직 확인

**결과**: [x] Pass  [ ] Fail  **코멘트**: test_fundamentals_fail PASSED

---

### TC-023 [실패] 🤖 AI검증 — quote API 실패 → 비교 데이터에 None

**사전조건**: `get_quote` mock이 None 반환, fundamentals/technicals는 정상
**실행 단계**:
1. `get_comparison_data(["NVDA", "AAPL"])` 호출
**입력값**: `["NVDA", "AAPL"]`
**예상 결과**: `result["data"]["NVDA"]["quote"]`이 None, 나머지 구조는 정상 유지, 에러 발생 없음
**확인 방법**: result["data"]["NVDA"]["quote"] is None 검증, result["tickers"]와 result["comparison_type"] 키 존재 확인

**결과**: [x] Pass  [ ] Fail  **코멘트**: get_comparison_data는 개별 API 실패를 None으로 저장하고 계속 진행

---

### TC-024 [실패] 🤖 AI검증 — AI 비교 분석 호출 실패 → error 반환

**사전조건**: `call_claude` mock이 `{"parsed": False, "data": None, "error": "API timeout"}` 반환
**실행 단계**:
1. `run_compare_analysis(["NVDA", "AAPL"], "same_sector", ticker_data)` 호출
**입력값**: tickers=["NVDA", "AAPL"], comparison_type="same_sector"
**예상 결과**: `{"status": "failed", "comparison_type": "same_sector", "analysis": None, "error": "API timeout"}`
**확인 방법**: result["status"] == "failed", result["analysis"] is None, result["error"]에 에러 메시지 포함

**결과**: [x] Pass  [ ] Fail  **코멘트**: test_ai_failure PASSED

---

### TC-025 [실패] 🤖 AI검증 — AI 비교 분석 JSON 파싱 실패

**사전조건**: `call_claude` mock이 `{"parsed": False, "data": None, "error": "JSON parse error"}` 반환
**실행 단계**:
1. `run_compare_analysis(["NVDA", "AAPL"], "cross_sector", ticker_data)` 호출
**입력값**: tickers=["NVDA", "AAPL"], comparison_type="cross_sector"
**예상 결과**: `{"status": "failed", "analysis": None, "error": "JSON parse error"}` — Claude가 비정형 텍스트 반환 시
**확인 방법**: result["status"] == "failed", "error" 키에 파싱 실패 메시지 포함

**결과**: [x] Pass  [ ] Fail  **코멘트**: call_claude 내부에서 JSON 파싱 실패 시 parsed=False 반환, compare_agent가 이를 status="failed"로 전환

---

### TC-026 [실패] 🤖 AI검증 — Watchlist 빈 문자열 추가 → ValueError

**사전조건**: 아무 상태
**실행 단계**:
1. `add_to_watchlist("")` 호출
**입력값**: `""`
**예상 결과**: `ValueError("티커가 비어있습니다.")` 예외 발생
**확인 방법**: `with pytest.raises(ValueError)` 검증

**결과**: [x] Pass  [ ] Fail  **코멘트**: test_add_empty_raises PASSED

---

### TC-027 [실패] 🤖 AI검증 — Watchlist 없는 종목 제거 → KeyError

**사전조건**: watchlist.json에 "NVDA"만 존재
**실행 단계**:
1. `remove_from_watchlist("AAPL")` 호출 — 존재하지 않는 종목
**입력값**: `"AAPL"`
**예상 결과**: `KeyError("'AAPL'이(가) Watchlist에 없습니다.")` 예외 발생
**확인 방법**: `with pytest.raises(KeyError)` 검증

**결과**: [x] Pass  [ ] Fail  **코멘트**: test_remove_not_found PASSED

---

### TC-028 [실패] 🤖 AI검증 — 시장 지수 API 실패 → None 반환

**사전조건**: `api_client.get_market_indices()` mock이 None 반환, 캐시 비어있음
**실행 단계**:
1. `get_market_indices()` 호출
**입력값**: 없음
**예상 결과**: `None` 반환, 에러 발생 없음
**확인 방법**: `assert get_market_indices() is None`

**결과**: [x] Pass  [ ] Fail  **코멘트**: test_market_indices_fail PASSED

---

### TC-029 [실패] 🤖 AI검증 — 시장 뉴스 API 실패 → None 반환

**사전조건**: `api_client.finnhub.get_market_news()` mock이 None 반환, 캐시 비어있음
**실행 단계**:
1. `get_market_news()` 호출
**입력값**: 없음
**예상 결과**: `None` 반환, 에러 발생 없음
**확인 방법**: `assert get_market_news() is None`

**결과**: [x] Pass  [ ] Fail  **코멘트**: test_market_news_fail PASSED

---

### TC-030 [실패] 🤖 AI검증 — top_movers Finviz 실패 → None 반환

**사전조건**: `finvizfinance` import 시 Exception 발생 또는 screener_view() 실패
**실행 단계**:
1. `get_top_movers()` 호출
**입력값**: 없음
**예상 결과**: `None` 반환 — `except Exception` 블록에서 로깅 후 None 리턴
**확인 방법**: `assert get_top_movers() is None` — try/except 블록이 Exception을 포괄적으로 처리하는지 코드 확인

**결과**: [x] Pass  [ ] Fail  **코멘트**: get_top_movers() 내 `except Exception as e` 블록에서 logger.warning 후 None 반환 확인

---

## 테스트 완료 체크리스트

- [x] 모든 정상 케이스 Pass
- [x] 엣지 케이스에서 앱이 크래시 없이 처리됨
- [x] 실패 케이스에서 적절한 에러/None 반환 확인됨
- [x] 43개 단위 테스트 전체 PASSED (`pytest tests/test_phase5_compare.py -v`)

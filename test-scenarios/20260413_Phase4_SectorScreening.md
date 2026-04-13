# 테스트 시나리오 — Phase 4 Sector Screening

- **생성일**: 2026-04-13
- **대상 Phase**: Phase 4
- **구현 기능**: 섹터/테마 선택 → 3단계 필터(공통/프리셋/적응형 완화) → AI 축약 분석 → Top 5 추천
- **전제조건**: Phase 2-3 완료, `.env`에 `ANTHROPIC_API_KEY` 설정, `config/themes.json` 존재

---

## 시나리오 목록

| ID | 유형 | 제목 | 검증 | 우선순위 |
|----|------|------|------|---------|
| TC-001 | 정상 | GICS 섹터 종목 조회 정상 반환 | 🤖 AI검증 | High |
| TC-002 | 정상 | 커스텀 테마 티커 조회 | 🤖 AI검증 | High |
| TC-003 | 정상 | GICS 섹터 → 프리셋 매핑 확인 | 🤖 AI검증 | High |
| TC-004 | 정상 | themes.json 정상 로드 및 기본 5개 테마 존재 | 🤖 AI검증 | High |
| TC-005 | 정상 | 테마 생성 성공 (5개 티커 + 유효 프리셋) | 🤖 AI검증 | High |
| TC-006 | 정상 | 테마 삭제 성공 | 🤖 AI검증 | Medium |
| TC-007 | 정상 | large_stable 프리셋 필터 — 시총 $50B+ PE 양수만 통과 | 🤖 AI검증 | High |
| TC-008 | 정상 | 적응형 완화 없이 10개+ 통과 → 상위 10개 선정 | 🤖 AI검증 | High |
| TC-009 | 정상 | 전체 섹터 스크리닝 파이프라인 (필터 → AI → Top 5) | 🤖 AI검증 | High |
| TC-010 | 정상 | 커스텀 테마 스크리닝 파이프라인 | 🤖 AI검증 | High |
| TC-011 | 엣지 | 알 수 없는 섹터 → mid_growth 기본값 폴백 | 🤖 AI검증 | Medium |
| TC-012 | 엣지 | early_growth 프리셋 — PE 음수 종목도 통과 | 🤖 AI검증 | Medium |
| TC-013 | 엣지 | dividend 프리셋 — 배당률 2% 미만 제외 | 🤖 AI검증 | Medium |
| TC-014 | 엣지 | 적응형 완화 3~4개 통과 → 시총 기준 1단계 완화 | 🤖 AI검증 | High |
| TC-015 | 엣지 | 적응형 완화 0~2개 통과 → 필터 무시, 시총 상위 10개 | 🤖 AI검증 | High |
| TC-016 | 엣지 | _to_number에 "1.5T", "200B", "15.3%" 등 다양한 형식 입력 | 🤖 AI검증 | Medium |
| TC-017 | 엣지 | 테마 생성 시 소문자 티커 → 대문자 자동 변환 | 🤖 AI검증 | Low |
| TC-018 | 엣지 | 캐시 적중 시 AI 호출 없이 즉시 반환 | 🤖 AI검증 | High |
| TC-019 | 실패 | 티커 5개 미만으로 테마 생성 → ValueError | 🤖 AI검증 | High |
| TC-020 | 실패 | 유효하지 않은 프리셋으로 테마 생성 → ValueError | 🤖 AI검증 | High |
| TC-021 | 실패 | 존재하지 않는 테마 삭제 → KeyError | 🤖 AI검증 | Medium |
| TC-022 | 실패 | 섹터 종목 조회 실패 (API 실패) → None 반환 | 🤖 AI검증 | High |
| TC-023 | 실패 | AI 분석 2회 모두 실패 → status "partial" 반환 | 🤖 AI검증 | High |
| TC-024 | 실패 | 빈 종목 리스트 필터 → 빈 배열 + 경고 메시지 | 🤖 AI검증 | Medium |
| TC-025 | 실패 | 존재하지 않는 테마 티커 조회 → None | 🤖 AI검증 | Medium |

---

### TC-001 [정상] 🤖 AI검증 — GICS 섹터 종목 조회 정상 반환

**사전조건**: `data/sector_data.py` 구현 완료, Finviz 스크리너 API 접속 가능
**실행 단계**:
1. `get_sector_tickers("Information Technology")` 호출
2. 반환값 확인
**입력값**: 섹터 = `"Information Technology"`
**예상 결과**: 반환값이 `None`이 아닌 리스트이고, 각 항목에 `ticker`, `name`, `market_cap` 키가 존재하며, 종목 수 1개 이상
**확인 방법**: `pytest tests/test_phase4_sector.py::TestSectorData::test_get_sector_tickers -v` 실행 후 PASSED 확인

**결과**: [x] Pass  [ ] Fail  **코멘트**: PASSED (2026-04-13)

---

### TC-002 [정상] 🤖 AI검증 — 커스텀 테마 티커 조회

**사전조건**: `config/themes.json`에 기본 테마 존재
**실행 단계**:
1. `get_theme_tickers("AI_semiconductor")` 호출
2. 반환 리스트 확인
**입력값**: 테마 = `"AI_semiconductor"`
**예상 결과**: `["NVDA", "AMD", "AVGO", "TSM", "MRVL", "INTC", "QCOM"]` 반환, 길이 7개
**확인 방법**: `pytest tests/test_phase4_sector.py::TestSectorData::test_get_theme_tickers -v`

**결과**: [x] Pass  [ ] Fail  **코멘트**: PASSED (2026-04-13)

---

### TC-003 [정상] 🤖 AI검증 — GICS 섹터 → 프리셋 매핑 확인

**사전조건**: `SECTOR_PRESET_MAP` 정의 완료
**실행 단계**:
1. `get_preset_for_sector("Information Technology")` → `"large_stable"` 확인
2. `get_preset_for_sector("Health Care")` → `"early_growth"` 확인
3. `get_preset_for_sector("Utilities")` → `"dividend"` 확인
4. `get_preset_for_sector("Energy")` → `"mid_growth"` 확인
**입력값**: 4종 대표 섹터
**예상 결과**: 각 섹터가 설계 문서의 프리셋 매핑과 일치
**확인 방법**: `pytest tests/test_phase4_sector.py::TestSectorData::test_preset_for_sector_known -v`

**결과**: [x] Pass  [ ] Fail  **코멘트**: PASSED (2026-04-13)

---

### TC-004 [정상] 🤖 AI검증 — themes.json 정상 로드 및 기본 5개 테마 존재

**사전조건**: `config/themes.json` 파일 존재
**실행 단계**:
1. `load_themes()` 호출
2. 반환된 dict 확인
**입력값**: 없음
**예상 결과**: 반환값이 `dict`이고, `"AI_semiconductor"`, `"defense"`, `"clean_energy"`, `"cybersecurity"`, `"space"` 5개 키 존재. 각 테마에 `tickers`(5개+), `preset`(4종 중 하나) 키 포함
**확인 방법**: `pytest tests/test_phase4_sector.py::TestThemeManager::test_load_themes_returns_dict -v`

**결과**: [x] Pass  [ ] Fail  **코멘트**: PASSED (2026-04-13)

---

### TC-005 [정상] 🤖 AI검증 — 테마 생성 성공 (5개 티커 + 유효 프리셋)

**사전조건**: `themes.json` 정상 상태
**실행 단계**:
1. `create_theme("test_theme", ["AAPL", "MSFT", "GOOGL", "AMZN", "META"], "large_stable")` 호출
2. `load_themes()` 호출하여 `"test_theme"` 존재 확인
3. 테스트 후 `delete_theme("test_theme")` 으로 정리
**입력값**: 이름 = `"test_theme"`, 티커 5개, 프리셋 = `"large_stable"`
**예상 결과**: `themes.json`에 `"test_theme"` 키가 생성되고, `preset`이 `"large_stable"`, `tickers` 길이 5
**확인 방법**: `pytest tests/test_phase4_sector.py::TestThemeManager::test_create_theme_success -v`

**결과**: [x] Pass  [ ] Fail  **코멘트**: PASSED (2026-04-13)

---

### TC-006 [정상] 🤖 AI검증 — 테마 삭제 성공

**사전조건**: 삭제 대상 테마가 존재하는 상태
**실행 단계**:
1. `create_theme("to_delete", [...5개...], "mid_growth")` 으로 테마 생성
2. `delete_theme("to_delete")` 호출
3. `load_themes()` 에서 `"to_delete"` 부재 확인
**입력값**: 삭제 대상 = `"to_delete"`
**예상 결과**: `load_themes()` 결과에 `"to_delete"` 키가 존재하지 않음
**확인 방법**: `pytest tests/test_phase4_sector.py::TestThemeManager::test_delete_theme_success -v`

**결과**: [x] Pass  [ ] Fail  **코멘트**: PASSED (2026-04-13)

---

### TC-007 [정상] 🤖 AI검증 — large_stable 프리셋 필터 — 시총 $50B+ PE 양수만 통과

**사전조건**: `stock_filter.py` 구현 완료
**실행 단계**:
1. 시총 $200B~$130B 범위의 종목 15개 생성 (PE 양수)
2. `filter_stocks(stocks, "large_stable")` 호출
**입력값**: 15개 종목 (시총 $50B+ 통과 가능)
**예상 결과**: 반환 리스트 길이 ≤ 10, `relaxed` = `False`, `warning` = `None`. 모든 통과 종목의 `market_cap` ≥ 50,000,000,000
**확인 방법**: `pytest tests/test_phase4_sector.py::TestStockFilter::test_large_stable_normal -v`

**결과**: [x] Pass  [ ] Fail  **코멘트**: PASSED (2026-04-13)

---

### TC-008 [정상] 🤖 AI검증 — 적응형 완화 없이 10개+ 통과 → 상위 10개 선정

**사전조건**: 프리셋 통과 종목이 10개 이상인 데이터
**실행 단계**:
1. 시총 $200B~$130B 범위의 종목 15개 생성
2. `filter_stocks(stocks, "large_stable")` 호출
3. 반환 리스트 길이 확인
**입력값**: 15개 종목 (모두 $50B+ 통과)
**예상 결과**: 정확히 10개 반환, 시총 내림차순 정렬, `relaxed` = `False`
**확인 방법**: `len(filtered) == 10`, `filtered[0]["market_cap"] > filtered[9]["market_cap"]`

**결과**: [x] Pass  [ ] Fail  **코멘트**: PASSED (2026-04-13)

---

### TC-009 [정상] 🤖 AI검증 — 전체 섹터 스크리닝 파이프라인 (필터 → AI → Top 5)

**사전조건**: API 접속 가능, Claude API 키 설정 완료
**실행 단계**:
1. `run_sector_screening("Information Technology")` 호출
2. 반환된 dict의 전체 구조 확인
**입력값**: 섹터 = `"Information Technology"`
**예상 결과**: `status`가 `"success"`, `sector`가 `"Information Technology"`, `top5` 배열 길이 5, 각 항목에 `ticker`, `score`, `reason` 키 존재. `sector_outlook`이 비어있지 않은 문자열. `is_theme`이 `False`
**확인 방법**: `pytest tests/test_phase4_sector.py::TestSectorAnalyzer::test_run_sector_screening_success -v`

**결과**: [x] Pass  [ ] Fail  **코멘트**: PASSED (2026-04-13)

---

### TC-010 [정상] 🤖 AI검증 — 커스텀 테마 스크리닝 파이프라인

**사전조건**: `config/themes.json`에 `"AI_semiconductor"` 테마 존재
**실행 단계**:
1. `run_sector_screening("AI_semiconductor")` 호출
2. 반환값에서 `is_theme`, `filter_applied` 확인
**입력값**: 테마 = `"AI_semiconductor"`
**예상 결과**: `status`가 `"success"`, `is_theme`이 `True`, `sector`가 `"AI_semiconductor"`, `filter_applied`가 `"large_stable"`, `top5` 배열 존재
**확인 방법**: `pytest tests/test_phase4_sector.py::TestSectorAnalyzer::test_run_theme_screening -v`

**결과**: [x] Pass  [ ] Fail  **코멘트**: PASSED (2026-04-13)

---

### TC-011 [엣지] 🤖 AI검증 — 알 수 없는 섹터 → mid_growth 기본값 폴백

**사전조건**: `SECTOR_PRESET_MAP`에 없는 섹터명 준비
**실행 단계**:
1. `get_preset_for_sector("Unknown Sector")` 호출
**입력값**: 섹터 = `"Unknown Sector"`
**예상 결과**: `"mid_growth"` 반환 (기본값)
**확인 방법**: `pytest tests/test_phase4_sector.py::TestSectorData::test_preset_for_sector_unknown -v`

**결과**: [x] Pass  [ ] Fail  **코멘트**: PASSED (2026-04-13)

---

### TC-012 [엣지] 🤖 AI검증 — early_growth 프리셋 — PE 음수 종목도 통과

**사전조건**: `stock_filter.py` 구현 완료
**실행 단계**:
1. PE -10 (적자 기업) + PE 30 (흑자 기업) 종목 생성 (시총 $5B)
2. `filter_stocks(stocks, "early_growth")` 호출
**입력값**: PE 음수 1개 + PE 양수 1개
**예상 결과**: 두 종목 모두 통과. `early_growth`는 `pe_positive`가 `False`이므로 PE 조건 미적용
**확인 방법**: `pytest tests/test_phase4_sector.py::TestStockFilter::test_early_growth_no_pe_requirement -v`

**결과**: [x] Pass  [ ] Fail  **코멘트**: PASSED (2026-04-13)

---

### TC-013 [엣지] 🤖 AI검증 — dividend 프리셋 — 배당률 2% 미만 제외

**사전조건**: `stock_filter.py` 구현 완료
**실행 단계**:
1. 배당률 3.5% / 0.5% / 없음 3종목 생성 (시총 $10B, PE 양수)
2. `filter_stocks(stocks, "dividend")` 호출
**입력값**: 배당률 3.5%, 0.5%, None
**예상 결과**: 배당률 3.5% 종목만 통과. 0.5%는 기준 미달, None은 데이터 없음으로 미통과
**확인 방법**: `pytest tests/test_phase4_sector.py::TestStockFilter::test_dividend_filter -v`

**결과**: [x] Pass  [ ] Fail  **코멘트**: PASSED (2026-04-13)

---

### TC-014 [엣지] 🤖 AI검증 — 적응형 완화 3~4개 통과 → 시총 기준 1단계 완화

**사전조건**: large_stable 기준($50B+) 통과 종목이 3개뿐인 데이터
**실행 단계**:
1. 시총 $80B, $60B, $55B, $30B, $25B 종목 5개 생성 (PE 양수)
2. `filter_stocks(stocks, "large_stable")` 호출
**입력값**: 5개 종목 (3개만 $50B+ 통과)
**예상 결과**: `relaxed`가 `True`, `warning`에 `"완화"` 문자열 포함. 완화 기준 $20B+ 적용으로 $30B, $25B 종목도 포함되어 총 4~5개 반환
**확인 방법**: `pytest tests/test_phase4_sector.py::TestStockFilter::test_adaptive_relaxation_3_4 -v`

**결과**: [x] Pass  [ ] Fail  **코멘트**: PASSED (2026-04-13)

---

### TC-015 [엣지] 🤖 AI검증 — 적응형 완화 0~2개 통과 → 필터 무시, 시총 상위 10개

**사전조건**: large_stable 기준($50B+) 통과 종목이 0개인 데이터
**실행 단계**:
1. 시총 $30B, $20B, $10B 종목 3개 생성 (모두 $50B 미달)
2. `filter_stocks(stocks, "large_stable")` 호출
**입력값**: 3개 종목 (모두 $50B 미달)
**예상 결과**: `relaxed`가 `True`, `warning`에 `"시총 상위"` 문자열 포함. 프리셋 필터 무시하고 시총 내림차순 3개 전부 반환. `filtered[0]["ticker"]`이 시총 최대 종목
**확인 방법**: `pytest tests/test_phase4_sector.py::TestStockFilter::test_adaptive_relaxation_0_2 -v`

**결과**: [x] Pass  [ ] Fail  **코멘트**: PASSED (2026-04-13)

---

### TC-016 [엣지] 🤖 AI검증 — _to_number에 다양한 형식 입력

**사전조건**: `stock_filter.py`의 `_to_number` 함수 구현 완료
**실행 단계**:
1. `_to_number(100)` → `100.0`
2. `_to_number("1.5T")` → `1.5e12`
3. `_to_number("200B")` → `200e9`
4. `_to_number("50M")` → `50e6`
5. `_to_number("15.3%")` → `15.3`
6. `_to_number(None)` → `None`
7. `_to_number("invalid")` → `None`
**입력값**: int, float, Finviz 형식 문자열, None, 잘못된 문자열
**예상 결과**: 각 입력에 대해 위에 명시된 값 반환
**확인 방법**: `pytest tests/test_phase4_sector.py::TestStockFilter::test_to_number_variants -v`

**결과**: [x] Pass  [ ] Fail  **코멘트**: PASSED (2026-04-13)

---

### TC-017 [엣지] 🤖 AI검증 — 테마 생성 시 소문자 티커 → 대문자 자동 변환

**사전조건**: `theme_manager.py` 구현 완료
**실행 단계**:
1. `create_theme("upper_test", ["aapl", "msft", "googl", "amzn", "meta"], "large_stable")` 호출
2. `load_themes()["upper_test"]["tickers"][0]` 확인
3. 정리: `delete_theme("upper_test")`
**입력값**: 소문자 티커 5개
**예상 결과**: 저장된 티커가 모두 대문자 (`"AAPL"`, `"MSFT"`, ...)
**확인 방법**: `pytest tests/test_phase4_sector.py::TestThemeManager::test_create_theme_uppercase -v`

**결과**: [x] Pass  [ ] Fail  **코멘트**: PASSED (2026-04-13)

---

### TC-018 [엣지] 🤖 AI검증 — 캐시 적중 시 AI 호출 없이 즉시 반환

**사전조건**: 이전 호출로 캐시에 결과 저장된 상태
**실행 단계**:
1. 캐시에 `"Energy"` 섹터 결과가 존재하도록 설정
2. `run_sector_screening("Energy")` 호출
**입력값**: 캐시에 저장된 섹터 = `"Energy"`
**예상 결과**: 캐시된 결과가 그대로 반환. `get_sector_tickers`, `filter_stocks`, `call_claude` 함수가 호출되지 않음
**확인 방법**: `pytest tests/test_phase4_sector.py::TestSectorAnalyzer::test_cache_hit -v`

**결과**: [x] Pass  [ ] Fail  **코멘트**: PASSED (2026-04-13)

---

### TC-019 [실패] 🤖 AI검증 — 티커 5개 미만으로 테마 생성 → ValueError

**사전조건**: `theme_manager.py` 구현 완료
**실행 단계**:
1. `create_theme("bad_theme", ["AAPL", "MSFT"], "large_stable")` 호출
**입력값**: 티커 2개 (최소 5개 미달)
**예상 결과**: `ValueError` 발생, 메시지에 `"최소 5개"` 포함. `themes.json`에 `"bad_theme"` 미생성
**확인 방법**: `pytest tests/test_phase4_sector.py::TestThemeManager::test_create_theme_min_tickers -v`

**결과**: [x] Pass  [ ] Fail  **코멘트**: PASSED (2026-04-13)

---

### TC-020 [실패] 🤖 AI검증 — 유효하지 않은 프리셋으로 테마 생성 → ValueError

**사전조건**: `theme_manager.py` 구현 완료
**실행 단계**:
1. `create_theme("bad_theme", ["A", "B", "C", "D", "E"], "invalid_preset")` 호출
**입력값**: 프리셋 = `"invalid_preset"` (허용: large_stable, mid_growth, early_growth, dividend)
**예상 결과**: `ValueError` 발생, 메시지에 `"유효하지 않은 프리셋"` 포함
**확인 방법**: `pytest tests/test_phase4_sector.py::TestThemeManager::test_create_theme_invalid_preset -v`

**결과**: [x] Pass  [ ] Fail  **코멘트**: PASSED (2026-04-13)

---

### TC-021 [실패] 🤖 AI검증 — 존재하지 않는 테마 삭제 → KeyError

**사전조건**: `themes.json`에 해당 테마가 없는 상태
**실행 단계**:
1. `delete_theme("nonexistent_theme_xyz")` 호출
**입력값**: 존재하지 않는 테마 = `"nonexistent_theme_xyz"`
**예상 결과**: `KeyError` 발생, 메시지에 `"존재하지 않습니다"` 포함
**확인 방법**: `pytest tests/test_phase4_sector.py::TestThemeManager::test_delete_theme_not_found -v`

**결과**: [x] Pass  [ ] Fail  **코멘트**: PASSED (2026-04-13)

---

### TC-022 [실패] 🤖 AI검증 — 섹터 종목 조회 실패 (API 실패) → None 반환

**사전조건**: `sector_data.py` 구현 완료
**실행 단계**:
1. API가 `None`을 반환하도록 설정
2. `get_sector_tickers("Nonexistent Sector")` 호출
**입력값**: 존재하지 않는 섹터
**예상 결과**: `None` 반환, 예외 발생 없음
**확인 방법**: `pytest tests/test_phase4_sector.py::TestSectorData::test_get_sector_tickers_fail -v`

**결과**: [x] Pass  [ ] Fail  **코멘트**: PASSED (2026-04-13)

---

### TC-023 [실패] 🤖 AI검증 — AI 분석 2회 모두 실패 → status "partial" 반환

**사전조건**: `sector_analyzer.py` 구현 완료, Claude `call_claude`가 `parsed: False` 반환
**실행 단계**:
1. `call_claude`가 `{"parsed": False, "raw_output": "", "error": "API error"}` 반환하도록 설정
2. `run_sector_screening("Information Technology")` 호출
**입력값**: AI 분석 실패 상태
**예상 결과**: `status`가 `"partial"`, `error`에 `"AI 분석 실패"` 포함, `top5` 배열이 필터 결과에서 상위 5개로 채워짐 (score = None), `sector_outlook`이 `None`
**확인 방법**: `pytest tests/test_phase4_sector.py::TestSectorAnalyzer::test_run_sector_ai_fail_partial -v`

**결과**: [x] Pass  [ ] Fail  **코멘트**: PASSED (2026-04-13)

---

### TC-024 [실패] 🤖 AI검증 — 빈 종목 리스트 필터 → 빈 배열 + 경고 메시지

**사전조건**: `stock_filter.py` 구현 완료
**실행 단계**:
1. `filter_stocks([], "large_stable")` 호출
**입력값**: 빈 리스트 `[]`
**예상 결과**: `filtered`가 빈 리스트 `[]`, `warning`이 `None`이 아닌 경고 메시지 (`"종목 데이터가 없습니다."`)
**확인 방법**: `pytest tests/test_phase4_sector.py::TestStockFilter::test_empty_stocks -v`

**결과**: [x] Pass  [ ] Fail  **코멘트**: PASSED (2026-04-13)

---

### TC-025 [실패] 🤖 AI검증 — 존재하지 않는 테마 티커 조회 → None

**사전조건**: `themes.json`에 해당 테마가 없는 상태
**실행 단계**:
1. `get_theme_tickers("nonexistent_xyz")` 호출
**입력값**: 존재하지 않는 테마 = `"nonexistent_xyz"`
**예상 결과**: `None` 반환, 예외 발생 없음
**확인 방법**: `pytest tests/test_phase4_sector.py::TestSectorData::test_get_theme_tickers_not_found -v`

**결과**: [x] Pass  [ ] Fail  **코멘트**: PASSED (2026-04-13)

---

## 테스트 완료 체크리스트

- [x] 모든 정상 케이스 Pass (TC-001 ~ TC-010)
- [x] 엣지 케이스에서 앱이 크래시 없이 처리됨 (TC-011 ~ TC-018)
- [x] 실패 케이스에서 적절한 예외 또는 안전한 반환값 (TC-019 ~ TC-025)
- [x] pytest 39개 테스트 전부 PASSED (23.32초, 2026-04-13)

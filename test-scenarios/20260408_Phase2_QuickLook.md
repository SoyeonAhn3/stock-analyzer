# 테스트 시나리오 — Phase 2 Quick Look

- **생성일**: 2026-04-08
- **대상 Phase**: Phase 2
- **구현 기능**: 시세/히스토리/재무/기술지표 데이터 수집 + Python 직접 계산 폴백 + 차트 빌더 + 툴팁
- **전제조건**: Phase 1 완료 (API 래퍼 + 캐싱 사용 가능), Python 패키지 설치 완료

---

## 시나리오 목록

| ID | 유형 | 제목 | 검증 | 우선순위 |
|----|------|------|------|---------|
| TC-001 | 정상 | quote.py 시세 조회 정상 반환 | 🤖 AI검증 | High |
| TC-002 | 정상 | history.py 1Y 히스토리 DataFrame 반환 | 🤖 AI검증 | High |
| TC-003 | 정상 | history.py MA50/MA200 컬럼 포함 확인 | 🤖 AI검증 | High |
| TC-004 | 정상 | fundamentals.py 재무 지표 정상 반환 | 🤖 AI검증 | High |
| TC-005 | 정상 | technicals.py 기술지표 + 신호 판정 | 🤖 AI검증 | High |
| TC-006 | 정상 | indicators.py RSI Python 직접 계산 | 🤖 AI검증 | High |
| TC-007 | 정상 | indicators.py MACD Python 직접 계산 | 🤖 AI검증 | High |
| TC-008 | 정상 | indicators.py 볼린저밴드 Python 직접 계산 | 🤖 AI검증 | High |
| TC-009 | 정상 | chart_builder 라인 차트 생성 | 🤖 AI검증 | Medium |
| TC-010 | 정상 | chart_builder 캔들스틱 차트 생성 | 🤖 AI검증 | Medium |
| TC-011 | 정상 | tooltips 키 조회 | 🤖 AI검증 | Low |
| TC-012 | 엣지 | quote.py 존재하지 않는 티커 → None | 🤖 AI검증 | Medium |
| TC-013 | 엣지 | history.py 매핑에 없는 기간 입력 | 🤖 AI검증 | Medium |
| TC-014 | 엣지 | fundamentals.py force_fallback=True | 🤖 AI검증 | Medium |
| TC-015 | 엣지 | technicals.py force_fallback=True (Python 계산 폴백) | 🤖 AI검증 | High |
| TC-016 | 엣지 | indicators.py 데이터 부족 시 None 반환 | 🤖 AI검증 | Medium |
| TC-017 | 엣지 | chart_builder 빈 DataFrame 입력 | 🤖 AI검증 | Medium |
| TC-018 | 엣지 | tooltips 존재하지 않는 키 → 빈 문자열 | 🤖 AI검증 | Low |
| TC-019 | 실패 | quote.py API 전체 실패 시 None | 🤖 AI검증 | High |
| TC-020 | 실패 | history.py API 전체 실패 시 None | 🤖 AI검증 | High |
| TC-021 | 실패 | technicals.py API + 폴백 모두 실패 시 None | 🤖 AI검증 | High |
| TC-022 | 정상 | technicals.py RSI 신호 판정 경계값 (30/70) | 🤖 AI검증 | Medium |

---

### TC-001 [정상] 🤖 AI검증 — quote.py 시세 조회 정상 반환

**사전조건**: api_client.get_quote가 정상 응답 반환
**실행 단계**:
1. api_client.get_quote 호출 (price=120.5, previous_close=118.3, change=2.2 등)
2. `get_quote("NVDA")` 호출
**입력값**: 티커 = `"NVDA"`
**예상 결과**: `ticker`가 `"NVDA"`, `price`가 `120.5`, `change`가 `2.2`, `change_percent`가 존재, `source` 필드 존재
**확인 방법**: pytest assertion으로 각 필드 값 검증

**결과**: [x] Pass  [ ] Fail  **코멘트**: PASSED

---

### TC-002 [정상] 🤖 AI검증 — history.py 1Y 히스토리 DataFrame 반환

**사전조건**: api_client.get_history가 1년치 OHLCV 데이터 반환
**실행 단계**:
1. api_client.get_history 호출 (100행 OHLCV 데이터)
2. `get_history("NVDA", "1Y")` 호출
**입력값**: 티커 = `"NVDA"`, 기간 = `"1Y"`
**예상 결과**: 반환 타입이 `pd.DataFrame`, 컬럼에 `Date`, `Open`, `High`, `Low`, `Close`, `Volume` 포함, 행 수 100개
**확인 방법**: `isinstance(result, pd.DataFrame)`, `result.columns` 확인

**결과**: [x] Pass  [ ] Fail  **코멘트**: PASSED

---

### TC-003 [정상] 🤖 AI검증 — history.py MA50/MA200 컬럼 포함 확인

**사전조건**: TC-002와 동일
**실행 단계**:
1. `get_history("NVDA", "1Y")` 호출 (일봉 데이터)
**입력값**: 100행 OHLCV 데이터
**예상 결과**: DataFrame에 `MA50`, `MA200` 컬럼이 존재하고, 값이 NaN이 아닌 행이 1개 이상
**확인 방법**: `"MA50" in df.columns`, `df["MA50"].notna().sum() > 0`

**결과**: [x] Pass  [ ] Fail  **코멘트**: PASSED

---

### TC-004 [정상] 🤖 AI검증 — fundamentals.py 재무 지표 정상 반환

**사전조건**: api_client.get_fundamentals가 정상 응답 반환
**실행 단계**:
1. api_client.get_fundamentals 호출 (pe_ratio=35.2, eps=4.05, sector="Technology" 등)
2. `get_fundamentals("NVDA")` 호출
**입력값**: 티커 = `"NVDA"`
**예상 결과**: `pe`가 `35.2`, `eps`가 `4.05`, `sector`가 `"Technology"`, `industry` 필드 존재
**확인 방법**: pytest assertion으로 각 필드 값 검증

**결과**: [x] Pass  [ ] Fail  **코멘트**: PASSED

---

### TC-005 [정상] 🤖 AI검증 — technicals.py 기술지표 + 신호 판정

**사전조건**: api_client.get_technicals / get_quote 정상 응답
**실행 단계**:
1. get_technicals 호출 (RSI values, MACD values, BBands values, MA50/MA200 values)
2. get_quote 호출 (price=120.5)
3. `get_technicals("NVDA")` 호출
**입력값**: 티커 = `"NVDA"`
**예상 결과**: `rsi`에 `value`와 `signal` 존재, `macd`에 `signal`과 `detail` 존재, `source`가 `"twelvedata"`
**확인 방법**: 각 지표 dict의 키 존재 여부 및 signal 값이 "bullish"/"neutral"/"bearish" 중 하나

**결과**: [x] Pass  [ ] Fail  **코멘트**: PASSED

---

### TC-006 [정상] 🤖 AI검증 — indicators.py RSI Python 직접 계산

**사전조건**: 없음 (순수 계산 함수)
**실행 단계**:
1. 100개의 종가 pd.Series 생성 (100~200 사이 임의값)
2. `calc_rsi(close_prices)` 호출
**입력값**: 100개 종가 Series
**예상 결과**: 반환 타입이 `pd.Series`, 길이가 100, 유효한 RSI 값(15번째부터)이 0~100 범위
**확인 방법**: `isinstance(result, pd.Series)`, `0 <= rsi_val <= 100`

**결과**: [x] Pass  [ ] Fail  **코멘트**: PASSED

---

### TC-007 [정상] 🤖 AI검증 — indicators.py MACD Python 직접 계산

**사전조건**: 없음 (순수 계산 함수)
**실행 단계**:
1. 100개의 종가 pd.Series 생성
2. `calc_macd(close_prices)` 호출
**입력값**: 100개 종가 Series
**예상 결과**: 반환값이 dict, `"macd"`, `"signal"`, `"histogram"` 키 존재, 각각 pd.Series 타입
**확인 방법**: `"macd" in result`, `isinstance(result["macd"], pd.Series)`

**결과**: [x] Pass  [ ] Fail  **코멘트**: PASSED

---

### TC-008 [정상] 🤖 AI검증 — indicators.py 볼린저밴드 Python 직접 계산

**사전조건**: 없음 (순수 계산 함수)
**실행 단계**:
1. 100개의 종가 pd.Series 생성
2. `calc_bbands(close_prices)` 호출
**입력값**: 100개 종가 Series
**예상 결과**: `"upper"`, `"middle"`, `"lower"` 키 존재, upper > middle > lower 관계 성립 (유효 구간)
**확인 방법**: 마지막 유효값에서 `upper > middle > lower` 확인

**결과**: [x] Pass  [ ] Fail  **코멘트**: PASSED

---

### TC-009 [정상] 🤖 AI검증 — chart_builder 라인 차트 생성

**사전조건**: OHLCV + MA50/MA200 컬럼이 있는 DataFrame
**실행 단계**:
1. 50행 OHLCV DataFrame 생성 (MA50, MA200 포함)
2. `build_price_chart(df, chart_type="line")` 호출
**입력값**: 50행 DataFrame
**예상 결과**: 반환 타입이 `go.Figure`, `fig.data`에 trace가 1개 이상 존재
**확인 방법**: `isinstance(fig, go.Figure)`, `len(fig.data) >= 1`

**결과**: [x] Pass  [ ] Fail  **코멘트**: PASSED

---

### TC-010 [정상] 🤖 AI검증 — chart_builder 캔들스틱 차트 생성

**사전조건**: TC-009와 동일
**실행 단계**:
1. `build_price_chart(df, chart_type="candlestick")` 호출
**입력값**: 50행 DataFrame
**예상 결과**: `fig.data[0]`의 타입이 `go.Candlestick`
**확인 방법**: `isinstance(fig.data[0], go.Candlestick)`

**결과**: [x] Pass  [ ] Fail  **코멘트**: PASSED

---

### TC-011 [정상] 🤖 AI검증 — tooltips 키 조회

**사전조건**: 없음
**실행 단계**:
1. `get_tooltip("pe")` 호출
2. `get_tooltip("rsi")` 호출
**입력값**: 키 = `"pe"`, `"rsi"`
**예상 결과**: 빈 문자열이 아닌 설명 텍스트 반환, "주가수익비율" 포함 (pe), "상대강도지수" 포함 (rsi)
**확인 방법**: `len(result) > 0`, 키워드 포함 확인

**결과**: [x] Pass  [ ] Fail  **코멘트**: PASSED

---

### TC-012 [엣지] 🤖 AI검증 — quote.py 존재하지 않는 티커 → None

**사전조건**: api_client.get_quote가 None 반환
**실행 단계**:
1. `get_quote("ZZZZZ999")` 호출
**입력값**: 티커 = `"ZZZZZ999"`
**예상 결과**: `None` 반환, 예외 발생 없음
**확인 방법**: `result is None`

**결과**: [x] Pass  [ ] Fail  **코멘트**: PASSED

---

### TC-013 [엣지] 🤖 AI검증 — history.py 매핑에 없는 기간 입력

**사전조건**: api_client.get_history가 데이터 반환
**실행 단계**:
1. `get_history("NVDA", "10Y")` 호출 (PERIOD_MAP에 없는 기간)
**입력값**: 기간 = `"10Y"`
**예상 결과**: 기본값 `("1y", "1d")`로 폴백하여 정상 DataFrame 반환, 크래시 없음
**확인 방법**: `isinstance(result, pd.DataFrame)`

**결과**: [x] Pass  [ ] Fail  **코멘트**: PASSED

---

### TC-014 [엣지] 🤖 AI검증 — fundamentals.py force_fallback=True

**사전조건**: api_client.finviz.get_fundamentals 호출
**실행 단계**:
1. `get_fundamentals("NVDA", force_fallback=True)` 호출
**입력값**: 티커 = `"NVDA"`, force_fallback = `True`
**예상 결과**: api_client.get_fundamentals 대신 api_client.finviz.get_fundamentals가 호출되어 결과 반환
**확인 방법**: finviz 호출 여부 확인

**결과**: [x] Pass  [ ] Fail  **코멘트**: PASSED (FMP → Finviz 변경, 2026-04-13)

---

### TC-015 [엣지] 🤖 AI검증 — technicals.py force_fallback=True (Python 계산 폴백)

**사전조건**: api_client.get_history가 1년치 OHLCV 데이터 반환
**실행 단계**:
1. `get_technicals("NVDA", force_fallback=True)` 호출
**입력값**: 티커 = `"NVDA"`
**예상 결과**: `source`가 `"python_calc"`, `rsi`/`macd`/`bollinger` 등 신호 판정 결과 포함
**확인 방법**: `result["source"] == "python_calc"`, 각 지표 dict에 `signal` 키 존재

**결과**: [x] Pass  [ ] Fail  **코멘트**: PASSED

---

### TC-016 [엣지] 🤖 AI검증 — indicators.py 데이터 부족 시 None 반환

**사전조건**: 없음
**실행 단계**:
1. 5개 종가 pd.Series 생성 (RSI 14기간보다 적음)
2. `calc_rsi(short_series)` 호출
3. `calc_macd(short_series)` 호출
4. `calc_bbands(short_series)` 호출
**입력값**: 5개 종가 Series
**예상 결과**: 세 함수 모두 `None` 반환, 예외 발생 없음
**확인 방법**: `result is None`

**결과**: [x] Pass  [ ] Fail  **코멘트**: PASSED

---

### TC-017 [엣지] 🤖 AI검증 — chart_builder 빈 DataFrame 입력

**사전조건**: 없음
**실행 단계**:
1. 빈 DataFrame 생성 (`pd.DataFrame()`)
2. `build_price_chart(pd.DataFrame())` 호출
3. `build_price_chart(None)` 호출
**입력값**: 빈 DataFrame, None
**예상 결과**: 두 경우 모두 `None` 반환, 예외 발생 없음
**확인 방법**: `result is None`

**결과**: [x] Pass  [ ] Fail  **코멘트**: PASSED

---

### TC-018 [엣지] 🤖 AI검증 — tooltips 존재하지 않는 키 → 빈 문자열

**사전조건**: 없음
**실행 단계**:
1. `get_tooltip("nonexistent_key")` 호출
**입력값**: 키 = `"nonexistent_key"`
**예상 결과**: 빈 문자열 `""` 반환
**확인 방법**: `result == ""`

**결과**: [x] Pass  [ ] Fail  **코멘트**: PASSED

---

### TC-019 [실패] 🤖 AI검증 — quote.py API 전체 실패 시 None

**사전조건**: api_client.get_quote가 None 반환
**실행 단계**:
1. api_client.get_quote가 None 반환하도록 설정
2. `get_quote("NVDA")` 호출
**입력값**: 티커 = `"NVDA"`
**예상 결과**: `None` 반환, 예외 발생 없음
**확인 방법**: `result is None`

**결과**: [x] Pass  [ ] Fail  **코멘트**: PASSED

---

### TC-020 [실패] 🤖 AI검증 — history.py API 전체 실패 시 None

**사전조건**: api_client.get_history가 None 반환
**실행 단계**:
1. api_client.get_history가 None 반환하도록 설정
2. `get_history("NVDA", "1Y")` 호출
**입력값**: 티커 = `"NVDA"`
**예상 결과**: `None` 반환, 예외 발생 없음
**확인 방법**: `result is None`

**결과**: [x] Pass  [ ] Fail  **코멘트**: PASSED

---

### TC-021 [실패] 🤖 AI검증 — technicals.py API + 폴백 모두 실패 시 None

**사전조건**: api_client.get_technicals = None, api_client.get_history = None
**실행 단계**:
1. 두 함수 모두 None 반환하도록 설정
2. `get_technicals("NVDA")` 호출
**입력값**: 티커 = `"NVDA"`
**예상 결과**: API 실패 → Python 계산 시도 → 히스토리도 실패 → 최종 `None` 반환
**확인 방법**: `result is None`

**결과**: [x] Pass  [ ] Fail  **코멘트**: PASSED

---

### TC-022 [정상] 🤖 AI검증 — technicals.py RSI 신호 판정 경계값 (30/70)

**사전조건**: 없음 (내부 함수 직접 테스트)
**실행 단계**:
1. `_rsi_signal(75)` 호출
2. `_rsi_signal(25)` 호출
3. `_rsi_signal(50)` 호출
4. `_rsi_signal(70)` 호출 (경계값)
5. `_rsi_signal(30)` 호출 (경계값)
**입력값**: RSI 값 = 75, 25, 50, 70, 30
**예상 결과**: 75→"bearish", 25→"bullish", 50→"neutral", 70→"bearish", 30→"bullish"
**확인 방법**: 각 반환값 직접 비교

**결과**: [x] Pass  [ ] Fail  **코멘트**: PASSED

---

## 테스트 완료 체크리스트

- [x] 모든 정상 케이스 Pass (TC-001 ~ TC-011, TC-022)
- [x] 엣지 케이스에서 앱이 크래시 없이 처리됨 (TC-012 ~ TC-018)
- [x] 실패 케이스에서 None 반환 (TC-019 ~ TC-021)
- [x] pytest 31개 테스트 전부 PASSED (0.90초)

---

## 실제 API 테스트 (2026-04-13)

실제 API로 Quick Look 전체 파이프라인을 검증했다.

**테스트 파일**: `tests/test_phase2_real_api.py` — 19개 테스트 전체 PASSED

### 결과 요약

| 모듈 | 테스트 항목 | 결과 | 비고 |
|------|------------|------|------|
| quote.py | 시세 조회, 필수 필드, 잘못된 티커, 장전시세 | 4/4 PASSED | AAPL $260.48, source=finnhub |
| history.py | 1Y, MA포함, 1M, 1W, 5Y, 전체 기간 | 6/6 PASSED | 1Y=250rows, MA50=260.84, MA200=250.31 |
| fundamentals.py | 재무 조회, 필수 필드, Finviz 폴백 | 3/3 PASSED | PE=33.01, sector=Technology |
| technicals.py | API 경유, Python 폴백, API/Python 일관성 | 3/3 PASSED | RSI=55.6, MACD=bullish, diff=0.0 |
| chart_builder.py | 실제 데이터 라인/캔들스틱 차트 | 2/2 PASSED | 각 4 traces |
| 전체 파이프라인 | Quick Look 전체 흐름 | 1/1 PASSED | quote→fundamentals→technicals→chart 정상 |

### 수정 사항

- `fundamentals.py` force_fallback 대상을 FMP → Finviz로 변경 (FMP 무료 플랜 403 제한)
- 테스트에서 FMP skip 제거, Finviz 정상 호출로 변경 → 19개 전부 PASSED

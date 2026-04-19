# 개발 백로그

향후 개발 예정 기능 목록. 우선순위/상태를 표로 관리하고, 상세 스펙은 아래 섹션에 기술한다.

## 요약

| # | 기능 | 우선순위 | 상태 | 담당 Phase |
|---|------|---------|------|-----------|
| 1 | AI 재분석 버튼 | 중 | **완료** | — |
| 2 | AI 분석 품질 개선 (Analyst 프롬프트 + CV 완화) | 상 | **완료** | — |
| 3 | Agent별 의견 UI | 상 | **완료** | — |
| 4 | AI 분석 QuickLook 인라인 통합 | 상 | **완료** | — |
| 5 | Compare 페이지 크래시 수정 (프롬프트 C + 방어 렌더링 A) | 긴급 | **완료** | — |
| 6 | Sector Screening GICS→Finviz 매핑 누락 수정 | 중 | **완료** | — |
| 7 | Guide 차트 패턴 마커 표시 (수동 지정) | 중 | **완료** | — |
| 8 | Watchlist 해제 즉시 반영 (이벤트 기반 갱신) | 중 | **완료** | — |

---

## 1. AI 재분석 버튼

### 배경
현재 AI 분석 결과는 24시간 SQLite 캐시에 저장된다 (`data/analysis_cache.py:20`, `CACHE_TTL_HOURS = 24`). 사용자가 동일 티커를 24시간 내 재분석하면 항상 캐시된 결과가 반환되어, 시장 상황 변화에도 새 분석을 받을 방법이 없다.

### UI 스펙
- **위치**: `QuickLook` 페이지 AI 분석 카드 우상단
- **형태**: "재분석" 텍스트 버튼 + refresh 아이콘
- **동작**:
  1. 클릭 시 확인 다이얼로그 표시 — "AI 호출 5회가 발생합니다 (일일 한도 차감). 진행할까요?"
  2. 승인 시 `POST /api/analysis/{ticker}?force=true` 호출
  3. 취소 시 아무 동작 없음
- **로딩 UX**: 기존 분석 스켈레톤 재사용 (1~2분 소요)
- **부가 정보**: 카드 하단에 "마지막 분석: 3시간 전" 상대 시각 표시

### 백엔드 변경
- `POST /api/analysis/{ticker}` 엔드포인트에 `force: bool = False` 쿼리 파라미터 추가
- `force=True`인 경우 `get_cached_analysis()` 호출 생략, 바로 새 분석 실행
- 새 결과는 그대로 캐시에 overwrite (`save_analysis()`)

### 구현 범위
- [ ] `backend/routers/analysis.py` — `force` 파라미터 추가 및 캐시 우회 로직
- [ ] `frontend/src/pages/QuickLook.tsx` — 재분석 버튼 + 확인 다이얼로그 추가
- [ ] `frontend/src/hooks/useAnalysis.ts` — `trigger(force?: boolean)` 옵션 추가
- [ ] 마지막 분석 시각 UI (백엔드 응답에 `created_at` 노출)
- [ ] 일일 한도(100회) 경고 표시 — 한도 초과 시 버튼 비활성화

### 예상 공수
프론트 2h + 백엔드 30m + 테스트 30m ≈ **3시간**

### 참고
- 현재 캐시 로직: `data/analysis_cache.py:23` (`get_cached_analysis`)
- 일일 한도 관리: `utils/usage_tracker.py`
- 기존 분석 라우터: `backend/routers/analysis.py:14`

---

## 2. AI 분석 품질 개선 (Analyst 프롬프트 + Cross Validation 완화)

### 배경
현재 모든 종목이 HOLD / medium으로 수렴하는 문제 발생. 원인은 두 가지:
1. **Analyst 프롬프트가 과도하게 보수적**: "투자 자문 아님", "매수 추천 대신 다른 표현 사용", "데이터 불완전할 수 있음" 등의 지시가 Claude를 HOLD로 유도
2. **Cross Validation이 자연스러운 관점 차이를 "충돌"로 간주**: 뉴스/재무/거시경제는 본질적으로 관점이 다른데 항상 `downgrade_one` 이상을 출력

### 변경 내역

#### A. Analyst 프롬프트 수정 (`agents/analyst_agent.py:16~37`)

**Before (보수적)**:
```
- 투자 자문이 아닌 데이터 기반 분석임을 명시해.
- "매수 추천" 대신 "데이터 기반 분석: 긍정 신호 우세" 같은 표현을 사용해.
- 분석 결과가 부분적일 수 있으니 가용 데이터 범위 내에서 판단해.
```

**After (판단 기준 명시)**:
```
- 긍정 신호가 우세하면 BUY, 부정 신호가 우세하면 SELL을 명확히 줘.
- HOLD는 긍정/부정이 정말 비슷하게 혼재할 때만 사용해.
- confidence 기준:
  - high: 3개 Agent 의견 방향 일치 + 기술/재무 뒷받침
  - medium: 2개 일치 또는 일부 혼재
  - low: 전반적으로 신호 혼재 또는 데이터 부족
- disclaimer는 항상 포함하되, 판단 자체는 명확하게.
```

#### B. Cross Validation 프롬프트 완화 (`agents/cross_validation.py:16~34`)

**Before**:
```
- 각 분석가의 의견이 서로 다른 부분을 명확히 지적해.
```

**After**:
```
- "관점 차이"와 "진짜 모순"을 구분해:
  - 관점 차이: 뉴스는 긍정인데 기술 지표가 중립 → 정상, 충돌 아님
  - 진짜 모순: 한 쪽은 "과매수"라 하고 다른 쪽은 "저평가"라 하는 경우 → 충돌
- confidence_adjustment 기준:
  - none: 충돌이 없거나 low severity만 존재
  - downgrade_one: high severity 충돌 1건 이상
  - downgrade_two: high severity 충돌 2건 이상이고 투자 방향 자체가 모순
```

### 구현 범위
- [ ] `agents/analyst_agent.py` — SYSTEM_PROMPT 교체
- [ ] `agents/cross_validation.py` — SYSTEM_PROMPT 교체
- [ ] 기존 분석 캐시 전체 삭제 (수정 전 결과 무효화)
- [ ] 테스트: 5개 이상 종목 분석 → BUY/HOLD/SELL 분포 확인

### 예상 공수
프롬프트 수정 30m + 캐시 초기화 5m + 테스트(5종목 × 1분) 10m ≈ **45분**

### 참고
- Analyst 프롬프트: `agents/analyst_agent.py:16`
- CV 프롬프트: `agents/cross_validation.py:16`
- 현재 신뢰도 조정 코드: `agents/analyst_agent.py:101` (`_adjust_confidence`) — `success_count` 기반만 적용 중, `cv.confidence_adjustment`는 미적용

---

## 3. Agent별 의견 UI

### 배경
현재 AI 분석 화면은 Analyst의 최종 verdict/confidence만 표시. 사용자가 "왜 이 판단인지" 알 수 없음. 실제 응답에는 News/Data/Macro 각 Agent의 분석 결과가 이미 포함돼 있으나 프론트엔드에서 렌더링하지 않음.

### UI 스펙

#### 레이아웃 (상세 항상 펼침)

```
┌───────────────────────────────────────────┐
│  최종: BUY / confidence: high              │  ← 기존 Analyst 카드
│  summary: "종합 분석 요약..."               │
├───────────────────────────────────────────┤
│  Agent 분석 상세                            │
│                                            │
│  📰 뉴스 분석        Bullish               │
│  "애널리스트 매수 추천 우세, 실적 서프라이즈"    │
│                                            │
│  📊 재무/기술 분석    Bullish               │
│  "PEG 0.77 저평가, MACD 강세 신호"          │
│                                            │
│  🌐 거시경제 분석     Neutral               │
│  "금리 안정적, 다만 규제 불확실성 존재"         │
│                                            │
│  ⚖️ 교차검증         충돌 1건               │
│  "뉴스와 기술분석 간 관점 차이 존재"           │
└───────────────────────────────────────────┘
```

#### 데이터 매핑 (추가 API 호출 불필요)

| UI 항목 | 응답 필드 | 표시 값 |
|---------|----------|--------|
| 뉴스 감성 | `agent_results.news.overall_sentiment` | Bullish / Bearish / Mixed |
| 뉴스 요약 | `agent_results.news.summary` | 텍스트 |
| 재무/기술 추세 | `agent_results.data.technicals_summary.trend` | Bullish / Bearish / Neutral |
| 재무/기술 요약 | `agent_results.data.summary` | 텍스트 |
| 거시경제 전망 | `agent_results.macro.market_sentiment` | Bullish / Bearish / Neutral |
| 거시경제 요약 | `agent_results.macro.summary` | 텍스트 |
| 교차검증 충돌 수 | `cross_validation.conflicts.length` | "충돌 N건" 또는 "충돌 없음" |
| 교차검증 소견 | `cross_validation.notes` | 텍스트 |

#### 감성 색상

| 값 | 색상 |
|----|------|
| Bullish / Positive | `theme.up` (초록) |
| Bearish / Negative | `theme.down` (빨강) |
| Neutral / Mixed | `theme.warning` (주황) |

### 구현 범위
- [ ] `frontend/src/pages/QuickLook.tsx` 또는 `AIAnalysis.tsx` — Agent 상세 섹션 추가
- [ ] `frontend/src/components/AgentDetail.tsx` — Agent 한 줄 표시 컴포넌트 (재사용)
- [ ] 감성 색상 매핑 유틸
- [ ] 교차검증 충돌 목록 표시 (severity별 색상)

### 예상 공수
컴포넌트 설계 1h + 구현 2h + 스타일링 1h + 테스트 30m ≈ **4.5시간**

### 참고
- 현재 분석 응답 구조: `backend/routers/analysis.py` → `agents/orchestrator.py:83~91`
- 기존 AI 분석 UI: `frontend/src/pages/AIAnalysis.tsx`, `frontend/src/components/AiRecommendation.tsx`
- 디자인 토큰: `frontend/src/styles/tokens.ts`

---

## 4. AI 분석 QuickLook 인라인 통합

### 배경
현재 AI 분석 흐름: QuickLook에서 "AI 분석" 버튼 클릭 → AIAnalysis 페이지로 이동 → 다시 버튼 클릭하여 분석 실행. 2번의 클릭 + 페이지 이동이 필요해 UX가 불편하다.

### 변경 내역
별도 AIAnalysis 페이지 대신, QuickLook 페이지 하단에 AI 분석 섹션을 인라인으로 통합한다.

### UI 스펙

#### 변경 전
```
[QuickLook 페이지]
  시세 / KPI / 차트
  [AI 분석 버튼] → 페이지 이동

[AIAnalysis 페이지]
  [분석 실행 버튼] → 1~2분 대기
  결과 표시
```

#### 변경 후
```
[QuickLook 페이지]
  시세 / KPI / 차트
  ─────────────────
  AI 분석 섹션
    [분석 실행] 버튼 → 클릭 1번으로 바로 실행
    로딩 중: 스켈레톤 (상단 시세/차트는 그대로 인터랙션 가능)
    결과: Analyst 카드 + Agent별 의견 (백로그 #3과 통합)
```

#### 핵심 UX 요구사항
- 분석 로딩(1~2분) 동안 **상단 시세/차트는 정상 동작** (스크롤, 기간 변경 등 가능)
- 분석 결과는 KPI/차트 **아래**에 자연스럽게 위치
- 캐시된 결과가 있으면 버튼 없이 즉시 표시, 재분석 버튼만 노출 (백로그 #1과 연동)
- 캐시 없을 때만 "AI 분석 실행" 버튼 표시

### 구현 범위
- [ ] `frontend/src/pages/QuickLook.tsx` — 하단에 AI 분석 섹션 추가
- [ ] `frontend/src/components/AiRecommendation.tsx` — QuickLook 내장용으로 리팩토링
- [ ] `frontend/src/hooks/useAnalysis.ts` — 자동 캐시 조회 + 수동 트리거 분리
- [ ] `frontend/src/pages/AIAnalysis.tsx` — 제거 또는 QuickLook으로 리다이렉트
- [ ] 라우터에서 `/analysis/:ticker` 경로 정리
- [ ] 백로그 #1(재분석 버튼), #3(Agent별 의견)과 동시 구현 시 통합 설계

### 의존 관계
- 백로그 #1 (재분석 버튼) — 캐시 있을 때 재분석 UX
- 백로그 #3 (Agent별 의견 UI) — 분석 결과 하단에 Agent 상세 표시

### 예상 공수
QuickLook 통합 2h + AiRecommendation 리팩토링 1h + AIAnalysis 페이지 정리 30m + 테스트 30m ≈ **4시간**
(#1, #3과 동시 구현 시 총 **8시간** — 개별 합산 대비 중복 제거로 단축)

### 참고
- 현재 QuickLook: `frontend/src/pages/QuickLook.tsx`
- 현재 AIAnalysis: `frontend/src/pages/AIAnalysis.tsx`
- 분석 훅: `frontend/src/hooks/useAnalysis.ts`
- 라우터: `frontend/src/App.tsx`

---

## 5. Compare 페이지 크래시 수정 (프롬프트 C + 방어 렌더링 A)

### 배경
`/compare` 페이지에서 AI Compare Analysis 실행 시 빈 화면(크래시) 발생. React 에러: `Objects are not valid as a React child (found: object with keys {sector, key_driver, sector_outlook})`. AI가 중첩 객체를 반환하는데 프론트엔드가 문자열로 직접 렌더링하려다 크래시.

### 원인
`agents/compare_agent.py`의 cross_sector 프롬프트가 AI에게 **중첩 객체**를 요청:
```json
"sector_context": { "AAPL": {"sector": "...", "key_driver": "...", "sector_outlook": "..."} }
"macro_scenarios": { "rate_hold": {"winner": "...", "reason": "..."} }
```
`CompareMode.tsx`는 이 값을 `<p>{context}</p>`로 직접 렌더링 → 객체는 React child로 불가 → 크래시.

### 해결: C + A 이중 방어

#### C — 프롬프트 수정 (근본 해결)

**파일**: `agents/compare_agent.py`

cross_sector 프롬프트 (`_build_cross_sector_prompt`)에서 중첩 객체를 문자열로 변경:

**Before**:
```json
"sector_context": {
    "AAPL": {"sector": "...", "key_driver": "...", "sector_outlook": "..."}
},
"valuation_vs_sector": {
    "AAPL": {"pe_vs_sector": "...", "assessment": "..."}
},
"sector_neutral_metrics": {
    "AAPL": {"fcf_yield": "...", "roe": "...", "de_ratio": "..."}
},
"macro_scenarios": {
    "rate_hold": {"winner": "...", "reason": "..."}
},
"recommendation_by_style": {
    "growth_investor": {"pick": "...", "reason": "..."}
}
```

**After**:
```json
"sector_context": {
    "AAPL": "섹터명. 핵심 동력 설명. 전망 한 줄."
},
"valuation_vs_sector": {
    "AAPL": "섹터 평균 PER 대비 평가 한 줄."
},
"sector_neutral_metrics": {
    "AAPL": "FCF Yield, ROE, D/E 요약 한 줄."
},
"macro_scenarios": {
    "rate_hold": "유리한 종목과 이유를 한 문장으로."
},
"recommendation_by_style": {
    "growth_investor": "추천 종목과 이유를 한 문장으로."
}
```

same_sector 프롬프트 (`_build_same_sector_prompt`)도 `recommendation_by_style` 동일 변경.

#### A — 방어적 렌더링 (안전망)

**파일**: `frontend/src/pages/CompareMode.tsx`

AI가 간혹 객체를 반환해도 크래시하지 않도록 헬퍼 함수 추가:

```tsx
function safeRender(val: any): string {
  if (val == null) return '--';
  if (typeof val === 'string') return val;
  if (typeof val === 'number') return String(val);
  if (typeof val === 'object' && !Array.isArray(val)) {
    return Object.entries(val).map(([k, v]) => `${k}: ${v}`).join('. ');
  }
  return JSON.stringify(val);
}
```

적용 위치:
- `sector_context` 렌더링 (line 293~302): `<p>{context}</p>` → `<p>{safeRender(context)}</p>`
- `macro_scenarios` 렌더링 (line 330~336): `<span>{impact}</span>` → `<span>{safeRender(impact)}</span>`
- `recommendation_by_style` 등 객체가 올 수 있는 모든 렌더링 위치

### 구현 범위
- [ ] `agents/compare_agent.py` — cross_sector 프롬프트 중첩 객체 → 문자열 변경
- [ ] `agents/compare_agent.py` — same_sector 프롬프트 recommendation_by_style 문자열 변경
- [ ] `frontend/src/pages/CompareMode.tsx` — `safeRender` 헬퍼 추가 + 렌더링 3곳 적용

### 예상 공수
프롬프트 수정 15m + safeRender 적용 15m ≈ **30분**

### 참고
- Compare Agent: `agents/compare_agent.py:129` (cross_sector), `agents/compare_agent.py:88` (same_sector)
- 크래시 위치: `frontend/src/pages/CompareMode.tsx:293` (sector_context), `:330` (macro_scenarios)
- Vite 에러 로그: `Objects are not valid as a React child (found: object with keys {sector, key_driver, sector_outlook})`

---

## 6. Sector Screening GICS→Finviz 매핑 누락 수정

### 배경
Sector Screening에서 "Information Technology", "Health Care", "Consumer Discretionary" 등 GICS 표준 섹터명을 사용하면 Finviz가 `Invalid filter option` 에러를 반환하며 스크리닝이 실패했다.

### 원인
`data/sector_data.py`의 `GICS_SECTORS` 리스트는 GICS 표준명을 사용하지만, Finviz는 자체 섹터명을 사용한다. `data/finviz_client.py`의 `SECTOR_MAP`에 GICS→Finviz 변환이 5개 누락되어 있었다.

### 수정 내역 (완료)

**파일**: `data/finviz_client.py` — `SECTOR_MAP`에 누락 매핑 5개 추가

| GICS 이름 | Finviz 이름 | 상태 |
|-----------|------------|------|
| Information Technology | Technology | 추가 완료 |
| Health Care | Healthcare | 추가 완료 |
| Consumer Discretionary | Consumer Cyclical | 추가 완료 |
| Consumer Staples | Consumer Defensive | 추가 완료 |
| Materials | Basic Materials | 추가 완료 |

### 테스트 결과
- `Information Technology` → `Technology` → Finviz 154개 종목 반환 확인

---

## 7. Guide 차트 패턴 마커 표시 (수동 지정)

### 배경
Beginner's Guide의 Chart Basics 섹션에서 라이브 차트를 보여주지만, 어느 지점이 반전 신호이고 어느 지점이 지속 신호인지 차트 위에 표시가 없어서 초보자가 패턴을 찾기 어렵다.

### 현재 구조
- 차트 라이브러리: **Lightweight Charts** (`frontend/src/components/Chart.tsx`)
- 가이드 데이터: `config/guide/chart_basics.json` — 각 토픽에 `chart_example` 필드 (ticker, period, description)
- 현재 description은 "찾아보세요" 식의 안내만 존재

### 해결: Lightweight Charts `setMarkers()` 활용

Lightweight Charts는 캔들 시리즈에 마커를 추가하는 기능을 기본 제공한다:

```typescript
candleSeries.setMarkers([
  { time: '2026-03-15', position: 'belowBar', color: 'green', shape: 'arrowUp', text: '망치형' },
  { time: '2026-04-01', position: 'aboveBar', color: 'red', shape: 'arrowDown', text: '저항 돌파' },
]);
```

### 구현 방식

1. `config/guide/chart_basics.json`의 `chart_example`에 `markers` 배열 추가:
```json
"chart_example": {
  "ticker": "AMD",
  "period": "3M",
  "description": "...",
  "markers": [
    { "date": "2026-03-15", "position": "belowBar", "shape": "arrowUp", "color": "green", "text": "망치형" },
    { "date": "2026-03-20", "position": "aboveBar", "shape": "arrowDown", "color": "red", "text": "저항선" }
  ]
}
```

2. `Chart` 컴포넌트에 `markers` prop 추가 → 데이터 로드 후 `candleSeries.setMarkers()` 호출

3. Guide 페이지에서 `chart_example.markers`를 `Chart`에 전달

### 구현 범위
- [ ] `config/guide/chart_basics.json` — 각 토픽의 chart_example에 markers 배열 추가 (반전 신호, 지속 신호, 삼각형, 헤드앤숄더 등)
- [ ] `frontend/src/components/Chart.tsx` — `markers` prop 수용 + `setMarkers()` 호출
- [ ] `frontend/src/pages/Guide.tsx` — `Chart`에 markers 전달

### 유지보수 참고
- 수동 지정이므로 시간이 지나면 마커 날짜가 차트 범위 밖으로 밀릴 수 있음
- 주기적으로 markers 날짜를 갱신하거나, period를 충분히 길게 설정하여 완화

### 예상 공수
Chart 컴포넌트 수정 30m + JSON 마커 데이터 작성 1h + 테스트 30m ≈ **2시간**

### 향후 확장 — 자동 패턴 감지
수동 마커가 안정화되면, 백엔드에서 TA-Lib 등의 라이브러리로 캔들 패턴(망치형, 장악형, 도지 등)을 자동 탐지하고 마커 위치를 동적으로 생성하는 방식으로 전환 검토. 자동 감지로 전환하면 차트 데이터가 바뀌어도 항상 올바른 위치에 마커가 표시되므로 유지보수가 불필요해진다.

### 참고
- Chart 컴포넌트: `frontend/src/components/Chart.tsx`
- 가이드 데이터: `config/guide/chart_basics.json`
- Guide 페이지: `frontend/src/pages/Guide.tsx`
- Lightweight Charts markers API: `ISeriesApi.setMarkers()`

---

## 8. Watchlist 해제 즉시 반영 (이벤트 기반 갱신)

### 배경
Watchlist에서 종목을 해제(★ 버튼 클릭)하면 백엔드에서는 삭제되지만, 사이드바 목록이 즉시 갱신되지 않아 "해제가 안 된다"는 느낌을 줌.

### 원인
`WatchlistButton`(★ 버튼)과 `Sidebar`(목록)가 상태를 공유하지 않음.
- `WatchlistButton`: 자체 `inWatchlist` state만 관리, `DELETE` 성공해도 외부에 알리지 않음
- `Sidebar`: `usePolling('/watchlist', 60_000)` — 60초마다 갱신, 중간 변경은 반영 안 됨

### 수정 내역 (완료)

**방식**: `window` 커스텀 이벤트 기반 즉시 갱신

1. **`frontend/src/hooks/useApi.ts`** — `usePolling`에 `listenEvent` 파라미터 추가. 해당 이벤트 발생 시 즉시 `refetch()` 호출
2. **`frontend/src/components/WatchlistButton.tsx`** — 추가/삭제 성공 후 `window.dispatchEvent(new Event('watchlist-changed'))` 발생
3. **`frontend/src/components/Sidebar.tsx`** — `usePolling('/watchlist', 60_000, 'watchlist-changed')` 로 이벤트 구독

### 참고
- `usePolling` hook: `frontend/src/hooks/useApi.ts:73`
- WatchlistButton: `frontend/src/components/WatchlistButton.tsx`
- Sidebar watchlist: `frontend/src/components/Sidebar.tsx:25`

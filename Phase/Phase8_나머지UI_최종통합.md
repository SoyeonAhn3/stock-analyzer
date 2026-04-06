# Phase 8 — 나머지 UI + 최종 통합 `🔲 미시작`

> Sector, Compare, Guide, Market Overview UI 완성 + 전체 시나리오 테스트

**상태**: 🔲 미시작
**선행 조건**: Phase 7 완료 (Quick Look + AI 결과 UI)

---

## 개요

남은 4개 화면(Sector Screening, Compare Mode, Beginner's Guide, Market Overview)의 UI를 완성하고, 전체 앱을 처음부터 끝까지 시나리오 테스트한다. 면책 조항 5군데 배치, 로딩 상태, 에러 배너 등 마감 작업을 포함한다.

---

## 완료 예정 / 완료 항목

| # | 모듈 | 상태 | 설명 |
|---|---|---|---|
| 1 | `screens/sector_screening.py` | 🔲 | Sector Screening UI |
| 2 | `screens/compare_mode.py` | 🔲 | Compare Mode UI |
| 3 | `screens/guide.py` | 🔲 | Beginner's Guide UI |
| 4 | `screens/market_overview.py` | 🔲 | Market Overview UI |
| 5 | `screens/components/loading.py` | 🔲 | 로딩 상태 컴포넌트 |
| 6 | `screens/components/error_banner.py` | 🔲 | API 실패 경고 배너 |

---

## Sector Screening UI (UI.txt 8장)

- GICS 버튼 그리드 (Primary 600) + Custom Themes (Primary 700)
- "+ New Theme" 버튼 + 생성 폼 (테마명, 티커 태그, 프리셋 라디오)
- 분석 진행 표시 (스피너 + Stage 1/2)
- 필터 완화 경고 (amber 배너)
- Top 5 결과 (순위 원형 + 체크박스 + 점수 + 추천 이유)
- "Compare selected" 버튼 (체크 2개+ 시 표시)

---

## Compare Mode UI (UI.txt 7장)

- 비교 바 (기준/비교 종목 태그 + 추가 input + × 삭제)
- 비교 유형 배지:
  - same_sector: 파란 배지 (즉시 표시)
  - cross_sector: 노란 배지
  - 판정 불가: 회색 배지
- 비교 테이블
- 수익률 비교 차트 (정규화 100 기준)
- AI 비교 분석 버튼
- same_sector 결과: 카테고리별 3열 카드, 순위 뱃지, Key Risks, 투자 성향 추천
- cross_sector 결과: Sector Context, Relative Valuation, Macro Scenarios, Diversification

---

## Beginner's Guide UI (UI.txt 9장)

- 카테고리별 펼치기/접기
- 난이도 뱃지 (green/amber/blue)
- 펼친 내용: 좌측 3px Primary 보더

---

## Market Overview UI (UI.txt 4장)

- 시장 지수 카드 4열 그리드
- 2열 그리드: Today's movers + Market news
- 종목 클릭 → Quick Look 이동

---

## 데이터 로딩 상태 (UI.txt 12장)

| 화면 | 로딩 표시 |
|------|----------|
| Quick Look | "—" placeholder, "Loading..." |
| AI 분석 | Agent 5단계 인디케이터 |
| Sector | 스피너 + Stage 1/2 |
| API 실패 | amber 배너 (부분 실패 허용) |

---

## 면책 조항 최종 배치 (UI.txt 13장)

| 위치 | 버전 |
|------|------|
| 사이드바 최하단 | 축약: "AI-generated reference. Not financial advice." |
| AI 분석 결과 하단 | 전체 문구 |
| AI 비교 분석 하단 | 전체 문구 |
| Sector 결과 하단 | 축약 |
| 판정 뱃지 아래 | confidence 표시 |

---

## 최종 통합 시나리오 테스트

전체 앱을 처음부터 끝까지 수동 테스트.

### 메인 시나리오
```
□ 앱 열기 → Market Overview 표시 (지수 4개 + 급등락 + 뉴스)
□ NVDA 검색 → Quick Look (시세 + 차트 + 재무 + 기술지표)
□ AI 분석 실행 → Agent 5단계 진행 → BUY/HOLD/SELL 결과
□ + Compare → AMD 추가 → 비교 테이블 + same_sector 배지
□ AI 비교 분석 → 카테고리별 순위 + 투자 성향 추천
□ Sector Screening → IT 선택 → Top 5 결과
□ Top 5 체크박스 2개 → "Compare selected" → Compare Mode
□ Beginner's Guide → 카테고리 펼치기/접기
□ Watchlist → 종목 추가 → 등락률 표시 → 클릭 → Quick Look
```

### 에러 시나리오
```
□ 잘못된 티커 입력 → 에러 아닌 "종목을 찾을 수 없습니다" 표시
□ API 1개 실패 → 해당 섹션 "N/A" + 나머지 정상 표시
□ AI Agent 1개 실패 → amber 경고 + 나머지로 분석 진행
□ AI 리밋 100회 → 사이드바 red + AI 버튼 전부 비활성
□ Sector 니치 테마 → 적응형 완화 경고 표시
□ cross_sector 비교 → 노란 배지 + 섹터별 상대 비교
```

### 일관성 확인
```
□ 면책 조항 5군데 전부 배치
□ 모든 화면에서 사이드바 일관성
□ 캐시 동작: 같은 티커 재검색 시 즉시 표시
□ "Data delayed ~15 min" 사이드바에 항상 표시
```

---

## 선행 조건 및 의존성

- Phase 6~7 완료
- Phase 1~5의 모든 데이터 함수
- UI.txt 전체 참조

---

## 개발 시 주의사항

- 이 Phase가 끝나면 MVP 완성
- 시나리오 테스트에서 발견된 버그는 해당 Phase의 ���드를 수정 (Phase 역행 가능)
- 성능 이슈(로딩 느림)는 캐시 TTL 조정으로 해결
- pre-requirement/Phase.txt는 더 이상 사용하지 않음. Phase/ 디렉토리가 정본

---

## 변경 이력

| 날짜 | 내용 |
|---|---|
| 2026-04-06 | 최초 작성 |

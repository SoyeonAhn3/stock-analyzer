# Phase 7 — Quick Look + AI 결과 UI `🔲 미시작`

> Quick Look 화면과 AI 분석 결과 화면을 UI.txt 디자인대로 완성

**상태**: 🔲 미시작
**선행 조건**: Phase 6 완료 (디자인 시스템 + 사이드바 + 화면 전환)

---

## 개요

가장 자주 사용되는 두 화면(Quick Look, AI 분석 결과)을 UI.txt 디자인대로 구현한다. 시세 헤더, 인터랙티브 차트, Fundamentals/Technicals 탭, 인라인 툴팁, AI Agent 진행 상태, BUY/HOLD/SELL 판정 카드 등 핵심 UI 컴포넌트를 완성한다.

---

## 완료 예정 / 완료 항목

| # | 모듈 | 상태 | 설명 |
|---|---|---|---|
| 1 | `screens/quick_look.py` | 🔲 | Quick Look 전체 화면 |
| 2 | `screens/ai_analysis.py` | 🔲 | AI 분석 결과 화면 |
| 3 | `screens/components/tooltip.py` | 🔲 | 커스텀 인라인 툴팁 |
| 4 | `screens/components/signal_badge.py` | 🔲 | 신호 뱃지 (bullish/neutral/bearish) |
| 5 | `screens/components/agent_status.py` | 🔲 | Agent 5단계 진행 표시 |

---

## Quick Look UI (screens/quick_look.py)

### 구현 내용 (UI.txt 5장)

**시세 헤더 (5-1)**
- 티커(26px) + 회사명 + 섹터 태그 + "+ Compare" 버튼
- 가격(30px) + 등락률(green/red) + 등락액
- Vol, Day Range, Pre-market
- 미니 스파크라인 (150x48px)

**차트 카드 (5-2)**
- 기간 선택 버튼 (1W~5Y, 활성/비활성)
- Plotly 차트 커스텀 (그리드, 가격 라인, 영역 그라데이션, MA 라인)

**Fundamentals / Technicals 탭 (5-3)**
- 탭 버튼 (활성/비활성)
- Fundamentals: 3열 그리드, 라벨 + 값 + 툴팁
- Technicals: 리스트, 지표명 + 값 + 신호 뱃지

**인라인 툴팁 (5-4)**
- ⓘ 아이콘 호버 → 다크 배경 팝업 (250px)

**AI 분석 실행 버튼 (5-5)**
- 그라데이션 배경, 전체 너비
- 리밋 도달 시 회색 비활성

---

## AI 분석 결과 UI (screens/ai_analysis.py)

### 구현 내용 (UI.txt 6장)

**Agent 진행 상태 (6-1)**
- 5줄 리스트, 원형 인디케이터 (미실행/진행/완료/실패)

**Agent 실패 경고 (6-7)**
- amber 배너, ⚠ 아이콘, 영향 설명

**판정 결과 헤더 (6-2)**
- BUY/HOLD/SELL 뱃지 (green/amber/red, 28px) + 점수 + confidence

**Bull / Bear Case (6-3)**
- 2열 그리드, green/red 카드

**Catalyst (6-4)** — amber 카드
**Action Summary (6-5)** — Primary 50 카드
**면책 조항 (6-6)** — 상단 보더 + 10px 가운데 정렬

---

## 선행 조건 및 의존성

- Phase 6: 디자인 시스템 CSS + 사이드바 + 화면 전환
- Phase 2: Quick Look 데이터 함수
- Phase 3: AI 분석 결과 (analysis_state)
- UI.txt 5장, 6장 참조

---

## 변경 이력

| 날짜 | 내용 |
|---|---|
| 2026-04-06 | 최초 작성 |

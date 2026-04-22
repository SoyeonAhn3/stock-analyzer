# Phase 11 — UI/UX 개선 + 모바일 최적화 `🔲 미시작`

> 모바일 반응형 레이아웃, 모바일 네비게이션, 터치 UX, 스켈레톤 UI, 전반적 UI 다듬기

**상태**: 🔲 미시작
**선행 조건**: Phase 10 완료 (UX 개선 + 데이터 영속화)

---

## 개요

현재 앱은 데스크톱 중심으로 설계되어 모바일 접속 시 레이아웃이 깨지거나 사용성이 떨어진다. Phase 10에서 `useBreakpoint` 훅과 기본 반응형을 도입했으나, 개별 페이지/컴포넌트 레벨의 모바일 최적화는 미흡하다. 이 Phase에서는 모바일 퍼스트 관점으로 전체 UI를 재정비한다.

---

## 완료 예정 항목

| # | 항목 | 상태 | 설명 |
|---|---|---|---|
| 1 | 모바일 반응형 레이아웃 | 🔲 | 전 페이지 그리드/카드/테이블 breakpoint 재조정 |
| 2 | 모바일 네비게이션 개선 | 🔲 | 바텀 탭 바 또는 햄버거 드로어 UX 개선 |
| 3 | 터치 UX 최적화 | 🔲 | 버튼 최소 크기 44px, 간격 확보, 스와이프 제스처 |
| 4 | 스켈레톤 UI | 🔲 | 데이터 로딩 중 플레이스홀더 표시 (빈 화면 방지) |
| 5 | UI 일관성 다듬기 | 🔲 | 폰트 크기, 간격, 카드 스타일 통일 |

---

## 1. 모바일 반응형 레이아웃

### 현재 상태

- `useBreakpoint.ts`: mobile(≤640px), tablet(≤1024px), desktop 3단계 정의
- `App.tsx`: 사이드바 드로어 전환, 패딩 조정 구현됨
- `MarketOverview.tsx`: 모바일 시 1컬럼 그리드 적용됨
- `AiAnalysisInline.tsx`: 모바일 시 1컬럼 그리드 적용됨
- **미적용 페이지**: `QuickLook`, `CompareMode`, `SectorScreening`, `AIAnalysis`, `Guide`, `Settings`

### 개선 대상

| 페이지/컴포넌트 | 현재 문제 | 개선 방향 |
|---|---|---|
| `QuickLook.tsx` | KPI 카드 3열 고정 → 모바일에서 넘침 | 모바일 1열, 태블릿 2열 |
| `CompareMode.tsx` | 2종목 나란히 비교 → 모바일에서 읽기 어려움 | 모바일 시 탭 전환 또는 세로 스택 |
| `SectorScreening.tsx` | 테이블 너비 초과 | 가로 스크롤 + 고정 컬럼 또는 카드 뷰 전환 |
| `Chart.tsx` | 차트 고정 높이 → 모바일에서 비율 안 맞음 | 뷰포트 비례 높이 (aspect-ratio) |
| `PriceHeader.tsx` | 큰 폰트 → 모바일에서 잘림 | 모바일 폰트 축소 |
| `Sidebar.tsx` | 드로어로 전환되나 닫기 UX 부족 | 스와이프 닫기 + 오버레이 터치 닫기 |

---

## 2. 모바일 네비게이션 개선

### 현재 상태

- 모바일/태블릿: 상단 고정 헤더(48px) + 햄버거 버튼으로 사이드바 드로어 토글
- 오버레이 클릭 시 닫기 구현됨
- 바텀 탭 바 없음

### 개선 방향

**옵션 A — 바텀 탭 바 (권장)**

```
┌─────────────────────────────┐
│        페이지 콘텐츠          │
│                             │
├─────────────────────────────┤
│ 🏠 홈  📊 분석  🔍 검색  ⚙ 설정  │  ← 바텀 탭 (모바일만)
├─────────────────────────────┤
│ TickerBar                   │
└─────────────────────────────┘
```

- 핵심 4개 메뉴를 바텀 탭으로 노출
- 나머지 메뉴(Compare, Sector, Guide)는 햄버거 드로어 유지
- iOS/Android 앱과 동일한 사용 패턴

**옵션 B — 햄버거 드로어 개선**

- 현재 구조 유지하되 스와이프 제스처, 애니메이션 보강

---

## 3. 터치 UX 최적화

### 적용 기준

| 항목 | 기준 | 근거 |
|---|---|---|
| 터치 타겟 최소 크기 | 44×44px | Apple HIG / Material Design |
| 버튼 간 최소 간격 | 8px | 오터치 방지 |
| 입력 필드 높이 | 최소 44px | 모바일 키보드 대응 |
| 폰트 최소 크기 | 14px | 모바일 가독성 |

### 주요 대상

- 사이드바 메뉴 항목 (현재 패딩 작음)
- Watchlist 추가/삭제 버튼
- Alert 설정 모달 내 입력 필드
- 검색 자동완성 드롭다운 항목
- TickerBar 내 지수 항목

---

## 4. 스켈레톤 UI

### 현재 상태

- `LoadingSkeleton.tsx` 컴포넌트 존재 (Phase 10에서 생성)
- 실제 적용 범위 확인 필요

### 적용 대상

| 위치 | 스켈레톤 형태 |
|---|---|
| MarketOverview — Movers 카드 | 카드 2개 플레이스홀더 (제목 바 + 리스트 4줄) |
| MarketOverview — News 카드 | 카드 1개 플레이스홀더 (뉴스 항목 5줄) |
| QuickLook — KPI 카드 | 카드 3개 플레이스홀더 (숫자 + 라벨) |
| QuickLook — 차트 | 차트 영역 크기의 회색 박스 + 펄스 애니메이션 |
| SectorScreening — 테이블 | 테이블 헤더 + 행 5줄 플레이스홀더 |
| TickerBar — 지수 | 인라인 바 형태 플레이스홀더 |

### 구현 방식

```
기존 LoadingSkeleton.tsx 확장
├── SkeletonCard       — 카드 형태
├── SkeletonTable      — 테이블 형태
├── SkeletonChart      — 차트 영역
└── SkeletonText       — 텍스트 줄 (너비 랜덤)

애니메이션: CSS shimmer (linear-gradient + @keyframes)
```

---

## 5. UI 일관성 다듬기

### 점검 항목

| 항목 | 현재 상태 | 개선 |
|---|---|---|
| 카드 border-radius | 일부 8px, 일부 미적용 | `RADIUS.card` (8px) 통일 |
| 카드 패딩 | 페이지마다 다름 | `SPACING.md` (16px) 통일 |
| 섹션 제목 스타일 | 인라인 스타일 혼재 | 공통 `SectionTitle` 컴포넌트 또는 클래스 |
| 숫자 폰트 | 일부 `JetBrains Mono` 미적용 | `.numeric` 클래스 전면 적용 |
| 색상 하드코딩 | 일부 hex 직접 사용 | `theme.xxx` 토큰으로 교체 |
| 버튼 스타일 | 페이지마다 상이 | 공통 버튼 variant (primary, secondary, ghost) |

---

## 관련 파일

| 위치 | 파일 | 역할 |
|---|---|---|
| Frontend | `hooks/useBreakpoint.ts` | 반응형 breakpoint 감지 |
| Frontend | `theme/tokens.ts` | 디자인 토큰 (폰트, 간격, 크기) |
| Frontend | `styles/global.css` | 글로벌 CSS + 모바일 미디어쿼리 |
| Frontend | `App.tsx` | 전체 레이아웃 + 사이드바 드로어 |
| Frontend | `components/LoadingSkeleton.tsx` | 기존 스켈레톤 컴포넌트 |
| Frontend | `components/Sidebar.tsx` | 사이드바 네비게이션 |
| Frontend | `components/TickerBar.tsx` | 하단 시세 바 |

---

## 설계 결정 사항

| 결정 | 선택 | 이유 |
|---|---|---|
| CSS 방식 | 인라인 스타일 + tokens.ts 유지 | 기존 패턴과 일관성 유지, CSS-in-JS 라이브러리 추가 불필요 |
| breakpoint 기준 | mobile ≤640, tablet ≤1024 | Phase 10에서 정의한 기준 유지 |
| 스켈레톤 라이브러리 | 자체 구현 | 이미 LoadingSkeleton.tsx 존재, 외부 의존성 추가 불필요 |

---

## 변경 이력

| 날짜 | 내용 |
|---|---|
| 2026-04-22 | Phase 11 문서 신규 생성 |

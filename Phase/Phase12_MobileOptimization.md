# Phase 12 — UI/UX + Mobile Optimization `✅ Completed`

> Mobile responsive layout, mobile navigation, touch UX, skeleton UI, and overall UI polish

**Completed**: 2026-04-27
**Status**: ✅ Completed
**Prerequisites**: Phase 11 completed (Code Quality)

---

## Overview

The app was designed desktop-first, causing layout breakage and poor usability on mobile devices. Phase 10 introduced `useBreakpoint` and basic responsiveness, but individual page/component-level mobile optimization was incomplete. This Phase overhauls the entire UI from a mobile-first perspective.

---

## Deliverables

| # | Module | Status | Type |
|---|---|---|---|
| 1 | Mobile Responsive Layout | ✅ | project-specific |
| 2 | Mobile Navigation (Bottom Tab Bar) | ✅ | project-specific |
| 3 | Touch UX Optimization | ✅ | general |
| 4 | Skeleton UI Expansion | ✅ | general |
| 5 | UI Consistency Polish | ✅ | project-specific |

---

## 1. Mobile Responsive Layout

### Purpose
Adapt all pages to mobile (≤640px) and tablet (≤1024px) breakpoints.

### Prior State
- `useBreakpoint.ts`: 3-stage detection (mobile/tablet/desktop)
- `App.tsx`: Sidebar drawer toggle, padding adjustment
- `MarketOverview.tsx`, `AiAnalysisInline.tsx`: 1-column grid on mobile
- **Not yet adapted**: QuickLook, CompareMode, SectorScreening, AIAnalysis, Guide, Settings

### Changes

| Page / Component | Desktop | Mobile |
|---|---|---|
| `QuickLook.tsx` | KPI 3-column | 1-column mobile, 2-column tablet |
| `CompareMode.tsx` | Side-by-side comparison | Vertical stack or tab switching |
| `SectorScreening.tsx` | Full-width table | Horizontal scroll + fixed column or card view |
| `Chart.tsx` | Fixed height | Viewport-proportional height (aspect-ratio) |
| `PriceHeader.tsx` | Large font | Scaled-down font for mobile |
| `Sidebar.tsx` | Drawer toggle | Swipe-to-close + overlay tap close |

---

## 2. Mobile Navigation

### Bottom Tab Bar (mobile only)

```
+-----------------------------+
|        Page Content          |
|                              |
+-----------------------------+
| Home  Analysis  Search  Settings |  <-- Bottom tabs (mobile)
+-----------------------------+
| TickerBar                    |
+-----------------------------+
```

- 4 core tabs exposed in bottom bar
- Remaining menus (Compare, Sector, Guide) stay in hamburger drawer
- Follows iOS/Android native app navigation pattern

### Implementation Files
- `components/BottomTabBar.tsx` (new)
- `App.tsx` (conditional rendering based on breakpoint)

---

## 3. Touch UX Optimization

### Standards Applied

| Criteria | Value | Source |
|---|---|---|
| Min touch target | 44x44px | Apple HIG / Material Design |
| Min button spacing | 8px | Mistouch prevention |
| Min input height | 44px | Mobile keyboard ergonomics |
| Min font size | 14px | Mobile readability |

### Target Components
- Sidebar menu items (padding was too small)
- Watchlist add/remove buttons
- Alert modal input fields
- Search autocomplete dropdown items
- TickerBar index items

---

## 4. Skeleton UI Expansion

### Prior State
`LoadingSkeleton.tsx` existed (Phase 10) with basic implementation.

### Expanded Variants

```
LoadingSkeleton.tsx (extended)
+-- SkeletonCard       -- Card placeholder
+-- SkeletonTable      -- Table header + 5 row placeholders
+-- SkeletonChart      -- Chart area placeholder
+-- SkeletonText       -- Text lines (randomized width)

Animation: CSS shimmer (linear-gradient + @keyframes)
```

### Application Points

| Location | Skeleton Type |
|---|---|
| MarketOverview — Movers | Card x2 (title bar + 4 list lines) |
| MarketOverview — News | Card x1 (5 news lines) |
| QuickLook — KPI | Card x3 (number + label) |
| QuickLook — Chart | Gray box with pulse animation |
| SectorScreening — Table | Header + 5 row placeholders |
| TickerBar — Indices | Inline bar placeholder |

---

## 5. UI Consistency Polish

| Item | Before | After |
|---|---|---|
| Card border-radius | Mixed (8px / none) | `RADIUS.card` (8px) unified |
| Card padding | Varies by page | `SPACING.md` (16px) unified |
| Section title style | Inline styles mixed | Common pattern applied |
| Numeric font | Partial JetBrains Mono | `.numeric` class applied everywhere |
| Color hardcoding | Some raw hex values | `theme.xxx` tokens only |
| Button styles | Inconsistent per page | Common variants (primary, secondary, ghost) |

---

## Implementation Files

| Location | File | Role |
|---|---|---|
| Frontend | `hooks/useBreakpoint.ts` | Responsive breakpoint detection |
| Frontend | `theme/tokens.ts` | Design tokens (font, spacing, size) |
| Frontend | `styles/global.css` | Global CSS + mobile media queries |
| Frontend | `App.tsx` | Layout + sidebar drawer |
| Frontend | `components/LoadingSkeleton.tsx` | Skeleton component |
| Frontend | `components/Sidebar.tsx` | Sidebar navigation |
| Frontend | `components/TickerBar.tsx` | Bottom ticker bar |
| Frontend | `components/BottomTabBar.tsx` | Mobile bottom tab bar |

---

## Design Decisions

| Decision | Choice | Reason |
|---|---|---|
| CSS approach | Inline styles + tokens.ts | Consistency with existing patterns, no CSS-in-JS library needed |
| Breakpoint thresholds | mobile ≤640, tablet ≤1024 | Defined in Phase 10, maintained for consistency |
| Skeleton library | Custom implementation | LoadingSkeleton.tsx already exists, no external dependency needed |
| Bottom tab bar | 4 core tabs | Most-used screens prioritized, rest in drawer |

---

## Change Log

| Date | Description |
|---|---|
| 2026-04-22 | Initial creation (as Phase 11) |
| 2026-04-24 | Renumbered to Phase 12 (Phase 11 reassigned to Code Quality) |
| 2026-04-27 | Phase 12 complete — responsive layout, bottom tab bar, touch UX, skeleton expansion, UI consistency |

---
---

# Phase 12 — UI/UX 개선 + 모바일 최적화 `✅ 완료`

> 모바일 반응형 레이아웃, 모바일 네비게이션, 터치 UX, 스켈레톤 UI, 전반적 UI 다듬기

**완료일**: 2026-04-27
**상태**: ✅ 완료
**선행 조건**: Phase 11 완료 (코드 품질 개선)

---

## 개요

현재 앱은 데스크톱 중심으로 설계되어 모바일 접속 시 레이아웃이 깨지거나 사용성이 떨어진다. Phase 10에서 `useBreakpoint` 훅과 기본 반응형을 도입했으나, 개별 페이지/컴포넌트 레벨의 모바일 최적화는 미흡하다. 이 Phase에서는 모바일 퍼스트 관점으로 전체 UI를 재정비한다.

---

## 완료 항목

| # | 모듈 | 상태 | 스킬 타입 |
|---|---|---|---|
| 1 | 모바일 반응형 레이아웃 | ✅ | project-specific |
| 2 | 모바일 네비게이션 (바텀 탭 바) | ✅ | project-specific |
| 3 | 터치 UX 최적화 | ✅ | general |
| 4 | 스켈레톤 UI 확장 | ✅ | general |
| 5 | UI 일관성 다듬기 | ✅ | project-specific |

---

## 1. 모바일 반응형 레이아웃

### 목적
모든 페이지를 모바일(≤640px) 및 태블릿(≤1024px) breakpoint에 맞게 적응시킨다.

### 기존 상태
- `useBreakpoint.ts`: mobile/tablet/desktop 3단계 감지
- `App.tsx`: 사이드바 드로어 전환, 패딩 조정 구현됨
- `MarketOverview.tsx`, `AiAnalysisInline.tsx`: 모바일 시 1컬럼 그리드 적용됨
- **미적용 페이지**: QuickLook, CompareMode, SectorScreening, AIAnalysis, Guide, Settings

### 변경 사항

| 페이지 / 컴포넌트 | 데스크톱 | 모바일 |
|---|---|---|
| `QuickLook.tsx` | KPI 3열 | 모바일 1열, 태블릿 2열 |
| `CompareMode.tsx` | 나란히 비교 | 세로 스택 또는 탭 전환 |
| `SectorScreening.tsx` | 풀 너비 테이블 | 가로 스크롤 + 고정 컬럼 또는 카드 뷰 |
| `Chart.tsx` | 고정 높이 | 뷰포트 비례 높이 |
| `PriceHeader.tsx` | 큰 폰트 | 모바일 폰트 축소 |
| `Sidebar.tsx` | 드로어 토글 | 스와이프 닫기 + 오버레이 터치 닫기 |

---

## 2. 모바일 네비게이션

### 바텀 탭 바 (모바일 전용)

```
+-----------------------------+
|        페이지 콘텐츠          |
|                              |
+-----------------------------+
| 홈  분석  검색  설정           |  <-- 바텀 탭 (모바일)
+-----------------------------+
| TickerBar                    |
+-----------------------------+
```

- 핵심 4개 메뉴를 바텀 탭으로 노출
- 나머지 메뉴(Compare, Sector, Guide)는 햄버거 드로어 유지
- iOS/Android 앱과 동일한 사용 패턴

### 구현 파일
- `components/BottomTabBar.tsx` (신규)
- `App.tsx` (breakpoint 기반 조건부 렌더링)

---

## 3. 터치 UX 최적화

### 적용 기준

| 항목 | 기준 | 근거 |
|---|---|---|
| 터치 타겟 최소 크기 | 44x44px | Apple HIG / Material Design |
| 버튼 간 최소 간격 | 8px | 오터치 방지 |
| 입력 필드 높이 | 최소 44px | 모바일 키보드 대응 |
| 폰트 최소 크기 | 14px | 모바일 가독성 |

### 주요 대상
- 사이드바 메뉴 항목 (패딩 작았음)
- Watchlist 추가/삭제 버튼
- Alert 설정 모달 내 입력 필드
- 검색 자동완성 드롭다운 항목
- TickerBar 내 지수 항목

---

## 4. 스켈레톤 UI 확장

### 기존 상태
`LoadingSkeleton.tsx` 컴포넌트 존재 (Phase 10에서 생성), 기본 구현만 있었음.

### 확장 변형

```
LoadingSkeleton.tsx (확장)
+-- SkeletonCard       -- 카드 플레이스홀더
+-- SkeletonTable      -- 테이블 헤더 + 행 5줄 플레이스홀더
+-- SkeletonChart      -- 차트 영역 플레이스홀더
+-- SkeletonText       -- 텍스트 줄 (너비 랜덤)

애니메이션: CSS shimmer (linear-gradient + @keyframes)
```

### 적용 위치

| 위치 | 스켈레톤 형태 |
|---|---|
| MarketOverview — Movers | 카드 2개 (제목 바 + 리스트 4줄) |
| MarketOverview — News | 카드 1개 (뉴스 항목 5줄) |
| QuickLook — KPI | 카드 3개 (숫자 + 라벨) |
| QuickLook — 차트 | 회색 박스 + 펄스 애니메이션 |
| SectorScreening — 테이블 | 헤더 + 행 5줄 플레이스홀더 |
| TickerBar — 지수 | 인라인 바 플레이스홀더 |

---

## 5. UI 일관성 다듬기

| 항목 | 변경 전 | 변경 후 |
|---|---|---|
| 카드 border-radius | 혼재 (8px / 미적용) | `RADIUS.card` (8px) 통일 |
| 카드 패딩 | 페이지마다 다름 | `SPACING.md` (16px) 통일 |
| 섹션 제목 스타일 | 인라인 스타일 혼재 | 공통 패턴 적용 |
| 숫자 폰트 | JetBrains Mono 부분 적용 | `.numeric` 클래스 전면 적용 |
| 색상 하드코딩 | 일부 hex 직접 사용 | `theme.xxx` 토큰으로 교체 |
| 버튼 스타일 | 페이지마다 상이 | 공통 variant (primary, secondary, ghost) |

---

## 관련 파일

| 위치 | 파일 | 역할 |
|---|---|---|
| Frontend | `hooks/useBreakpoint.ts` | 반응형 breakpoint 감지 |
| Frontend | `theme/tokens.ts` | 디자인 토큰 (폰트, 간격, 크기) |
| Frontend | `styles/global.css` | 글로벌 CSS + 모바일 미디어쿼리 |
| Frontend | `App.tsx` | 전체 레이아웃 + 사이드바 드로어 |
| Frontend | `components/LoadingSkeleton.tsx` | 스켈레톤 컴포넌트 |
| Frontend | `components/Sidebar.tsx` | 사이드바 네비게이션 |
| Frontend | `components/TickerBar.tsx` | 하단 시세 바 |
| Frontend | `components/BottomTabBar.tsx` | 모바일 바텀 탭 바 |

---

## 설계 결정 사항

| 결정 | 선택 | 이유 |
|---|---|---|
| CSS 방식 | 인라인 스타일 + tokens.ts 유지 | 기존 패턴과 일관성 유지, CSS-in-JS 라이브러리 추가 불필요 |
| Breakpoint 기준 | mobile ≤640, tablet ≤1024 | Phase 10에서 정의한 기준 유지 |
| 스켈레톤 라이브러리 | 자체 구현 | LoadingSkeleton.tsx 존재, 외부 의존성 추가 불필요 |
| 바텀 탭 바 | 핵심 4개 탭 | 가장 많이 사용하는 화면 우선, 나머지는 드로어 |

---

## 변경 이력

| 날짜 | 내용 |
|---|---|
| 2026-04-22 | Phase 11로 최초 작성 |
| 2026-04-24 | Phase 12로 번호 변경 (Phase 11에 코드 품질 개선 삽입) |
| 2026-04-27 | Phase 12 전체 완료 — 반응형 레이아웃, 바텀 탭 바, 터치 UX, 스켈레톤 확장, UI 일관성 |

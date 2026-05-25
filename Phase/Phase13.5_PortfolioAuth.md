# Phase 13.5 — Portfolio Authentication System `✅ Completed`

> Code+PIN based multi-user authentication for portfolio access control and server-side data storage.

**Status**: ✅ Completed
**Prerequisites**: Phase 13 (Portfolio) completed

---

## Overview

Phase 13 Portfolio stores data in browser localStorage with no access control — anyone who opens the app can view and modify holdings. The existing Sync feature (Phase 13 Step 8) is a manual backup tool hidden in Settings, unrelated to portfolio access protection.

This phase adds a **code + 4-digit PIN authentication gate** to the Portfolio page. Each user receives a unique 12-character code, and all portfolio data is stored server-side (Render SQLite) keyed by that code. No signup or login required — just code + PIN.

---

## Deliverables

| # | Module / Component | Status | Type |
|---|---|---|---|
| 1 | `PortfolioLoginGate.tsx` — Login/Register popup | ✅ | frontend |
| 2 | Session management (sessionStorage + localStorage) | ✅ | frontend |
| 3 | `usePortfolio` server integration | ✅ | frontend |
| 4 | Settings page MY ACCOUNT section | ✅ | frontend |
| 5 | Portfolio header code display + logout button | ✅ | frontend |

---

## User Flow

### New User

```
Portfolio click
  → Login popup displayed
  → "Don't have a code?" → [Get a Code] click
  → Set 4-digit PIN (enter + confirm)
  → Unique code issued (e.g., ABCD-1234-EFGH)
  → "Save this code!" notice + copy button
  → Auto-login → empty portfolio displayed
```

### Existing User

```
Portfolio click
  → Login popup displayed
  → Enter code + PIN
  → ☑ Remember on this browser (optional)
  → Auth success → load portfolio from server
  → Auth failure → "Invalid code or PIN" error popup
```

### Remembered User (Return Visit)

```
Portfolio click
  → Saved code auto-filled from localStorage
  → Enter PIN only
  → Login
```

### Logout

```
Portfolio header [Logout] button click
  → Session cleared
  → Return to login popup
```

---

## Step 1: Login Popup (PortfolioLoginGate)

### Component Structure

```
Portfolio page entry
  ├─ No session → <PortfolioLoginGate>
  │   ├─ Default: code input + PIN input + [Login] button
  │   │   └─ ☑ Remember on this browser
  │   ├─ "Don't have a code?" → [Get a Code]
  │   │   └─ PIN setup → code generation → notice popup
  │   └─ Error state: "Invalid code or PIN"
  └─ Session exists → <Portfolio> (existing component)
```

### Login Screen UI

```
┌──────────────────────────────────┐
│         My Portfolio             │
│                                  │
│  ┌────────────────────────────┐  │
│  │  ABCD-1234-EFGH            │  │  ← Code input (12 chars, auto-hyphen)
│  └────────────────────────────┘  │
│  ┌────────────────────────────┐  │
│  │  ●●●●                     │  │  ← PIN input (4 digits, masked)
│  └────────────────────────────┘  │
│                                  │
│  ☑ Remember on this browser      │
│                                  │
│  ┌────────────────────────────┐  │
│  │          Login              │  │
│  └────────────────────────────┘  │
│                                  │
│  Don't have a code? [Get a Code] │
└──────────────────────────────────┘
```

### Code Registration Screen UI

```
┌──────────────────────────────────┐
│      Create New Portfolio        │
│                                  │
│  Set a 4-digit PIN.              │
│  This PIN cannot be changed,     │
│  please remember it.             │
│                                  │
│  ┌────────────────────────────┐  │
│  │  ●●●●                     │  │  ← Set PIN
│  └────────────────────────────┘  │
│  ┌────────────────────────────┐  │
│  │  ●●●●                     │  │  ← Confirm PIN
│  └────────────────────────────┘  │
│                                  │
│  [Create]             [Back]     │
└──────────────────────────────────┘
```

### Code Issued Notice

```
┌──────────────────────────────────┐
│     ✓ Portfolio Created!         │
│                                  │
│  Your unique code:               │
│  ┌────────────────────────────┐  │
│  │  ZJXV-ENDA-AIMI    [Copy] │  │
│  └────────────────────────────┘  │
│                                  │
│  ⚠ Save this code!              │
│  You cannot access your          │
│  portfolio without it.           │
│                                  │
│  [Start Portfolio]               │
└──────────────────────────────────┘
```

### Error Popup

```
┌──────────────────────────────────┐
│  ✗ Login Failed                  │
│                                  │
│  Invalid code or PIN.            │
│  Please try again.               │
│                                  │
│  (30s lockout after 3 failures)  │
│                                  │
│  [OK]                            │
└──────────────────────────────────┘
```

### New File

| File | Role |
|------|------|
| `frontend/src/components/portfolio/PortfolioLoginGate.tsx` | Login/register popup component |

### Modified File

| File | Change |
|------|--------|
| `frontend/src/pages/Portfolio.tsx` | Session check → Gate or existing Portfolio branch |

---

## Step 2: Session Management

### Storage

| Key | Storage | Content |
|-----|---------|---------|
| `portfolio_session` | sessionStorage | `{ code, pin }` — expires when browser tab closes |
| `portfolio_remember` | localStorage | `{ code }` — code only when "remember" checked (no PIN) |

### Session Flow

```
Login success
  → Save code + pin in sessionStorage
  → If "remember" checked, save code only in localStorage
  → Pass code + pin to usePortfolio hook

Page revisit
  → Check sessionStorage → if present, auto-login (no popup)
  → If no sessionStorage:
    → Check localStorage → if present, auto-fill code (PIN only input)
    → If neither → show login popup

Logout
  → Delete sessionStorage
  → Keep localStorage (remembered code persists)
```

### Modified File

| File | Change |
|------|--------|
| `frontend/src/services/syncApi.ts` | Add session save/load/delete functions |

---

## Step 3: usePortfolio Server Integration

### Before (localStorage-based)

```
usePortfolio()
  → loadHoldings() — read from localStorage
  → addHolding() — write to localStorage
  → updateHolding() — write to localStorage
  → removeHolding() — write to localStorage
```

### After (server-based)

```
usePortfolio(code, pin)
  → Initial load: pullSync(code, pin) — read from server
  → addHolding() — update state → pushSync(code, pin, data) — write to server
  → updateHolding() — update state → pushSync() — write to server
  → removeHolding() — update state → pushSync() — write to server
```

### Key Changes
- Add `code`, `pin` parameters to `usePortfolio` hook
- Replace initial load from `loadHoldings()` (localStorage) → `pullSync()` (server)
- Add `pushSync()` at every `saveHoldings()` call site (auto server sync)
- Keep localStorage as offline cache (optional)

### Modified Files

| File | Change |
|------|--------|
| `frontend/src/hooks/usePortfolio.ts` | code+pin params, server-based load/save |
| `frontend/src/services/portfolioApi.ts` | Adapt loadHoldings/saveHoldings for server or keep alongside |

---

## Step 4: Settings Page Integration

### Settings UI (Logged In)

```
┌──────────────────────────────────┐
│  MY ACCOUNT                      │
│                                  │
│  My Code: ZJXV-ENDA-AIMI [Copy] │
│  Last accessed: 2026-05-13 14:30 │
│                                  │
│  [Logout]                        │
└──────────────────────────────────┘
```

### Settings UI (Not Logged In)

```
┌──────────────────────────────────┐
│  MY ACCOUNT                      │
│                                  │
│  Please log in from Portfolio    │
│  to use this feature.            │
│                                  │
│  [Go to Portfolio]               │
└──────────────────────────────────┘
```

### Modified File

| File | Change |
|------|--------|
| `frontend/src/pages/Settings.tsx` | PORTFOLIO SYNC → MY ACCOUNT, login state branch |

---

## Step 5: Portfolio Header Logout Button

### Logged In State

```
┌────────────────────────────────────────────┐
│  Portfolio            ⟳ Refresh  + Add Stock │
│  ZJXV-ENDA-AIMI                   [Logout] │
└────────────────────────────────────────────┘
```

### Modified File

| File | Change |
|------|--------|
| `frontend/src/pages/Portfolio.tsx` | Header code display + logout button |

---

## Backend Changes

Reuses existing `sync_service.py` + `backend/routers/sync.py` APIs. **No additional backend development needed.**

| Purpose | Existing API | Change |
|---------|-------------|--------|
| Code issuance | POST `/api/sync/create` | None |
| Login (code+PIN verify) | POST `/api/sync/connect` | None |
| Portfolio load | POST `/api/sync/pull` | None |
| Portfolio save | POST `/api/sync/push` | None |
| Logout | — | Frontend only (session delete) |

---

## Security

- PIN: bcrypt hash stored server-side (existing sync_service)
- 3 consecutive PIN failures → 30s lockout (existing sync_service)
- 90 days inactive → auto-delete server data (existing sync_service)
- sessionStorage: session expires when browser tab closes
- localStorage: code only, PIN is never stored

---

## PIN Recovery Policy

- **Current policy**: No recovery. Lost code+PIN → must create new code (existing data inaccessible)
- **Notice**: "PIN cannot be changed or recovered. Please remember it." warning at code issuance
- **Future extension**: Recovery phrase (8-word) method under consideration if needed

---

## Design Decisions

| Decision | Rationale |
|----------|-----------|
| Code+PIN instead of email/password | No signup friction, aligns with existing sync infrastructure |
| Server-side data (Render SQLite) | Multi-user + cross-device support; localStorage only as cache |
| sessionStorage for session | Auto-expire on tab close for security |
| localStorage stores code only, not PIN | Balance between convenience (remember code) and security (always enter PIN) |
| Reuse sync API without changes | All needed endpoints already exist, minimizes scope |
| PIN immutable | Simplifies implementation; recovery phrase can be added later |

---

## Implementation Order & Dependencies

```
Step 1 (Login Gate) + Step 2 (Session Mgmt) ← parallel
  |
Step 3 (usePortfolio server integration) ← requires Step 1, 2
  |
Step 4 (Settings) + Step 5 (Header buttons) ← parallel, requires Step 3
```

---

## Implementation Files Summary

### New Files

| File | Role |
|------|------|
| `frontend/src/components/portfolio/PortfolioLoginGate.tsx` | Login/register popup |

### Modified Files

| File | Change |
|------|--------|
| `frontend/src/pages/Portfolio.tsx` | Gate wrapping + header code/logout |
| `frontend/src/hooks/usePortfolio.ts` | Server-based load/save |
| `frontend/src/services/syncApi.ts` | Session management functions |
| `frontend/src/pages/Settings.tsx` | MY ACCOUNT section |

---

## Estimated Effort

| Step | Task | Time |
|------|------|------|
| 1 | PortfolioLoginGate component | 3h |
| 2 | Session management logic | 1h |
| 3 | usePortfolio server integration | 2h |
| 4 | Settings page integration | 1h |
| 5 | Portfolio header buttons | 30m |
| Test | Login/register/logout/remember | 1h |
| **Total** | | **8.5h** |

---

## Prerequisites & Dependencies

- Phase 13 (Portfolio) — completed
- Phase 13 Step 8 (Sync) — backend API reused (`sync_service.py`, `backend/routers/sync.py`)
- Render deployment — SQLite DB for server-side storage

---

## Development Notes

- Render free plan SQLite may reset on server restart. If data loss occurs, consider migrating to PostgreSQL.
- The existing `portfolio_sync` SQLite table stores holdings as JSON string — same structure is reused.
- `bcrypt` dependency already installed (fixed in commit `3ab41f2`).

---

## Change Log

| Date | Description |
|------|-------------|
| 2026-05-13 | Initial creation |
| 2026-05-25 | Implementation completed — all 5 deliverables done (PortfolioLoginGate, session management, usePortfolio server integration, Settings MY ACCOUNT, Portfolio header logout). TypeScript + Vite build passed. |

---
---

# Phase 13.5 — 포트폴리오 사용자 인증 시스템 `✅ 완료`

> 코드+PIN 기반 다중 사용자 인증으로 포트폴리오 접근 제어 및 서버 측 데이터 저장.

**상태**: ✅ 완료
**선행 조건**: Phase 13 (Portfolio) 완료

---

## 개요

Phase 13 Portfolio는 브라우저 localStorage에 인증 없이 데이터를 저장하여 누구나 접근 가능하다. 기존 Sync 기능(Phase 13 Step 8)은 Settings에 숨어있는 수동 백업 도구일 뿐, 포트폴리오 접근 보호와는 무관하다.

이 Phase에서는 Portfolio 페이지에 **코드 + 4자리 PIN 인증 게이트**를 추가한다. 사용자마다 고유 12자리 코드를 발급받고, 모든 포트폴리오 데이터는 서버(Render SQLite)에 해당 코드로 키잉하여 저장한다. 회원가입/로그인 없이 코드+PIN만으로 인증.

---

## 완료 예정 / 완료 항목

| # | 모듈 / 컴포넌트 | 상태 | 타입 |
|---|---|---|---|
| 1 | `PortfolioLoginGate.tsx` — 로그인/발급 팝업 | ✅ | frontend |
| 2 | 세션 관리 (sessionStorage + localStorage) | ✅ | frontend |
| 3 | `usePortfolio` 서버 연동 | ✅ | frontend |
| 4 | Settings 페이지 MY ACCOUNT 섹션 | ✅ | frontend |
| 5 | Portfolio 헤더 코드 표시 + 로그아웃 버튼 | ✅ | frontend |

---

## 사용자 흐름

### 신규 사용자

```
Portfolio 클릭
  → 로그인 팝업 표시
  → "코드가 없으신가요?" → [발급받기] 클릭
  → PIN 4자리 설정 (입력 + 확인)
  → 고유 코드 발급 (예: ABCD-1234-EFGH)
  → "이 코드를 반드시 저장하세요!" 안내 + 복사 버튼
  → 자동 로그인 → 빈 포트폴리오 표시
```

### 기존 사용자

```
Portfolio 클릭
  → 로그인 팝업 표시
  → 코드 + PIN 입력
  → ☑ 이 브라우저에서 기억하기 (선택)
  → 인증 성공 → 서버에서 해당 코드의 포트폴리오 로드
  → 인증 실패 → "코드 또는 PIN이 올바르지 않습니다" 오류 팝업
```

### 기억하기 체크 시 재방문

```
Portfolio 클릭
  → localStorage에 저장된 코드 자동 입력
  → PIN만 입력
  → 로그인
```

### 로그아웃

```
Portfolio 헤더의 [로그아웃] 버튼 클릭
  → 세션 초기화
  → 로그인 팝업으로 복귀
```

---

## Step 1: 로그인 팝업 (PortfolioLoginGate)

### 컴포넌트 구조

```
Portfolio 페이지 진입
  ├─ 세션 없음 → <PortfolioLoginGate>
  │   ├─ 기본 화면: 코드 입력 + PIN 입력 + [로그인] 버튼
  │   │   └─ ☑ 이 브라우저에서 기억하기
  │   ├─ "코드가 없으신가요?" → [발급받기]
  │   │   └─ PIN 설정 → 코드 생성 → 안내 팝업
  │   └─ 오류 상태: "코드 또는 PIN이 올바르지 않습니다"
  └─ 세션 있음 → <Portfolio> (기존 컴포넌트)
```

### 로그인 화면 UI

```
┌──────────────────────────────────┐
│         My Portfolio             │
│                                  │
│  ┌────────────────────────────┐  │
│  │  ABCD-1234-EFGH            │  │  ← 코드 입력 (12자리, 자동 하이픈)
│  └────────────────────────────┘  │
│  ┌────────────────────────────┐  │
│  │  ●●●●                     │  │  ← PIN 입력 (4자리, 마스킹)
│  └────────────────────────────┘  │
│                                  │
│  ☑ 이 브라우저에서 기억하기       │
│                                  │
│  ┌────────────────────────────┐  │
│  │         로그인              │  │
│  └────────────────────────────┘  │
│                                  │
│  코드가 없으신가요? [발급받기]    │
└──────────────────────────────────┘
```

### 코드 발급 화면 UI

```
┌──────────────────────────────────┐
│       새 포트폴리오 만들기        │
│                                  │
│  4자리 PIN을 설정하세요.          │
│  이 PIN은 변경할 수 없으니         │
│  반드시 기억해 주세요.            │
│                                  │
│  ┌────────────────────────────┐  │
│  │  ●●●●                     │  │  ← PIN 설정
│  └────────────────────────────┘  │
│  ┌────────────────────────────┐  │
│  │  ●●●●                     │  │  ← PIN 확인 (동일한지 체크)
│  └────────────────────────────┘  │
│                                  │
│  [생성하기]          [돌아가기]   │
└──────────────────────────────────┘
```

### 코드 발급 완료 안내

```
┌──────────────────────────────────┐
│       ✓ 포트폴리오 생성 완료!     │
│                                  │
│  내 고유 코드:                    │
│  ┌────────────────────────────┐  │
│  │  ZJXV-ENDA-AIMI    [복사]  │  │
│  └────────────────────────────┘  │
│                                  │
│  ⚠ 이 코드를 반드시 저장하세요!   │
│  코드를 분실하면 포트폴리오에      │
│  다시 접근할 수 없습니다.         │
│                                  │
│  [포트폴리오 시작하기]            │
└──────────────────────────────────┘
```

### 오류 팝업

```
┌──────────────────────────────────┐
│  ✗ 로그인 실패                   │
│                                  │
│  코드 또는 PIN이 올바르지         │
│  않습니다. 다시 확인해 주세요.    │
│                                  │
│  (3회 실패 시 30초 대기)          │
│                                  │
│  [확인]                          │
└──────────────────────────────────┘
```

### 신규 파일

| 파일 | 역할 |
|------|------|
| `frontend/src/components/portfolio/PortfolioLoginGate.tsx` | 로그인/발급 팝업 컴포넌트 |

### 수정 파일

| 파일 | 변경 내용 |
|------|----------|
| `frontend/src/pages/Portfolio.tsx` | 세션 체크 → Gate 또는 기존 Portfolio 분기 |

---

## Step 2: 세션 관리

### 세션 저장소

| 키 | 저장소 | 내용 |
|---|---|---|
| `portfolio_session` | sessionStorage | `{ code, pin }` — 브라우저 탭 닫으면 만료 |
| `portfolio_remember` | localStorage | `{ code }` — "기억하기" 체크 시 코드만 저장 (PIN 제외) |

### 세션 흐름

```
로그인 성공
  → sessionStorage에 code + pin 저장
  → "기억하기" 체크 시 localStorage에 code만 추가 저장
  → usePortfolio 훅에 code + pin 전달

페이지 재방문
  → sessionStorage 확인 → 있으면 자동 로그인 (팝업 안 뜸)
  → sessionStorage 없으면:
    → localStorage 확인 → 있으면 코드 자동 입력 (PIN만 입력)
    → 둘 다 없으면 → 로그인 팝업 표시

로그아웃
  → sessionStorage 삭제
  → localStorage 유지 (기억하기 코드는 남김)
```

### 수정 파일

| 파일 | 변경 내용 |
|------|----------|
| `frontend/src/services/syncApi.ts` | 세션 저장/로드/삭제 함수 추가 |

---

## Step 3: usePortfolio 서버 연동

### 변경 전 (localStorage 기반)

```
usePortfolio()
  → loadHoldings() — localStorage에서 읽기
  → addHolding() — localStorage에 쓰기
  → updateHolding() — localStorage에 쓰기
  → removeHolding() — localStorage에 쓰기
```

### 변경 후 (서버 기반)

```
usePortfolio(code, pin)
  → 초기 로드: pullSync(code, pin) — 서버에서 읽기
  → addHolding() — 상태 업데이트 → pushSync(code, pin, data) — 서버에 쓰기
  → updateHolding() — 상태 업데이트 → pushSync() — 서버에 쓰기
  → removeHolding() — 상태 업데이트 → pushSync() — 서버에 쓰기
```

### 변경 포인트
- `usePortfolio` 훅에 `code`, `pin` 파라미터 추가
- 초기 로드를 `loadHoldings()` (localStorage) → `pullSync()` (서버)로 교체
- `saveHoldings()` 호출 위치마다 `pushSync()` 추가 (자동 서버 동기화)
- localStorage는 오프라인 캐시 용도로 병행 유지 (선택)

### 수정 파일

| 파일 | 변경 내용 |
|------|----------|
| `frontend/src/hooks/usePortfolio.ts` | code+pin 파라미터, 서버 로드/저장으로 전환 |
| `frontend/src/services/portfolioApi.ts` | loadHoldings/saveHoldings를 서버 기반으로 변경 또는 병행 |

---

## Step 4: Settings 페이지 연동

### Settings UI (로그인 상태)

```
┌──────────────────────────────────┐
│  MY ACCOUNT                      │
│                                  │
│  내 코드: ZJXV-ENDA-AIMI [복사]  │
│  마지막 접속: 2026-05-13 14:30    │
│                                  │
│  [로그아웃]                      │
└──────────────────────────────────┘
```

### Settings UI (미로그인 상태)

```
┌──────────────────────────────────┐
│  MY ACCOUNT                      │
│                                  │
│  포트폴리오를 사용하려면          │
│  먼저 로그인하세요.               │
│                                  │
│  [Portfolio로 이동]              │
└──────────────────────────────────┘
```

### 수정 파일

| 파일 | 변경 내용 |
|------|----------|
| `frontend/src/pages/Settings.tsx` | PORTFOLIO SYNC → MY ACCOUNT, 로그인 상태 분기 |

---

## Step 5: Portfolio 헤더에 로그인/로그아웃 버튼

### 로그인 상태

```
┌────────────────────────────────────────────┐
│  Portfolio            ⟳ Refresh  + Add Stock │
│  ZJXV-ENDA-AIMI                 [로그아웃]  │
└────────────────────────────────────────────┘
```

### 수정 파일

| 파일 | 변경 내용 |
|------|----------|
| `frontend/src/pages/Portfolio.tsx` | 헤더에 코드 표시 + 로그아웃 버튼 추가 |

---

## 백엔드 변경

기존 `sync_service.py` + `backend/routers/sync.py`의 API를 **그대로 재활용**한다. 추가 백엔드 개발 없음.

| 용도 | 기존 API | 변경 |
|------|---------|------|
| 코드 발급 | POST `/api/sync/create` | 없음 |
| 로그인 (코드+PIN 검증) | POST `/api/sync/connect` | 없음 |
| 포트폴리오 로드 | POST `/api/sync/pull` | 없음 |
| 포트폴리오 저장 | POST `/api/sync/push` | 없음 |
| 로그아웃 | — | 프론트엔드만 (세션 삭제) |

---

## 보안

- PIN: bcrypt 해시로 서버 저장 (기존 sync_service 동일)
- 3회 연속 PIN 실패 → 30초 잠금 (기존 sync_service 동일)
- 90일 미접속 시 서버 데이터 자동 삭제 (기존 sync_service 동일)
- sessionStorage: 브라우저 탭 닫으면 세션 만료
- localStorage: 코드만 저장, PIN은 저장하지 않음

---

## PIN 분실 정책

- **현재 정책**: PIN 복구 불가. 코드+PIN 분실 시 새 코드를 발급받아야 함 (기존 데이터 접근 불가)
- **안내 문구**: 코드 발급 시 "PIN은 변경 및 복구가 불가능합니다. 반드시 기억해 주세요." 경고 표시
- **향후 확장**: 필요 시 복구 문구(8단어 recovery phrase) 방식 추가 검토

---

## 설계 결정 사항

| 결정 | 근거 |
|------|------|
| 이메일/비밀번호 대신 코드+PIN | 회원가입 부담 없음, 기존 sync 인프라 재활용 |
| 서버 측 데이터 저장 (Render SQLite) | 다중 사용자 + 크로스 디바이스 지원; localStorage는 캐시 용도 |
| 세션에 sessionStorage 사용 | 탭 닫으면 자동 만료되어 보안성 확보 |
| localStorage에 코드만, PIN은 저장 안 함 | 편의성(코드 기억)과 보안성(매번 PIN 입력) 균형 |
| sync API 변경 없이 재사용 | 필요한 엔드포인트가 이미 모두 존재, 범위 최소화 |
| PIN 변경 불가 | 구현 단순화; 복구 문구는 추후 추가 가능 |

---

## 구현 순서 및 의존 관계

```
Step 1 (로그인 팝업 Gate) + Step 2 (세션 관리) ← 병렬 가능
  |
Step 3 (usePortfolio 서버 연동) ← Step 1, 2 완료 필요
  |
Step 4 (Settings 연동) + Step 5 (헤더 버튼) ← 병렬 가능, Step 3 필요
```

---

## 구현 파일 요약

### 신규 파일

| 파일 | 역할 |
|------|------|
| `frontend/src/components/portfolio/PortfolioLoginGate.tsx` | 로그인/발급 팝업 |

### 수정 파일

| 파일 | 변경 내용 |
|------|----------|
| `frontend/src/pages/Portfolio.tsx` | Gate 래핑 + 헤더에 코드/로그아웃 |
| `frontend/src/hooks/usePortfolio.ts` | 서버 기반 로드/저장 |
| `frontend/src/services/syncApi.ts` | 세션 관리 함수 추가 |
| `frontend/src/pages/Settings.tsx` | MY ACCOUNT 섹션으로 변경 |

---

## 예상 공수

| Step | 작업 | 시간 |
|------|------|------|
| 1 | PortfolioLoginGate 컴포넌트 | 3h |
| 2 | 세션 관리 로직 | 1h |
| 3 | usePortfolio 서버 연동 | 2h |
| 4 | Settings 페이지 연동 | 1h |
| 5 | Portfolio 헤더 버튼 | 30m |
| 테스트 | 로그인/발급/로그아웃/기억하기 | 1h |
| **합계** | | **8.5시간** |

---

## 선행 조건 및 의존성

- Phase 13 (Portfolio) — 완료
- Phase 13 Step 8 (Sync) — 백엔드 API 재사용 (`sync_service.py`, `backend/routers/sync.py`)
- Render 배포 — 서버 측 저장용 SQLite DB

---

## 개발 시 주의사항

- Render 무료 플랜 SQLite는 서버 재시작 시 초기화될 수 있음. 데이터 유실 발생 시 PostgreSQL 마이그레이션 검토.
- 기존 `portfolio_sync` SQLite 테이블은 holdings를 JSON 문자열로 저장 — 동일 구조 재사용.
- `bcrypt` 의존성은 이미 설치됨 (커밋 `3ab41f2`에서 수정).

---

## 변경 이력

| 날짜 | 내용 |
|------|------|
| 2026-05-13 | 최초 작성 |
| 2026-05-25 | 구현 완료 — 5개 항목 전부 완료 (PortfolioLoginGate, 세션 관리, usePortfolio 서버 연동, Settings MY ACCOUNT, Portfolio 헤더 로그아웃). TypeScript + Vite 빌드 통과. |

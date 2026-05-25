# Phase 14 — Free Trial Hybrid (3+3) System `🔲 Not Started`

> Device-based anonymous 3 free analyses + email registration for 3 more (total 6). Designed for future migration to email-only and paid tier.

**Status**: 🔲 Not Started
**Prerequisites**: Phase 13 completed (Portfolio), Phase 13.5 completed (Portfolio Auth)

---

## Overview

The app currently has no per-user tracking — all API endpoints are public with only a global 100/day AI call limit. This Phase introduces a hybrid free trial system that:

1. **Anonymous tier (3 uses)**: Identifies devices via UUID stored in localStorage, sent as `X-Device-Id` header
2. **Email tier (+3 uses, total 6)**: Email verification upgrades the anonymous user to 6 lifetime analyses
3. **Cache hits are free**: Only fresh AI pipeline executions count toward the trial limit

**Migration path**: Hybrid → Email-only requires changing 2 lines of code (make `X-Device-Id` required + check `email_verified`). Paid tier integration adds a payment check to the same gate.

---

## Deliverables

| # | Module | Status | Type | Est. Hours |
|---|---|---|---|---|
| 1 | DB Schema (trial_users + email_verification) | 🔲 | backend | 0.5h |
| 2 | Email Sender (pluggable, console default) | 🔲 | backend | 0.5h |
| 3 | Trial Service (core business logic) | 🔲 | backend | 2h |
| 4 | Trial API Router (status, request-code, verify) | 🔲 | backend | 1h |
| 5 | Analysis Endpoint Trial Gate | 🔲 | backend | 1h |
| 6 | Device ID + Trial API Client (frontend) | 🔲 | frontend | 1h |
| 7 | useTrial Hook | 🔲 | frontend | 1h |
| 8 | useAnalysis Hook Modification | 🔲 | frontend | 1h |
| 9 | TrialBanner Component | 🔲 | frontend | 1h |
| 10 | EmailRegistrationModal Component | 🔲 | frontend | 2h |
| 11 | TrialLimitModal Component | 🔲 | frontend | 1h |
| 12 | Existing Component Wiring (Sidebar, AiAnalysisInline, QuickLook) | 🔲 | frontend | 1h |
| 13 | Integration Test + QA | 🔲 | general | 1.5h |

**Total: ~14.5 hours**

---

## 1. DB Schema

### Purpose

Add two new tables to SQLite for per-device usage tracking and email verification code management.

### Implementation Files

| File | Change |
|------|--------|
| `data/database.py` | Add `trial_users` + `email_verification` tables to `CREATE_TABLES_SQL` |

### Schema

```sql
CREATE TABLE IF NOT EXISTS trial_users (
    device_id TEXT PRIMARY KEY,
    email TEXT UNIQUE,
    email_verified INTEGER DEFAULT 0,
    usage_count INTEGER DEFAULT 0,
    max_usage INTEGER DEFAULT 3,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS email_verification (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    device_id TEXT NOT NULL,
    email TEXT NOT NULL,
    code TEXT NOT NULL,
    attempts INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP NOT NULL,
    FOREIGN KEY (device_id) REFERENCES trial_users(device_id)
);
```

### Design Decisions

- `usage_count` is **lifetime** (not daily) — the existing global 100/day limit in `utils/usage_tracker.py` handles daily throttling separately
- `email UNIQUE` constraint prevents one email from being used across multiple devices for unlimited +3 bonuses
- `max_usage` defaults to 3 (anonymous), updated to 6 on email verification
- Uses `CREATE TABLE IF NOT EXISTS` pattern — no migration needed, tables appear on next `init_db()` call

---

## 2. Email Sender (Pluggable)

### Purpose

Pluggable email sending module that defaults to console output for development, switchable to SMTP for production.

### Implementation Files

| File | Change |
|------|--------|
| `services/email_sender.py` | **New** — `send_verification_email(email, code) → bool` |

### Core Logic

- Reads `EMAIL_BACKEND` env var: `"console"` (default) or `"smtp"`
- Console mode: logs 6-digit code to stdout
- SMTP mode: uses `SMTP_HOST`, `SMTP_PORT`, `SMTP_USER`, `SMTP_PASS` env vars

---

## 3. Trial Service

### Purpose

Core business logic for trial user management, usage tracking, and email verification.

### Implementation Files

| File | Change |
|------|--------|
| `services/trial_service.py` | **New** — 5 functions for trial lifecycle management |

### Functions

| Function | Role |
|----------|------|
| `get_or_create_user(device_id)` | Lookup/create user. `INSERT OR IGNORE` pattern for concurrent safety |
| `check_and_increment_usage(device_id)` | Atomic check+increment via `UPDATE ... WHERE usage_count < max_usage` |
| `request_verification(device_id, email)` | Generate 6-digit code, store in DB, send via email_sender. 10-min expiry |
| `verify_code(device_id, email, code)` | Verify code, on success set `max_usage=6`. Max 3 wrong attempts per code |
| `get_trial_status(device_id)` | Read-only status: usage_count, max_usage, remaining, tier |

### Concurrency Safety

- `UPDATE trial_users SET usage_count = usage_count + 1 WHERE device_id = ? AND usage_count < max_usage` is atomic in SQLite WAL mode
- `INSERT OR IGNORE` handles race conditions on first-time user creation

---

## 4. Trial API Router

### Purpose

REST endpoints for trial status checking, email verification code request, and code verification.

### Implementation Files

| File | Change |
|------|--------|
| `backend/routers/trial.py` | **New** — 3 endpoints |
| `backend/main.py` | Add trial router import + registration |

### Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/trial/status` | GET | Current trial status for device |
| `/api/trial/request-code` | POST | Send verification code to email |
| `/api/trial/verify` | POST | Verify 6-digit code |

All endpoints require `X-Device-Id` header (FastAPI `Header(...)` auto-extraction).

---

## 5. Analysis Endpoint Trial Gate

### Purpose

Insert a trial usage check between cache lookup and AI pipeline execution in the analysis endpoint.

### Implementation Files

| File | Change |
|------|--------|
| `backend/routers/analysis.py` | Add `X-Device-Id` header param + trial gate logic |

### Modified Flow

```
Before: Cache check → Data fetch → AI pipeline → Cache save
After:  Cache check → [Trial Gate] → Data fetch → AI pipeline → Cache save
```

- Cache hits return before the gate — **free, no usage consumed**
- `X-Device-Id` is `Optional[str]` for backward compatibility (migration to required = email-only mode)
- Over-limit returns HTTP 429 with `{ error: "trial_limit_reached", usage_count, max_usage, email_registered }`
- Successful analysis includes `trial_status` in response body

---

## 6. Frontend — Device ID + Trial API Client

### Purpose

Generate and persist a unique device identifier, and provide typed API functions for trial endpoints.

### Implementation Files

| File | Change |
|------|--------|
| `frontend/src/services/deviceId.ts` | **New** — `getDeviceId()` using `crypto.randomUUID()` + localStorage |
| `frontend/src/services/trialApi.ts` | **New** — `fetchTrialStatus()`, `requestVerificationCode()`, `verifyEmailCode()` |

### Device ID Strategy

- UUID v4 generated via `crypto.randomUUID()` (supported in all modern browsers)
- Stored in localStorage under `quantai_device_id`
- All trial API calls include `X-Device-Id` header automatically

---

## 7. useTrial Hook

### Purpose

React hook managing trial state with auto-refresh on analysis completion.

### Implementation Files

| File | Change |
|------|--------|
| `frontend/src/hooks/useTrial.ts` | **New** — trial state management hook |

### Core Behavior

- Fetches `GET /api/trial/status` on mount
- Listens for `trial-status-changed` CustomEvent (dispatched after successful analysis)
- Returns `{ status, loading, refreshStatus }`

---

## 8. useAnalysis Hook Modification

### Purpose

Add device identification headers and trial limit handling to the existing analysis hook.

### Implementation Files

| File | Change |
|------|--------|
| `frontend/src/hooks/useAnalysis.ts` | Add X-Device-Id header, 429 handling, event dispatch |

### Changes

1. **Line 35**: Add `headers: { 'X-Device-Id': getDeviceId() }` to fetch call
2. **New state**: `trialBlocked` — set when HTTP 429 with `trial_limit_reached`
3. **Post-success**: Dispatch `trial-status-changed` CustomEvent
4. **Return**: Add `trialBlocked` to hook return value

---

## 9. TrialBanner Component

### Purpose

Sidebar widget showing remaining trial uses and email registration prompt.

### Implementation Files

| File | Change |
|------|--------|
| `frontend/src/components/TrialBanner.tsx` | **New** — trial status display |
| `frontend/src/components/Sidebar.tsx` | Replace hardcoded "AI USAGE 0/100" (lines 154-187) with `<TrialBanner />` |

### UI Spec

- "FREE TRIAL" label (xs, muted text)
- Remaining count in numeric font with accent color (e.g., "2/3 remaining")
- 4px progress bar with theme.accent fill
- Anonymous tier: "Get +3 more with email" link → opens EmailRegistrationModal
- Email tier: checkmark + "Email verified" text

---

## 10. EmailRegistrationModal Component

### Purpose

Two-step modal for email registration and verification code entry.

### Implementation Files

| File | Change |
|------|--------|
| `frontend/src/components/EmailRegistrationModal.tsx` | **New** — email verification flow modal |

### UI Flow

**Step 1 — Email Input:**
- Heading: "Get 3 More Free Analyses"
- Email input field
- "Send Code" button

**Step 2 — Code Input:**
- Heading: "Enter Verification Code"
- 6-digit code input (numeric, centered)
- "Verify" button
- "Resend code" link (60-second cooldown timer)
- Error display for wrong/expired codes

### Modal Pattern

- Fixed overlay `rgba(0,0,0,0.5)`, zIndex: 500
- Centered card with `theme.bg_card`
- Click-outside dismiss via stopPropagation
- Follows existing AlertModal/AddStockModal pattern

---

## 11. TrialLimitModal Component

### Purpose

Modal shown when analysis returns HTTP 429 (trial limit reached). Two variants based on registration status.

### Implementation Files

| File | Change |
|------|--------|
| `frontend/src/components/TrialLimitModal.tsx` | **New** — limit reached modal |

### Variants

**Variant A — Anonymous (email_registered = false):**
- "Free Trial Limit Reached"
- "Register your email to get 3 more!"
- [Register Email] button → opens EmailRegistrationModal
- [Maybe Later] button → closes

**Variant B — Email user (email_registered = true):**
- "Trial Limit Reached"
- "You've used all 6 available analyses. Premium plans coming soon."
- [Got it] button → closes

---

## 12. Existing Component Wiring

### Purpose

Connect trial state and modals to existing components.

### Implementation Files

| File | Change |
|------|--------|
| `frontend/src/components/AiAnalysisInline.tsx` | Add `trialBlocked` prop, show TrialLimitModal on block |
| `frontend/src/pages/QuickLook.tsx` | Pass `trialBlocked` from useAnalysis to AiAnalysisInline |

### AiAnalysisInline Changes

- Accept new `trialBlocked` prop
- When `trialBlocked` is set, render TrialLimitModal
- Update re-analyze confirm message (line 82) to reflect trial remaining count

### QuickLook Changes

- Destructure `trialBlocked` from `useAnalysis` hook (line 31)
- Pass to `<AiAnalysisInline trialBlocked={...} />` (line 108)

---

## Edge Cases & Safety

| Scenario | Handling |
|----------|----------|
| localStorage cleared | New UUID generated, fresh 3-use trial. Same email can't be re-verified (UNIQUE) |
| Concurrent analysis requests | Atomic `UPDATE WHERE usage_count < max_usage` — one succeeds, other gets 429 |
| Global 100/day limit hit | Trial usage consumed but AI pipeline fails with daily limit error |
| Same email on different device | `request_verification` rejects: "This email is already registered" |
| Verification code brute-force | Max 3 attempts per code, 10-minute expiry (6-digit = 1M possibilities) |
| Code spam | Max 3 active codes per device in 10 minutes |

---

## Migration Paths

### Hybrid → Email-Only (2 code changes)

1. `backend/routers/analysis.py`: Change `x_device_id: Optional[str] = Header(None)` → `x_device_id: str = Header(...)`
2. Add check in `check_and_increment_usage`: if `email_verified == 0`, return `allowed: false, reason: "email_required"`

### Email-Only → Paid Tier (future)

- Add `tier` column to `trial_users` (`free`, `premium`)
- Add payment verification step before upgrading tier
- `max_usage` set to unlimited (or high number) for premium

---

## Implementation Order

```
Backend (independent, testable first):
  1. data/database.py          — schema foundation
  2. services/email_sender.py  — no dependencies
  3. services/trial_service.py — depends on database
  4. backend/routers/trial.py  — depends on trial_service
  5. backend/main.py           — router registration
  6. backend/routers/analysis.py — trial gate insertion

Frontend (after backend is working):
  7. frontend/src/services/deviceId.ts   — no dependencies
  8. frontend/src/services/trialApi.ts   — depends on deviceId
  9. frontend/src/hooks/useTrial.ts      — depends on trialApi
  10. frontend/src/hooks/useAnalysis.ts  — depends on deviceId
  11. frontend/src/components/TrialBanner.tsx
  12. frontend/src/components/EmailRegistrationModal.tsx
  13. frontend/src/components/TrialLimitModal.tsx
  14. frontend/src/components/Sidebar.tsx — TrialBanner swap
  15. frontend/src/components/AiAnalysisInline.tsx — modal wiring
  16. frontend/src/pages/QuickLook.tsx    — prop passing
```

---

## File Summary

### New Files (9)

| File | Purpose |
|------|---------|
| `services/email_sender.py` | Pluggable email sending (console/SMTP) |
| `services/trial_service.py` | Core trial business logic |
| `backend/routers/trial.py` | Trial API endpoints |
| `frontend/src/services/deviceId.ts` | Device ID generation + persistence |
| `frontend/src/services/trialApi.ts` | Trial API client functions |
| `frontend/src/hooks/useTrial.ts` | Trial state management hook |
| `frontend/src/components/TrialBanner.tsx` | Sidebar trial status banner |
| `frontend/src/components/EmailRegistrationModal.tsx` | Email verification modal |
| `frontend/src/components/TrialLimitModal.tsx` | Limit reached modal |

### Modified Files (6)

| File | Change |
|------|--------|
| `data/database.py` | Add 2 tables to CREATE_TABLES_SQL |
| `backend/main.py` | Import + register trial router |
| `backend/routers/analysis.py` | Add X-Device-Id header + trial gate |
| `frontend/src/hooks/useAnalysis.ts` | Add device header + 429 handling |
| `frontend/src/components/Sidebar.tsx` | Replace AI USAGE with TrialBanner |
| `frontend/src/components/AiAnalysisInline.tsx` | Wire trialBlocked + modal |
| `frontend/src/pages/QuickLook.tsx` | Pass trialBlocked prop |

---

## Verification

### Backend Testing

1. **Unit tests**: trial_service functions (create user, increment, limit, verify code)
2. **API test**: `curl -H "X-Device-Id: test-uuid" http://localhost:8000/api/trial/status`
3. **429 test**: Exhaust 3 uses, verify 4th returns 429 with correct detail body
4. **Cache bypass test**: Cached analysis doesn't increment usage_count

### Frontend Manual Testing

1. Fresh browser → run analysis → TrialBanner shows "2/3 remaining"
2. Run 3 analyses → TrialLimitModal appears with "Register Email" option
3. Complete email verification → TrialBanner updates to "3/6 remaining"
4. Run 3 more → TrialLimitModal shows "Trial Limit Reached" (no email option)
5. Clear localStorage → new device ID → fresh "3/3 remaining"
6. Try same email on new device → error message

---

## Change Log

| Date | Change | Author |
|------|--------|--------|
| 2026-05-16 | Document created — initial planning (as Phase 15) | AI |
| 2026-05-16 | Renumbered from Phase 15 → Phase 14 (swapped with i18n) | AI |

---
---

# Phase 14 — 무료체험 하이브리드(3+3) 시스템 `🔲 미시작`

> 기기 기반 익명 3회 무료 + 이메일 등록 시 3회 추가 (총 6회). 향후 이메일 전용 및 유료 전환 가능한 구조.

**상태**: 🔲 미시작
**선행 조건**: Phase 13 완료 (포트폴리오), Phase 13.5 완료 (포트폴리오 인증)

---

## 개요

현재 앱은 사용자별 추적 기능이 없다 — 모든 API 엔드포인트가 공개되어 있고 글로벌 일일 100회 AI 호출 제한만 존재한다. 이 Phase에서는 하이브리드 무료체험 시스템을 도입한다:

1. **익명 티어 (3회)**: localStorage의 UUID로 기기 식별, `X-Device-Id` 헤더로 전송
2. **이메일 티어 (+3회, 총 6회)**: 이메일 인증 완료 시 누적 6회 분석 가능
3. **캐시 결과는 무료**: 새로운 AI 파이프라인 실행만 횟수 차감

**전환 경로**: 하이브리드 → 이메일 전용은 코드 2곳만 수정. 유료 티어 연동은 동일한 게이트에 결제 확인 추가.

---

## 산출물

| # | 모듈 | 상태 | 유형 | 예상 시간 |
|---|------|------|------|-----------|
| 1 | DB 스키마 (trial_users + email_verification) | 🔲 | 백엔드 | 0.5h |
| 2 | 이메일 발송 모듈 (플러그인, 콘솔 기본) | 🔲 | 백엔드 | 0.5h |
| 3 | 트라이얼 서비스 (핵심 비즈니스 로직) | 🔲 | 백엔드 | 2h |
| 4 | 트라이얼 API 라우터 (status, request-code, verify) | 🔲 | 백엔드 | 1h |
| 5 | 분석 엔드포인트 트라이얼 게이트 | 🔲 | 백엔드 | 1h |
| 6 | 기기 ID + 트라이얼 API 클라이언트 (프론트엔드) | 🔲 | 프론트엔드 | 1h |
| 7 | useTrial 훅 | 🔲 | 프론트엔드 | 1h |
| 8 | useAnalysis 훅 수정 | 🔲 | 프론트엔드 | 1h |
| 9 | TrialBanner 컴포넌트 | 🔲 | 프론트엔드 | 1h |
| 10 | EmailRegistrationModal 컴포넌트 | 🔲 | 프론트엔드 | 2h |
| 11 | TrialLimitModal 컴포넌트 | 🔲 | 프론트엔드 | 1h |
| 12 | 기존 컴포넌트 연결 (Sidebar, AiAnalysisInline, QuickLook) | 🔲 | 프론트엔드 | 1h |
| 13 | 통합 테스트 + QA | 🔲 | 공통 | 1.5h |

**총 예상: ~14.5시간**

---

## 1. DB 스키마

### 목적

SQLite에 기기별 사용량 추적과 이메일 인증 코드 관리를 위한 테이블 2개 추가.

### 구현 파일

| 파일 | 변경 |
|------|------|
| `data/database.py` | `CREATE_TABLES_SQL`에 `trial_users` + `email_verification` 테이블 추가 |

### 스키마

```sql
CREATE TABLE IF NOT EXISTS trial_users (
    device_id TEXT PRIMARY KEY,
    email TEXT UNIQUE,
    email_verified INTEGER DEFAULT 0,
    usage_count INTEGER DEFAULT 0,
    max_usage INTEGER DEFAULT 3,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS email_verification (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    device_id TEXT NOT NULL,
    email TEXT NOT NULL,
    code TEXT NOT NULL,
    attempts INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP NOT NULL,
    FOREIGN KEY (device_id) REFERENCES trial_users(device_id)
);
```

### 설계 결정 사항

- `usage_count`는 **누적(lifetime)** — 기존 `utils/usage_tracker.py`의 글로벌 일일 100회 제한과 독립적
- `email UNIQUE` 제약으로 하나의 이메일이 여러 기기에서 +3 보너스 받는 것 방지
- `max_usage` 기본값 3 (익명), 이메일 인증 시 6으로 업데이트
- `CREATE TABLE IF NOT EXISTS` 패턴 사용 — 마이그레이션 불필요, `init_db()` 호출 시 자동 생성

---

## 2. 이메일 발송 모듈 (플러그인)

### 목적

개발 시 콘솔 출력, 배포 시 SMTP 전환 가능한 이메일 발송 모듈.

### 구현 파일

| 파일 | 변경 |
|------|------|
| `services/email_sender.py` | **신규** — `send_verification_email(email, code) → bool` |

### 핵심 로직

- `EMAIL_BACKEND` 환경변수: `"console"` (기본값) 또는 `"smtp"`
- 콘솔 모드: 6자리 코드를 stdout에 출력
- SMTP 모드: `SMTP_HOST`, `SMTP_PORT`, `SMTP_USER`, `SMTP_PASS` 환경변수 사용

---

## 3. 트라이얼 서비스

### 목적

무료체험 사용자 관리, 사용량 추적, 이메일 인증의 핵심 비즈니스 로직.

### 구현 파일

| 파일 | 변경 |
|------|------|
| `services/trial_service.py` | **신규** — 트라이얼 라이프사이클 관리 함수 5개 |

### 함수 목록

| 함수 | 역할 |
|------|------|
| `get_or_create_user(device_id)` | 유저 조회/생성. `INSERT OR IGNORE` 패턴으로 동시성 안전 |
| `check_and_increment_usage(device_id)` | 원자적 체크+증가: `UPDATE ... WHERE usage_count < max_usage` |
| `request_verification(device_id, email)` | 6자리 코드 생성, DB 저장, email_sender로 발송. 10분 만료 |
| `verify_code(device_id, email, code)` | 코드 검증, 성공 시 `max_usage=6` 설정. 코드당 최대 3회 오입력 |
| `get_trial_status(device_id)` | 읽기 전용 상태: usage_count, max_usage, remaining, tier |

### 동시성 안전

- `UPDATE trial_users SET usage_count = usage_count + 1 WHERE device_id = ? AND usage_count < max_usage`는 SQLite WAL 모드에서 원자적
- `INSERT OR IGNORE`로 첫 사용자 생성 시 레이스 컨디션 처리

---

## 4. 트라이얼 API 라우터

### 목적

무료체험 상태 확인, 이메일 인증 코드 요청, 코드 검증을 위한 REST 엔드포인트.

### 구현 파일

| 파일 | 변경 |
|------|------|
| `backend/routers/trial.py` | **신규** — 엔드포인트 3개 |
| `backend/main.py` | trial 라우터 import + 등록 추가 |

### 엔드포인트

| 엔드포인트 | 메서드 | 설명 |
|------------|--------|------|
| `/api/trial/status` | GET | 기기의 현재 무료체험 상태 조회 |
| `/api/trial/request-code` | POST | 이메일로 인증 코드 발송 |
| `/api/trial/verify` | POST | 6자리 인증 코드 검증 |

모든 엔드포인트에서 `X-Device-Id` 헤더 필수 (FastAPI `Header(...)` 자동 추출).

---

## 5. 분석 엔드포인트 트라이얼 게이트

### 목적

분석 엔드포인트의 캐시 조회와 AI 파이프라인 실행 사이에 트라이얼 사용량 체크 삽입.

### 구현 파일

| 파일 | 변경 |
|------|------|
| `backend/routers/analysis.py` | `X-Device-Id` 헤더 파라미터 + 트라이얼 게이트 로직 추가 |

### 수정된 흐름

```
이전: 캐시 확인 → 데이터 수집 → AI 파이프라인 → 캐시 저장
이후: 캐시 확인 → [트라이얼 게이트] → 데이터 수집 → AI 파이프라인 → 캐시 저장
```

- 캐시 히트는 게이트 이전에 리턴 — **무료, 횟수 차감 없음**
- `X-Device-Id`는 `Optional[str]`로 하위 호환 (이메일 전용 전환 시 필수로 변경)
- 한도 초과 시 HTTP 429: `{ error: "trial_limit_reached", usage_count, max_usage, email_registered }`
- 분석 성공 시 응답에 `trial_status` 포함

---

## 6. 프론트엔드 — 기기 ID + 트라이얼 API 클라이언트

### 목적

고유 기기 식별자 생성/저장 + 트라이얼 엔드포인트용 타입드 API 함수 제공.

### 구현 파일

| 파일 | 변경 |
|------|------|
| `frontend/src/services/deviceId.ts` | **신규** — `getDeviceId()`: `crypto.randomUUID()` + localStorage |
| `frontend/src/services/trialApi.ts` | **신규** — `fetchTrialStatus()`, `requestVerificationCode()`, `verifyEmailCode()` |

### 기기 ID 전략

- `crypto.randomUUID()` (모든 모던 브라우저 지원)
- localStorage `quantai_device_id` 키에 저장
- 모든 트라이얼 API 호출에 `X-Device-Id` 헤더 자동 첨부

---

## 7. useTrial 훅

### 목적

분석 완료 시 자동 갱신되는 트라이얼 상태 관리 React 훅.

### 구현 파일

| 파일 | 변경 |
|------|------|
| `frontend/src/hooks/useTrial.ts` | **신규** — 트라이얼 상태 관리 훅 |

### 핵심 동작

- 마운트 시 `GET /api/trial/status` 호출
- `trial-status-changed` CustomEvent 리스닝 (분석 성공 시 dispatch됨)
- 리턴: `{ status, loading, refreshStatus }`

---

## 8. useAnalysis 훅 수정

### 목적

기존 분석 훅에 기기 식별 헤더 + 트라이얼 한도 처리 추가.

### 구현 파일

| 파일 | 변경 |
|------|------|
| `frontend/src/hooks/useAnalysis.ts` | X-Device-Id 헤더, 429 처리, 이벤트 dispatch 추가 |

### 변경사항

1. **Line 35**: fetch 호출에 `headers: { 'X-Device-Id': getDeviceId() }` 추가
2. **새 상태**: `trialBlocked` — HTTP 429 + `trial_limit_reached` 시 설정
3. **성공 후**: `trial-status-changed` CustomEvent dispatch
4. **리턴값**: `trialBlocked` 추가

---

## 9. TrialBanner 컴포넌트

### 목적

사이드바에 잔여 무료체험 횟수와 이메일 등록 안내를 표시.

### 구현 파일

| 파일 | 변경 |
|------|------|
| `frontend/src/components/TrialBanner.tsx` | **신규** — 트라이얼 상태 표시 |
| `frontend/src/components/Sidebar.tsx` | 하드코딩된 "AI USAGE 0/100" (lines 154-187) → `<TrialBanner />` 교체 |

### UI 명세

- "FREE TRIAL" 라벨 (xs, muted 텍스트)
- 잔여 횟수 (numeric 폰트, accent 색상, 예: "2/3 remaining")
- 4px 프로그레스바 (theme.accent 채움)
- 익명 티어: "이메일 등록하면 +3회" 링크 → EmailRegistrationModal 열기
- 이메일 티어: 체크마크 + "Email verified" 텍스트

---

## 10. EmailRegistrationModal 컴포넌트

### 목적

이메일 등록 및 인증 코드 입력을 위한 2단계 모달.

### 구현 파일

| 파일 | 변경 |
|------|------|
| `frontend/src/components/EmailRegistrationModal.tsx` | **신규** — 이메일 인증 플로우 모달 |

### UI 플로우

**1단계 — 이메일 입력:**
- 제목: "Get 3 More Free Analyses"
- 이메일 입력 필드
- "Send Code" 버튼

**2단계 — 코드 입력:**
- 제목: "Enter Verification Code"
- 6자리 코드 입력 (숫자, 가운데 정렬)
- "Verify" 버튼
- "코드 재발송" 링크 (60초 쿨다운 타이머)
- 오류/만료 코드 에러 표시

### 모달 패턴

- Fixed overlay `rgba(0,0,0,0.5)`, zIndex: 500
- `theme.bg_card`로 카드 중앙 배치
- 외부 클릭 시 닫기 (stopPropagation)
- 기존 AlertModal/AddStockModal 패턴 준수

---

## 11. TrialLimitModal 컴포넌트

### 목적

분석 시 HTTP 429 응답(트라이얼 한도 도달) 시 표시되는 모달. 등록 상태에 따라 2가지 변형.

### 구현 파일

| 파일 | 변경 |
|------|------|
| `frontend/src/components/TrialLimitModal.tsx` | **신규** — 한도 도달 모달 |

### 변형

**변형 A — 익명 (email_registered = false):**
- "Free Trial Limit Reached"
- "이메일 등록하면 3회 더!"
- [이메일 등록] 버튼 → EmailRegistrationModal 열기
- [나중에] 버튼 → 닫기

**변형 B — 이메일 유저 (email_registered = true):**
- "Trial Limit Reached"
- "6회 무료 체험을 모두 사용했습니다. 프리미엄 플랜 준비 중입니다."
- [확인] 버튼 → 닫기

---

## 12. 기존 컴포넌트 연결

### 목적

트라이얼 상태와 모달을 기존 컴포넌트에 연결.

### 구현 파일

| 파일 | 변경 |
|------|------|
| `frontend/src/components/AiAnalysisInline.tsx` | `trialBlocked` prop 추가, 블록 시 TrialLimitModal 표시 |
| `frontend/src/pages/QuickLook.tsx` | useAnalysis에서 `trialBlocked` 받아서 AiAnalysisInline에 전달 |

### AiAnalysisInline 변경

- 새 `trialBlocked` prop 수용
- `trialBlocked` 설정 시 TrialLimitModal 렌더링
- 재분석 confirm 메시지 (line 82) 트라이얼 잔여 횟수 반영

### QuickLook 변경

- `useAnalysis` 훅에서 `trialBlocked` 구조 분해 (line 31)
- `<AiAnalysisInline trialBlocked={...} />`로 전달 (line 108)

---

## 엣지 케이스 & 안전장치

| 시나리오 | 처리 |
|----------|------|
| localStorage 초기화 | 새 UUID 생성, 새 3회 체험. 동일 이메일 재인증 불가 (UNIQUE) |
| 동시 분석 요청 | 원자적 `UPDATE WHERE usage_count < max_usage` — 하나 성공, 나머지 429 |
| 글로벌 100/일 한도 도달 | 트라이얼 횟수 소비되나 AI 파이프라인 일일 한도 에러 반환 |
| 다른 기기에서 동일 이메일 | `request_verification` 거부: "이 이메일은 이미 등록되어 있습니다" |
| 인증 코드 무차별 대입 | 코드당 최대 3회 시도, 10분 만료 (6자리 = 100만 경우의 수) |
| 코드 스팸 | 기기당 10분 내 최대 3개 활성 코드 |

---

## 전환 경로

### 하이브리드 → 이메일 전용 (코드 2곳 수정)

1. `backend/routers/analysis.py`: `x_device_id: Optional[str] = Header(None)` → `x_device_id: str = Header(...)`
2. `check_and_increment_usage`에 체크 추가: `email_verified == 0`이면 `allowed: false, reason: "email_required"` 반환

### 이메일 전용 → 유료 티어 (향후)

- `trial_users`에 `tier` 컬럼 추가 (`free`, `premium`)
- 티어 업그레이드 전 결제 확인 단계 추가
- 프리미엄 사용자 `max_usage` 무제한(또는 고수치) 설정

---

## 구현 순서

```
백엔드 (독립적, 먼저 테스트 가능):
  1. data/database.py          — 스키마 기반
  2. services/email_sender.py  — 의존성 없음
  3. services/trial_service.py — database 의존
  4. backend/routers/trial.py  — trial_service 의존
  5. backend/main.py           — 라우터 등록
  6. backend/routers/analysis.py — 트라이얼 게이트 삽입

프론트엔드 (백엔드 완성 후):
  7. frontend/src/services/deviceId.ts   — 의존성 없음
  8. frontend/src/services/trialApi.ts   — deviceId 의존
  9. frontend/src/hooks/useTrial.ts      — trialApi 의존
  10. frontend/src/hooks/useAnalysis.ts  — deviceId 의존
  11. frontend/src/components/TrialBanner.tsx
  12. frontend/src/components/EmailRegistrationModal.tsx
  13. frontend/src/components/TrialLimitModal.tsx
  14. frontend/src/components/Sidebar.tsx — TrialBanner 교체
  15. frontend/src/components/AiAnalysisInline.tsx — 모달 연결
  16. frontend/src/pages/QuickLook.tsx    — prop 전달
```

---

## 파일 요약

### 신규 파일 (9개)

| 파일 | 용도 |
|------|------|
| `services/email_sender.py` | 플러그인 이메일 발송 (콘솔/SMTP) |
| `services/trial_service.py` | 핵심 트라이얼 비즈니스 로직 |
| `backend/routers/trial.py` | 트라이얼 API 엔드포인트 |
| `frontend/src/services/deviceId.ts` | 기기 ID 생성 + 저장 |
| `frontend/src/services/trialApi.ts` | 트라이얼 API 클라이언트 |
| `frontend/src/hooks/useTrial.ts` | 트라이얼 상태 관리 훅 |
| `frontend/src/components/TrialBanner.tsx` | 사이드바 트라이얼 배너 |
| `frontend/src/components/EmailRegistrationModal.tsx` | 이메일 인증 모달 |
| `frontend/src/components/TrialLimitModal.tsx` | 한도 도달 모달 |

### 수정 파일 (7개)

| 파일 | 변경 |
|------|------|
| `data/database.py` | CREATE_TABLES_SQL에 테이블 2개 추가 |
| `backend/main.py` | trial 라우터 import + 등록 |
| `backend/routers/analysis.py` | X-Device-Id 헤더 + 트라이얼 게이트 |
| `frontend/src/hooks/useAnalysis.ts` | 기기 헤더 + 429 처리 |
| `frontend/src/components/Sidebar.tsx` | AI USAGE → TrialBanner 교체 |
| `frontend/src/components/AiAnalysisInline.tsx` | trialBlocked + 모달 연결 |
| `frontend/src/pages/QuickLook.tsx` | trialBlocked prop 전달 |

---

## 검증

### 백엔드 테스트

1. **단위 테스트**: trial_service 함수별 (유저 생성, 증가, 한도, 코드 검증)
2. **API 테스트**: `curl -H "X-Device-Id: test-uuid" http://localhost:8000/api/trial/status`
3. **429 테스트**: 3회 소진 후 4번째 요청 → 429 + 상세 바디 확인
4. **캐시 우회 테스트**: 캐시된 분석은 usage_count 미증가 확인

### 프론트엔드 수동 테스트

1. 새 브라우저 → 분석 실행 → TrialBanner "2/3 remaining" 확인
2. 3회 분석 → TrialLimitModal + "이메일 등록" 옵션 표시
3. 이메일 인증 완료 → TrialBanner "3/6 remaining" 업데이트
4. 3회 추가 분석 → TrialLimitModal "체험 종료" 표시 (이메일 옵션 없음)
5. localStorage 초기화 → 새 기기 ID → "3/3 remaining" 초기화
6. 동일 이메일 재등록 시도 → 에러 메시지

---

## 변경 이력

| 날짜 | 변경 | 작성자 |
|------|------|--------|
| 2026-05-16 | 문서 신규 작성 — 초기 계획 (Phase 15로) | AI |
| 2026-05-16 | Phase 15 → Phase 14로 번호 변경 (i18n과 교체) | AI |

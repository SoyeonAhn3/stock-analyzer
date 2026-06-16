# Phase 14 — Free Trial (Google Login Gate) System `🔶 In Progress (Implemented, Manual QA Pending)`

> Google-login-gated free trial: AI analysis requires sign-in, granting **3 free analyses per account**. Other features (quotes, charts, sectors, compare) remain open. The wallet/ledger/hold core is reused as-is for the future paid tier.

**Status**: 🔶 In Progress — Backend + Frontend ✅ Implemented (2026-06-16) · Browser manual QA 🔲 Pending
**Prerequisites**: Phase 13 completed (Portfolio), Phase 13.5 completed (Portfolio Auth)

> **⚠️ Design pivot (decided 2026-06-15) — Email verification → Google login**
> The original design was a hybrid "anonymous 3 + email-verified +3 (6 total)". It is replaced by:
> - **Auth method**: 6-digit email code → **Google OAuth login** (no SMTP/code sending, simpler UX, direct path to the V2-2 paid account)
> - **Free grant**: anonymous 3 + email 3 = 6 → **3 on login**
> - **Gate scope**: not the whole app → login is required **only when clicking "AI 분석"**. Quotes, charts, sectors, and compare stay usable without login
> - **Identity**: `X-Device-Id` (localStorage UUID) → **Google `sub` (verified ID token)**. The wallet/ledger/hold core is reused unchanged; only the identity key value is swapped
> - **UI**: no "n left" next to the analyze button (shown only in the sidebar banner)
> - **Removed**: email sender (`email_sender.py`), the `email_verification` table, and the `/trial/request-code`·`/trial/verify` endpoints
> - Corporate-network blocking is out of scope here (Google reachability assumed)
>
> **⚠️ Design note (decided 2026-06-09 — still valid)**: This Phase is implemented as a **"credit wallet + transaction ledger + reserve-commit (hold) pattern"**, not a simple counter. Free credits are the wallet's initial balance. **Real payment (PG) / prepaid credit sales are split into [`BACKLOG.md` V2-2](../BACKLOG.md)** — designed so the wallet built here only needs a "top-up" action added. Billing model: 1 AI analysis = 1 credit (same for portfolio / single stock / multi-compare); cache hits are free.

---

## Overview

The app has no per-user tracking — all API endpoints are public with only a global 100/day AI call limit. This Phase introduces a **Google-login-gated** free trial:

1. **Open features**: Quotes, charts, sector screening, compare — usable without login (unchanged)
2. **Gated feature**: Clicking "AI 분석" requires Google sign-in; each account gets **3 free analyses**
3. **Cache hits are free**: Only fresh AI pipeline executions count toward the trial limit

**Identity**: A Google ID token (`Authorization: Bearer <token>`) is verified server-side; the token's `sub` keys the credit wallet. Because `sub` is signed by Google, it cannot be forged — and unlike a device UUID, **clearing localStorage and re-logging-in returns the same wallet** (credits do not reset).

**Migration path**: Free → Paid (V2-2) adds a `topup` ledger type to the same wallet — no redesign.

---

## Deliverables

| # | Module | Status | Type | Est. Hours |
|---|---|---|---|---|
| 1 | DB Schema (wallets + ledger) — `email_verification` unused | ✅ | backend | 0.5h |
| 2 | Trial Service (wallet/ledger/hold core) — email functions removed | ✅ | backend | 2h |
| 3 | Trial API Router — only `/trial/status` (request-code/verify removed) | ✅ | backend | 0.5h |
| 4 | Analysis Trial Gate — `X-Device-Id` → verified Google `sub`, always gated | ✅ | backend | 1h |
| 5 | Backend Google Token Verify (`backend/auth.py`, `google-auth`) | ✅ | backend | 1.5h |
| 6 | Frontend Auth — `@react-oauth/google` + `GoogleOAuthProvider` + `useAuth` | ✅ | frontend | 2h |
| 7 | useAnalysis Hook — `Authorization` header + 429 → `trialBlocked` | ✅ | frontend | 1h |
| 8 | LoginButton Component | ✅ | frontend | 0.5h |
| 9 | TrialBanner Component (remaining + user + logout, replaces Sidebar AI USAGE) | ✅ | frontend | 1h |
| 10 | TrialLimitModal Component (single variant: "3 used up, premium coming") | ✅ | frontend | 0.5h |
| 11 | Gate Wiring (AiAnalysisInline two buttons: login-first when signed out) | ✅ | frontend | 1h |
| 12 | Integration Test + QA | 🔶 | general | 1.5h |

**Total: ~13 hours** · Backend (#1–5) ✅ + Frontend (#6–11) ✅ Done (2026-06-16) · #12 manual browser QA pending

### Implementation status (as of 2026-06-16)

**✅ Backend done (PHASE A — Google login pivot)**
- `data/database.py` — `wallets` / `ledger` tables (wallet/ledger reused, no schema change)
- `services/trial_service.py` — `reserve`/`commit`/`release`/`get_status` (hold pattern). Email functions (`request_verification`/`verify_code`), the `email_sender` import, `EMAIL_BONUS`, and code constants all removed; `_status_dict` → `{balance, held, available}`; the identity key (`device_id` column) now stores the Google `sub`; `INITIAL_CREDITS=3`
- `backend/auth.py` (new) — Google ID token verification via `google-auth`. `verify_google_token()` + FastAPI dependency `get_current_user()` (Bearer header → `sub`/`email`/`name`/`picture`; 401 on missing/malformed/invalid). `GOOGLE_CLIENT_ID` env for audience check
- `backend/routers/analysis.py` — `user = Depends(get_current_user)`, **always gated** (login required), `sub`-based reserve/commit/release, cache hits free
- `backend/routers/trial.py` — `request-code`/`verify` removed, only token-based `/trial/status`
- `requirements.txt` — `google-auth>=2.28.0` · `.env.example` — `GOOGLE_CLIENT_ID` / `VITE_GOOGLE_CLIENT_ID`
- `tests/test_phase14_trial.py` (new) — wallet reserve/commit/release/429/idempotency/account-isolation + `get_current_user` 401 paths: **12 tests pass**

**✅ Frontend done (PHASE B — 2026-06-16)**
- `@react-oauth/google` installed; `App.tsx` wrapped in `<GoogleOAuthProvider>` + `<AuthProvider>`
- `frontend/src/config.ts` — `GOOGLE_CLIENT_ID` export
- `frontend/src/auth/AuthProvider.tsx` (new) — `AuthProvider` + `useAuth`; stores the Google ID token in localStorage, decodes the JWT payload for display, drops expired tokens
- `frontend/src/components/LoginButton.tsx` (new) — `@react-oauth/google` `<GoogleLogin>` wrapper (theme-aware)
- `frontend/src/components/TrialBanner.tsx` (new) — sidebar: login CTA when signed out; user + remaining count + progress bar + logout when signed in; fetches `/trial/status` and refreshes on the `trial-changed` event
- `frontend/src/components/TrialLimitModal.tsx` (new) — single-variant modal on HTTP 429 (AlertModal pattern)
- `frontend/src/hooks/useAnalysis.ts` — `Authorization: Bearer` + `X-Request-Id` (`crypto.randomUUID`), 429 → `trialBlocked`, 401 → session-expired error, dispatches `trial-changed` on success; returns `trialBlocked`/`clearTrialBlocked`
- `frontend/src/components/Sidebar.tsx` — hardcoded "AI USAGE 0/100" → `<TrialBanner />`
- `frontend/src/components/AiAnalysisInline.tsx` — `useAuth` gate (both buttons login-first when signed out), `TrialLimitModal` on `trialBlocked`, re-analyze confirm reworded to "uses 1 free analysis"
- `frontend/src/pages/QuickLook.tsx` — passes `trialBlocked` / `onClearTrialBlocked`
- Verified: `tsc -b` type-check + `vite build` (80 modules) pass; backend live check — `/trial/status` & `POST /analysis` return 401 without/with-invalid token

**🔲 Remaining — manual browser QA (#12)**
- Sign in with Google → run analysis → banner shows remaining → exhaust 3 → TrialLimitModal → re-login same account keeps credits

**🗑️ Removed (transitioned to unused)** — `services/email_sender.py` (**deleted** 2026-06-16), `email_verification` table (kept in schema, unused)

**🔑 Prerequisite ✅ Done**: Google Cloud OAuth client ID issued → `.env` `GOOGLE_CLIENT_ID` + `frontend/.env` `VITE_GOOGLE_CLIENT_ID` set

---

## Architecture / Data Flow

```
Frontend (signed in with Google)
  → POST /api/analysis/{ticker}
     Authorization: Bearer <Google ID token>
     X-Request-Id: <uuid>   (idempotency key)
        │
        ▼
  get_current_user  ── verify token ──► sub  (401 if invalid/missing)
        │
        ▼
  Cache hit? ── yes ──► return (free, no credit)
        │ no
        ▼
  reserve_credit(sub, ref_id)
        │   no credit → HTTP 429 {error:"trial_limit_reached", available:0, ...}
        ▼
  run 5-agent pipeline
        ├─ exception / all agents fail → release_credit (refund)
        └─ success → save cache → commit_credit (balance-1)
        ▼
  response { ...analysis, wallet:{balance,held,available} }
```

---

## 1. DB Schema

### Purpose
Per-account credit **wallet** + an append-only **ledger** (audit trail of every credit movement). Both already exist from the 2026-06-09 build and are reused unchanged. The `device_id` column is kept as the primary key but now holds the Google `sub` — no migration needed.

### Files
| File | Change |
|------|--------|
| `data/database.py` | `wallets` + `ledger` tables in `CREATE_TABLES_SQL` (already present). `email_verification` table kept but unused. |

### Schema
```sql
-- Per-account credit wallet (one row per Google sub). available = balance - held
CREATE TABLE IF NOT EXISTS wallets (
    device_id TEXT PRIMARY KEY,        -- holds the verified Google sub
    balance INTEGER DEFAULT 3,         -- granted credits (3 on first login)
    held INTEGER DEFAULT 0,            -- credits locked during in-flight analysis
    email TEXT UNIQUE,                 -- legacy column (unused after pivot)
    email_verified INTEGER DEFAULT 0,  -- legacy column (unused after pivot)
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Append-only audit trail of every credit movement
CREATE TABLE IF NOT EXISTS ledger (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    device_id TEXT NOT NULL,
    type TEXT NOT NULL CHECK(type IN ('grant','hold','commit','release','topup')),
    amount INTEGER NOT NULL,           -- signed delta (+3 grant, +1 hold, -1 commit/release)
    ref_id TEXT,                       -- idempotency key (one per analysis request)
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (device_id) REFERENCES wallets(device_id)
);

CREATE INDEX IF NOT EXISTS idx_ledger_ref_id ON ledger(ref_id);
CREATE INDEX IF NOT EXISTS idx_ledger_device_id ON ledger(device_id);
```

### Key formula
**Available credits = `balance - held`** — held credits are excluded from what can be spent. This one formula drives the gate.

### Design decisions
- Credits are **lifetime** (not daily) — independent of the global 100/day limit in `utils/usage_tracker.py`
- **Wallet + ledger instead of one counter**: the ledger proves "charged but no result" disputes — mandatory once credits become money in V2-2
- `balance` + `held` enable the **reserve → commit/release** pattern — concurrency-safe and refund-safe
- `ref_id` = **idempotency key**: a retried request with the same ref_id is never charged twice
- **Paid extension (V2-2)**: add a `topup` ledger type doing `balance += purchased` — no redesign

---

## 2. Trial Service

### Purpose
Core wallet lifecycle: reserve → commit/release with idempotency. No email logic.

### Files
| File | Change |
|------|--------|
| `services/trial_service.py` | Wallet lifecycle functions. `INITIAL_CREDITS=3`. |

### Functions
| Function | Role |
|----------|------|
| `get_or_create_user(sub)` | Lookup/create wallet. `INSERT OR IGNORE`, initial `balance=3` + a `grant` ledger row |
| `get_status(sub)` | Read-only status: `{balance, held, available}` |
| `reserve_credit(sub, ref_id)` | **Atomic hold**: `UPDATE wallets SET held = held + 1 WHERE device_id = ? AND (balance - held) >= 1`. 0 rows → no credit. Writes a `hold` row. Idempotent on `ref_id` |
| `commit_credit(sub, ref_id)` | **On success**: `balance = balance - 1, held = held - 1`. Writes a `commit` row |
| `release_credit(sub, ref_id)` | **On failure (refund)**: `held = held - 1`. Writes a `release` row |

### Concurrency & idempotency
- `UPDATE ... WHERE (balance - held) >= 1` is **atomic** in SQLite WAL — concurrent requests can never oversell
- `INSERT OR IGNORE` handles first-time wallet creation races
- Each ledger write checks for an existing row with the same `(sub, ref_id, type)` first → retries reuse the existing hold/commit/release instead of double-acting

---

## 3. Backend Google Token Verify

### Purpose
Verify the Google ID token sent by the frontend and expose the verified identity as a FastAPI dependency. Replaces the old email-sender module.

### Files
| File | Change |
|------|--------|
| `backend/auth.py` | **New** — `verify_google_token()` + `get_current_user()` dependency |

### Core logic
```python
GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID", "")  # audience; None skips check (dev only)

def verify_google_token(token: str) -> dict:
    info = id_token.verify_oauth2_token(token, _transport, GOOGLE_CLIENT_ID or None)
    return {"sub": info["sub"], "email": info.get("email"),
            "name": info.get("name"), "picture": info.get("picture")}

def get_current_user(authorization: Optional[str] = Header(None)) -> dict:
    # "Bearer <token>" → verify → user dict; else HTTPException(401)
```

### Design decisions
| Decision | Choice | Reason |
|----------|--------|--------|
| Token delivery | `Authorization: Bearer` header | HTTP standard |
| Verification | `google-auth` `verify_oauth2_token` | Validates Google signature + expiry + audience |
| Missing/invalid token | HTTP 401 | Frontend prompts login |
| `GOOGLE_CLIENT_ID` unset | audience check skipped (dev) | Production must set it |

---

## 4. Trial API Router

### Purpose
Expose only the wallet status. Reserve/commit/release are internal to the analysis endpoint, not user-callable.

### Files
| File | Change |
|------|--------|
| `backend/routers/trial.py` | `/trial/status` only (request-code/verify removed) |
| `backend/main.py` | trial router registered (already present) |

### Endpoints
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/trial/status` | GET | Wallet status for the logged-in account (`Depends(get_current_user)` → `get_status(sub)`) |

---

## 5. Analysis Endpoint Trial Gate

### Purpose
Require login and run the reserve → commit/release flow around the AI pipeline.

### Files
| File | Change |
|------|--------|
| `backend/routers/analysis.py` | `user = Depends(get_current_user)` + gate logic |

### Flow (reserve → run → commit/release)
```
Login required (get_current_user) → Cache check (free) → reserve →
    success: commit → save cache
    hard failure / exception: release (refund)
```
- **Cache hits return before reserve** — free (login still required to reach the endpoint)
- `reserve_credit` fails → HTTP 429 `{error:"trial_limit_reached", reason:"no_credit", balance, held, available}`
- **Hard failure** (all agents fail / exception / timeout) → `release_credit` (refund). **Partial success** (1–2 agents fail, result produced) → `commit_credit`
- `X-Request-Id` = idempotency key; auto-generated if absent
- The success response includes `wallet` (`balance`, `held`, `available`)

---

## 6. Frontend — Auth (`useAuth`)

### Purpose
Sign in with Google, persist the ID token, and expose user/auth state.

### Files
| File | Change |
|------|--------|
| `frontend/package.json` | Add `@react-oauth/google` |
| `frontend/src/main.tsx` (or `App.tsx`) | Wrap app in `<GoogleOAuthProvider clientId={VITE_GOOGLE_CLIENT_ID}>` |
| `frontend/src/hooks/useAuth.ts` | **New** — token + user state, login/logout, localStorage persistence |

### Behavior
- On Google login success, store the ID token (localStorage `quantai_token`) + decoded profile
- Expose `{ user, token, isLoggedIn, login, logout }`
- Token attached to API calls as `Authorization: Bearer <token>`

---

## 7. useAnalysis Hook

### Files
| File | Change |
|------|--------|
| `frontend/src/hooks/useAnalysis.ts` | Add `Authorization` header, 429 handling, `trialBlocked` state |

### Changes
1. Add `headers: { Authorization: 'Bearer ' + token, 'X-Request-Id': uuid }`
2. New state `trialBlocked` — set on HTTP 429 `trial_limit_reached`
3. After success, refresh trial status (banner)
4. Return `trialBlocked`

---

## 8. LoginButton + TrialBanner

### Files
| File | Change |
|------|--------|
| `frontend/src/components/LoginButton.tsx` | **New** — Google login/logout button |
| `frontend/src/components/TrialBanner.tsx` | **New** — sidebar widget |
| `frontend/src/components/Sidebar.tsx` | Replace hardcoded "AI USAGE 0/100" with `<TrialBanner />` |

### TrialBanner spec
- Signed out: "Sign in for 3 free AI analyses" + LoginButton
- Signed in: user name/email + remaining count (e.g., "2/3 remaining") + 4px progress bar + logout

---

## 9. TrialLimitModal

### Files
| File | Change |
|------|--------|
| `frontend/src/components/TrialLimitModal.tsx` | **New** — shown on HTTP 429 |

### Single variant
- "Free Trial Limit Reached"
- "You've used all 3 free analyses. Premium plans coming soon."
- [Got it] → closes
- Follows the existing AlertModal/AddStockModal pattern (fixed overlay, centered card, click-outside dismiss)

---

## 10. Gate Wiring (AiAnalysisInline)

### Files
| File | Change |
|------|--------|
| `frontend/src/components/AiAnalysisInline.tsx` | Login-first on the two analyze buttons; show TrialLimitModal on `trialBlocked` |
| `frontend/src/pages/QuickLook.tsx` | Pass `trialBlocked` from `useAnalysis` |

### Behavior
- If signed out, clicking "AI 분석" / "Re-analyze" opens the login flow instead of calling the API
- If signed in but out of credits (429), render TrialLimitModal

---

## Edge Cases & Safety

| Scenario | Handling |
|----------|----------|
| Not logged in | `get_current_user` → 401; frontend prompts Google login |
| localStorage cleared | Re-login with the same Google account → **same `sub` → same wallet** (credits not reset) |
| Cache hit | Free — returns before reserve (login still required to reach the endpoint) |
| Concurrent analysis requests | Atomic `UPDATE ... WHERE (balance - held) >= 1` — no oversell; surplus get 429 |
| Hard pipeline failure | `release_credit` refunds the hold — credit not lost |
| Retry / double-submit | Same `ref_id` reuses the hold → charged once (idempotent) |
| Global 100/day cap hit | Hold already placed → treated as hard failure → `release` (refund). V2-2 replaces the cap with a high-threshold circuit breaker |
| Invalid / expired token | `verify_oauth2_token` raises → 401 |

---

## Migration Paths

### Free → Paid Tier (V2-2, see [`BACKLOG.md`](../BACKLOG.md))
- Add a `topup` ledger type — payment webhook → `balance += purchased`. **No wallet/ledger redesign**
- Replace the global 100/day hard cap (`utils/usage_tracker.py`) with a **high-threshold circuit breaker** (paid users never blocked)
- The reserve → commit/release flow and idempotency are reused unchanged for paid credits

---

## Implementation Order

```
PHASE A — Backend (✅ done, Client ID not required):
  1. services/trial_service.py   — remove email logic, sub-keyed wallet
  2. backend/auth.py             — Google token verify + get_current_user
  3. backend/routers/analysis.py — Depends(get_current_user), always gated
  4. backend/routers/trial.py    — /trial/status only
  5. tests/test_phase14_trial.py — unit tests (12 pass)

PHASE B — Frontend (after Google Client ID issued):
  6. @react-oauth/google + GoogleOAuthProvider
  7. useAuth hook
  8. useAnalysis — Authorization header + 429
  9. LoginButton + TrialBanner (Sidebar swap) + TrialLimitModal
 10. Gate wiring (AiAnalysisInline)

PHASE C — Integration Test + QA
```

---

## File Summary

### New Files
| File | Purpose | Status |
|------|---------|--------|
| `backend/auth.py` | Google ID token verification + dependency | ✅ |
| `tests/test_phase14_trial.py` | Wallet + auth unit tests | ✅ |
| `frontend/src/auth/AuthProvider.tsx` | `AuthProvider` + `useAuth` (Google auth state) | ✅ |
| `frontend/src/components/LoginButton.tsx` | Google login/logout button | ✅ |
| `frontend/src/components/TrialBanner.tsx` | Sidebar trial banner | ✅ |
| `frontend/src/components/TrialLimitModal.tsx` | Limit-reached modal | ✅ |

### Modified Files
| File | Change | Status |
|------|--------|--------|
| `services/trial_service.py` | Email logic removed, sub-keyed wallet | ✅ |
| `backend/routers/analysis.py` | Login-required gate, sub-based reserve/commit/release | ✅ |
| `backend/routers/trial.py` | `/trial/status` only | ✅ |
| `requirements.txt` | `google-auth>=2.28.0` | ✅ |
| `.env.example` | `GOOGLE_CLIENT_ID` / `VITE_GOOGLE_CLIENT_ID` | ✅ |
| `frontend/src/config.ts` | `GOOGLE_CLIENT_ID` export | ✅ |
| `frontend/src/App.tsx` | `GoogleOAuthProvider` + `AuthProvider` wrap | ✅ |
| `frontend/src/hooks/useAnalysis.ts` | Auth header + 429 handling | ✅ |
| `frontend/src/components/Sidebar.tsx` | Replace AI USAGE with TrialBanner | ✅ |
| `frontend/src/components/AiAnalysisInline.tsx` | Gate wiring + modal | ✅ |
| `frontend/src/pages/QuickLook.tsx` | Pass `trialBlocked` | ✅ |

### Deleted Files
| File | Reason |
|------|--------|
| `services/email_sender.py` | Dead code after pivot (no imports) — deleted 2026-06-16 |

---

## Verification

### Backend (✅ done)
1. **Unit tests** (`tests/test_phase14_trial.py`): create wallet, reserve/commit/release, refund on failure, 429 on exhaustion, idempotency, account isolation, `get_current_user` 401 paths — **12 pass**
2. **Import check**: `from backend.main import app` loads clean; only `/api/trial/status` exposed
3. **Manual** (after Client ID): `curl -H "Authorization: Bearer <token>" http://localhost:8001/api/trial/status`

### Frontend (✅ built — `tsc -b` + `vite build` pass)
1. Signed out → "AI 분석" opens Google login *(manual QA pending)*
2. Signed in → run analysis → TrialBanner shows "2/3 left" *(manual QA pending)*
3. Use 3 → TrialLimitModal "premium coming soon" *(manual QA pending)*
4. Clear localStorage → re-login same account → credits unchanged (same `sub`) *(manual QA pending)*

---

## Change Log

| Date | Change | Author |
|------|--------|--------|
| 2026-05-16 | Document created — initial planning (as Phase 15) | AI |
| 2026-05-16 | Renumbered from Phase 15 → Phase 14 (swapped with i18n) | AI |
| 2026-06-09 | Redesigned to **wallet + ledger + reserve/commit (hold)** pattern; payment split to BACKLOG V2-2; global daily cap → circuit breaker on paid migration | AI |
| 2026-06-15 | Pivoted email-code verification → **Google OAuth login**; free grant 6→3; gate scoped to "AI 분석" click (login required) | AI |
| 2026-06-16 | **PHASE A backend pivot done** — new `backend/auth.py`, trial_service email logic removed, analysis/trial routers switched to verified `sub`, 12 unit tests pass | AI |
| 2026-06-16 | Deleted dead `services/email_sender.py`; **full bilingual doc rewrite** to the post-pivot design (detailed sections §1–10 resynced EN/KR) | AI |
| 2026-06-16 | **PHASE B frontend done** — `@react-oauth/google` + `AuthProvider`/`useAuth`/`LoginButton`/`TrialBanner`/`TrialLimitModal`, useAnalysis auth+429, Sidebar/AiAnalysisInline gate wiring; build passes; Google Client ID configured. #12 manual QA pending | AI |

---
---

# Phase 14 — 무료체험 (Google 로그인 게이트) 시스템 `🔶 진행 중 (구현 완료, 수동 QA 대기)`

> Google 로그인 게이트 무료체험: AI 분석은 로그인이 필요하며 **계정당 무료 3회**를 제공한다. 그 외 기능(시세·차트·섹터·비교)은 비로그인 사용을 유지한다. 지갑/원장/hold 코어는 향후 유료 티어를 위해 그대로 재사용한다.

**상태**: 🔶 진행 중 — 백엔드 + 프론트엔드 ✅ 구현 완료 (2026-06-16) · 브라우저 수동 QA 🔲 대기
**선행 조건**: Phase 13 완료 (포트폴리오), Phase 13.5 완료 (포트폴리오 인증)

> **⚠️ 설계 피벗 (2026-06-15 결정) — 이메일 인증 → Google 로그인**
> 당초 "익명 3회 + 이메일 인증 +3회(총 6회)" 하이브리드였으나 아래로 변경한다:
> - **인증 방식**: 이메일 6자리 코드 → **Google OAuth 로그인** (SMTP/코드발송 불필요, UX 단순, V2-2 유료계정으로 직결)
> - **무료 제공량**: 익명3+이메일3=6회 → **로그인 시 3회**
> - **게이트 범위**: 앱 전체 아님 → **"AI 분석" 클릭 시에만** 로그인 요구. 시세·차트·섹터·비교는 비로그인 유지
> - **신원 식별**: `X-Device-Id`(localStorage UUID) → **Google `sub`(검증된 ID 토큰)**. 지갑/원장/hold 코어는 그대로, 신원 키 값만 교체
> - **UI**: 분석 버튼 옆 "n회 남음" 미표시 (사이드바 배너에만 노출)
> - **폐기**: 이메일 발송기(`email_sender.py`), `email_verification` 테이블, `/trial/request-code`·`/trial/verify` 엔드포인트
> - 사내망 차단 환경은 이번 범위 제외 (Google 접속 전제)
>
> **⚠️ 설계 노트 (2026-06-09 결정 — 유효)**: 단순 카운터가 아니라 **"크레딧 지갑 + 거래 원장 + 예약-확정(hold) 패턴"**으로 구현한다. 무료 크레딧은 지갑의 초기 잔액이다. **실제 결제(PG)·선불 크레딧 판매는 [`BACKLOG.md` V2-2](../BACKLOG.md)로 분리** — 지갑에 "충전" 동작만 얹는 형태로 설계. 과금: AI 분석 1회 = 1크레딧(포트폴리오/개별주/다중비교 공통), 캐시 히트 무차감.

---

## 개요

현재 앱은 사용자별 추적이 없다 — 모든 엔드포인트가 공개이고 글로벌 일일 100회 제한만 있다. 이 Phase는 **Google 로그인 게이트** 무료체험을 도입한다:

1. **공개 기능**: 시세·차트·섹터 스크리닝·비교 — 비로그인 사용 (그대로)
2. **게이트 기능**: "AI 분석" 클릭 시 Google 로그인 필요, 계정당 **무료 3회**
3. **캐시 결과는 무료**: 새 AI 파이프라인 실행만 횟수 차감

**신원**: Google ID 토큰(`Authorization: Bearer <token>`)을 서버에서 검증하고, 토큰의 `sub`가 지갑 키가 된다. `sub`는 구글이 서명해 위조 불가하며, 기기 UUID와 달리 **localStorage를 지우고 다시 로그인해도 같은 지갑**을 돌려준다(크레딧 초기화 안 됨).

**전환 경로**: 무료 → 유료(V2-2)는 같은 지갑에 `topup` 원장 타입만 추가 — 재설계 없음.

---

## 산출물

| # | 모듈 | 상태 | 유형 | 예상 |
|---|------|------|------|------|
| 1 | DB 스키마 (wallets + ledger) — `email_verification` 미사용 | ✅ | 백엔드 | 0.5h |
| 2 | 트라이얼 서비스 (지갑/원장/hold 코어) — 이메일 함수 제거 | ✅ | 백엔드 | 2h |
| 3 | 트라이얼 API 라우터 — `/trial/status`만 (request-code/verify 제거) | ✅ | 백엔드 | 0.5h |
| 4 | 분석 게이트 — `X-Device-Id` → 검증된 Google `sub`, 상시 적용 | ✅ | 백엔드 | 1h |
| 5 | 백엔드 Google 토큰 검증 (`backend/auth.py`, `google-auth`) | ✅ | 백엔드 | 1.5h |
| 6 | 프론트 Auth — `@react-oauth/google` + `GoogleOAuthProvider` + `useAuth` | ✅ | 프론트 | 2h |
| 7 | useAnalysis 훅 — `Authorization` 헤더 + 429 → `trialBlocked` | ✅ | 프론트 | 1h |
| 8 | LoginButton 컴포넌트 | ✅ | 프론트 | 0.5h |
| 9 | TrialBanner 컴포넌트 (잔여 + 유저 + 로그아웃, Sidebar 교체) | ✅ | 프론트 | 1h |
| 10 | TrialLimitModal 컴포넌트 (단일 변형 "3회 소진, 프리미엄 준비중") | ✅ | 프론트 | 0.5h |
| 11 | 게이트 와이어링 (AiAnalysisInline 두 버튼: 비로그인 시 로그인 우선) | ✅ | 프론트 | 1h |
| 12 | 통합 테스트 + QA | 🔶 | 공통 | 1.5h |

**총 ~13시간** · 백엔드(#1~5) ✅ + 프론트(#6~11) ✅ 완료 (2026-06-16) · #12 브라우저 수동 QA 대기

### 구현 현황 (2026-06-16 기준)

**✅ 백엔드 완료 (PHASE A — Google 로그인 피벗)**
- `data/database.py` — `wallets` / `ledger` 테이블 (지갑/원장 그대로 재사용, 스키마 무변경)
- `services/trial_service.py` — `reserve`/`commit`/`release`/`get_status` (hold 패턴). 이메일 함수(`request_verification`/`verify_code`)·`email_sender` import·`EMAIL_BONUS`·코드 상수 전부 제거, `_status_dict` → `{balance, held, available}`, 신원 키(`device_id` 컬럼)에 Google `sub` 저장, `INITIAL_CREDITS=3`
- `backend/auth.py` (신규) — `google-auth`로 Google ID 토큰 검증. `verify_google_token()` + FastAPI 의존성 `get_current_user()` (Bearer 헤더 → `sub`/`email`/`name`/`picture`, 누락·형식오류·검증실패 시 401). `GOOGLE_CLIENT_ID` env로 audience 검증
- `backend/routers/analysis.py` — `user = Depends(get_current_user)`, 게이트 **상시 적용**(로그인 필수), `sub` 기반 reserve/commit/release, 캐시 히트 무차감
- `backend/routers/trial.py` — `request-code`/`verify` 제거, 토큰 기반 `/trial/status`만
- `requirements.txt` — `google-auth>=2.28.0` · `.env.example` — `GOOGLE_CLIENT_ID` / `VITE_GOOGLE_CLIENT_ID`
- `tests/test_phase14_trial.py` (신규) — 지갑 reserve/commit/release/429/멱등성/계정격리 + `get_current_user` 401 경로 **12개 통과**

**✅ 프론트엔드 완료 (PHASE B — 2026-06-16)**
- `@react-oauth/google` 설치; `App.tsx`를 `<GoogleOAuthProvider>` + `<AuthProvider>`로 래핑
- `frontend/src/config.ts` — `GOOGLE_CLIENT_ID` export
- `frontend/src/auth/AuthProvider.tsx` (신규) — `AuthProvider` + `useAuth`; Google ID 토큰 localStorage 보관, JWT payload 디코드(표시용), 만료 토큰 자동 제거
- `frontend/src/components/LoginButton.tsx` (신규) — `@react-oauth/google` `<GoogleLogin>` 래퍼 (테마 연동)
- `frontend/src/components/TrialBanner.tsx` (신규) — 사이드바: 비로그인 시 로그인 CTA, 로그인 시 유저+잔여횟수+프로그레스바+로그아웃, `/trial/status` fetch + `trial-changed` 이벤트 갱신
- `frontend/src/components/TrialLimitModal.tsx` (신규) — HTTP 429 시 단일 변형 모달 (AlertModal 패턴)
- `frontend/src/hooks/useAnalysis.ts` — `Authorization: Bearer` + `X-Request-Id`(`crypto.randomUUID`), 429→`trialBlocked`, 401→세션만료 에러, 성공 시 `trial-changed` dispatch, `trialBlocked`/`clearTrialBlocked` 반환
- `frontend/src/components/Sidebar.tsx` — 하드코딩 "AI USAGE 0/100" → `<TrialBanner />`
- `frontend/src/components/AiAnalysisInline.tsx` — `useAuth` 게이트(비로그인 시 두 버튼 로그인 우선), `trialBlocked` 시 `TrialLimitModal`, 재분석 confirm "무료 분석 1회 사용"으로
- `frontend/src/pages/QuickLook.tsx` — `trialBlocked` / `onClearTrialBlocked` 전달
- 검증: `tsc -b` 타입체크 + `vite build`(80 모듈) 통과; 백엔드 라이브 — `/trial/status`·`POST /analysis` 토큰 없음/잘못된 토큰 모두 401

**🔲 남은 작업 — 브라우저 수동 QA (#12)**
- Google 로그인 → 분석 실행 → 배너 잔여 표시 → 3회 소진 → TrialLimitModal → 같은 계정 재로그인 시 크레딧 유지

**🗑️ 폐기 (미사용 전환)** — `services/email_sender.py` (**삭제 완료** 2026-06-16), `email_verification` 테이블 (스키마 잔존·미사용)

**🔑 선행 ✅ 완료**: Google Cloud OAuth 클라이언트 ID 발급 → `.env` `GOOGLE_CLIENT_ID` + `frontend/.env` `VITE_GOOGLE_CLIENT_ID` 설정 완료

---

## 아키텍처 / 데이터 흐름

```
프론트엔드 (Google 로그인 상태)
  → POST /api/analysis/{ticker}
     Authorization: Bearer <Google ID 토큰>
     X-Request-Id: <uuid>   (멱등성 키)
        │
        ▼
  get_current_user  ── 토큰 검증 ──► sub  (무효/누락 시 401)
        │
        ▼
  캐시 히트? ── 예 ──► 반환 (무료, 무차감)
        │ 아니오
        ▼
  reserve_credit(sub, ref_id)
        │   크레딧 없음 → HTTP 429 {error:"trial_limit_reached", available:0, ...}
        ▼
  5-Agent 파이프라인 실행
        ├─ 예외 / 전 에이전트 실패 → release_credit (환불)
        └─ 성공 → 캐시 저장 → commit_credit (balance-1)
        ▼
  응답 { ...분석결과, wallet:{balance,held,available} }
```

---

## 1. DB 스키마

### 목적
계정별 크레딧 **지갑** + 추가 전용 **원장**(모든 크레딧 이동 감사). 둘 다 2026-06-09 구축분을 그대로 재사용한다. `device_id` 컬럼은 PK로 유지하되 이제 Google `sub`를 담는다 — 마이그레이션 불필요.

### 파일
| 파일 | 변경 |
|------|------|
| `data/database.py` | `wallets` + `ledger` 테이블 (이미 존재). `email_verification`은 유지하되 미사용 |

### 스키마
```sql
-- 계정별 크레딧 지갑 (Google sub당 1줄). 사용가능 = balance - held
CREATE TABLE IF NOT EXISTS wallets (
    device_id TEXT PRIMARY KEY,        -- 검증된 Google sub 저장
    balance INTEGER DEFAULT 3,         -- 보유 크레딧 (첫 로그인 시 3)
    held INTEGER DEFAULT 0,            -- 분석 진행 중 잠긴 크레딧
    email TEXT UNIQUE,                 -- 레거시 컬럼 (피벗 후 미사용)
    email_verified INTEGER DEFAULT 0,  -- 레거시 컬럼 (피벗 후 미사용)
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS ledger (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    device_id TEXT NOT NULL,
    type TEXT NOT NULL CHECK(type IN ('grant','hold','commit','release','topup')),
    amount INTEGER NOT NULL,           -- 부호 있는 증감 (+3 지급, +1 예약, -1 확정/환불)
    ref_id TEXT,                       -- 멱등성 키 (분석 요청당 1개)
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (device_id) REFERENCES wallets(device_id)
);

CREATE INDEX IF NOT EXISTS idx_ledger_ref_id ON ledger(ref_id);
CREATE INDEX IF NOT EXISTS idx_ledger_device_id ON ledger(device_id);
```

### 핵심 공식
**사용 가능 크레딧 = `balance - held`** — 잠긴 크레딧은 쓸 수 있는 양에서 제외. 이 공식 하나가 게이트를 움직인다.

### 설계 결정
- 크레딧은 **누적(lifetime)** — 글로벌 일일 100회와 독립
- **단일 카운터 대신 지갑+원장**: "차감됐는데 결과 없음" 분쟁 증명 — V2-2에서 필수
- `balance`+`held`로 **예약 → 확정/환불** 패턴 — 동시성·환불 안전
- `ref_id` = **멱등성 키**: 같은 ref_id 재시도는 두 번 차감 안 됨
- **유료 확장(V2-2)**: `topup` 원장 타입으로 `balance += 구매량` — 재설계 없음

---

## 2. 트라이얼 서비스

### 목적
지갑 라이프사이클: 예약 → 확정/환불 + 멱등성. 이메일 로직 없음.

### 파일
| 파일 | 변경 |
|------|------|
| `services/trial_service.py` | 지갑 라이프사이클 함수. `INITIAL_CREDITS=3` |

### 함수
| 함수 | 역할 |
|------|------|
| `get_or_create_user(sub)` | 지갑 조회/생성. `INSERT OR IGNORE`, 초기 `balance=3` + `grant` 원장 |
| `get_status(sub)` | 읽기 전용 상태: `{balance, held, available}` |
| `reserve_credit(sub, ref_id)` | **원자적 예약**: `UPDATE wallets SET held = held + 1 WHERE device_id = ? AND (balance - held) >= 1`. 0행 → 크레딧 없음. `hold` 원장. `ref_id` 멱등 |
| `commit_credit(sub, ref_id)` | **성공 시**: `balance-1, held-1`. `commit` 원장 |
| `release_credit(sub, ref_id)` | **실패 시(환불)**: `held-1`. `release` 원장 |

### 동시성 & 멱등성
- `UPDATE ... WHERE (balance - held) >= 1`는 SQLite WAL에서 **원자적** — 동시 요청 초과 사용 불가
- `INSERT OR IGNORE`로 첫 지갑 생성 레이스 처리
- 각 원장 기록 전에 같은 `(sub, ref_id, type)` 존재 여부를 먼저 확인 → 재시도는 기존 hold/commit/release 재사용

---

## 3. 백엔드 Google 토큰 검증

### 목적
프론트가 보낸 Google ID 토큰을 서버에서 검증하고, 검증된 신원을 FastAPI 의존성으로 노출. 구 이메일 발송 모듈을 대체.

### 파일
| 파일 | 변경 |
|------|------|
| `backend/auth.py` | **신규** — `verify_google_token()` + `get_current_user()` 의존성 |

### 핵심 로직
```python
GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID", "")  # audience; None이면 검증 생략(개발용)

def verify_google_token(token: str) -> dict:
    info = id_token.verify_oauth2_token(token, _transport, GOOGLE_CLIENT_ID or None)
    return {"sub": info["sub"], "email": info.get("email"),
            "name": info.get("name"), "picture": info.get("picture")}

def get_current_user(authorization: Optional[str] = Header(None)) -> dict:
    # "Bearer <token>" → 검증 → 유저 dict; 아니면 HTTPException(401)
```

### 설계 결정
| 결정 | 선택 | 이유 |
|------|------|------|
| 토큰 전달 | `Authorization: Bearer` 헤더 | HTTP 표준 |
| 검증 | `google-auth` `verify_oauth2_token` | 구글 서명 + 만료 + audience 검증 |
| 누락/무효 토큰 | HTTP 401 | 프론트가 로그인 유도 |
| `GOOGLE_CLIENT_ID` 미설정 | audience 검증 생략(개발) | 운영은 반드시 설정 |

---

## 4. 트라이얼 API 라우터

### 목적
지갑 상태만 노출. 예약/확정/환불은 분석 엔드포인트 내부 처리이며 사용자가 직접 호출하지 않는다.

### 파일
| 파일 | 변경 |
|------|------|
| `backend/routers/trial.py` | `/trial/status`만 (request-code/verify 제거) |
| `backend/main.py` | trial 라우터 등록 (이미 존재) |

### 엔드포인트
| 엔드포인트 | 메서드 | 설명 |
|------------|--------|------|
| `/api/trial/status` | GET | 로그인 계정의 지갑 상태 (`Depends(get_current_user)` → `get_status(sub)`) |

---

## 5. 분석 엔드포인트 트라이얼 게이트

### 목적
로그인 필수 + AI 파이프라인 주위에 예약 → 확정/환불 흐름 적용.

### 파일
| 파일 | 변경 |
|------|------|
| `backend/routers/analysis.py` | `user = Depends(get_current_user)` + 게이트 로직 |

### 흐름 (예약 → 실행 → 확정/환불)
```
로그인 필수 (get_current_user) → 캐시 확인(무료) → 예약 →
    성공: 확정(commit) → 캐시 저장
    하드 실패/예외: 환불(release)
```
- **캐시 히트는 예약 이전 반환** — 무료 (엔드포인트 도달엔 로그인 필요)
- `reserve_credit` 실패 → HTTP 429 `{error:"trial_limit_reached", reason:"no_credit", balance, held, available}`
- **하드 실패**(전 에이전트 실패/예외/타임아웃) → `release_credit`(환불). **부분 성공**(1~2개 실패해도 결과 생성) → `commit_credit`
- `X-Request-Id` = 멱등성 키, 없으면 자동 생성
- 성공 응답에 `wallet`(`balance`, `held`, `available`) 포함

---

## 6. 프론트엔드 — Auth (`useAuth`)

### 목적
Google 로그인, ID 토큰 영속, 유저/인증 상태 노출.

### 파일
| 파일 | 변경 |
|------|------|
| `frontend/package.json` | `@react-oauth/google` 추가 |
| `frontend/src/main.tsx` (또는 `App.tsx`) | `<GoogleOAuthProvider clientId={VITE_GOOGLE_CLIENT_ID}>`로 앱 래핑 |
| `frontend/src/hooks/useAuth.ts` | **신규** — 토큰+유저 상태, login/logout, localStorage 영속 |

### 동작
- Google 로그인 성공 시 ID 토큰(localStorage `quantai_token`) + 프로필 저장
- `{ user, token, isLoggedIn, login, logout }` 노출
- API 호출에 `Authorization: Bearer <token>` 첨부

---

## 7. useAnalysis 훅

### 파일
| 파일 | 변경 |
|------|------|
| `frontend/src/hooks/useAnalysis.ts` | `Authorization` 헤더, 429 처리, `trialBlocked` 상태 |

### 변경
1. `headers: { Authorization: 'Bearer ' + token, 'X-Request-Id': uuid }` 추가
2. 새 상태 `trialBlocked` — HTTP 429 `trial_limit_reached` 시 설정
3. 성공 후 트라이얼 상태 갱신(배너)
4. `trialBlocked` 리턴

---

## 8. LoginButton + TrialBanner

### 파일
| 파일 | 변경 |
|------|------|
| `frontend/src/components/LoginButton.tsx` | **신규** — Google 로그인/로그아웃 버튼 |
| `frontend/src/components/TrialBanner.tsx` | **신규** — 사이드바 위젯 |
| `frontend/src/components/Sidebar.tsx` | 하드코딩 "AI USAGE 0/100" → `<TrialBanner />` 교체 |

### TrialBanner 명세
- 로그아웃 상태: "로그인하고 무료 3회 받기" + LoginButton
- 로그인 상태: 유저 이름/이메일 + 잔여 횟수(예: "2/3 remaining") + 4px 프로그레스바 + 로그아웃

---

## 9. TrialLimitModal

### 파일
| 파일 | 변경 |
|------|------|
| `frontend/src/components/TrialLimitModal.tsx` | **신규** — HTTP 429 시 표시 |

### 단일 변형
- "무료 체험 한도 도달"
- "무료 3회를 모두 사용했습니다. 프리미엄 플랜 준비 중입니다."
- [확인] → 닫기
- 기존 AlertModal/AddStockModal 패턴 준수 (fixed overlay, 중앙 카드, 외부 클릭 닫기)

---

## 10. 게이트 와이어링 (AiAnalysisInline)

### 파일
| 파일 | 변경 |
|------|------|
| `frontend/src/components/AiAnalysisInline.tsx` | 두 분석 버튼 로그인 우선; `trialBlocked` 시 TrialLimitModal |
| `frontend/src/pages/QuickLook.tsx` | `useAnalysis`의 `trialBlocked` 전달 |

### 동작
- 로그아웃 상태에서 "AI 분석"/"재분석" 클릭 시 API 대신 로그인 플로우 오픈
- 로그인했으나 크레딧 소진(429) 시 TrialLimitModal 렌더

---

## 엣지 케이스 & 안전장치

| 시나리오 | 처리 |
|----------|------|
| 비로그인 | `get_current_user` → 401; 프론트가 Google 로그인 유도 |
| localStorage 초기화 | 같은 Google 계정으로 재로그인 → **같은 `sub` → 같은 지갑** (크레딧 초기화 안 됨) |
| 캐시 히트 | 무료 — 예약 이전 반환 (엔드포인트 도달엔 로그인 필요) |
| 동시 분석 요청 | 원자적 `UPDATE ... WHERE (balance - held) >= 1` — 초과 사용 없음, 초과분 429 |
| 하드 파이프라인 실패 | `release_credit`로 환불 — 크레딧 유실 안 됨 |
| 재시도 / 중복 제출 | 같은 `ref_id`로 기존 예약 재사용 → 1회만 차감(멱등) |
| 글로벌 100/일 한도 도달 | 예약 이미 잡힘 → 하드 실패로 간주 → `release`(환불). V2-2에서 고임계 서킷브레이커로 교체 |
| 무효/만료 토큰 | `verify_oauth2_token` 예외 → 401 |

---

## 전환 경로

### 무료 → 유료 티어 (V2-2, [`BACKLOG.md`](../BACKLOG.md) 참조)
- `topup` 원장 타입 추가 — 결제 웹훅 → `balance += 구매량`. **지갑/원장 재설계 없음**
- 글로벌 100/일 하드캡(`utils/usage_tracker.py`)을 **고임계 서킷브레이커**로 교체 (유료 사용자는 안 막힘)
- 예약 → 확정/환불 흐름과 멱등성은 유료 크레딧에도 그대로 재사용

---

## 구현 순서

```
PHASE A — 백엔드 (✅ 완료, Client ID 불필요):
  1. services/trial_service.py   — 이메일 로직 제거, sub 기반 지갑
  2. backend/auth.py             — Google 토큰 검증 + get_current_user
  3. backend/routers/analysis.py — Depends(get_current_user), 상시 게이트
  4. backend/routers/trial.py    — /trial/status만
  5. tests/test_phase14_trial.py — 단위 테스트 (12개 통과)

PHASE B — 프론트엔드 (Google Client ID 발급 후):
  6. @react-oauth/google + GoogleOAuthProvider
  7. useAuth 훅
  8. useAnalysis — Authorization 헤더 + 429
  9. LoginButton + TrialBanner (Sidebar 교체) + TrialLimitModal
 10. 게이트 와이어링 (AiAnalysisInline)

PHASE C — 통합 테스트 + QA
```

---

## 파일 요약

### 신규 파일
| 파일 | 용도 | 상태 |
|------|------|------|
| `backend/auth.py` | Google ID 토큰 검증 + 의존성 | ✅ |
| `tests/test_phase14_trial.py` | 지갑 + 인증 단위 테스트 | ✅ |
| `frontend/src/auth/AuthProvider.tsx` | `AuthProvider` + `useAuth` (Google 인증 상태) | ✅ |
| `frontend/src/components/LoginButton.tsx` | Google 로그인/로그아웃 버튼 | ✅ |
| `frontend/src/components/TrialBanner.tsx` | 사이드바 트라이얼 배너 | ✅ |
| `frontend/src/components/TrialLimitModal.tsx` | 한도 도달 모달 | ✅ |

### 수정 파일
| 파일 | 변경 | 상태 |
|------|------|------|
| `services/trial_service.py` | 이메일 로직 제거, sub 기반 지갑 | ✅ |
| `backend/routers/analysis.py` | 로그인 필수 게이트, sub 기반 예약/확정/환불 | ✅ |
| `backend/routers/trial.py` | `/trial/status`만 | ✅ |
| `requirements.txt` | `google-auth>=2.28.0` | ✅ |
| `.env.example` | `GOOGLE_CLIENT_ID` / `VITE_GOOGLE_CLIENT_ID` | ✅ |
| `frontend/src/config.ts` | `GOOGLE_CLIENT_ID` export | ✅ |
| `frontend/src/App.tsx` | `GoogleOAuthProvider` + `AuthProvider` 래핑 | ✅ |
| `frontend/src/hooks/useAnalysis.ts` | 인증 헤더 + 429 처리 | ✅ |
| `frontend/src/components/Sidebar.tsx` | AI USAGE → TrialBanner 교체 | ✅ |
| `frontend/src/components/AiAnalysisInline.tsx` | 게이트 와이어링 + 모달 | ✅ |
| `frontend/src/pages/QuickLook.tsx` | `trialBlocked` 전달 | ✅ |

### 삭제 파일
| 파일 | 이유 |
|------|------|
| `services/email_sender.py` | 피벗 후 dead code (import 없음) — 2026-06-16 삭제 |

---

## 검증

### 백엔드 (✅ 완료)
1. **단위 테스트** (`tests/test_phase14_trial.py`): 지갑 생성, 예약/확정/환불, 실패 시 환불, 소진 시 429, 멱등성, 계정 격리, `get_current_user` 401 경로 — **12개 통과**
2. **Import 확인**: `from backend.main import app` 클린 로드; `/api/trial/status`만 노출
3. **수동** (Client ID 발급 후): `curl -H "Authorization: Bearer <token>" http://localhost:8001/api/trial/status`

### 프론트엔드 (✅ 빌드 통과 — `tsc -b` + `vite build`)
1. 로그아웃 상태 → "AI 분석" 클릭 시 Google 로그인 오픈 *(수동 QA 대기)*
2. 로그인 → 분석 실행 → TrialBanner "2/3 left" *(수동 QA 대기)*
3. 3회 사용 → TrialLimitModal "프리미엄 준비 중" *(수동 QA 대기)*
4. localStorage 초기화 → 같은 계정 재로그인 → 크레딧 불변 (같은 `sub`) *(수동 QA 대기)*

---

## 변경 이력

| 날짜 | 변경 | 작성자 |
|------|------|--------|
| 2026-05-16 | 문서 신규 작성 — 초기 계획 (Phase 15로) | AI |
| 2026-05-16 | Phase 15 → Phase 14로 번호 변경 (i18n과 교체) | AI |
| 2026-06-09 | **지갑 + 원장 + 예약/확정(hold)** 패턴으로 재설계; 결제는 BACKLOG V2-2로 분리; 유료 전환 시 글로벌 일일 캡 → 서킷브레이커 | AI |
| 2026-06-15 | 이메일 코드 인증 → **Google OAuth 로그인** 피벗; 무료 제공량 6→3; 게이트를 "AI 분석" 클릭 시 로그인 요구로 축소 | AI |
| 2026-06-16 | **PHASE A 백엔드 피벗 완료** — `backend/auth.py` 신규, trial_service 이메일 로직 제거, analysis/trial 라우터 검증된 `sub` 기반 전환, 단위 테스트 12개 통과 | AI |
| 2026-06-16 | dead code `services/email_sender.py` 삭제; **문서 전체 영/한 재작성** (피벗 반영, §1~10 상세 섹션 EN/KR 재동기화) | AI |
| 2026-06-16 | **PHASE B 프론트엔드 완료** — `@react-oauth/google` + `AuthProvider`/`useAuth`/`LoginButton`/`TrialBanner`/`TrialLimitModal`, useAnalysis 인증+429, Sidebar/AiAnalysisInline 게이트 와이어링; 빌드 통과; Google Client ID 설정 완료. #12 수동 QA 대기 | AI |

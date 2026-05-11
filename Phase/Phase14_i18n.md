# Phase 14 — Internationalization (i18n) `🔲 Not Started`

> KO/EN bilingual support — full UI + AI analysis results + guide content language switching

**Status**: 🔲 Not Started
**Prerequisites**: Phase 13 completed (Portfolio)

---

## Overview

The app currently has hardcoded Korean strings in the frontend UI and AI Agent system prompts. This Phase introduces react-i18next-based i18n infrastructure with a global EN/KO toggle button (always visible at top-right), so that UI text, AI analysis results, and Guide educational content all render in the selected language.

**Core principle**: Preserve all existing Korean functionality while adding English. Language preference is stored in localStorage and persists across visits.

---

## Deliverables

| # | Module | Status | Type | Est. Hours |
|---|---|---|---|---|
| 1 | i18n Infrastructure (react-i18next + LangToggle) | 🔲 | general | 2h |
| 2 | Frontend UI Text Translation | 🔲 | project-specific | 3h |
| 3 | AI Agent Prompt Bilingual Support | 🔲 | project-specific | 3h |
| 4 | Guide Content English Translation | 🔲 | project-specific | 3h |
| 5 | Backend Response Message i18n | 🔲 | project-specific | 1h |
| 6 | Integration Test + QA | 🔲 | general | 2h |

**Total: ~14 hours**

---

## 1. i18n Infrastructure

### Purpose

Install react-i18next, create translation JSON files, and add a global EN/KO toggle button that is always visible at the top-right corner of the app.

### Implementation Files

| File | Change |
|------|--------|
| `frontend/package.json` | Add i18next, react-i18next, i18next-browser-languagedetector |
| `frontend/src/i18n/index.ts` | **New** — i18n initialization + config |
| `frontend/src/i18n/ko.json` | **New** — Korean translation key-values |
| `frontend/src/i18n/en.json` | **New** — English translation key-values |
| `frontend/src/main.tsx` | Add `import './i18n'` |
| `frontend/src/components/LangToggle.tsx` | **New** — EN/KO toggle button component |
| `frontend/src/App.tsx` | Place LangToggle in desktop top-right + mobile header |

### Core Structure

```
frontend/src/
├── i18n/
│   ├── index.ts          # i18next init + config
│   ├── ko.json           # Korean translations
│   └── en.json           # English translations
├── components/
│   └── LangToggle.tsx    # Global language toggle button
```

**i18n/index.ts**:
```typescript
import i18n from 'i18next';
import { initReactI18next } from 'react-i18next';
import LanguageDetector from 'i18next-browser-languagedetector';
import ko from './ko.json';
import en from './en.json';

i18n
  .use(LanguageDetector)
  .use(initReactI18next)
  .init({
    resources: { ko: { translation: ko }, en: { translation: en } },
    fallbackLng: 'ko',
    interpolation: { escapeValue: false },
    detection: {
      order: ['localStorage', 'navigator'],
      lookupLocalStorage: 'language',
    },
  });

export default i18n;
```

**LangToggle placement** — always visible at top-right:

Desktop (inside `<main>` area):
```
┌──────────┬──────────────────────────────────────┐
│ Sidebar  │                              [KO|EN] │
│          │   (page content)                      │
└──────────┴──────────────────────────────────────┘
```

Mobile/Tablet (inside existing header bar):
```
┌─────────────────────────────────────────┐
│ ☰  QuantAI                     [KO|EN] │
├─────────────────────────────────────────┤
│   (page content)                         │
└─────────────────────────────────────────┘
```

### Design Decisions

| Decision | Choice | Reason |
|----------|--------|--------|
| i18n library | react-i18next | React ecosystem standard, hook-based API |
| Default language | Korean (ko) | Preserve existing user experience |
| Detection order | localStorage > navigator | Explicit choice first, browser auto-detect as fallback |
| Toggle placement | Global top-right (not Settings) | Always accessible from any page |

---

## 2. Frontend UI Text Translation

### Purpose

Replace ~47 hardcoded Korean strings across 6 frontend files with `t('key')` calls.

### Implementation Files

| File | Korean Strings | Content |
|------|---------------|---------|
| `components/portfolio/PortfolioAnalysis.tsx` | ~31 | Concentration, performance, risk, style analysis labels |
| `pages/Settings.tsx` | ~9 | Sync instructions, success/failure messages |
| `pages/Portfolio.tsx` | ~3 | Empty state text, minimum stock count notice |
| `components/portfolio/AddStockModal.tsx` | ~2 | Validation error, placeholder |
| `components/AiAnalysisInline.tsx` | ~1 | Re-analysis confirmation dialog |
| `pages/SectorScreening.tsx` | ~1 | Theme name placeholder |
| `i18n/ko.json` | — | Add Korean key-values |
| `i18n/en.json` | — | Add English key-values |

### Usage Example

```tsx
// Before
<p>아직 추가된 종목이 없습니다.</p>

// After
const { t } = useTranslation();
<p>{t('portfolio.empty_title')}</p>
```

```json
// ko.json
{ "portfolio": { "empty_title": "아직 추가된 종목이 없습니다." } }

// en.json
{ "portfolio": { "empty_title": "No holdings added yet." } }
```

---

## 3. AI Agent Prompt Bilingual Support

### Purpose

Pass the user's language selection from frontend to backend, and maintain KO/EN prompt dictionaries in each Agent so AI responds in the selected language.

### Implementation Files

| File | Change |
|------|--------|
| `frontend/src/hooks/useApi.ts` | Auto-add `Accept-Language` header to all requests |
| `backend/routers/analysis.py` | Extract lang from header, pass to orchestrator |
| `backend/routers/sector.py` | Extract lang, pass to sector_analyzer |
| `backend/routers/compare.py` | Extract lang, pass to compare_agent |
| `backend/routers/portfolio.py` | Extract lang, pass to portfolio_agent |
| `agents/orchestrator.py` | Propagate `lang` param to all child agents |
| `agents/analyst_agent.py` | `SYSTEM_PROMPTS` KO/EN dictionary (~27 lines each) |
| `agents/news_agent.py` | `SYSTEM_PROMPTS` KO/EN + user message i18n (~20 lines) |
| `agents/data_agent.py` | `SYSTEM_PROMPTS` KO/EN + user message i18n (~26 lines) |
| `agents/macro_agent.py` | `SYSTEM_PROMPTS` KO/EN + user message i18n (~26 lines) |
| `agents/cross_validation.py` | `SYSTEM_PROMPTS` KO/EN dictionary (~25 lines) |
| `agents/sector_analyzer.py` | Prompt builder KO/EN (~37 lines) |
| `agents/compare_agent.py` | same_sector + cross_sector KO/EN (~130 lines) |
| `agents/portfolio_agent.py` | `SYSTEM_PROMPTS` KO/EN + judgment criteria (~59 lines) |

### Core Structure

```python
# agents/analyst_agent.py
SYSTEM_PROMPTS = {
    "ko": """너는 시니어 주식 애널리스트야. ...""",
    "en": """You are a senior stock analyst. ...""",
}

def run(agent_results, cross_validation, lang="ko"):
    prompt = SYSTEM_PROMPTS.get(lang, SYSTEM_PROMPTS["ko"])
    ...
```

### Data Flow

```
Frontend (lang='en')
  → HTTP header: Accept-Language: en
    → Backend router: extract lang
      → orchestrator.run(ticker, lang='en')
        → Each agent receives lang → selects EN prompt
          → Claude responds in English
```

### Design Decisions

| Decision | Choice | Reason |
|----------|--------|--------|
| Language delivery | Accept-Language header | HTTP standard, no extra query param needed |
| Prompt management | Per-language dictionary | Manual curation ensures translation quality over dynamic translation |
| Disclaimer | Language-keyed constant | Legal text must be precise in both languages |

---

## 4. Guide Content English Translation

### Purpose

Translate 7 Guide JSON files (100% Korean educational content) into English, organized by language subdirectories.

### Implementation Files

| File | Change |
|------|--------|
| `config/guide/ko/` | **New directory** — move existing 7 JSON files here |
| `config/guide/en/` | **New directory** — 7 English translation JSON files |
| `backend/routers/guide.py` | Language-based path routing + Korean fallback |
| `data/guide_content.py` | Add language parameter support |

### Core Structure

```
config/guide/
├── ko/                         # Existing files moved here
│   ├── chart_basics.json
│   ├── key_metrics.json
│   ├── technicals.json
│   ├── market_concepts.json
│   ├── investment_styles.json
│   ├── us_market_basics.json
│   └── psychology.json
└── en/                         # New English translations
    ├── chart_basics.json
    ├── key_metrics.json
    ├── technicals.json
    ├── market_concepts.json
    ├── investment_styles.json
    ├── us_market_basics.json
    └── psychology.json
```

### Guide Router Change

```python
# backend/routers/guide.py
@router.get("/api/guide/{category}")
async def get_guide(category: str, request: Request):
    lang = request.headers.get("accept-language", "ko")[:2]
    path = f"config/guide/{lang}/{category}.json"
    if not os.path.exists(path):
        path = f"config/guide/ko/{category}.json"  # fallback
```

### Design Decisions

| Decision | Choice | Reason |
|----------|--------|--------|
| File organization | Language subdirectories | Same JSON structure, path-only branching — simple and extensible |
| Fallback | Korean if EN file missing | Graceful degradation, never show empty content |

---

## 5. Backend Response Message i18n

### Purpose

Translate ~10 user-facing error/status messages in backend routers. Internal logging remains unchanged.

### Implementation Files

| File | Change |
|------|--------|
| `backend/messages.py` | **New** — bilingual message dictionary |
| `backend/routers/portfolio.py` | Error messages → `msg()` calls |
| `backend/routers/sync.py` | Error messages → `msg()` calls |

### Core Structure

```python
# backend/messages.py
MESSAGES = {
    "price_fetch_failed": {
        "ko": "현재가를 조회할 수 없습니다. 잠시 후 재시도해주세요.",
        "en": "Unable to fetch current price. Please try again later.",
    },
    "stock_not_found": {
        "ko": "종목 정보를 찾을 수 없습니다.",
        "en": "Stock not found.",
    },
    "sync_code_not_found": {
        "ko": "동기화 코드를 찾을 수 없습니다.",
        "en": "Sync code not found.",
    },
    "incorrect_pin": {
        "ko": "PIN이 올바르지 않습니다.",
        "en": "Incorrect PIN.",
    },
}

def msg(key: str, lang: str = "ko") -> str:
    return MESSAGES.get(key, {}).get(lang, MESSAGES[key]["ko"])
```

### Design Decisions

| Decision | Choice | Reason |
|----------|--------|--------|
| Implementation | Central dictionary (messages.py) | Only ~10 messages, no need for a full i18n library on backend |

---

## 6. Integration Test + QA

### Purpose

Verify all language switching works correctly across the entire app.

### Test Matrix

| Test Item | Verification |
|-----------|-------------|
| Language toggle | KO↔EN toggle at top-right switches entire UI instantly |
| Language persistence | Selected language survives page refresh (localStorage) |
| AI Analysis (EN) | Deep Analysis → English result output |
| AI Analysis (KO) | Existing Korean analysis still works |
| Portfolio AI | Portfolio analysis → report in selected language |
| Compare AI | Compare analysis → result in selected language |
| Sector AI | Sector screening → AI summary in selected language |
| Guide content | Language switch changes educational content |
| Error messages | Invalid ticker etc. shows error in selected language |
| Mobile | Language toggle works on mobile layout |
| Fallback | Missing EN translation falls back to Korean |

---

## Phase 14 Skill Classification

| Module | Classification | Reason |
|--------|---------------|--------|
| i18n Infrastructure | general | Reusable i18n setup pattern for any React app |
| Frontend UI Translation | project-specific | App-specific UI strings |
| AI Agent Bilingual Prompts | project-specific | Domain-specific financial analysis prompts |
| Guide Content Translation | project-specific | App-specific educational content |
| Backend Message i18n | general | Reusable message dictionary pattern |
| Integration Test | general | Standard i18n QA checklist |

---

## Prerequisites & Dependencies

| Dependency | Required By | Status |
|-----------|-------------|--------|
| Phase 13 (Portfolio) completed | All steps | ✅ |
| npm packages: i18next, react-i18next, i18next-browser-languagedetector | Step 1 | Install needed |
| Existing Agent SYSTEM_PROMPTs in Korean | Step 3 | ✅ Available |
| Existing Guide JSON files in Korean | Step 4 | ✅ Available |

### Implementation Order

```
Step 1 (i18n Infrastructure)
  ↓
Step 2 (Frontend UI) ← requires Step 1
  ↓
Step 3 (AI Agents) ← requires Step 1 language delivery logic
  ↓
Step 4 (Guide Content)  ┐
                         ├── parallel, independent
Step 5 (Backend Messages)┘
  ↓
Step 6 (Integration Test) ← requires all above
```

---

## Development Notes

- Only user-facing strings need translation; internal logs and comments stay as-is
- Agent prompts are manually curated per language (not auto-translated) to ensure financial terminology accuracy
- `fallbackLng: 'ko'` ensures the app never shows blank text if an EN key is missing
- The LangToggle button must be accessible on every page without navigating to Settings

---

## Change Log

| Date | Description |
|------|-------------|
| 2026-05-11 | Phase 14 document created |

---
---

# Phase 14 — 다국어 지원 (i18n) `🔲 미시작`

> 한/영 동시 지원 — UI 전체 + AI 분석 결과 + 교육 콘텐츠 언어 전환

**상태**: 🔲 미시작
**선행 조건**: Phase 13 완료 (Portfolio)

---

## 개요

현재 앱은 프론트엔드 UI와 AI Agent 시스템 프롬프트에 한국어가 하드코딩되어 있다. react-i18next 기반 다국어 인프라를 구축하고, 앱 우상단에 항상 보이는 EN/KO 토글 버튼으로 UI 텍스트 + AI 분석 결과 + Guide 교육 콘텐츠를 선택 언어로 표시한다.

**핵심 원칙**: 기존 한국어 기능은 그대로 유지하면서 영어를 추가한다. 언어 설정은 localStorage에 저장하여 재방문 시 유지.

---

## 완료 예정 / 완료 항목

| # | 모듈 | 상태 | 스킬 타입 | 예상 시간 |
|---|---|---|---|---|
| 1 | i18n 인프라 (react-i18next + LangToggle) | 🔲 | general | 2h |
| 2 | 프론트엔드 UI 텍스트 번역 | 🔲 | project-specific | 3h |
| 3 | AI Agent 프롬프트 다국어 지원 | 🔲 | project-specific | 3h |
| 4 | Guide 교육 콘텐츠 영문 번역 | 🔲 | project-specific | 3h |
| 5 | 백엔드 응답 메시지 다국어 처리 | 🔲 | project-specific | 1h |
| 6 | 통합 테스트 + QA | 🔲 | general | 2h |

**총 예상 소요: ~14시간**

---

## 1. i18n 인프라

### 목적

react-i18next를 설치하고, 번역 JSON 파일을 생성하고, 앱 우상단에 항상 보이는 EN/KO 토글 버튼을 배치한다.

### 구현 파일

| 파일 | 변경 |
|------|------|
| `frontend/package.json` | i18next, react-i18next, i18next-browser-languagedetector 추가 |
| `frontend/src/i18n/index.ts` | **신규** — i18n 초기화 + 설정 |
| `frontend/src/i18n/ko.json` | **신규** — 한국어 번역 키-값 |
| `frontend/src/i18n/en.json` | **신규** — 영어 번역 키-값 |
| `frontend/src/main.tsx` | `import './i18n'` 추가 |
| `frontend/src/components/LangToggle.tsx` | **신규** — EN/KO 토글 버튼 컴포넌트 |
| `frontend/src/App.tsx` | LangToggle을 데스크톱 우상단 + 모바일 헤더에 배치 |

### 핵심 구조

```
frontend/src/
├── i18n/
│   ├── index.ts          # i18next 초기화 + 설정
│   ├── ko.json           # 한국어 번역
│   └── en.json           # 영어 번역
├── components/
│   └── LangToggle.tsx    # 글로벌 언어 전환 버튼
```

**i18n/index.ts**:
```typescript
import i18n from 'i18next';
import { initReactI18next } from 'react-i18next';
import LanguageDetector from 'i18next-browser-languagedetector';
import ko from './ko.json';
import en from './en.json';

i18n
  .use(LanguageDetector)
  .use(initReactI18next)
  .init({
    resources: { ko: { translation: ko }, en: { translation: en } },
    fallbackLng: 'ko',
    interpolation: { escapeValue: false },
    detection: {
      order: ['localStorage', 'navigator'],
      lookupLocalStorage: 'language',
    },
  });

export default i18n;
```

**LangToggle 배치** — 항상 우상단에 표시:

데스크톱 (`<main>` 영역 내):
```
┌──────────┬──────────────────────────────────────┐
│ Sidebar  │                              [KO|EN] │
│          │   (페이지 콘텐츠)                      │
└──────────┴──────────────────────────────────────┘
```

모바일/태블릿 (기존 헤더 바 내):
```
┌─────────────────────────────────────────┐
│ ☰  QuantAI                     [KO|EN] │
├─────────────────────────────────────────┤
│   (페이지 콘텐츠)                         │
└─────────────────────────────────────────┘
```

### 설계 결정 사항

| 결정 | 선택 | 이유 |
|------|------|------|
| i18n 라이브러리 | react-i18next | React 생태계 표준, 훅 기반 사용 편리 |
| 기본 언어 | 한국어 (ko) | 기존 사용자 경험 유지 |
| 언어 감지 | localStorage > navigator | 명시적 선택 우선, 브라우저 언어 자동 감지 fallback |
| 토글 위치 | 글로벌 우상단 (Settings 아님) | 어느 페이지에서든 즉시 접근 가능 |

---

## 2. 프론트엔드 UI 텍스트 번역

### 목적

6개 프론트엔드 파일의 하드코딩된 한국어 문자열 ~47개를 `t('key')` 호출로 교체한다.

### 구현 파일

| 파일 | 한국어 문자열 수 | 주요 내용 |
|------|----------------|----------|
| `components/portfolio/PortfolioAnalysis.tsx` | ~31개 | 집중도, 성과, 위험, 스타일 분석 라벨 |
| `pages/Settings.tsx` | ~9개 | 동기화 안내 문구, 성공/실패 메시지 |
| `pages/Portfolio.tsx` | ~3개 | 빈 상태 안내, 종목 수 부족 안내 |
| `components/portfolio/AddStockModal.tsx` | ~2개 | 유효성 에러, placeholder |
| `components/AiAnalysisInline.tsx` | ~1개 | 재분석 확인 다이얼로그 |
| `pages/SectorScreening.tsx` | ~1개 | 테마 이름 placeholder |
| `i18n/ko.json` | — | 한국어 키-값 추가 |
| `i18n/en.json` | — | 영어 키-값 추가 |

### 사용 예시

```tsx
// Before
<p>아직 추가된 종목이 없습니다.</p>

// After
const { t } = useTranslation();
<p>{t('portfolio.empty_title')}</p>
```

```json
// ko.json
{ "portfolio": { "empty_title": "아직 추가된 종목이 없습니다." } }

// en.json
{ "portfolio": { "empty_title": "No holdings added yet." } }
```

---

## 3. AI Agent 프롬프트 다국어 지원

### 목적

프론트엔드에서 선택한 언어를 백엔드에 전달하고, 각 Agent의 시스템 프롬프트를 한/영 딕셔너리로 관리하여 AI가 선택 언어로 응답하도록 한다.

### 구현 파일

| 파일 | 변경 |
|------|------|
| `frontend/src/hooks/useApi.ts` | 모든 요청에 `Accept-Language` 헤더 자동 추가 |
| `backend/routers/analysis.py` | 헤더에서 lang 추출, orchestrator에 전달 |
| `backend/routers/sector.py` | lang 추출, sector_analyzer에 전달 |
| `backend/routers/compare.py` | lang 추출, compare_agent에 전달 |
| `backend/routers/portfolio.py` | lang 추출, portfolio_agent에 전달 |
| `agents/orchestrator.py` | `lang` 파라미터를 모든 하위 Agent에 전파 |
| `agents/analyst_agent.py` | `SYSTEM_PROMPTS` 한/영 딕셔너리 (~27줄씩) |
| `agents/news_agent.py` | `SYSTEM_PROMPTS` 한/영 + 사용자 메시지 영문화 (~20줄) |
| `agents/data_agent.py` | `SYSTEM_PROMPTS` 한/영 + 사용자 메시지 영문화 (~26줄) |
| `agents/macro_agent.py` | `SYSTEM_PROMPTS` 한/영 + 사용자 메시지 영문화 (~26줄) |
| `agents/cross_validation.py` | `SYSTEM_PROMPTS` 한/영 딕셔너리 (~25줄) |
| `agents/sector_analyzer.py` | 프롬프트 빌더 한/영 (~37줄) |
| `agents/compare_agent.py` | same_sector + cross_sector 한/영 (~130줄) |
| `agents/portfolio_agent.py` | `SYSTEM_PROMPTS` 한/영 + 판단 기준표 (~59줄) |

### 핵심 구조

```python
# agents/analyst_agent.py
SYSTEM_PROMPTS = {
    "ko": """너는 시니어 주식 애널리스트야. ...""",
    "en": """You are a senior stock analyst. ...""",
}

def run(agent_results, cross_validation, lang="ko"):
    prompt = SYSTEM_PROMPTS.get(lang, SYSTEM_PROMPTS["ko"])
    ...
```

### 데이터 흐름

```
Frontend (lang='en')
  → HTTP header: Accept-Language: en
    → Backend router: lang 추출
      → orchestrator.run(ticker, lang='en')
        → 각 Agent가 lang 수신 → EN 프롬프트 선택
          → Claude가 영어로 응답
```

### 설계 결정 사항

| 결정 | 선택 | 이유 |
|------|------|------|
| 언어 전달 | Accept-Language 헤더 | HTTP 표준, 별도 파라미터 불필요 |
| 프롬프트 관리 | 언어별 딕셔너리 | 수동 관리가 금융 용어 번역 품질 보장 |
| 면책 조항 | 언어별 상수 | 법적 문구는 양쪽 언어 모두 정확해야 함 |

---

## 4. Guide 교육 콘텐츠 영문 번역

### 목적

100% 한국어로 된 Guide JSON 파일 7개를 영어로 번역하고, 언어별 서브디렉토리로 분리한다.

### 구현 파일

| 파일 | 변경 |
|------|------|
| `config/guide/ko/` | **신규 디렉토리** — 기존 7개 JSON 이동 |
| `config/guide/en/` | **신규 디렉토리** — 영문 번역 7개 JSON |
| `backend/routers/guide.py` | 언어별 경로 분기 + 한국어 fallback |
| `data/guide_content.py` | 언어 파라미터 지원 |

### 핵심 구조

```
config/guide/
├── ko/                         # 기존 파일 여기로 이동
│   ├── chart_basics.json
│   ├── key_metrics.json
│   ├── technicals.json
│   ├── market_concepts.json
│   ├── investment_styles.json
│   ├── us_market_basics.json
│   └── psychology.json
└── en/                         # 영문 번역 신규 생성
    ├── chart_basics.json
    ├── key_metrics.json
    ├── technicals.json
    ├── market_concepts.json
    ├── investment_styles.json
    ├── us_market_basics.json
    └── psychology.json
```

### Guide 라우터 변경

```python
# backend/routers/guide.py
@router.get("/api/guide/{category}")
async def get_guide(category: str, request: Request):
    lang = request.headers.get("accept-language", "ko")[:2]
    path = f"config/guide/{lang}/{category}.json"
    if not os.path.exists(path):
        path = f"config/guide/ko/{category}.json"  # fallback
```

### 설계 결정 사항

| 결정 | 선택 | 이유 |
|------|------|------|
| 파일 구조 | 언어별 서브디렉토리 | JSON 구조 동일, 경로만 분기 — 단순하고 확장 용이 |
| Fallback | EN 파일 없으면 한국어 | 빈 콘텐츠 방지, graceful degradation |

---

## 5. 백엔드 응답 메시지 다국어 처리

### 목적

사용자에게 노출되는 에러/상태 메시지 ~10개를 다국어 처리한다. 내부 로깅은 변경하지 않는다.

### 구현 파일

| 파일 | 변경 |
|------|------|
| `backend/messages.py` | **신규** — 다국어 메시지 딕셔너리 |
| `backend/routers/portfolio.py` | 에러 메시지 → `msg()` 호출 |
| `backend/routers/sync.py` | 에러 메시지 → `msg()` 호출 |

### 핵심 구조

```python
# backend/messages.py
MESSAGES = {
    "price_fetch_failed": {
        "ko": "현재가를 조회할 수 없습니다. 잠시 후 재시도해주세요.",
        "en": "Unable to fetch current price. Please try again later.",
    },
    "stock_not_found": {
        "ko": "종목 정보를 찾을 수 없습니다.",
        "en": "Stock not found.",
    },
    "sync_code_not_found": {
        "ko": "동기화 코드를 찾을 수 없습니다.",
        "en": "Sync code not found.",
    },
    "incorrect_pin": {
        "ko": "PIN이 올바르지 않습니다.",
        "en": "Incorrect PIN.",
    },
}

def msg(key: str, lang: str = "ko") -> str:
    return MESSAGES.get(key, {}).get(lang, MESSAGES[key]["ko"])
```

### 설계 결정 사항

| 결정 | 선택 | 이유 |
|------|------|------|
| 구현 방식 | 중앙 딕셔너리 (messages.py) | 메시지 ~10개, 백엔드용 별도 i18n 라이브러리 불필요 |

---

## 6. 통합 테스트 + QA

### 목적

전체 앱에서 언어 전환이 정상 동작하는지 검증한다.

### 테스트 매트릭스

| 테스트 항목 | 확인 내용 |
|------------|----------|
| 언어 전환 | 우상단 KO↔EN 토글 시 전체 UI 즉시 반영 |
| 언어 유지 | 페이지 새로고침 후에도 선택 언어 유지 (localStorage) |
| AI 분석 (영어) | Deep Analysis 실행 → 영문 결과 출력 |
| AI 분석 (한국어) | 기존 한국어 분석 기능 정상 유지 |
| Portfolio AI | Portfolio 분석 → 선택 언어로 리포트 출력 |
| Compare AI | 비교 분석 → 선택 언어로 결과 출력 |
| Sector AI | 섹터 스크리닝 → 선택 언어로 AI 축약 분석 |
| Guide 콘텐츠 | 한/영 전환 시 교육 콘텐츠 언어 변경 |
| 에러 메시지 | 잘못된 티커 등 에러 시 선택 언어로 표시 |
| 모바일 | 모바일 레이아웃에서 언어 전환 정상 동작 |
| Fallback | 영문 번역 누락 시 한국어로 fallback |

---

## Phase 14 스킬 범용/전용 분류

| 모듈 | 분류 | 이유 |
|------|------|------|
| i18n 인프라 | general | 모든 React 앱에 재사용 가능한 i18n 셋업 패턴 |
| 프론트엔드 UI 번역 | project-specific | 앱 고유 UI 문자열 |
| AI Agent 다국어 프롬프트 | project-specific | 금융 도메인 특화 분석 프롬프트 |
| Guide 콘텐츠 번역 | project-specific | 앱 고유 교육 콘텐츠 |
| 백엔드 메시지 다국어 | general | 재사용 가능한 메시지 딕셔너리 패턴 |
| 통합 테스트 | general | 표준 i18n QA 체크리스트 |

---

## 선행 조건 및 의존성

| 의존성 | 필요 Step | 상태 |
|--------|----------|------|
| Phase 13 (Portfolio) 완료 | 전체 | ✅ |
| npm 패키지: i18next, react-i18next, i18next-browser-languagedetector | Step 1 | 설치 필요 |
| 기존 Agent SYSTEM_PROMPT (한국어) | Step 3 | ✅ 존재 |
| 기존 Guide JSON 파일 (한국어) | Step 4 | ✅ 존재 |

### 구현 순서

```
Step 1 (i18n 인프라)
  ↓
Step 2 (프론트엔드 UI) ← Step 1 필요
  ↓
Step 3 (AI Agent)      ← Step 1의 언어 전달 로직 필요
  ↓
Step 4 (Guide 콘텐츠)  ┐
                       ├── 병렬 가능, 독립적
Step 5 (백엔드 메시지) ┘
  ↓
Step 6 (통합 테스트)   ← 전체 완료 후
```

---

## 개발 시 주의사항

- 사용자에게 보이는 문자열만 번역 대상. 내부 로그/주석은 그대로 유지
- Agent 프롬프트는 자동 번역이 아닌 수동 작성으로 금융 용어 정확성 확보
- `fallbackLng: 'ko'`로 EN 키 누락 시에도 빈 텍스트 방지
- LangToggle 버튼은 Settings가 아닌 모든 페이지 우상단에 항상 노출

---

## 변경 이력

| 날짜 | 내용 |
|------|------|
| 2026-05-11 | Phase 14 문서 최초 작성 |

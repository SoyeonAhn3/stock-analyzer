# Phase 4 — Sector Screening `✅ 완료`

> 섹터 선택 → 3단계 필터(공통/프리셋/적응형 완화) → AI 축약 분석 → Top 5 추천

**상태**: ✅ 완료
**선행 조건**: Phase 3 완료 (AI 호출 구조 재사용)

---

## 개요

사용자가 GICS 섹터 또는 커스텀 테마를 선택하면, 3단계 필터로 종목을 걸러낸 뒤 AI 축약 분석으로 Top 5를 추천한다. 모든 섹터에 동일 필터를 적용하면 바이오는 전멸하고 빅테크는 전부 통과하므로, 4종 프리셋 + 적응형 완화로 섹터 특성을 반영한다. 커스텀 테마 생성 기능도 포함.

---

## 완료 예정 / 완료 항목

| # | 모듈 | 상태 | 설명 |
|---|---|---|---|
| 1 | `data/sector_data.py` | ✅ | GICS 섹터 종목 조회 (FMP) |
| 2 | `data/theme_manager.py` | ✅ | themes.json CRUD |
| 3 | `data/stock_filter.py` | ✅ | 3단계 필터 (공통 + 프리셋 + 적응형 완화) |
| 4 | `agents/sector_analyzer.py` | ✅ | AI 축약 분석 (10개 → Top 5) |

---

## 섹터 데이터 (sector_data.py)

### 목적
GICS 11개 섹터의 종목 리스트 조회

### 핵심 함수
```python
def get_sector_tickers(sector: str) -> list[str]:
    """FMP Stock Screener API로 섹터별 종목 조회"""

def get_preset_for_sector(sector: str) -> str:
    """GICS 섹터 → 프리셋 매핑"""
    SECTOR_PRESET_MAP = {
        "Information Technology": "large_stable",
        "Financials": "large_stable",
        "Communication Services": "large_stable",
        "Consumer Discretionary": "large_stable",
        "Industrials": "mid_growth",
        "Energy": "mid_growth",
        "Materials": "mid_growth",
        "Consumer Staples": "mid_growth",
        "Health Care": "early_growth",
        "Utilities": "dividend",
        "Real Estate": "dividend",
    }
```

---

## 테마 매니저 (theme_manager.py)

### 목적
themes.json 읽기/쓰기/삭제

### 핵심 함수
```python
def load_themes() -> dict
def create_theme(name: str, tickers: list, preset: str) -> None
def delete_theme(name: str) -> None
```

### 설계 결정 사항
- 티커 최소 5개 강제 (미만이면 ValueError)
- preset은 4종 중 하나만 허용
- themes.json이 없으면 기본 5개 테마로 자동 생성

---

## 3단계 필터 (stock_filter.py)

### 목적
섹터 종목을 걸러내어 AI 분석 대상을 축소

### 핵심 함수
```python
def filter_stocks(tickers: list, preset: str) -> tuple[list, bool, str | None]:
    """
    반환: (필터된 티커 리스트, 완화 적용 여부, 경고 메시지)
    """
```

### 3단계 상세

**1단계 — 공통 필터** (불량 데이터 제거)
- 일평균 거래량 0 제외
- 주요 재무 데이터 누락 제외
- 미국 상장만 (OTC 제외)

**2단계 — 유형별 프리셋** (4종)

| 프리셋 | 시총 | 수익성 | 특수 조건 |
|--------|------|--------|----------|
| `large_stable` | $50B+ | PE 양수 | - |
| `mid_growth` | $10B+ | PE 양수 | - |
| `early_growth` | $2B+ | 무관 | 매출 성장 20%+ |
| `dividend` | $5B+ | PE 양수 | 배당률 2%+ |

**3단계 — 적응형 완화** (통과 종목 수에 따라 자동 조정)

| 통과 수 | 처리 | 완화 |
|---------|------|------|
| 10개+ | 상위 10개 선정 | False |
| 5~9개 | 전부 통과 | False |
| 3~4개 | 시총 기준 1단계 완화 ($50B→$20B, $10B→$5B, $2B→$1B) | True |
| 0~2개 | 필터 무시, 시총 상위 10개 | True + 경고 메시지 |

---

## AI 축약 분석 (sector_analyzer.py)

### 목적
필터 통과 종목(최대 10개)에 대해 축약 AI 분석 → Top 5 선정

### 핵심 함수
```python
def run_sector_screening(sector_or_theme: str) -> dict:
    """
    반환: {
        "sector": "Information Technology",
        "filter_applied": "large_stable",
        "relaxed": False,
        "relaxation_message": None,
        "top5": [
            {"ticker": "LMT", "score": 82, "reason": "NATO 지출 확대 수혜"},
            ...
        ]
    }
    """
```

### 설계 결정 사항
- **일괄 호출**: 10개 종목 데이터를 하나의 프롬프트에 넣어 Claude 1회만 호출
  - 종목별 호출(10회) 대비 API 비용 85% 절감 ($0.90 → $0.15)
  - 일일 한도 소모: 10% → 1%
  - 종목 간 상대 비교가 가능하여 순위 정확도 향상
- max_tokens: 4096 (10개 종목 분석 응답이 잘리지 않도록 확보)
- 프롬프트에 "모든 종목을 동일한 깊이로 분석해" 명시 (후반부 품질 저하 방지)
- 축약 프롬프트: "뉴스 감성(1줄) + 핵심 재무(1줄) + 기술 신호(1줄) + 점수 0~100 + 한 줄 추천 이유"
- 점수 기준 정렬 → Top 5
- 호출 실패 시 1회 재시도 (일괄이므로 실패 시 10개 전부 재시도)

### 리스크 및 대응

| 리스크 | 대응 |
|--------|------|
| 응답 잘림 (JSON 파싱 실패) | max_tokens 4096 확보 + 축약 응답 형식 강제 |
| 후반부 종목 분석 품질 저하 | 프롬프트에 균일 분석 지시 + JSON 형식 강제 |
| 1회 실패 시 10개 전부 날아감 | 재시도 1회 로직 적용 |

---

## 선행 조건 및 의존성

- Phase 3 완료: Claude 호출 구조 (`claude_client.py`) 재사용
- Phase 2 완료: Quick Look 수준의 데이터 수집 함수 재사용
- config/themes.json 존재

---

## 개발 시 주의사항

- FMP 무료 일 250회. 섹터 조회 1회 + 재무 데이터 N회 소모. 테스트 시 과다 호출 주의
- 적응형 완화 시 경고 메시지를 반드시 반환. UI에서 사용자에게 표시해야 함
- themes.json 파일 I/O 동시성 이슈 없음 (Streamlit은 단일 프로세스)

---

## 변경 이력

| 날짜 | 내용 |
|---|---|
| 2026-04-06 | 최초 작성 |
| 2026-04-10 | AI 축약 분석 방식 변경 — 종목별 호출(10회) → 일괄 호출(1회) |
| 2026-04-13 | Phase 4 구현 완료. 4개 모듈 구현, 테스트 PASSED. |
| 2026-04-14 | 문서 상태 ✅ 완료로 업데이트 |

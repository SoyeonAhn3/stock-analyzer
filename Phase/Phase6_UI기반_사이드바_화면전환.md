# Phase 6 — UI 기반 + 사이드바 + 화면 전환 `🔲 미시작`

> CSS 디자인 시스템 구현, 사이드바 완성, Streamlit 화면 전환 로직 연결

**상태**: 🔲 미시작
**선행 조건**: Phase 5 완료 (모든 데이터 로직 pytest 통과)

---

## 개요

UI.txt 디자인 시스템(컬러, 타이포, 간격, 공통 컴포넌트)을 Streamlit custom CSS로 구현한다. 사이드바(검색, 모드 선택, Watchlist, AI 사용량)를 완성하고, Phase 5에서 미뤘던 **화면 전환 로직**(session_state 관리, 모드 분기)을 여기서 구현한다.

---

## 완료 예정 / 완료 항목

| # | 모듈 | 상태 | 설명 |
|---|---|---|---|
| 1 | `app.py` | 🔲 | Streamlit 메인 엔트리 + 모드 라우팅 |
| 2 | `screens/styles.py` | 🔲 | CSS 디자인 시스템 (컬러, 타이포, 컴포넌트) |
| 3 | `screens/sidebar.py` | 🔲 | 사이드바 전체 |
| 4 | `screens/state.py` | 🔲 | session_state 초기화 + 화면 전환 로직 |

---

## CSS 디자인 시스템 (styles.py)

### 목적
UI.txt 1장 + 10장의 디자인 토큰을 CSS 변수로 정의

### 구현 내용
- **컬러**: Primary 파랑 7단계, Neutral 회색 10단계, Semantic(상승/하락/주의)
- **폰트**: DM Sans (Google Fonts), 8단계 크기(10~30px), 4단계 무게
- **공통 컴포넌트**: 카드, 버튼(Primary/Secondary), 태그/뱃지, 구분선, 프로그레스 바, 스피너
- **레이아웃**: 사이드바 224px 고정, 메인 flex:1, 배경 Neutral 50

---

## 사이드바 (sidebar.py)

### 목적
UI.txt 3장 전체 구현

### 구현 내용 (위에서 아래 순서)
1. 로고 + 앱 이름 ("AI Stock Analyzer")
2. 티커 검색창 (Enter로 검색, 유효하지 않으면 힌트)
3. 모드 선택 버튼 5개 (활성/비활성 스타일)
4. "MODE" 라벨
5. Watchlist (등락률 + ±5% 하이라이트, 클릭 → Quick Look)
6. AI 사용량 (프로그레스 바 + 3단계: 정상/근접/도달)
7. 면책 + 지연 표시

---

## 화면 전환 로직 (state.py)

### 목적
Phase 5에서 분리된 session_state 관리 + 모드 라우팅

### 핵심 구조
```python
def init_state():
    """session_state 초기값 설정"""
    defaults = {
        "mode": "overview",       # overview|quick_look|ai_analysis|sector|compare|guide
        "ticker": None,
        "compare_tickers": [],
        "watchlist": [],
        "quick_look_data": None,
        "analysis_state": None,
    }

def route():
    """현재 mode에 따라 해당 screen 함수 호출"""
```

### 화면 전환 매트릭스 (UI.txt 11장)

| 현재 | 행동 | 결과 |
|------|------|------|
| overview | 티커 검색 Enter | quick_look |
| overview | Watchlist 종목 클릭 | quick_look |
| overview | 급등락 종목 클릭 | quick_look |
| overview | Sector 모드 선택 | sector |
| overview | Guide 모드 선택 | guide |
| quick_look | "AI 분석 실행" 클릭 | ai_analysis |
| quick_look | "+ Compare" 클릭 | compare (기준 종목 유지) |
| quick_look | 다른 티커 검색 | 새 quick_look |
| compare | "AI 비교 분석" 클릭 | compare + 결과 |
| compare | 비교 종목 전부 제거 | quick_look 복귀 |
| sector | Top 5 종목 클릭 | quick_look |
| sector | "Compare selected" | compare |

---

## 테스트

Phase 6부터는 **Streamlit 수동 확인**으로 검증.

### 확인 항목
```
□ DM Sans 폰트 적용
□ 컬러 시스템 CSS 변수 전부 정의
□ 카드/버튼/태그 공통 컴포넌트 스타일 적용
□ 사이드바 UI.txt 3장과 동일한 모양
□ 모드 버튼 활성/비활성 전환
□ AI 사용량 0~79: 파랑, 80~99: amber, 100: red
□ Watchlist ±5% 하이라이트
□ 티커 검색 → Quick Look 전환
□ 모든 모드 간 전환 정상 동작
□ Quick Look → + Compare → Compare Mode 전환 (리로드 없음)
□ Compare → 비교 종목 전부 제거 → Quick Look 복귀
```

---

## 선행 조건 및 의존성

- Phase 1~5 전부 완료 (모든 데이터 함수 사용 가능)
- pip: `streamlit`
- UI.txt 참조

---

## 개발 시 주의사항

- Phase 1~5의 순수 함수를 호출하여 화면에 연결. 데이터 로직 수정 금지
- Streamlit session_state 초기화는 app.py 최상단에서 1회만
- st.rerun() 남용 주의 — 무한 루프 가능

---

## 변경 이력

| 날짜 | 내용 |
|---|---|
| 2026-04-06 | 최초 작성 |

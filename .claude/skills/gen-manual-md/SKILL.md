---
name: gen-manual-md
version: 1.1
description: 프로그램의 Markdown 사용자 매뉴얼(.md)을 자동 생성한다. 한국어(기본) 및 영어 지원. /gen-manual-md, "md 매뉴얼 만들어줘", "마크다운 매뉴얼", "markdown manual" 등의 요청 시 트리거한다.
depends_on: []
produces:
  - manuals/YYYYMMDD_프로그램명_매뉴얼.md (한국어)
  - manuals/YYYYMMDD_ProgramName_Manual.md (영어)
references:
  - references/md-template.md   # 출력 MD 골격 템플릿
---

# gen-manual-md Skill

프로그램 정보를 수집하여 Markdown 사용자 매뉴얼(.md)을 생성한다. 외부 의존성 없이 Write만으로 완료.

---

## STEP 1 — 언어 감지 및 프로그램 정보 수집

### 언어 감지

| 감지 키워드 | 설정 |
|---|---|
| (기본, 언어 미지정) | `LANG = ko` |
| "영어로", "English", "in English", "영문" | `LANG = en` |

### 프로그램 정보 수집

사용자 설명 또는 대화 컨텍스트에서 아래 항목 파악 → 바로 STEP 2 진행.

**필수:** 프로그램 이름, 한 줄 설명, 주요 기능 목록(2개+)
**선택:** 버전(기본 v1.0), 대상 사용자, 플랫폼, 사전 요구사항, FAQ, 저장 경로

부족하면 한 번만 질문.

---

## STEP 2 — 섹션 구조 설계

아래 기준으로 포함할 섹션 결정 후 번호를 재조정한다:

| 섹션 | 조건 | i18n (ko → en) |
|---|---|---|
| 표지+메타 | 필수 | — |
| 목차 | 필수 | 목차 → Table of Contents |
| 개요 | 필수 | 개요 → Overview |
| 사전 준비사항 | 요구사항 있을 때 | 사전 준비사항 → Prerequisites |
| 시작하기 | 실행 절차 있을 때 | 시작하기 → Getting Started |
| 주요 기능 | 필수 | 주요 기능 → Key Features |
| 데이터 저장 | 저장 메커니즘 있을 때 | 데이터 저장 방식 → Data Storage |
| 주의사항 | 제약 있을 때 | 주의사항 및 제한사항 → Cautions & Limitations |
| FAQ | Q&A 있을 때 | 문제 해결 (FAQ) → Troubleshooting (FAQ) |

---

## STEP 3 — MD 생성

1. `Read(".claude/skills/gen-manual-md/references/md-template.md")` 로드
2. 템플릿 골격에 수집한 정보를 채워 완성된 MD 텍스트 구성
3. 조건부 섹션은 해당 없으면 통째로 제거, 번호 재조정

---

## STEP 4 — 저장

```
Write("manuals/YYYYMMDD_프로그램명_매뉴얼.md", content)   # 한국어
Write("manuals/YYYYMMDD_ProgramName_Manual.md", content)  # 영어
```

파일명: 공백은 `_` 치환, YYYYMMDD는 오늘 날짜.

---

## STEP 5 — README 매뉴얼 링크 삽입

프로젝트 루트에 README.md가 있으면 `## Overview`와 `## Table of Contents` 사이에 매뉴얼 섹션을 삽입한다.

**삽입 규칙:**
1. README.md를 Read하여 `## Overview` 섹션과 `## Table of Contents` 섹션 존재 확인
2. 두 섹션이 모두 존재하면 → 그 사이에 아래 블록 삽입 (Edit 사용)
3. `## Manual` 섹션이 이미 존재하면 → 테이블에 행만 추가 (중복 삽입 방지)
4. `## Overview` 또는 `## Table of Contents`가 없으면 → 스킵, 결과 출력에서 안내

**삽입 블록 (ko):**
```markdown
## Manual

| 언어 | 링크 |
|---|---|
| 한국어 | [User Manual](./manuals/YYYYMMDD_프로그램명_매뉴얼.md) |
```

**삽입 블록 (en):**
```markdown
## Manual

| Language | Link |
|---|---|
| English | [User Manual](./manuals/YYYYMMDD_ProgramName_Manual.md) |
```

**한국어+영어 모두 있을 경우 행을 합친다.**

---

## STEP 6 — 결과 출력

```
✅ MD 매뉴얼 생성 완료
🌐 언어: 한국어 / English
📁 저장 위치: manuals/YYYYMMDD_xxx.md
📋 포함 섹션: [목록]
📄 주요 기능: N개
📝 README: 매뉴얼 링크 삽입 완료 / 스킵 (사유)
```

---

## 실패 처리

| 실패 유형 | 처리 |
|---|---|
| 정보 부족 | STEP 1 질문 1회 |
| 저장 경로 없음 | manuals/ 디렉토리 생성 후 재시도 |

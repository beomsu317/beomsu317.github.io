# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

Jekyll 기반 Computer Science 논문 리뷰 블로그 — 시스템, 알고리즘, 네트워크, 보안, AI/ML 등 CS 전 분야 논문을 분석하고 리뷰합니다.

## Commands

- `bundle exec jekyll serve`: 로컬 개발 서버 실행 (http://localhost:4000)
- `bundle exec jekyll build`: 정적 사이트 빌드
- `bundle install`: gem 의존성 설치

## Repository Map

```text
_posts/       블로그 포스트 (YYYY-MM-DD-slug.md)
_layouts/     HTML 레이아웃 템플릿
_includes/    재사용 가능한 HTML 컴포넌트
_sass/        Sass 스타일시트
assets/       CSS 및 정적 자산 (이미지: assets/img/<slug>/)
_config.yml   사이트 전역 설정
.claude/rules/ 보조 규칙 파일 (methodology.md, images.md)
```

## Theme Notes

- GitHub Pages 배포: `_config.yml`에서 `remote_theme: chesterhow/tale` 사용 (현재 설정)
- 로컬 테스트: `theme: tale`으로 변경 후 빌드 (GitHub Pages는 `remote_theme` 필요)

## Working Rules

### 포스트 작성 규칙

새 리뷰 포스트는 반드시 `_posts/YYYY-MM-DD-slug.md` 형식으로 생성합니다.

```yaml
---
layout: post
title: "[논문 제목]"
authors: "[저자 목록]"
venue: "[학회/저널] [연도]"
arxiv: "https://arxiv.org/abs/XXXX.XXXXX"
tags: [<subject>, <topic-tags...>]
date: "YYYY-MM-DD"
---
```

### Tag Taxonomy

`tags` 필드는 **subject 태그**로 시작하고, 이후 논문의 핵심 topic 태그를 추가합니다.

### 본문 작성 규칙

- 기본 언어는 **한국어**로 작성합니다.
- 독자는 `여러분`으로 지칭하고 **존댓말**을 사용합니다.
- 문체는 **공식적이되 과도하게 딱딱하지 않은 세미나 발표 스타일**로 유지합니다.
- **섹션 제목(##, ###, ####)은 반드시 영어로 작성합니다.** 본문은 한국어이지만 제목은 영어를 사용합니다.
- 학술 전문 용어는 **영어 원문**을 그대로 사용합니다. 첫 등장 시에만 한국어 설명을 괄호 안에 추가합니다. 예: `autoregressive(자기 회귀)`
- 약어는 첫 등장 시 영어 전체 표기 후 약어를 괄호로 정의합니다. 예: `Large Language Model (LLM)`

### 수식 및 코드 규칙

- 수식은 반드시 **KaTeX/LaTeX** 문법을 사용합니다.
  - 인라인: `$...$` / 블록: `$$...$$`
- 코드 예제는 논문의 분야에 맞는 언어를 사용합니다. 코드 블록에 반드시 언어를 명시합니다.
  - AI/ML: **Python (PyTorch 우선)**
  - 시스템/OS/네트워크: **C / C++**
  - 분산 시스템/데이터베이스: **Java / Go / Python**
  - 알고리즘/이론: **Python 또는 의사코드(pseudocode)**

## Supplemental Rules

세부 작성 지침은 `.claude/rules/`에 분리되어 있습니다.

- `.claude/rules/methodology.md`: 방법론 섹션 심층 해설 규칙 (서술 순서, 수식 해설 패턴, 분야별 핵심 메커니즘)
- `.claude/rules/images.md`: PyMuPDF 이미지 추출 스크립트 및 사용 규칙

## Quality Bar

- 핵심 contribution이 분명한가
- 선행 연구와의 차별점이 설명되었는가
- 방법론의 각 구성 요소가 세부 해설되었는가
- 수식의 모든 기호가 정의되고 직관적으로 해석되었는가
- 설계 선택의 근거가 논문 기반으로 설명되었는가
- 실험 결과의 의미를 해석했는가
- 비전공자도 도입부의 상당 부분을 이해할 수 있는가

## Hard Constraints

IMPORTANT: 다음 규칙은 반드시 지킵니다.

- 논문에 없는 수치, 실험 결과, 비교 우위를 임의로 작성하지 않습니다.
- 근거 없는 평가를 하지 않습니다. 예: "이 논문이 가장 좋다"
- 불확실한 정보는 사실처럼 단정하지 않습니다.
- YOU MUST: 이미지는 반드시 논문 PDF에서 PyMuPDF로 직접 추출한 것만 사용합니다.

## Gotchas

- `assets/img/<slug>/` 디렉토리는 이미지 추출 전에 수동 생성이 필요합니다 (`mkdir -p` 사용).
- front matter의 `date` 필드는 파일명 날짜와 반드시 일치해야 합니다.
- KaTeX 수식에서 `\\{`, `\\}` 등 이스케이프 문자는 Jekyll 렌더링에서 깨질 수 있으니 확인합니다.
- KaTeX 수식 안에서 prime(′) 기호를 `'`로 쓰면 kramdown SmartyPants가 `'`(U+2019)로 변환해 KaTeX가 인식하지 못합니다. 반드시 `^{\prime}`를 사용합니다. 예: `$y'$` → `$y^{\prime}$`, `$s'$` → `$s^{\prime}$`.
- 인라인 수식에서 `\cmd{X}_` 패턴 (닫는 중괄호 `}` 바로 뒤에 `_`)을 사용하면 kramdown이 `}` 다음 `_`를 강조(emphasis) 시작 마커로 인식합니다. 같은 단락 내에 닫는 `_`가 있으면 중간 텍스트가 `<em>`으로 감싸져 `$...$` 구분자가 DOM 노드 간에 분리되고 KaTeX가 렌더링하지 못합니다. **해결책: 중괄호를 제거합니다.** `\mathcal{T}_u` → `\mathcal T_u`. `\mathcal T`와 `\mathcal{T}`는 KaTeX에서 동일하게 렌더링되지만, `_` 앞이 문자(word character)가 되어 kramdown emphasis가 발동하지 않습니다. 이 규칙은 인라인(`$...$`)과 display(`$$...$$`) 수식 모두에 적용됩니다.
- `_posts/` 파일명에 미래 날짜를 사용하면 Jekyll이 해당 포스트를 빌드하지 않습니다.
- 인라인 코드(`` `...` ``) 안에 백틱 3개(` ``` `)를 넣으면 마크다운 파서가 코드 펜스로 오인해 렌더링이 깨집니다. 백틱을 포함한 심볼을 표기할 때는 `"""` 같은 대체 표현이나 텍스트 설명으로 바꿉니다.
- 블로그 내부 포스트 링크는 반드시 permalink 패턴 `/:year-:month-:day/:title`을 따릅니다. 예: `2026-03-28-struq.md` → `https://beomsu317.github.io/2026-03-28/struq`. `/slug/` 형태의 단축 URL은 존재하지 않습니다.

## Metadata Handling

arXiv 링크가 주어지면 다음 정보를 우선적으로 정리합니다: 제목, 저자, 초록, 제출일, 카테고리.

## Preferred Output Types

사용자 요청이 없으면 **심층 리뷰(4,000자 이상)**를 기본값으로 사용합니다.

- 짧은 요약: 500–800자
- 표준 리뷰: 2,000–3,500자
- 심층 분석: 4,000자 이상

## Source of Truth

- 논문 내용이 최우선 근거입니다.
- 구현 예시는 논문 설명을 보조하기 위한 수준으로만 작성합니다.
- 블로그 내부 스타일은 기존 `_posts/`의 작성 패턴을 우선 참고합니다.

## Editing Policy

기존 포스트를 수정할 때는 다음 순서를 따릅니다.

1. 기존 글의 구조와 톤을 확인합니다.
2. 사실관계가 바뀌지 않는 범위에서 가독성을 개선합니다.
3. 논문 원문과 충돌하는 표현이 없는지 확인합니다.
4. front matter 형식이 유지되는지 확인합니다.

## Final Check Before Completing Work

- 파일명·위치가 규칙에 맞는가
- front matter가 올바른가 (날짜 일치 포함)
- 수식 문법이 깨지지 않는가
- 코드 블록 언어가 명시되었는가
- 근거 없는 수치/주장이 들어가지 않았는가
- 독자 친화적인 도입부가 포함되었는가
- 내부 포스트 링크가 `/:year-:month-:day/:title` 형식을 따르는가

# 논문 이미지 추출 (PyMuPDF)

논문 리뷰 시 그림(Figure), 표(Table), 알고리즘 블록 등 시각 자료가 필요하면 **PyMuPDF**를 사용해 PDF에서 직접 추출합니다.

## 포스트 작성 시 자동 실행 절차

사용자가 논문 URL을 제공하면 포스트 작성 전에 **반드시 아래를 순서대로 실행**합니다.

1. PDF 다운로드: `wget -q -O /tmp/<slug>.pdf "<URL>"` (arXiv는 `/abs/` → `/pdf/` 변환)
2. 이미지 디렉토리 생성: `mkdir -p assets/img/<slug>`
3. `page.get_text("blocks")`로 Figure 캡션 좌표 파악 — 캡션 블록의 y0을 크롭 하단 경계로 사용하지 않고, **캡션 블록 바로 위(y0)를 크롭 하단 경계**로 사용한다.
4. 2× 렌더링 + PIL 크롭으로 Figure 저장
5. **Read 도구로 크롭 결과 직접 확인** 후 필요 시 좌표 재조정
6. 포스트 본문 내 해당 Figure 언급 직후에 삽입

## 이미지 저장 위치

```text
assets/img/<slug>/        예: assets/img/attention-is-all-you-need/
```

포스트 slug는 `_posts/YYYY-MM-DD-slug.md`의 `slug`와 동일하게 사용합니다.

## 추출 스크립트

스크립트는 `scripts/extract_images.py`에 있습니다. Bash 도구로 직접 실행합니다.

```bash
python3 scripts/extract_images.py <pdf_path> <slug>
```

또는 인라인으로 함수를 import해 사용합니다.

```bash
python3 -c "
import sys; sys.path.insert(0, 'scripts')
from extract_images import extract_images_from_pdf
saved = extract_images_from_pdf('/tmp/<slug>.pdf', '<slug>')
print(saved)
"
```

## 포스트에서 이미지 참조

이미지와 캡션은 반드시 **가운데 정렬** HTML 블록으로 작성합니다.

```html
<p align="center">
  <img src="/assets/img/attention-is-all-you-need/fig-p003-00.png" alt="Figure 1: 모델 아키텍처 개요">
  <br>
  <em>Figure 1. Transformer 전체 구조 (Vaswani et al., 2017)</em>
</p>
```

마크다운 `![...](...)` + `*...*` 조합은 캡션이 좌측 정렬되므로 사용하지 않습니다.

## Figure 크롭 워크플로우

`get_images()`는 벡터 Figure를 추출하지 못합니다. 벡터 Figure는 **페이지 렌더링 → 좌표 크롭** 방식을 사용합니다.

1. `page.get_text("blocks")`에서 "Fig. N." 캡션 블록의 (x0, y0, x1, y1) 좌표 확인 (PDF points)
2. 2× 렌더링: `fitz.Matrix(2.0, 2.0)` → **PDF points × 2 = 픽셀**
3. PIL로 크롭: Figure 콘텐츠 상단부터 **캡션 블록 y0 바로 위(캡션 제외)** 까지만 크롭한다. 캡션 텍스트는 포스트 HTML의 `<em>` 태그로 별도 표기하므로 이미지에 포함하지 않는다.
4. **반드시 크롭 결과 이미지를 Read 도구로 직접 확인한다.** 인접 텍스트 컬럼이 경계에 침범하거나 Figure 일부가 잘린 경우, x0/x1/y0/y1 좌표를 조정해 재크롭한다.

## 이미지 사용 규칙

- 이미지는 반드시 **논문 PDF에서 직접 추출**한 것만 사용합니다.
- 캡션에는 `Figure N.` 번호와 **출처(저자, 연도)**를 표기합니다.
- 설명 없이 이미지만 단독 삽입하지 않습니다. 반드시 본문에서 해당 그림을 언급하고 해설합니다.
- `min_width` / `min_height` 필터로 의미 없는 소형 이미지(로고, 구분선 등)는 제외합니다.

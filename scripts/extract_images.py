import fitz  # PyMuPDF
from pathlib import Path

def extract_images_from_pdf(pdf_path: str, slug: str, min_width: int = 200, min_height: int = 200):
    """PDF에서 이미지를 추출해 assets/img/<slug>/ 에 저장합니다."""
    output_dir = Path(f"assets/img/{slug}")
    output_dir.mkdir(parents=True, exist_ok=True)

    doc = fitz.open(pdf_path)
    saved = []

    for page_num, page in enumerate(doc, start=1):
        for img_index, img in enumerate(page.get_images(full=True)):
            xref = img[0]
            pix = fitz.Pixmap(doc, xref)

            if pix.width < min_width or pix.height < min_height:
                continue  # 너무 작은 이미지(아이콘 등) 제외
            if pix.n > 4:
                pix = fitz.Pixmap(fitz.csRGB, pix)  # CMYK → RGB 변환

            filename = f"fig-p{page_num:03d}-{img_index:02d}.png"
            out_path = output_dir / filename
            pix.save(str(out_path))
            saved.append(str(out_path))

    doc.close()
    return saved

if __name__ == "__main__":
    import sys
    if len(sys.argv) != 3:
        print("Usage: python3 extract_images.py <pdf_path> <slug>")
        sys.exit(1)
    results = extract_images_from_pdf(sys.argv[1], sys.argv[2])
    for path in results:
        print(path)

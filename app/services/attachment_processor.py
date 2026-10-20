from pathlib import Path

from app.ocr.pymupdf_extractor import extract_pdf_text
from app.ocr.tesseract_engine import TesseractEngine


TEXT_THRESHOLD = 80


def process_attachment(path_str: str) -> str:
    path = Path(path_str)

    if not path.exists():
        return f"[attachment unavailable: {path.name}]"

    suffix = path.suffix.lower()

    if suffix == ".pdf":
        direct_text = extract_pdf_text(path)
        if len(direct_text.strip()) >= TEXT_THRESHOLD:
            return direct_text
        return TesseractEngine().extract(path)

    if suffix in {".png", ".jpg", ".jpeg", ".tif", ".tiff", ".bmp"}:
        return TesseractEngine().extract(path)

    if suffix in {".txt", ".md"}:
        return path.read_text(encoding="utf-8", errors="ignore")

    return f"[unsupported attachment type: {suffix}]"

from pathlib import Path

from app.ocr.azure_document_intelligence import extract_with_azure
from app.ocr.pymupdf_extractor import extract_pdf_text


NATIVE_PDF_TEXT_THRESHOLD = 80


def process_attachment(path_str: str) -> str:
    path = Path(path_str)
    if not path.exists():
        return f"[attachment unavailable: {path.name}]"

    suffix = path.suffix.lower()
    if suffix == ".pdf":
        native_text = extract_pdf_text(path)
        if len(native_text.strip()) >= NATIVE_PDF_TEXT_THRESHOLD:
            return native_text
        return extract_with_azure(path.read_bytes())

    if suffix in {".png", ".jpg", ".jpeg", ".tif", ".tiff", ".bmp"}:
        return extract_with_azure(path.read_bytes())

    if suffix in {".txt", ".md"}:
        return path.read_text(encoding="utf-8", errors="ignore")

    return f"[unsupported attachment type: {suffix}]"

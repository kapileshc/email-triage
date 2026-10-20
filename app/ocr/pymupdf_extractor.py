from pathlib import Path
import fitz


def extract_pdf_text(path: Path) -> str:
    doc = fitz.open(path)
    pages = [page.get_text("text").strip() for page in doc]
    return "\n\n".join(p for p in pages if p)

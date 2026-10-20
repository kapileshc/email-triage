from pathlib import Path
import io

import fitz
import pytesseract
from PIL import Image

from app.ocr.base import OCREngine


class TesseractEngine(OCREngine):
    def __init__(self, languages: str = "eng+hin"):
        self.languages = languages

    def extract(self, path: Path) -> str:
        suffix = path.suffix.lower()

        if suffix == ".pdf":
            doc = fitz.open(path)
            pages = []
            for page in doc:
                pix = page.get_pixmap(dpi=200)
                image = Image.open(io.BytesIO(pix.tobytes("png")))
                pages.append(
                    pytesseract.image_to_string(image, lang=self.languages)
                )
            return "\n\n".join(pages).strip()

        image = Image.open(path)
        return pytesseract.image_to_string(
            image, lang=self.languages
        ).strip()

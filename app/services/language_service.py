from langdetect import detect, LangDetectException


def detect_language(text: str) -> str:
    if not text or len(text.strip()) < 3:
        return "unknown"
    try:
        return detect(text)
    except LangDetectException:
        return "unknown"


def normalize_for_retrieval(text: str, language: str) -> str:
    # Extension point for fully-offline translation such as Argos/NLLB.
    return text

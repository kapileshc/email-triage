import json
import re

from app.llm.azure_foundry import generate_text
from app.prompts import TRIAGE_SYSTEM_PROMPT
from app.schemas import TriageDecision


HIGH_RISK = (
    "legal", "lawyer", "fraud", "security breach", "unauthorized",
    "chargeback", "court", "police", "identity theft",
)

RETRIEVAL_HINTS = (
    "policy", "refund", "eligible", "eligibility", "procedure", "how do i",
    "how can i", "what is", "reset", "access", "document", "required",
)


def _heuristic_triage(subject: str, body: str, language: str, has_attachments: bool) -> TriageDecision:
    text = f"{subject}\n{body}".lower()
    risky = any(term in text for term in HIGH_RISK)
    needs_retrieval = any(term in text for term in RETRIEVAL_HINTS)

    category = "general"
    if "refund" in text:
        category = "refund"
    elif "login" in text or "password" in text or "access" in text:
        category = "account_access"
    elif "document" in text or "attachment" in text:
        category = "document_request"

    return TriageDecision(
        category=category,
        priority="high" if risky else "medium",
        language=language,
        needs_attachment_processing=has_attachments,
        needs_retrieval=needs_retrieval,
        needs_reply=True,
        human_review_required=risky,
        reason="Rule-based fallback triage used.",
    )


def _extract_json(text: str) -> dict:
    cleaned = re.sub(r"^```(?:json)?", "", text.strip()).strip()
    cleaned = re.sub(r"```$", "", cleaned).strip()
    start, end = cleaned.find("{"), cleaned.rfind("}")
    if start == -1 or end == -1:
        raise ValueError("No JSON object found")
    return json.loads(cleaned[start:end + 1])


def triage_email(subject: str, body: str, language: str, has_attachments: bool) -> TriageDecision:
    fallback = _heuristic_triage(subject, body, language, has_attachments)
    prompt = f"""Detected language: {language}\nAttachments present: {has_attachments}\n\nSubject:\n{subject}\n\nBody:\n{body}"""
    try:
        payload = _extract_json(generate_text(TRIAGE_SYSTEM_PROMPT, prompt, temperature=0.0, max_tokens=350))
        payload["language"] = language
        return TriageDecision.model_validate(payload)
    except Exception:
        return fallback

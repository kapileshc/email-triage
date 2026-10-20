import json
import re

from langchain_core.messages import HumanMessage, SystemMessage

from app.llm.gemma import get_llm
from app.prompts import TRIAGE_SYSTEM_PROMPT
from app.schemas import TriageDecision


HIGH_RISK = (
    "legal",
    "lawyer",
    "fraud",
    "security breach",
    "unauthorized",
    "chargeback",
    "court",
    "police",
    "identity theft",
)

RETRIEVAL_HINTS = (
    "policy",
    "refund",
    "eligible",
    "eligibility",
    "procedure",
    "how do i",
    "how can i",
    "what is",
    "reset",
    "access",
    "document",
    "required",
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

    return TriageDecision(category=category, priority="high" if risky else "medium", language=language, needs_attachment_processing=has_attachments, needs_retrieval=needs_retrieval, needs_reply=True, human_review_required=risky, reason="Rule-based fallback triage used.")


def _extract_json(text: str) -> dict:
    text = text.strip()
    text = re.sub(r"^```(?:json)?", "", text).strip()
    text = re.sub(r"```$", "", text).strip()
    start = text.find("{")
    end = text.rfind("}")
    if start == -1 or end == -1:
        raise ValueError("No JSON object found")
    return json.loads(text[start:end + 1])


def triage_email(subject: str, body: str, language: str, has_attachments: bool) -> TriageDecision:
    fallback = _heuristic_triage(subject, body, language, has_attachments)
    try:
        llm = get_llm(temperature=0.0)
        response = llm.invoke([
            SystemMessage(content=TRIAGE_SYSTEM_PROMPT),
            HumanMessage(content=f"""
Detected language: {language}
Attachments present: {has_attachments}

Subject:
{subject}

Body:
{body}
"""),
        ])
        payload = _extract_json(response.content)
        payload["language"] = language
        return TriageDecision.model_validate(payload)
    except Exception:
        return fallback

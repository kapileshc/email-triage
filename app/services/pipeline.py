from langchain_core.messages import HumanMessage, SystemMessage

from app.agents.triage_agent import triage_email
from app.llm.gemma import get_llm
from app.prompts import REPLY_SYSTEM_PROMPT
from app.rag.qdrant_store import retrieve
from app.schemas import EmailRequest, TriageResponse
from app.services.attachment_processor import process_attachment
from app.services.language_service import detect_language, normalize_for_retrieval


def _format_evidence(evidence):
    if not evidence:
        return "No approved knowledge retrieved."
    return "\n\n".join(f"[{item.source}]\n{item.text}" for item in evidence)


def run_pipeline(request: EmailRequest) -> TriageResponse:
    trace: list[str] = []
    language = detect_language(f"{request.subject}\n{request.body}")
    trace.append(f"language_detected:{language}")

    decision = triage_email(request.subject, request.body, language, bool(request.attachments))
    trace.append("triage_completed")

    extracted: dict[str, str] = {}
    if decision.needs_attachment_processing:
        for attachment in request.attachments:
            extracted[attachment.filename] = process_attachment(attachment.path)
        trace.append("attachments_processed")

    normalized_query = normalize_for_retrieval("\n".join([request.subject, request.body, *extracted.values()]), language)
    evidence = retrieve(normalized_query) if decision.needs_retrieval else []
    if decision.needs_retrieval:
        trace.append("knowledge_retrieved")

    draft = None
    if decision.needs_reply:
        attachment_text = "\n\n".join(f"### {name}\n{text}" for name, text in extracted.items()) or "No extracted attachments."
        prompt = f"""
INCOMING EMAIL
From: {request.sender}
Subject: {request.subject}

{request.body}

EXTRACTED ATTACHMENTS
{attachment_text}

APPROVED RETRIEVED CONTEXT
{_format_evidence(evidence)}

Human review required: {decision.human_review_required}
"""
        try:
            draft = get_llm(temperature=0.1).invoke([SystemMessage(content=REPLY_SYSTEM_PROMPT), HumanMessage(content=prompt)]).content.strip()
            trace.append("reply_generated")
        except Exception:
            draft = "Local Gemma 3 is unavailable. Start Ollama and pull the configured Gemma 3 model to generate a reply."
            trace.append("reply_generation_unavailable")

    return TriageResponse(decision=decision, extracted_attachments=extracted, retrieved_context=evidence, draft_reply=draft, trace=trace)

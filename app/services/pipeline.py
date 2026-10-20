from app.agents.triage_agent import triage_email
from app.llm.azure_foundry import generate_text
from app.prompts import REPLY_SYSTEM_PROMPT
from app.rag.qdrant_store import retrieve
from app.schemas import EmailRequest, TriageResponse
from app.services.attachment_processor import process_attachment
from app.services.language_service import detect_language, normalize_for_retrieval


def _format_evidence(evidence) -> str:
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
        trace.append("attachments_processed:azure_document_intelligence")

    normalized_query = normalize_for_retrieval(
        "\n".join([request.subject, request.body, *extracted.values()]), language
    )
    evidence = retrieve(normalized_query) if decision.needs_retrieval else []
    if decision.needs_retrieval:
        trace.append("knowledge_retrieved:qdrant_cloud")

    draft = None
    if decision.needs_reply:
        attachment_text = "\n\n".join(
            f"### {name}\n{text}" for name, text in extracted.items()
        ) or "No extracted attachments."
        prompt = f"""INCOMING EMAIL\nFrom: {request.sender}\nSubject: {request.subject}\n\n{request.body}\n\nEXTRACTED ATTACHMENTS\n{attachment_text}\n\nAPPROVED RETRIEVED CONTEXT\n{_format_evidence(evidence)}\n\nHuman review required: {decision.human_review_required}"""
        try:
            draft = generate_text(REPLY_SYSTEM_PROMPT, prompt, temperature=0.1)
            trace.append("reply_generated:azure_foundry")
        except Exception as exc:
            draft = "Reply generation is temporarily unavailable. Please route this email for human review."
            trace.append(f"reply_generation_failed:{type(exc).__name__}")

    return TriageResponse(
        decision=decision,
        extracted_attachments=extracted,
        retrieved_context=evidence,
        draft_reply=draft,
        trace=trace,
    )

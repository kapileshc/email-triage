from typing import Literal
from pydantic import BaseModel, Field


class AttachmentInput(BaseModel):
    filename: str
    path: str


class EmailRequest(BaseModel):
    sender: str = ""
    subject: str
    body: str
    attachments: list[AttachmentInput] = Field(default_factory=list)


class TriageDecision(BaseModel):
    category: str
    priority: Literal["low", "medium", "high", "critical"]
    language: str
    needs_attachment_processing: bool
    needs_retrieval: bool
    needs_reply: bool
    human_review_required: bool
    reason: str


class Evidence(BaseModel):
    source: str
    text: str
    score: float | None = None


class TriageResponse(BaseModel):
    decision: TriageDecision
    extracted_attachments: dict[str, str]
    retrieved_context: list[Evidence]
    draft_reply: str | None
    trace: list[str]

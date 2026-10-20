from pathlib import Path
import tempfile

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.schemas import AttachmentInput, EmailRequest, TriageResponse
from app.services.pipeline import run_pipeline


app = FastAPI(
    title="Multimodal Agentic Email Triage",
    version="0.2.0",
    description="Lightweight EC2 API using Azure OCR/LLM and Qdrant Cloud.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/health")
def health():
    return {"status": "ok", "environment": settings.app_env}


@app.post("/api/triage", response_model=TriageResponse)
def triage(request: EmailRequest):
    return run_pipeline(request)


@app.post("/api/triage-with-files", response_model=TriageResponse)
async def triage_with_files(
    sender: str = Form(""),
    subject: str = Form(...),
    body: str = Form(...),
    files: list[UploadFile] = File(default=[]),
):
    if len(files) > settings.max_attachments:
        raise HTTPException(400, f"Maximum {settings.max_attachments} attachments are allowed")

    allowed = {".pdf", ".png", ".jpg", ".jpeg", ".tif", ".tiff", ".bmp", ".txt", ".md"}
    attachments: list[AttachmentInput] = []

    with tempfile.TemporaryDirectory(prefix="email-triage-") as tmp:
        for upload in files:
            suffix = Path(upload.filename or "attachment").suffix.lower()
            if suffix not in allowed:
                raise HTTPException(400, f"Unsupported attachment type: {suffix or 'unknown'}")
            content = await upload.read()
            if len(content) > settings.max_attachment_mb * 1024 * 1024:
                raise HTTPException(413, f"{upload.filename} exceeds {settings.max_attachment_mb} MB")
            path = Path(tmp) / (upload.filename or "attachment")
            path.write_bytes(content)
            attachments.append(AttachmentInput(filename=path.name, path=str(path)))

        request = EmailRequest(sender=sender, subject=subject, body=body, attachments=attachments)
        return run_pipeline(request)

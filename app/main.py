from fastapi import FastAPI

from app.schemas import EmailRequest, TriageResponse
from app.services.pipeline import run_pipeline


app = FastAPI(title="Multimodal Agentic Email Triage", version="0.1.0", description="Local-first multimodal email triage with offline OCR, RAG and Gemma 3.")


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/triage", response_model=TriageResponse)
def triage(request: EmailRequest):
    return run_pipeline(request)

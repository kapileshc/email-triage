from functools import lru_cache

from azure.ai.documentintelligence import DocumentIntelligenceClient
from azure.core.credentials import AzureKeyCredential

from app.config import settings


@lru_cache(maxsize=1)
def _client() -> DocumentIntelligenceClient:
    if not settings.azure_document_intelligence_endpoint or not settings.azure_document_intelligence_key:
        raise RuntimeError("Azure Document Intelligence endpoint/key are not configured")
    return DocumentIntelligenceClient(
        endpoint=settings.azure_document_intelligence_endpoint,
        credential=AzureKeyCredential(settings.azure_document_intelligence_key),
    )


def extract_with_azure(content: bytes) -> str:
    poller = _client().begin_analyze_document(
        model_id=settings.azure_document_model,
        body=content,
        content_type="application/octet-stream",
    )
    result = poller.result()
    if getattr(result, "content", None):
        return result.content.strip()

    lines: list[str] = []
    for page in result.pages or []:
        for line in page.lines or []:
            lines.append(line.content)
    return "\n".join(lines).strip()

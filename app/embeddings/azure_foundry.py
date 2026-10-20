from functools import lru_cache

from azure.ai.inference import EmbeddingsClient
from azure.core.credentials import AzureKeyCredential

from app.config import settings


@lru_cache(maxsize=1)
def _client() -> EmbeddingsClient:
    if not settings.azure_embedding_endpoint or not settings.azure_embedding_api_key:
        raise RuntimeError("Azure embedding endpoint/key are not configured")
    return EmbeddingsClient(
        endpoint=settings.azure_embedding_endpoint,
        credential=AzureKeyCredential(settings.azure_embedding_api_key),
    )


def embed_texts(texts: list[str]) -> list[list[float]]:
    kwargs = {"input": texts}
    if settings.azure_embedding_model:
        kwargs["model"] = settings.azure_embedding_model
    response = _client().embed(**kwargs)
    return [item.embedding for item in response.data]


def embed_text(text: str) -> list[float]:
    return embed_texts([text])[0]

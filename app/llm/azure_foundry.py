from functools import lru_cache

from azure.ai.inference import ChatCompletionsClient
from azure.ai.inference.models import SystemMessage, UserMessage
from azure.core.credentials import AzureKeyCredential

from app.config import settings


@lru_cache(maxsize=1)
def _client() -> ChatCompletionsClient:
    if not settings.azure_model_endpoint or not settings.azure_model_api_key:
        raise RuntimeError("Azure Foundry model endpoint/key are not configured")
    return ChatCompletionsClient(
        endpoint=settings.azure_model_endpoint,
        credential=AzureKeyCredential(settings.azure_model_api_key),
    )


def generate_text(system_prompt: str, user_prompt: str, *, temperature: float = 0.1, max_tokens: int | None = None) -> str:
    kwargs = {
        "messages": [SystemMessage(content=system_prompt), UserMessage(content=user_prompt)],
        "temperature": temperature,
        "max_tokens": max_tokens or settings.azure_model_max_tokens,
    }
    if settings.azure_model_name:
        kwargs["model"] = settings.azure_model_name
    response = _client().complete(**kwargs)
    return response.choices[0].message.content.strip()

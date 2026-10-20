from functools import lru_cache

from openai import OpenAI

from app.config import settings


@lru_cache(maxsize=1)
def _client() -> OpenAI:
    if not settings.azure_model_endpoint or not settings.azure_model_api_key:
        raise RuntimeError("Azure OpenAI endpoint/key are not configured")

    base_url = settings.azure_model_endpoint.rstrip("/") + "/"
    return OpenAI(
        base_url=base_url,
        api_key=settings.azure_model_api_key,
        default_headers={"api-key": settings.azure_model_api_key},
    )


def generate_text(
    system_prompt: str,
    user_prompt: str,
    *,
    temperature: float = 0.1,
    max_tokens: int | None = None,
) -> str:
    response = _client().chat.completions.create(
        model=settings.azure_model_name,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        temperature=temperature,
        max_tokens=max_tokens or settings.azure_model_max_tokens,
    )
    content = response.choices[0].message.content
    return (content or "").strip()

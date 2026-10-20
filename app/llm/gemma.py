from langchain_ollama import ChatOllama
from app.config import settings


def get_llm(temperature: float = 0.1) -> ChatOllama:
    return ChatOllama(
        model=settings.ollama_model,
        base_url=settings.ollama_base_url,
        temperature=temperature,
    )

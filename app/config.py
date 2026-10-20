from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "gemma3:4b"
    qdrant_url: str = "http://localhost:6333"
    qdrant_collection: str = "email_triage_knowledge"
    embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"
    top_k: int = 4
    use_llm_triage: bool = True

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()

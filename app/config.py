from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_env: str = "development"
    api_host: str = "0.0.0.0"
    api_port: int = 8001
    allowed_origins: str = "http://localhost:5173"

    azure_model_endpoint: str = "https://kapilesh1-2109-resource.services.ai.azure.com/openai/v1"
    azure_model_api_key: str = ""
    azure_model_name: str = "gpt-4.1-mini"
    azure_model_max_tokens: int = 600

    azure_embedding_endpoint: str = ""
    azure_embedding_api_key: str = ""
    azure_embedding_model: str = ""

    azure_document_intelligence_endpoint: str = ""
    azure_document_intelligence_key: str = ""
    azure_document_model: str = "prebuilt-read"

    qdrant_url: str = ""
    qdrant_api_key: str = ""
    qdrant_collection: str = "email_triage_knowledge"
    top_k: int = 4

    max_attachment_mb: int = 4
    max_attachments: int = 5

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    @property
    def origins(self) -> list[str]:
        return [item.strip() for item in self.allowed_origins.split(",") if item.strip()]


settings = Settings()

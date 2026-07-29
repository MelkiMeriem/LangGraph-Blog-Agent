from pydantic_settings import BaseSettings, SettingsConfigDict

SUPPORTED_LANGUAGES = ["french", "spanish", "arabic", "german"]


class Settings(BaseSettings):
    groq_api_key: str
    groq_model: str = "llama-3.3-70b-versatile"
    max_transcript_chars: int = 8000

    langsmith_api_key: str | None = None
    langsmith_project: str = "blog-generation-agent"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()

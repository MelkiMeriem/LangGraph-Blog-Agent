from functools import lru_cache

from langchain_groq import ChatGroq

from app.config import settings


@lru_cache(maxsize=None)
def get_llm(temperature: float) -> ChatGroq:
    return ChatGroq(
        model=settings.groq_model,
        api_key=settings.groq_api_key,
        temperature=temperature,
        max_retries=2,
        timeout=60,
    )

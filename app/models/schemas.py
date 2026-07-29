from typing import Literal

from pydantic import BaseModel, field_validator

from app.config import SUPPORTED_LANGUAGES


class GenerateRequest(BaseModel):
    input_type: Literal["topic", "youtube"]
    content: str
    target_language: str | None = None

    @field_validator("target_language")
    @classmethod
    def check_supported_language(cls, v: str | None) -> str | None:
        if v is None:
            return v
        normalized = v.lower()
        if normalized not in SUPPORTED_LANGUAGES:
            raise ValueError(f"Unsupported target_language. Choose from: {SUPPORTED_LANGUAGES}")
        return normalized


class GenerateResponse(BaseModel):
    input_type: str
    video_id: str | None = None
    titles: list[str]
    selected_title: str
    blog_content: str
    target_language: str | None = None
    translated_title: str | None = None
    translated_content: str | None = None

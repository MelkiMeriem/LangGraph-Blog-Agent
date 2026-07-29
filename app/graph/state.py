from typing import Literal, Optional, TypedDict


class GraphState(TypedDict, total=False):
    input_type: Literal["topic", "youtube"]
    raw_input: str
    video_id: Optional[str]
    transcript: Optional[str]

    titles: list[str]
    selected_title: str
    blog_content: str

    target_language: Optional[str]
    translated_title: Optional[str]
    translated_content: Optional[str]

    error: Optional[str]
    error_stage: Optional[str]

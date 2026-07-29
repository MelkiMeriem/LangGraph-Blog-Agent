import functools

import groq
from langgraph.graph import END
from pydantic import BaseModel, Field
from youtube_transcript_api import (
    CouldNotRetrieveTranscript,
    IpBlocked,
    NoTranscriptFound,
    RequestBlocked,
    TranscriptsDisabled,
    VideoUnavailable,
)

from app.config import SUPPORTED_LANGUAGES, settings
from app.graph.state import GraphState
from app.services.llm import get_llm
from app.services.youtube import extract_video_id, fetch_transcript_text


class TitleSuggestions(BaseModel):
    titles: list[str] = Field(..., description="3 to 5 candidate blog post titles")
    selected_title: str = Field(..., description="The single best title, must be one of `titles`")


class TranslatedBlog(BaseModel):
    translated_title: str = Field(..., description="Title translated into the target language")
    translated_content: str = Field(
        ..., description="Full blog body translated into the target language, preserving Markdown formatting"
    )


def _source_material(state: GraphState) -> str:
    return state.get("transcript") or state.get("raw_input") or ""


def _handle_llm_errors(stage: str):
    def decorator(fn):
        @functools.wraps(fn)
        def wrapper(state: GraphState) -> GraphState:
            try:
                return fn(state)
            except groq.RateLimitError as exc:
                return {"error": f"Groq rate limit exceeded: {exc}", "error_stage": f"{stage}_rate_limited"}
            except Exception as exc:
                return {"error": f"{stage} failed: {exc}", "error_stage": stage}

        return wrapper

    return decorator


def fetch_transcript_node(state: GraphState) -> GraphState:
    try:
        video_id = extract_video_id(state["raw_input"])
    except ValueError as exc:
        return {"error": str(exc), "error_stage": "fetch_transcript"}

    try:
        transcript = fetch_transcript_text(video_id, settings.max_transcript_chars)
    except VideoUnavailable as exc:
        return {"error": f"Video unavailable: {exc}", "error_stage": "fetch_transcript_unavailable"}
    except (IpBlocked, RequestBlocked) as exc:
        return {
            "error": f"YouTube blocked the transcript request from this network: {exc}",
            "error_stage": "fetch_transcript_blocked",
        }
    except (TranscriptsDisabled, NoTranscriptFound, CouldNotRetrieveTranscript) as exc:
        return {"error": f"No transcript available for this video: {exc}", "error_stage": "fetch_transcript"}

    return {"video_id": video_id, "transcript": transcript}


@_handle_llm_errors("brainstorm_titles")
def brainstorm_titles_node(state: GraphState) -> GraphState:
    llm = get_llm(0.9).with_structured_output(TitleSuggestions, method="json_mode")
    prompt = (
        "You are a blog title strategist. Based on the following source material, propose 3 to 5 "
        "engaging, SEO-friendly blog post titles, then pick the single best one.\n\n"
        "Respond with a single JSON object with exactly these keys: "
        '"titles" (an array of 3 to 5 strings) and "selected_title" (a string, must be one of the '
        "items in titles). Return JSON only, no other text.\n\n"
        f"Source material:\n{_source_material(state)[:6000]}"
    )
    result: TitleSuggestions = llm.invoke(prompt)
    return {"titles": result.titles, "selected_title": result.selected_title}


@_handle_llm_errors("generate_content")
def generate_content_node(state: GraphState) -> GraphState:
    llm = get_llm(0.5)
    prompt = (
        "You are a professional blog writer. Write a complete, well-structured blog post in Markdown "
        f'for the title "{state["selected_title"]}". The title is displayed separately by the caller, '
        "so do NOT include it as a heading in your output — start directly with the body, using "
        "second-level (##) headings or lower for any section headings. Use short paragraphs and a "
        "bullet list where useful. Base it on this source material:\n\n"
        f"{_source_material(state)[:6000]}"
    )
    content = llm.invoke(prompt).content
    return {"blog_content": content}


@_handle_llm_errors("translate")
def translate_node(state: GraphState) -> GraphState:
    llm = get_llm(0.2).with_structured_output(TranslatedBlog, method="json_mode")
    prompt = (
        f"Translate the following blog post title and Markdown body into {state['target_language']}. "
        "Preserve the Markdown structure (headings, lists, emphasis) exactly.\n\n"
        "Respond with a single JSON object with exactly these keys: "
        '"translated_title" (a string) and "translated_content" (a string containing the full '
        "translated Markdown body). Escape all quotes and special characters so the JSON is valid. "
        "Return JSON only, no other text.\n\n"
        f"Title: {state['selected_title']}\n\n"
        f"Body:\n{state['blog_content']}"
    )
    result: TranslatedBlog = llm.invoke(prompt)
    return {"translated_title": result.translated_title, "translated_content": result.translated_content}


def route_input(state: GraphState) -> str:
    return "fetch_transcript" if state["input_type"] == "youtube" else "brainstorm_titles"


def route_after_transcript(state: GraphState) -> str:
    return END if state.get("error") else "brainstorm_titles"


def route_after_titles(state: GraphState) -> str:
    return END if state.get("error") else "generate_content"


def route_translation(state: GraphState) -> str:
    if state.get("error"):
        return END
    lang = state.get("target_language")
    if lang and lang in SUPPORTED_LANGUAGES:
        return "translate"
    return END

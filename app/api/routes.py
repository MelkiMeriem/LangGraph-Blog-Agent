from fastapi import APIRouter, Depends, HTTPException

from app.config import SUPPORTED_LANGUAGES
from app.graph.builder import get_compiled_graph
from app.graph.state import GraphState
from app.models.schemas import GenerateRequest, GenerateResponse

router = APIRouter()

_ERROR_STAGE_STATUS = {
    "fetch_transcript": 422,
    "fetch_transcript_unavailable": 404,
    "fetch_transcript_blocked": 503,
    "brainstorm_titles": 502,
    "generate_content": 502,
    "translate": 502,
    "brainstorm_titles_rate_limited": 503,
    "generate_content_rate_limited": 503,
    "translate_rate_limited": 503,
}


@router.get("/health")
def health():
    return {"status": "ok"}


@router.get("/languages")
def languages():
    return {"supported_languages": SUPPORTED_LANGUAGES}


@router.post("/generate", response_model=GenerateResponse)
def generate(req: GenerateRequest, graph=Depends(get_compiled_graph)):
    initial_state: GraphState = {
        "input_type": req.input_type,
        "raw_input": req.content,
        "target_language": req.target_language,
    }

    try:
        result: GraphState = graph.invoke(initial_state)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Unexpected pipeline failure: {exc}") from exc

    if result.get("error"):
        stage = result.get("error_stage")
        status_code = _ERROR_STAGE_STATUS.get(stage, 502)
        raise HTTPException(status_code=status_code, detail=result["error"])

    return GenerateResponse(**result)

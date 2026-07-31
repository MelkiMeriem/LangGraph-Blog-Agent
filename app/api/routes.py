import groq
from fastapi import APIRouter, Depends, HTTPException, UploadFile

from app.config import SUPPORTED_LANGUAGES
from app.graph.builder import get_compiled_graph
from app.graph.state import GraphState
from app.models.schemas import GenerateRequest, GenerateResponse, TranscribeUploadResponse
from app.services.transcription import MAX_UPLOAD_BYTES, transcribe_audio

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


@router.post("/transcribe-upload", response_model=TranscribeUploadResponse)
async def transcribe_upload(file: UploadFile):
    file_bytes = await file.read()

    if not file_bytes:
        raise HTTPException(status_code=422, detail="Uploaded file is empty.")
    if len(file_bytes) > MAX_UPLOAD_BYTES:
        raise HTTPException(
            status_code=413,
            detail=f"File too large ({len(file_bytes) // (1024 * 1024)}MB). Max size is "
            f"{MAX_UPLOAD_BYTES // (1024 * 1024)}MB — please upload a shorter clip.",
        )

    try:
        transcript = transcribe_audio(file.filename or "upload", file_bytes)
    except groq.RateLimitError as exc:
        raise HTTPException(status_code=503, detail=f"Groq rate limit exceeded: {exc}") from exc
    except groq.APIError as exc:
        raise HTTPException(status_code=502, detail=f"Transcription failed: {exc}") from exc

    return TranscribeUploadResponse(transcript=transcript)


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

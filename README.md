# Autonomous Blog Generation Agent

A content generation engine that turns a **topic** or a **YouTube video URL** into a blog post,
built as a LangGraph DAG (title brainstorming → content generation → conditional translation)
and served over FastAPI.

## Architecture

```
START
  ├─ (youtube) ─▶ fetch_transcript ─▶ brainstorm_titles ─▶ generate_content ─┬─ (target_language set) ─▶ translate ─▶ END
  └─ (topic)   ───────────────────▶ brainstorm_titles ─▶ generate_content ─┘
                                                                            └─ (no translation) ─▶ END
```

- **fetch_transcript** — resolves a YouTube URL to a video ID and pulls its transcript (`youtube-transcript-api`).
- **brainstorm_titles** — Groq LLM call (creative, `temperature=0.9`) producing 3–5 candidate titles + a selected best one (structured output).
- **generate_content** — Groq LLM call (`temperature=0.5`) writing the full Markdown blog body.
- **translate** — conditional node, only reached if a supported `target_language` was requested; translates title + body (structured output, `temperature=0.2`).

Every node catches its own failures and sets `error`/`error_stage` on the graph state instead of raising,
so a single downstream routing check decides whether to continue or short-circuit to `END`.

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt   # or requirements.txt for runtime-only

cp .env .env
# then edit .env and set GROQ_API_KEY (free tier: https://console.groq.com)
```

Optional: set `LANGSMITH_API_KEY` in `.env` to enable request tracing in LangSmith
(https://smith.langchain.com — free tier). If left blank, the app runs untraced with no behavior change.

## Run

```bash
uvicorn app.main:app --reload
```

Swagger UI: http://127.0.0.1:8000/docs

## API

### `POST /generate`

```bash
# From a topic
curl -X POST http://127.0.0.1:8000/generate \
  -H "Content-Type: application/json" \
  -d '{"input_type": "topic", "content": "The history of coffee"}'

# From a YouTube video, with translation
curl -X POST http://127.0.0.1:8000/generate \
  -H "Content-Type: application/json" \
  -d '{"input_type": "youtube", "content": "https://youtu.be/VIDEO_ID", "target_language": "french"}'
```

Response:
```json
{
  "input_type": "topic",
  "video_id": null,
  "titles": ["...", "..."],
  "selected_title": "...",
  "blog_content": "# ...\n\n...",
  "target_language": null,
  "translated_title": null,
  "translated_content": null
}
```

### `GET /languages`
Returns the fixed list of supported translation target languages.

### `GET /health`
Liveness check.

### Error responses

| Failure | Status |
|---|---|
| Malformed YouTube URL | 422 |
| Transcript disabled / not found | 422 |
| Video unavailable / private | 404 |
| YouTube blocked the request (IP-level block) | 503 |
| Unsupported `target_language` | 422 |
| Groq API error | 502 |
| Groq rate limit (free-tier cap) | 503 |
| Unexpected pipeline failure | 500 |

## Testing

The full test suite runs offline — no `GROQ_API_KEY` or network access needed (an LLM stand-in and a
mocked transcript fetch are used via `tests/conftest.py`):

```bash
pytest -q
```

To verify against the real Groq API and a real YouTube video, set a valid `GROQ_API_KEY` in `.env`
and exercise `POST /generate` manually via `/docs` or the `curl` examples above.

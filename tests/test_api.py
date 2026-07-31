from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health():
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.json() == {"status": "ok"}


def test_languages():
    resp = client.get("/languages")
    assert resp.status_code == 200
    assert "french" in resp.json()["supported_languages"]


def test_generate_from_topic(fake_llm):
    resp = client.post("/generate", json={"input_type": "topic", "content": "The history of coffee"})
    assert resp.status_code == 200
    body = resp.json()
    assert body["selected_title"] == "Fake Title One"
    assert body["titles"] == ["Fake Title One", "Fake Title Two"]
    assert "fake generated blog content" in body["blog_content"].lower()
    assert body["translated_content"] is None


def test_generate_from_topic_with_translation(fake_llm):
    resp = client.post(
        "/generate",
        json={"input_type": "topic", "content": "The history of coffee", "target_language": "French"},
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["target_language"] == "french"
    assert body["translated_title"] == "Titre Faux"
    assert "Contenu de blog faux" in body["translated_content"]


def test_generate_rejects_unsupported_language(fake_llm):
    resp = client.post(
        "/generate",
        json={"input_type": "topic", "content": "The history of coffee", "target_language": "klingon"},
    )
    assert resp.status_code == 422


def test_generate_from_youtube(fake_llm, fake_transcript):
    resp = client.post(
        "/generate",
        json={"input_type": "youtube", "content": "https://youtu.be/dQw4w9WgXcQ"},
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["video_id"] == "dQw4w9WgXcQ"
    assert body["selected_title"] == "Fake Title One"


def test_generate_from_youtube_invalid_url(fake_llm):
    resp = client.post(
        "/generate",
        json={"input_type": "youtube", "content": "https://example.com/not-a-video"},
    )
    assert resp.status_code == 422


def test_transcribe_upload_success(fake_transcription):
    resp = client.post(
        "/transcribe-upload",
        files={"file": ("clip.mp4", b"fake-video-bytes", "video/mp4")},
    )
    assert resp.status_code == 200
    assert resp.json() == {"transcript": "This is a fake transcript from an uploaded video."}


def test_transcribe_upload_rejects_empty_file(fake_transcription):
    resp = client.post(
        "/transcribe-upload",
        files={"file": ("clip.mp4", b"", "video/mp4")},
    )
    assert resp.status_code == 422


def test_transcribe_upload_rejects_oversized_file(fake_transcription, monkeypatch):
    from app.api import routes as api_routes

    monkeypatch.setattr(api_routes, "MAX_UPLOAD_BYTES", 10)
    resp = client.post(
        "/transcribe-upload",
        files={"file": ("clip.mp4", b"this is more than ten bytes", "video/mp4")},
    )
    assert resp.status_code == 413


def test_uploaded_transcript_feeds_into_generate(fake_llm, fake_transcription):
    transcribed = client.post(
        "/transcribe-upload",
        files={"file": ("clip.mp4", b"fake-video-bytes", "video/mp4")},
    ).json()["transcript"]

    resp = client.post("/generate", json={"input_type": "topic", "content": transcribed})
    assert resp.status_code == 200
    assert resp.json()["selected_title"] == "Fake Title One"

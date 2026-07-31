from groq import Groq

from app.config import settings

MAX_UPLOAD_BYTES = 25 * 1024 * 1024  # Groq's transcription endpoint file size cap


def transcribe_audio(filename: str, file_bytes: bytes) -> str:
    client = Groq(api_key=settings.groq_api_key)
    transcription = client.audio.transcriptions.create(
        model="whisper-large-v3-turbo",
        file=(filename, file_bytes),
    )
    return transcription.text

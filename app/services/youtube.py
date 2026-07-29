from urllib.parse import parse_qs, urlparse

from youtube_transcript_api import NoTranscriptFound, YouTubeTranscriptApi

_EMBED_PREFIXES = ("/embed/", "/shorts/", "/live/")


def extract_video_id(url: str) -> str:
    url = url.strip()
    parsed = urlparse(url)
    host = parsed.netloc.lower().removeprefix("www.").removeprefix("m.")

    if host == "youtu.be":
        video_id = parsed.path.lstrip("/").split("/")[0]
        if video_id:
            return video_id

    if host in ("youtube.com", "music.youtube.com"):
        if parsed.path == "/watch":
            video_id = parse_qs(parsed.query).get("v", [None])[0]
            if video_id:
                return video_id
        for prefix in _EMBED_PREFIXES:
            if parsed.path.startswith(prefix):
                video_id = parsed.path[len(prefix):].split("/")[0]
                if video_id:
                    return video_id

    raise ValueError(f"Could not extract a YouTube video ID from URL: {url}")


def fetch_transcript_text(video_id: str, max_chars: int) -> str:
    api = YouTubeTranscriptApi()
    try:
        fetched = api.fetch(video_id, languages=["en"])
    except NoTranscriptFound:
        transcript_list = api.list(video_id)
        fetched = next(iter(transcript_list)).fetch()

    text = " ".join(snippet.text for snippet in fetched.snippets)
    return text[:max_chars]

import pytest

from app.services.youtube import extract_video_id

VALID_CASES = [
    ("https://www.youtube.com/watch?v=dQw4w9WgXcQ", "dQw4w9WgXcQ"),
    ("https://www.youtube.com/watch?v=dQw4w9WgXcQ&list=PL123&t=30s", "dQw4w9WgXcQ"),
    ("https://youtu.be/dQw4w9WgXcQ", "dQw4w9WgXcQ"),
    ("https://youtu.be/dQw4w9WgXcQ?si=abc123", "dQw4w9WgXcQ"),
    ("https://www.youtube.com/embed/dQw4w9WgXcQ", "dQw4w9WgXcQ"),
    ("https://www.youtube.com/shorts/dQw4w9WgXcQ", "dQw4w9WgXcQ"),
    ("https://m.youtube.com/watch?v=dQw4w9WgXcQ", "dQw4w9WgXcQ"),
    ("  https://youtu.be/dQw4w9WgXcQ  ", "dQw4w9WgXcQ"),
]


@pytest.mark.parametrize("url, expected_id", VALID_CASES)
def test_extract_video_id_valid(url, expected_id):
    assert extract_video_id(url) == expected_id


@pytest.mark.parametrize(
    "url",
    [
        "not a url at all",
        "https://example.com/watch?v=dQw4w9WgXcQ",
        "https://www.youtube.com/",
        "https://www.youtube.com/watch",
    ],
)
def test_extract_video_id_invalid(url):
    with pytest.raises(ValueError):
        extract_video_id(url)

from langgraph.graph import END

from app.graph.nodes import route_after_titles, route_after_transcript, route_input, route_translation


def test_route_input_youtube():
    assert route_input({"input_type": "youtube"}) == "fetch_transcript"


def test_route_input_topic():
    assert route_input({"input_type": "topic"}) == "brainstorm_titles"


def test_route_after_transcript_error_short_circuits():
    assert route_after_transcript({"error": "boom"}) == END


def test_route_after_transcript_ok():
    assert route_after_transcript({}) == "brainstorm_titles"


def test_route_after_titles_error_short_circuits():
    assert route_after_titles({"error": "boom"}) == END


def test_route_after_titles_ok():
    assert route_after_titles({}) == "generate_content"


def test_route_translation_error_short_circuits():
    assert route_translation({"error": "boom", "target_language": "french"}) == END


def test_route_translation_no_language():
    assert route_translation({}) == END


def test_route_translation_unsupported_language():
    assert route_translation({"target_language": "klingon"}) == END


def test_route_translation_supported_language():
    assert route_translation({"target_language": "french"}) == "translate"

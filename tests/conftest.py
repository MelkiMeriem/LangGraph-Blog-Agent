import os
from types import SimpleNamespace

import pytest

os.environ.setdefault("GROQ_API_KEY", "test-dummy-key")

from app.graph import nodes as graph_nodes  # noqa: E402


class _StructuredStub:
    def __init__(self, value):
        self._value = value

    def invoke(self, prompt):
        return self._value


class FakeChatModel:
    def invoke(self, prompt):
        return SimpleNamespace(content="# Fake Blog Title\n\nThis is fake generated blog content.")

    def with_structured_output(self, schema, **kwargs):
        if schema is graph_nodes.TitleSuggestions:
            return _StructuredStub(
                graph_nodes.TitleSuggestions(
                    titles=["Fake Title One", "Fake Title Two"],
                    selected_title="Fake Title One",
                )
            )
        if schema is graph_nodes.TranslatedBlog:
            return _StructuredStub(
                graph_nodes.TranslatedBlog(
                    translated_title="Titre Faux",
                    translated_content="# Titre Faux\n\nContenu de blog faux généré.",
                )
            )
        raise ValueError(f"Unexpected structured output schema in test double: {schema}")


@pytest.fixture
def fake_llm(monkeypatch):
    monkeypatch.setattr(graph_nodes, "get_llm", lambda temperature: FakeChatModel())


@pytest.fixture
def fake_transcript(monkeypatch):
    monkeypatch.setattr(
        graph_nodes,
        "fetch_transcript_text",
        lambda video_id, max_chars: "This is a fake transcript about test automation.",
    )

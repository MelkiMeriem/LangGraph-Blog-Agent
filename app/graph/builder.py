from functools import lru_cache

from langgraph.graph import END, START, StateGraph

from app.graph import nodes as N
from app.graph.state import GraphState


def build_graph():
    g = StateGraph(GraphState)

    g.add_node("fetch_transcript", N.fetch_transcript_node)
    g.add_node("brainstorm_titles", N.brainstorm_titles_node)
    g.add_node("generate_content", N.generate_content_node)
    g.add_node("translate", N.translate_node)

    g.add_conditional_edges(
        START,
        N.route_input,
        {"fetch_transcript": "fetch_transcript", "brainstorm_titles": "brainstorm_titles"},
    )
    g.add_conditional_edges(
        "fetch_transcript",
        N.route_after_transcript,
        {"brainstorm_titles": "brainstorm_titles", END: END},
    )
    g.add_conditional_edges(
        "brainstorm_titles",
        N.route_after_titles,
        {"generate_content": "generate_content", END: END},
    )
    g.add_conditional_edges(
        "generate_content",
        N.route_translation,
        {"translate": "translate", END: END},
    )
    g.add_edge("translate", END)

    return g.compile()


@lru_cache(maxsize=1)
def get_compiled_graph():
    return build_graph()

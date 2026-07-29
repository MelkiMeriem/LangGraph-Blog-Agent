from app.graph.builder import build_graph


def test_graph_compiles():
    build_graph()


def test_graph_nodes_and_edges():
    graph = build_graph().get_graph()

    node_names = set(graph.nodes.keys())
    assert node_names == {
        "__start__",
        "fetch_transcript",
        "brainstorm_titles",
        "generate_content",
        "translate",
        "__end__",
    }

    edge_pairs = {(e.source, e.target) for e in graph.edges}
    assert edge_pairs == {
        ("__start__", "fetch_transcript"),
        ("__start__", "brainstorm_titles"),
        ("fetch_transcript", "brainstorm_titles"),
        ("fetch_transcript", "__end__"),
        ("brainstorm_titles", "generate_content"),
        ("brainstorm_titles", "__end__"),
        ("generate_content", "translate"),
        ("generate_content", "__end__"),
        ("translate", "__end__"),
    }

    conditional_edges = {(e.source, e.target) for e in graph.edges if e.conditional}
    assert ("translate", "__end__") not in conditional_edges

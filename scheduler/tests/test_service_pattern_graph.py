from scheduler.network import create_scheduler_network
from scheduler.service_pattern_graph import ServicePatternGraph
from scheduler.tests.data import route_patterns


def test_create_service_pattern_graph():
    sn = create_scheduler_network(route_patterns)
    graph = ServicePatternGraph.from_scheduler_network(sn)
    # Check that the right nodes were created
    node_tags = [graph.get_node_tag(n) for n in graph.nodes]
    all_node_tags = [{"a"}, {"c"}, {"d"}, {"f"}, {"g"}, {"h"}, {"i"}]
    assert node_tags == all_node_tags
    roots = graph._get_roots()
    # Check for root
    root = list(roots)[0]
    assert len(roots) == 1 and graph.get_node_tag(root) == {"d"}
    # Check that `accepts` walks the graph upwards
    seen = []

    def accept(node):
        seen.append(graph.get_node_tag(node))
        return True

    graph.accepts(accept)
    assert all(tag in seen for tag in all_node_tags)

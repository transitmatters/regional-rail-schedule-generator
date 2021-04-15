from scheduler.network import create_scheduler_network, get_key_stations
from scheduler.tests.data import route_patterns


def test_create_scheduler_network():
    sn = create_scheduler_network(route_patterns)
    assert set(node.id for node in sn.nodes.values()) == get_key_stations(
        route_patterns
    )

    def _successor_ids_for(node):
        succs = set()
        for (parent, child) in sn.edges:
            if parent == node:
                succs.add(child.id)
        return succs

    assert _successor_ids_for(sn.nodes["a"]) == {"c", "d"}
    assert _successor_ids_for(sn.nodes["h"]) == set()
    assert _successor_ids_for(sn.nodes["g"]) == {"h", "i"}

from typing import Set, List, Dict
from functools import cache
from frozendict import frozendict

from scheduler.network import Node as NetworkNode, Service, SchedulerNetwork

ServicePattern = Dict[str, int]  # actually a frozendict


def _canonicalize_travel_times(
    ordered_services: List[Service], node: NetworkNode
) -> Dict[str, int]:
    baseline_service_id = ordered_services[0].id
    res = {}
    for service in ordered_services:
        travel_time = service.trip_time_to_node_seconds(node)
        res[service.id] = travel_time
    baseline_travel_time = res[baseline_service_id]
    for (service_id, travel_time) in res.items():
        res[service_id] = travel_time - baseline_travel_time
    return res


def _get_service_pattern(node: NetworkNode, network: SchedulerNetwork) -> ServicePattern:
    items = []
    services_for_node = network.get_services_for_node(node)
    ordered_services = sorted(services_for_node, key=lambda s: s.id)
    travel_times = _canonicalize_travel_times(ordered_services, node)
    for service in ordered_services:
        travel_time_to_node = travel_times[service.id]
        items.append((service.id, travel_time_to_node))
    return frozendict(items)


@cache
def _get_services_for_pattern(pattern: ServicePattern):
    res = set()
    for service in pattern.keys():
        res.add(service)
    return frozenset(res)


@cache
def _service_is_ancestor(maybe_ancestor: ServicePattern, maybe_descendant: ServicePattern):
    if maybe_ancestor == maybe_descendant:
        return False
    ancestor_services = _get_services_for_pattern(maybe_ancestor)
    descendant_services = _get_services_for_pattern(maybe_descendant)
    return descendant_services < ancestor_services


def _get_parents_for_service_pattern(patterns: Set[ServicePattern], target: ServicePattern):
    parents = set()
    for other in patterns:
        is_ancestor = _service_is_ancestor(other, target)
        if is_ancestor:
            is_ancestor_of_parent = any(_service_is_ancestor(other, parent) for parent in parents)
            if not is_ancestor_of_parent:
                parents.add(other)
                for parent in set(parents):
                    if _service_is_ancestor(parent, other):
                        parents.remove(parent)
    return frozenset(parents)


class ServicePatternGraph:
    def __init__(self):
        self.nodes = []
        self.node_tags = {}
        self.edges = []
        self.finalized = False

    def _tag_node(self, node: ServicePattern, tag: str):
        assert not self.finalized
        tags = self.node_tags.setdefault(node, set())
        tags.add(tag)

    def _ingest_node(self, network_node: NetworkNode, network: SchedulerNetwork):
        assert not self.finalized
        service_pattern = _get_service_pattern(network_node, network)
        self._tag_node(service_pattern, network_node.id)
        self.nodes.append(service_pattern)

    def _finalize(self):
        assert not self.finalized
        for node in self.nodes:
            parents = _get_parents_for_service_pattern(self.nodes, node)
            for parent in parents:
                self.edges.append((parent, node))
        self.finalized = True

    @cache
    def get_node_tag(self, node: ServicePattern):
        return self.node_tags[node]

    @cache
    def _get_roots(self):
        assert self.finalized
        roots = set(self.nodes)
        for (_, child) in self.edges:
            roots.discard(child)
        return frozenset(roots)

    @cache
    def _get_children(self, node: ServicePattern):
        children = set()
        for (parent, child) in self.edges:
            if parent == node:
                children.add(child)
        return frozenset(children)

    def accepts(self, callback_for_each_node):
        @cache
        def inner(node):
            children = self._get_children(node)
            if all(inner(child) for child in children):
                return callback_for_each_node(node)
            return False

        return all(inner(root) for root in self._get_roots())

    @classmethod
    def from_scheduler_network(cls, network: SchedulerNetwork):
        graph = cls()
        for node in network.nodes.values():
            graph._ingest_node(node, network)
        graph._finalize()
        return graph

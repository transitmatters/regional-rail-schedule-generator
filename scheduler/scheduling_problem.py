from dataclasses import dataclass
from functools import cached_property
from typing import Dict

from synthesize.util import listify
from scheduler.network import SchedulerNetwork


@dataclass
class SchedulingProblem:
    trips_per_period: Dict[str, int]
    network: SchedulerNetwork
    dispatch_spacing_time: int = 60
    exclusion_time: int = 60
    period: int = 3600

    @cached_property
    def _headways_by_service_id(self):
        res = {}
        for key, value in self.trips_per_period.items():
            if value:
                res[key] = self.period // value
        return res

    def get_service_headway(self, service):
        service_id = service if isinstance(service, str) else service.id
        return self._headways_by_service_id[service_id]

    @cached_property
    def nodes(self):
        return self.network.nodes

    @cached_property
    def services(self):
        return {
            service_id: value
            for (service_id, value) in self.network.services.items()
            if self.trips_per_period.get(service_id)
        }

    @cached_property
    def total_dispatches(self):
        total = 0
        for value in self.trips_per_period.values():
            total += value
        return total

    @listify
    def node_ids_for_service_id(self, service_id: str):
        service = self.network.services[service_id]
        for node in service.calls_at_nodes:
            yield node.id

    def trip_time_to_node(self, service_id: str, node_id: str):
        service = self.network.services[service_id]
        node = self.network.nodes[node_id]
        return service.trip_time_to_node_seconds(node)

    def is_dispatching_node(self, service_id: str, node_id: str):
        service = self.network.services[service_id]
        node = self.network.nodes[node_id]
        return service.calls_at_nodes[0] == node

    @listify
    def dispatched_services_for_node_id(self, node_id: str):
        for service_id in self.network.services.keys():
            if self.is_dispatching_node(service_id, node_id):
                yield service_id

    @listify
    def services_for_node_id(self, node_id: str):
        node = self.network.nodes[node_id]
        for service in self.network.services.values():
            if node in service.calls_at_nodes:
                yield service.id

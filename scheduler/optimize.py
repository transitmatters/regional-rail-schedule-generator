import itertools
import cvxpy as cp

from scheduler.variables import Variables
from scheduler.network import SchedulerNetwork, Service, Node


def get_trip_arrivals_for_node(network: SchedulerNetwork, node: Node):
    services_for_node = network.get_services_for_node(node)
    for service in services_for_node:
        for trip_number in range(service.trips_per_hour):
            yield (service, trip_number)


def get_trip_intersections_for_node(network: SchedulerNetwork, node: Node):
    services_for_node = list(network.get_services_for_node(node))
    for (s1, s2) in itertools.combinations_with_replacement(services_for_node, 2):
        trips_1 = range(s1.trips_per_hour)
        trips_2 = range(s2.trips_per_hour)
        for (t1, t2) in itertools.product(trips_1, trips_2):
            if not (s1 == s2 and t1 == t2):
                yield (s1, t1, s2, t2)


def get_indexed_arrival_expression(variables: Variables, service: Service, index: int, node: Node):
    # Returns an expression representing the time that a trip on a given service arrives at node.
    offset = variables.get_departure_offset_variable_name(service)
    trip_time = service.trip_time_to_node_seconds(node)
    if trip_time is None:
        raise ValueError("Got invalid trip time")
    return offset + service.headway_seconds * index + trip_time


def get_constraints_for_node(network: SchedulerNetwork, variables: Variables, node: Node):
    # Create safety constraints between all services at a given node
    max_diff = 12000
    for (s1, t1, s2, t2) in get_trip_intersections_for_node(network, node):
        # We want to create the constraint that abs(arrival_1 - arrival_2) > = exclusion_time
        # See http://lpsolve.sourceforge.net/5.1/absolute.htm for the technique used here.
        A_1 = get_indexed_arrival_expression(variables, s1, t1, node)
        A_2 = get_indexed_arrival_expression(variables, s2, t2, node)
        boolean = variables.get_exclusion_variable_name(node, s1, t1, s2, t2)
        # Yield one case where A_1 - A_2 >= 0
        yield (A_1 - A_2) + max_diff * boolean - node.exclusion_time >= 0
        # And one where A_2 - A_1 >= 0
        yield (A_2 - A_1) + max_diff - max_diff * boolean - node.exclusion_time >= 0


def get_scheduler_constraints(network: SchedulerNetwork, variables: Variables):
    constraints = []
    for node in network.nodes.values():
        constraints += get_constraints_for_node(network, variables, node)
    for service in network.services.values():
        last_trip_index = service.trips_per_hour - 1
        first_trip_node = service.calls_at_nodes[0]
        last_arrival_at_first_node = get_indexed_arrival_expression(
            variables, service, last_trip_index, first_trip_node
        )
        constraints.append(last_arrival_at_first_node <= 60 * 59.999)
    return constraints


def get_objective_function(network: SchedulerNetwork, variables: Variables):
    fn = 0
    for node in network.nodes.values():
        arrivals_at_node = []
        for (service, trip_number) in get_trip_arrivals_for_node(network, node):
            arrival = get_indexed_arrival_expression(variables, service, trip_number, node)
            arrivals_at_node.append(arrival)
        num_arrivals = len(arrivals_at_node)
        average_arrival_time = sum(arrivals_at_node) / num_arrivals
        sum_square_differences = sum((a - average_arrival_time) ** 2 for a in arrivals_at_node)
        variance = sum_square_differences / (num_arrivals - 1)
        fn += variance
    return fn


def solve_departure_offsets_for_services(network: SchedulerNetwork):
    variables = Variables()
    constraints = get_scheduler_constraints(network, variables)
    objective = get_objective_function(network, variables)
    problem = cp.Problem(cp.Minimize(objective), constraints)
    problem.solve(solver=cp.GUROBI)
    offsets = {}
    for service in network.services.values():
        departure_offset = variables.get_departure_offset_variable_name(service)
        offsets[service.id] = departure_offset.value
    return offsets

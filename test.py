import itertools
import numpy as np
import networkx as nx
import cvxpy as cp


class Service(object):
    def __init__(self, name, route, trips_per_period):
        self.name = name
        self.route = route
        self.trips_per_period = trips_per_period


def get_arrival_time_variable_name(node, service, index):
    return f"arrival_{service.name}_{index}_{node}"


def get_safety_constraint_variable_name(node, service_a, index_a, service_b, index_b):
    return f"bool_{node}_{service_a.name}_{index_a}_{service_b.name}_{index_b}"


def get_services_for_node(services, node):
    for service in services:
        if node in service.route:
            yield service


def get_pairwise_departures_for_service(service, variables):
    trips = list(range(service.trips_per_period))
    depart_from = service.route[0]
    for (trip_1, trip_2) in zip(trips, trips[1:]):
        var_1 = variables[get_arrival_time_variable_name(depart_from, service, trip_1)]
        var_2 = variables[get_arrival_time_variable_name(depart_from, service, trip_2)]
        yield (var_1, var_2)


def get_trip_intersections_for_node(node, services):
    services_for_node = get_services_for_node(services, node)
    for (s1, s2) in itertools.combinations_with_replacement(services_for_node, 2):
        trips_1 = range(s1.trips_per_period)
        trips_2 = range(s2.trips_per_period)
        for (t1, t2) in itertools.product(trips_1, trips_2):
            if not (s1 == s2 and t1 == t2):
                yield (s1, t1, s2, t2)


def create_problem_variables_dict(graph, services):
    variables = {}
    # For each node, for each trip on each service that passes through the node, create a variable
    # that represents the arrival time of the trip at that node.
    for node in graph:
        for service in get_services_for_node(services, node):
            for index in range(service.trips_per_period):
                name = get_arrival_time_variable_name(node, service, index)
                variables[name] = cp.Variable(name=name, nonneg=True)
    # For every node in the graph where two services intersect, we also need a boolean variable
    # to help us model the absolute value in the following constraint:
    #   | ( T_i + D_i) - (T_j + D_j) | >= T_safe_follow
    # Where i and j represent distinct trips, T_i and T_j represent the time that each trip takes
    # to arrive at the node (constants based on the structure of the network) and D_i and D_j are
    # sums of headway variables within a trip: sum(h_0...h_n) up to trip i or j.
    # Sooooo...for each node...
    for node in graph:
        # For each pair of trips intersecting at the node...
        for (s1, t1, s2, t2) in get_trip_intersections_for_node(node, services):
            # Create a boolean variable for the node/trip/trip triplet.
            name = get_safety_constraint_variable_name(node, s1, t1, s2, t2)
            variables[name] = cp.Variable(name=name, boolean=True)
    return variables


def get_constraints_for_node(node, services, variables, exclusion_time, max_diff):
    # Create safety constraints between all services on all routes
    for (s1, t1, s2, t2) in get_trip_intersections_for_node(node, services):
        # We want to create the constraint that abs(arrival_1 - arrival_2) > = exclusion_time
        # See http://lpsolve.sourceforge.net/5.1/absolute.htm for the technique used here.
        A_1 = variables[get_arrival_time_variable_name(node, s1, t1)]
        A_2 = variables[get_arrival_time_variable_name(node, s2, t2)]
        boolean = variables[get_safety_constraint_variable_name(node, s1, t1, s2, t2)]
        # Yield one case where A_1 - A_2 >= 0
        yield (A_1 - A_2) + max_diff * boolean - exclusion_time >= 0
        # And one where A_2 - A_1 >= 0
        yield (A_2 - A_1) + max_diff - max_diff * boolean - exclusion_time >= 0


def get_constraints_for_service(service, graph, variables):
    # For each trip on the service, for each node the service passes through, constraint the
    # difference in arrival time variables to the travel time between nodes. For instance on route
    # R with nodes a->b->c, where a->b takes 5 minutes and B=b->c takes 7 minutes we have:
    # arrival_b_R_k - arrival_a_R_k - 5 = 0, arrival_c_R_k - arrival_b_R_k - 7 = 0, etc.
    # So, for each trip on the service
    for trip_index in range(service.trips_per_period):
        # For each pair of nodes the service passes through...
        for first, second in zip(service.route, service.route[1:]):
            A_1 = variables[get_arrival_time_variable_name(first, service, trip_index)]
            A_2 = variables[get_arrival_time_variable_name(second, service, trip_index)]
            travel_time = graph.edges[first, second]["time"]
            yield A_2 - A_1 == travel_time


def get_departure_bounds_constraints(services, variables, period):
    for service in services:
        # For conveniences' sake, ensure that every indexed trip leaves before the next one
        # Otherwise the solver might decide that service A's trip 1 leaves before trip 0, which is
        # fine but annoying to deal with.
        for (dep_1, dep_2) in get_pairwise_departures_for_service(service, variables):
            yield dep_1 <= dep_2
        # Finally ensure the last trip leaves before the period is over
        yield dep_2 <= period


def get_objective_function(services, variables, period):
    fn = 0
    for service in services:
        desired_headway = period / (service.trips_per_period + 1)
        for (dep_1, dep_2) in get_pairwise_departures_for_service(service, variables):
            fn += ((dep_2 - dep_1) - desired_headway) ** 4
    return fn


def build_solver(graph, services, period=60):
    variables = create_problem_variables_dict(graph, services)
    constraints = []
    constraints += get_departure_bounds_constraints(services, variables, period)
    for node in graph:
        constraints += get_constraints_for_node(node, services, variables, 1, 120)
    for service in services:
        constraints += get_constraints_for_service(service, graph, variables)
    objective = get_objective_function(services, variables, period)
    print(objective)
    problem = cp.Problem(cp.Minimize(objective), constraints)
    problem.solve()
    if problem.status not in ["infeasible", "unbounded"]:
        print("STATUS", problem.status)
        for service in services:
            for index in range(service.trips_per_period):
                for node in service.route[0:1]:
                    var_name = get_arrival_time_variable_name(node, service, index)
                    variable = variables[var_name]
                    print(variable.name(), round(variable.value, 2) % period)


N = nx.Graph()
N.add_nodes_from("abcdef")
N.add_edge("a", "c", time=20)
N.add_edge("b", "c", time=30)
N.add_edge("c", "d", time=5)
N.add_edge("d", "e", time=60)
N.add_edge("d", "f", time=40)

services = [Service("A", "acdf", 6), Service("B", "acde", 10), Service("C", "bcde", 4)]

build_solver(N, services)

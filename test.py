import itertools
import numpy as np
import networkx as nx
import cvxpy as cp


class Node(object):
    def __init__(self, name, exclusion_time):
        self.name = name
        self.exclusion_time = exclusion_time

    def __str__(self):
        return self.name


class Terminus(Node):
    def __init__(self, name):
        super().__init__(name, 3)


class Junction(Node):
    def __init__(self, name):
        super().__init__(name, 1)


class Service(object):
    def __init__(self, name, route, trips_per_period):
        self.name = name
        self.route = route
        self.trips_per_period = trips_per_period


def create_route(graph, string):
    route = []
    for s in string:
        print(s, graph[s])
        route.append(graph.nodes[s])
    return route


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
    #   | A_i - A_j | >= T_exclusion
    # Where A_i and A_j represent distinct arrivals at the node.
    for node in graph:
        # For each pair of trips intersecting at the node...
        for (s1, t1, s2, t2) in get_trip_intersections_for_node(node, services):
            # Create a boolean variable for the node/trip/trip triplet.
            name = get_safety_constraint_variable_name(node, s1, t1, s2, t2)
            variables[name] = cp.Variable(name=name, boolean=True)
    return variables


def get_constraints_for_node(node, services, variables, max_diff):
    # Create safety constraints between all services on all routes
    for (s1, t1, s2, t2) in get_trip_intersections_for_node(node, services):
        # We want to create the constraint that abs(arrival_1 - arrival_2) > = exclusion_time
        # See http://lpsolve.sourceforge.net/5.1/absolute.htm for the technique used here.
        A_1 = variables[get_arrival_time_variable_name(node, s1, t1)]
        A_2 = variables[get_arrival_time_variable_name(node, s2, t2)]
        boolean = variables[get_safety_constraint_variable_name(node, s1, t1, s2, t2)]
        # Yield one case where A_1 - A_2 >= 0
        yield (A_1 - A_2) + max_diff * boolean - node.exclusion_time >= 0
        # And one where A_2 - A_1 >= 0
        yield (A_2 - A_1) + max_diff - max_diff * boolean - node.exclusion_time >= 0


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
        # For convenience's sake, ensure that every indexed trip leaves before the next one
        # Otherwise the solver might decide that service A's trip 1 leaves before trip 0, which is
        # fine but annoying to deal with.
        if service.trips_per_period > 1:
            for (dep_1, dep_2) in get_pairwise_departures_for_service(
                service, variables
            ):
                last = dep_2 or dep_1
                yield dep_1 <= dep_2
            # Finally ensure the last trip leaves before the period is over
            yield last <= period
        else:
            name = get_arrival_time_variable_name(service.route[0], service, 0)
            trip = variables[name]
            yield trip <= period


def get_objective_function(services, variables, period):
    fn = 0
    for service in services:
        desired_headway = period / service.trips_per_period
        for (dep_1, dep_2) in get_pairwise_departures_for_service(service, variables):
            fn += desired_headway * ((dep_2 - dep_1) - desired_headway) ** 2
    return fn


def build_solver(graph, services, period=60):
    variables = create_problem_variables_dict(graph, services)
    constraints = []
    constraints += get_departure_bounds_constraints(services, variables, period)
    for node in graph:
        constraints += get_constraints_for_node(node, services, variables, 12000)
    for service in services:
        constraints += get_constraints_for_service(service, graph, variables)
    objective = get_objective_function(services, variables, period)
    problem = cp.Problem(cp.Minimize(objective), constraints)
    problem.solve(solver=cp.GUROBI)
    if problem.status not in ["infeasible", "unbounded"]:
        print("STATUS", problem.status)
        for node in graph:
            service_times = []
            for service in get_services_for_node(services, node):
                for index in range(service.trips_per_period):
                    name = get_arrival_time_variable_name(node, service, index)
                    service_times.append(
                        (service.name, int(variables[name].value), index)
                    )
            print(
                node,
                " ".join(
                    [
                        f"{name}-{time}"
                        for (name, time, _) in sorted(service_times, key=lambda st: st[1])
                    ]
                ),
            )

N = nx.Graph()

q = Terminus("q")
a = Terminus("a")
b = Terminus("b")
f = Terminus("f")
e = Terminus("e")
c = Terminus("c")
d = Terminus("d")

A = Service("A", [a, c, d, f], 6)
B = Service("B", [a, c, d, e], 4)
C = Service("C", [b, c, d, e], 4)
D = Service("D", [q, c, d, f], 8)

services = [A, B, C, D]


N.add_nodes_from([q, a, f, e, c, d])

N.add_edge(q, c, time=15)
N.add_edge(a, c, time=20)
N.add_edge(b, c, time=30)
N.add_edge(c, d, time=5)
N.add_edge(d, e, time=60)
N.add_edge(d, f, time=40)


build_solver(N, services)

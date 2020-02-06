import numpy as np
import networkx as nx
import solver
import qpsolvers


class Service(object):
    def __init__(self, route, trips_per_period):
        self.route = route
        self.trips_per_period = trips_per_period


def get_travel_time(graph, route, target_node):
    total_time = 0
    for first, second in zip(route, route[1:]):
        if first == target_node:
            return total_time
        edge = graph.edges[first, second]
        if not edge:
            raise Exception(f"Graph does not contain route {route}.")
        total_time += edge.get("time")
    return total_time


def create_trip_indexer(services):
    service_tph = [service.trips_per_period for service in services]
    trip_count = sum(service_tph)

    def get_index(service, trip_index):
        service_index = services.index(service)
        return sum(service_tph[0:service_index]) + trip_index

    return get_index, trip_count


def get_travel_time_vector_for_node(
    graph, node, services, get_trip_index, trip_count, dim
):
    T = np.zeros((dim, 1))
    for service in services:
        for trip_index in range(service.trips_per_period):
            matrix_index = get_trip_index(service, trip_index)
            if node in service.route:
                travel_time = get_travel_time(graph, service.route, node)
                T[matrix_index,] = travel_time
    return T


def get_trip_indices_for_node(node, services, get_trip_index):
    indices = []
    for service in services:
        for trip_index in range(service.trips_per_period):
            if node in service.route:
                indices.append(get_trip_index(service, trip_index))
    return indices


def get_qp_matrices_for_node(
    graph, node, services, get_trip_index, trip_count, period, dim, safe_follow=1
):
    # Maximum value chosen to create constraints on absolute value:
    # |(T_m + x_m) - (T_n + x_n)| >= T_safe
    # (see http://lpsolve.sourceforge.net/5.1/absolute.htm)
    M = 1000
    # quadratic bunching matrix, item (m,n) indicates relationship between trips (m,n)
    Bn = np.zeros((dim, dim))
    # linear bunching matrix (denoted in the literature as c-transpose)
    bn = np.zeros((1, dim))
    # travel time matrix
    Tn = get_travel_time_vector_for_node(
        graph, node, services, get_trip_index, trip_count, dim
    )
    # Trip indices visited by this node
    trip_indices = get_trip_indices_for_node(node, services, get_trip_index)

    # Generate quadratic and linear bunching matrices
    for row in range(trip_count):
        for col in range(trip_count):
            is_intersection = row in trip_indices and col in trip_indices
            if row == col:
                Bn[row, col] = 2
            elif is_intersection:
                Bn[row, col] = -2
        if row == trip_indices[0]:
            term = (2 * trip_count) / period + 1 + 1 / trip_count
            bn[0, row] = term
        elif row == trip_indices[-1]:
            term = (1 / trip_count) - (2 * trip_count) / period + 1
            bn[0, row] = term

    # Generate safety constrain matrices
    constraint_rows = []
    constraint_constants = []
    for first in range(trip_count):
        period_max_row = np.zeros(dim)
        period_max_row[first] = 1
        constraint_rows.append(period_max_row)
        constraint_constants.append(period)
        period_min_row = np.zeros(dim)
        period_min_row[first] = -1
        constraint_rows.append(period_min_row)
        constraint_constants.append(0)
        for second in range(trip_count):
            is_intersection = first in trip_indices and second in trip_indices
            if is_intersection and first < second:
                binary_offset = first + ((second - 1) ** 2 + (second - 1)) // 2
                binary_constraint_index = trip_count + binary_offset
                # Case of T_first_arrival - T_second_arrival > 0
                positive_row = np.zeros(dim)
                positive_row[first] = -1
                positive_row[second] = 1
                positive_row[binary_constraint_index] = 0 - M
                positive_constant = Tn[first, 0] - Tn[second, 0] - safe_follow
                constraint_rows.append(positive_row)
                constraint_constants.append(positive_constant)
                # Case of T_first_arrival - T_second_arrival < 0
                negative_row = np.zeros(dim)
                negative_row[first] = 1
                negative_row[second] = -1
                negative_row[binary_constraint_index] = M
                negative_constant = M + Tn[second, 0] - Tn[first, 0] - safe_follow
                constraint_rows.append(negative_row)
                constraint_constants.append(negative_constant)
                # Finally, B <= 1
                binary_constraint_row = np.zeros(dim)
                binary_constraint_row[binary_constraint_index] = 1
                binary_constraint_constant = 1
                constraint_rows.append(binary_constraint_row)
                constraint_constants.append(binary_constraint_constant)
                # print(positive_row, positive_constant)
                # print(negative_row, negative_constant)
                # print(binary_constraint_row, binary_constraint_constant)
    Q = Bn
    cT = bn + np.matmul(Bn, Tn).transpose() + np.matmul(Tn.transpose(), Bn)
    A = np.array(constraint_rows).reshape((-1, dim))
    B = np.array(constraint_constants)
    return Q, cT, A, B


def build_solver(graph, services, period=60):
    get_trip_index, trip_count = create_trip_indexer(services)
    dim = trip_count + (trip_count ** 2 - trip_count) // 2
    Q = np.zeros((dim, dim))
    cT = np.zeros((1, dim))
    As = []
    Bs = []
    # Find constraint and objective matrices at each node in network
    for node in graph.nodes:
        Q_n, cT_n, A_n, B_n = get_qp_matrices_for_node(
            graph, node, services, get_trip_index, trip_count, period, dim
        )
        Q = Q + Q_n
        cT = cT + cT_n
        As.append(A_n)
        Bs.append(B_n)
    A = np.concatenate(As, axis=0)
    B = np.concatenate(Bs).reshape(-1)
    cT = cT.reshape(-1)
    print(dim, A.shape, B.shape, cT.shape, Q.shape)
    print(A)
    print(B)
    print(solver.gurobi_solve_qp(Q, cT, A, B))


N = nx.Graph()
N.add_nodes_from("abcdef")
N.add_edge("a", "c", time=20)
N.add_edge("b", "c", time=30)
N.add_edge("c", "d", time=5)
N.add_edge("d", "e", time=60)
N.add_edge("d", "f", time=40)

services = [Service("acdf", 1), Service("acde", 1), Service("bcde", 1)]
build_solver(N, services)
